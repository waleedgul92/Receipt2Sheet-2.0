import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import streamlit as st
import json
import unicodedata
from googletrans import Translator  # Import Google Translate API

# Load environment variables for API keys
load_dotenv("keys.env")
google_api_key = os.getenv("Gemini_key")


def extract_info_img_paid_out(img_paths):
    images_ = [Image.open(img_path) for img_path in img_paths]

    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = """
    Extract only the 'Paid out' transaction details from the bank statement image. 
    Do NOT extract or include 'Paid in' or 'Balance' data. 

    **Instructions:**
    - Identify transactions where an amount is present under 'Paid out'.
    - Ignore any transaction where 'Paid out' is missing, empty, null, or zero.
    - Do NOT extract any other columns like 'Paid in' or 'Balance'.
    - Format the extracted data in JSON.

    **Fields to Extract:**
    - **Date** (Format: 'DD MMM YY', e.g., '17 Jan 23')
    - **Payment Type & Description** (e.g., 'DD EE LIMITED', 'VIS eBay 013-09590-02 LONDON')
    - **Paid Out Amount** (Numeric value only, e.g., '2.49', '219.29')

    **Output Format (Example):**
    ```json
    {
        "paid_out_transactions": [
            {
                "date": "15 Jun 22",
                "type": "VIS",
                "description": "GATWICK DROP OFF CRAWLEY",
                "amount": "5.00"
            },
            {
                "date": "17 Jun 22",
                "type": "DD",
                "description": "EE LIMITED",
                "amount": "25.00"
            },
            {
                "date": "19 Jun 22",
                "type": "VIS",
                "description": "eBay 013-09590-02 LONDON",
                "amount": "2.49"
            }
        ]
    }
    ```
    **Rules:**
    - Remove any transaction if 'Paid out' is **null, empty, zero, or missing**.
    - Do NOT extract 'Paid in' or 'Balance' columns.
    - Ensure correct JSON structure.
    """

    input_model = [prompt] + images_
    result = model.generate_content(input_model)
    result_text = result.text  # Assuming the result is in JSON format.

    # Parse and clean the extracted data
    try:
        extracted_data = json.loads(result_text)

        # Remove transactions where 'amount' is missing, empty, null, or "0.00"
        if "paid_out_transactions" in extracted_data:
            extracted_data["paid_out_transactions"] = [
                txn for txn in extracted_data["paid_out_transactions"]
                if txn.get("amount") not in [None, "", "0.00", 0, "0"]
            ]
        
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response.")
        return None

    return extracted_data


def extract_info_img_paid_in(img_paths):
    images_ = [Image.open(img_path) for img_path in img_paths]

    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = """
    Extract only the 'Paid in' transaction details from the bank statement image.
    Do NOT extract or include 'Paid out' or 'Balance' data.

    **Instructions:**
    - Identify transactions where an amount is present under 'Paid in'.
    - Ignore any transaction where 'Paid in' is missing, empty, null, or zero.
    - Do NOT extract any other columns like 'Paid out' or 'Balance'.
    - Format the extracted data in JSON.

    **Fields to Extract:**
    - **Date** (Format: 'DD MMM YY', e.g., '17 Jan 23')
    - **Payment Type & Description** (e.g., 'CR MIDLETON J V04', 'BOB THE BUILDER (U')
    - **Paid In Amount** (Numeric value only, e.g., '390.00', '2,000.00')

    **Output Format (Example):**
    ```json
    {
        "paid_in_transactions": [
            {
                "date": "19 Jan 23",
                "type": "CR",
                "description": "Nicholas Solly & S",
                "amount": "390.00"
            },
            {
                "date": "20 Jan 23",
                "type": "CR",
                "description": "BOB THE BUILDER (U",
                "amount": "2,000.00"
            }
        ]
    }
    ```
    **Rules:**
    - Remove any transaction if 'Paid in' is **null, empty, zero, or missing**.
    - Do NOT extract 'Paid out' or 'Balance' columns.
    - Ensure correct JSON structure.
    """

    input_model = [prompt] + images_
    result = model.generate_content(input_model)
    result_text = result.text

    # Parse and clean the extracted data
    try:
        extracted_data = json.loads(result_text)

        # Remove transactions where 'amount' is missing, empty, null, or "0.00"
        if "paid_in_transactions" in extracted_data:
            extracted_data["paid_in_transactions"] = [
                txn for txn in extracted_data["paid_in_transactions"]
                if txn.get("amount") not in [None, "", "0.00", 0, "0"]
            ]
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response.")
        return None

    return extracted_data


import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import streamlit as st
import json

# Load environment variables for API keys
load_dotenv("keys.env")
google_api_key = os.getenv("Gemini_key")

# Configure Gemini AI
genai.configure(api_key=google_api_key)

def extract_account_details(uploaded_files):
    """
    Extracts account details from a bank statement image, including:
    - Image Name
    - Account Name
    - Account Number
    - Statement Period
    - Opening Balance
    - Closing Balance
    """
    images_ = [Image.open(img) for img in uploaded_files]

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = """
    Extract the following account details from the bank statement image:

    **Fields to Extract:**
    - **Image Name** (Extracted from the file name)
    - **Account Name** (e.g., 'DC ELECTRICAL & PROPERTY SERVICES LTD')
    - **Account Number** (e.g., '10123919')
    - **Statement Period** (e.g., '12 June to 30 June 2022')
    - **Opening Balance** (e.g., '564.41')
    - **Closing Balance** (e.g., '241.60')

    **Output Format (Example):**
    ```json
    {
        "img_name": "bank_statement.jpg",
        "accountName": "DC ELECTRICAL & PROPERTY SERVICES LTD",
        "accountNumber": "10123919",
        "statementPeriod": "12 June to 30 June 2022",
        "openingBalance": "564.41",
        "closingBalance": "241.60"
    }
    ```

    **Rules:**
    - Extract data accurately from the document.
    - Ignore any unrelated text or headers.
    - Ensure correct JSON formatting.
    """

    input_model = [prompt] + images_
    result = model.generate_content(input_model)
    result_text = result.text  # Assuming the result is in JSON format.

    try:
        extracted_data = json.loads(result_text)

        # Extract file name from the UploadedFile object
        extracted_data["img_name"] = uploaded_files[0].name  

    except json.JSONDecodeError:
        st.error("Failed to decode JSON response.")
        return None

    return extracted_data
