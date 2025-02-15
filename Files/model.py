import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import streamlit as st
import json
import re
import unicodedata
from googletrans import Translator  # Import Google Translate API

# Load environment variables for API keys
load_dotenv("keys.env")
google_api_key = os.getenv("Gemini_key")


def clean_item_name_general(name):
    """
    Cleans and normalizes item names for better readability and translation across languages.

    Args:
        name: The raw item name as a string.

    Returns:
        A cleaned and normalized string.
    """
    # Normalize Unicode
    name = unicodedata.normalize('NFKC', name)

    # Insert space between lowercase and uppercase letters
    name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)

    # Replace common separators with spaces
    name = re.sub(r'[._\-]', ' ', name)

    # Replace non-alphanumeric characters
    name = re.sub(r'[^\w\s]', ' ', name)

    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    return name

def refine_with_ai(json_data):
    """
    Refines the translated receipt information using AI for context-specific corrections.

    Args:
        json_data: JSON-formatted receipt data to refine.

    Returns:
        Refined JSON data as a string.
    """
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"},
    )

    # Create a new prompt for refining translation
    prompt = f'''
    Please refine the following receipt information, ensuring accuracy and proper structure AND TRANSLATE THE ITEM NAMES TO ENGLISH:
    ```json
    + ''' + json_data +''' 
    '''
    result = model.generate_content([prompt])
    return result.text  # Assuming the response is in JSON format


def extract_info_img(img_paths, language): 

    images_ = [Image.open(img_path) for img_path in img_paths]

    # Configure generative AI model
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"},
    )

    # Define prompt for initial extraction
    prompt = f'''
    Extract receipt information from the image, which is in {language}.
    Ensure all item names are written in English. If the items' names are not in English, translate them to English or provide their English equivalents.
    Extract the following information from the image:
    Shop or Mart Name
    Item Names
    Quantities (if unspecified, assume 1)
    Prices
    Currency Type (infer from context, using the full name instead of symbols)
    Structure the extracted information into the following JSON format:
    json
    Copy
    Edit
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
            // Additional items...
        ],
        "currency": "Currency Name"
        }}
        // Additional receipts...
    ]
        }}
        '''
    
    input_model = [prompt] + images_
# Extract the content using the model
    result = model.generate_content(input_model)
    result_text = result.text  # Assuming the result text is in JSON format.

    # Parse and process the result
    try:
        extracted_data = json.loads(result_text)
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response.")
        return None

    # Clean, translate, and refine item names
    for receipt in extracted_data.get('receipts', []):
        for item in receipt.get('items', []):
            # Clean and translate each item name
            cleaned_name = clean_item_name_general(item.get('item', ''))

    # Refine the translated data using AI
    refined_data = refine_with_ai(json.dumps(extracted_data, ensure_ascii=False, indent=4))

    # Return the refined JSON structure
    return refined_data
