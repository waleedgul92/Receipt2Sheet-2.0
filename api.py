import os
import io
import json
import re
import unicodedata
from typing import List

import uvicorn
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from PIL import Image

# --- Configuration ---

# Load environment variables
load_dotenv("keys.env")
google_api_key = os.getenv("Gemini_key")
model_name = os.getenv("Model_name")

# Validate environment variables
if not google_api_key or not model_name:
    raise EnvironmentError(
        "API keys (Gemini_key, Model_name) not found in keys.env"
    )

# Configure the Generative AI client
genai.configure(api_key=google_api_key)


# --- Helper Functions ---

def _clean_ai_response(response_text: str) -> str:
    """
    Extracts the JSON string from the AI's raw text response.
    Models can sometimes wrap JSON in markdown (```json ... ```) or text.
    """
    # Find the first '{' and the last '}' to extract the JSON block
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        return match.group(0)
    
    raise ValueError("No valid JSON object found in AI response.")


def clean_item_name_general(name: str) -> str:
    """
    Cleans and normalizes item names for better readability and translation.
    """
    # Normalize Unicode
    name = unicodedata.normalize('NFKC', name)
    # Insert space between lowercase and uppercase letters
    name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)
    # Replace common separators with spaces
    name = re.sub(r'[._\-]', ' ', name)
    # Replace non-alphanumeric characters (except whitespace)
    name = re.sub(r'[^\w\s]', ' ', name)
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def refine_with_ai(json_data: str) -> str:
    """
    Refines the translated receipt information using AI for context-specific
    corrections and ensures translation to English.
    """
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={"response_mime_type": "application/json"},
    )

    # Prompt for refining and translating
    prompt = f'''
    Please refine the following receipt information, ensuring accuracy 
    and proper structure AND TRANSLATE ALL ITEM NAMES TO ENGLISH.
    Keep the existing JSON structure.
    ```json
    {json_data}
    ```
    '''
    result = model.generate_content([prompt])
    
    try:
        # Clean the response to get just the JSON
        return _clean_ai_response(result.text)
    except ValueError as e:
        raise ValueError(
            f"AI refinement failed: {e} | Raw response: {result.text}"
        )


# --- Core Logic ---

def extract_info_img(images: List[Image.Image], language: str) -> str:
    """
    Extracts, cleans, and refines receipt information from a list of images.
    
    Args:
        images: A list of PIL Image objects.
        language: The source language of the receipts.

    Returns:
        A string containing the refined JSON data.
    """
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={"response_mime_type": "application/json"},
    )

    # Define prompt for initial extraction and translation
    prompt = f'''
    Extract receipt information from the image(s), which is in {language}.
    Ensure all item names are written in English. If the items' names are not 
    in English, translate them to English or provide their English equivalents.
    Extract the following information:
    - Shop or Mart Name
    - Item Names
    - Quantities (if unspecified, assume 1)
    - Prices
    - Currency Type (infer from context, using the full name, not symbols)
    
    Structure the extracted information into the following JSON format:
    {{
    "receipts": [
        {{
        "shop": "Shop Name",
        "items": [
            {{
            "item": "Item Name",
            "quantity": 1,
            "price": 10.99
            }}
        ],
        "currency": "Currency Name"
        }}
    ]
    }}
    '''
    
    # Combine the prompt and the images
    input_model = [prompt] + images
    
    # Extract the content using the model
    result = model.generate_content(input_model)
    
    # Parse and process the initial result
    try:
        result_text = _clean_ai_response(result.text)
        extracted_data = json.loads(result_text)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(
            f"Failed to decode initial AI response: {e} | Raw response: {result.text}"
        )

    # Clean item names in the extracted data
    for receipt in extracted_data.get('receipts', []):
        for item in receipt.get('items', []):
            if 'item' in item:
                cleaned_name = clean_item_name_general(item.get('item', ''))
                item['item'] = cleaned_name  # Update the dict with the cleaned name

    # Refine the extracted and cleaned data using a second AI pass
    refined_data_string = refine_with_ai(
        json.dumps(extracted_data, ensure_ascii=False, indent=4)
    )

    return refined_data_string


# --- API Definition ---

app = FastAPI(
    title="Receipt OCR API",
    description="Extracts and translates receipt information from images."
)

@app.post("/extract_receipts/")
async def process_receipts(
    language: str = Form(
        ..., 
        description="The language of the receipt (e.g., 'Spanish', 'German')"
    ),
    files: List[UploadFile] = File(
        ..., 
        description="One or more receipt images to process"
    )
):
    """
    Upload receipt images to extract, clean, and translate item information 
    into a structured JSON format.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No image files provided.")
    
    images = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, 
                detail=f"File '{file.filename}' is not an image."
            )
        try:
            # Read file contents into a BytesIO buffer
            contents = await file.read()
            image_stream = io.BytesIO(contents)
            img = Image.open(image_stream)
            images.append(img)
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to process image '{file.filename}': {str(e)}"
            )
    
    try:
        # Call the core processing logic
        refined_json_string = extract_info_img(images=images, language=language)
        
        # Parse the final JSON string to return as a JSON object
        # FastAPI will automatically serialize this dict to a JSON response
        final_json_output = json.loads(refined_json_string)
        return final_json_output
    
    except (json.JSONDecodeError, ValueError) as e:
        # Error from AI response parsing
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing AI response: {str(e)}"
        )
    except Exception as e:
        # Other unexpected errors
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}"
        )

# --- Run the API ---

if __name__ == "__main__":
    print("Starting FastAPI server at http://127.0.0.1:8000")
    print("View API docs at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8001)