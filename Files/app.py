import streamlit as st
import pandas as pd
from io import BytesIO
import os
from PIL import Image
from model import extract_info_img_paid_out , extract_info_img_paid_in , extract_account_details
from data_output import json_to_csv, json_to_xls
import time

def create_UI():
    st.set_page_config("Receipt2Sheet 2.0", initial_sidebar_state="collapsed")
    st.markdown(
        """
        <style>
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateX(-20px); }
            100% { opacity: 1; transform: translateX(0); }
        }

        .welcome-message {
            font-size: 48px; /* Adjust font size */
            text-align: center;
            color: white; /* Text color */
            animation: fadeIn 2.0s ease forwards; /* Apply animation */
            margin-top: 50px; /* Space above the message */
        }

        .stTextInput > div > input {
            height: 100%;  /* Adjust height */
            width: 100%;   /* Adjust width */
            font-size: 14px;  /* Adjust font size */
        }

        div[data-testid="column"] {
            width: fit-content !important;
            flex: unset;
            padding-left: 20px;  /* Left padding */
        }

        div[data-testid="column"] * {
            width: fit-content !important;
            vertical-align: left;  /* Align items to the left */
        }

        .stFileUploader {
            width: 100%;  /* Make the file uploader full width */
            border-radius: 5px;  /* Rounded corners */
            text-align: center;  /* Center text */
        }

        [data-testid='stFileUploader'] section {
            padding: 0;
            float: left;
        }

        [data-testid='stFileUploader'] section > input + div {
            display: none;  /* Hide the default uploader text */
        }

        .sidebar .stSelectbox, 
        .sidebar .stButton, 
        .sidebar .stFileUploader {
            animation: fadeIn 1s ease forwards;
        }

        .sidebar {
            animation: fadeIn 1s ease forwards;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='welcome-message'>Welcome to Receipt2Sheet 2.0 !</div>", unsafe_allow_html=True)
    
    st.sidebar.title("Settings")
    
    # Language selection dropdown


    st.sidebar.title("Upload Image(s)")
    uploaded_files_images = st.sidebar.file_uploader(
        "Upload Images", type=["jpg", "png", "jpeg"], 
        accept_multiple_files=True, label_visibility="hidden"
    )

    col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2.4, 3.7, 3.4], vertical_alignment="bottom", gap="small")  # Adjust column widths

    with col1:
        option = st.selectbox(
            'Output Format', 
            ('CSV', 'XLS'),
            key="output_format"
        )

    with col2:
        generate_button = st.button("Generate")

    with col3:
        download_placeholder = st.empty()

    if generate_button and uploaded_files_images:
        st.info("Processing image(s)...")
    
    # Extract data
        json_output_paid_out = extract_info_img_paid_out(uploaded_files_images)  
        json_output_paid_in = extract_info_img_paid_in(uploaded_files_images)   
        json_output_details = extract_account_details(uploaded_files_images)

        # Merge extracted data
        merged_data = {
            "account_details": json_output_details,
            "paid_in_transactions": json_output_paid_in.get("paid_in_transactions", []),
            "paid_out_transactions": json_output_paid_out.get("paid_out_transactions", [])
        }

        # Convert account details into a DataFrame
        account_df = pd.DataFrame([merged_data["account_details"]])  # Wrap in list for single-row DF
        
        # Convert transactions into DataFrames
        paid_in_df = pd.DataFrame(merged_data["paid_in_transactions"])
        paid_out_df = pd.DataFrame(merged_data["paid_out_transactions"])

        # Add a column to indicate transaction type
        paid_in_df["Transaction Type"] = "Paid In"
        paid_out_df["Transaction Type"] = "Paid Out"

        # Combine transaction DataFrames
        transactions_df = pd.concat([paid_in_df, paid_out_df], ignore_index=True)

        # Save as CSV or XLS
        if option == "CSV":
            csv_buffer = BytesIO()
            
            # Save Account Details
            account_df.to_csv(csv_buffer, index=False)
            csv_buffer.write(b"\n")  # Add a newline between sections
            
            # Save Transactions
            transactions_df.to_csv(csv_buffer, index=False)
            
            csv_data = csv_buffer.getvalue()
            
            # Provide Download Button
            download_placeholder.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="bank_statement.csv",
                mime="text/csv"
            )

        elif option == "XLS":
            xls_buffer = BytesIO()
            with pd.ExcelWriter(xls_buffer, engine="xlsxwriter") as writer:
                account_df.to_excel(writer, sheet_name="Account Details", index=False)
                transactions_df.to_excel(writer, sheet_name="Transactions", index=False)
            
            xls_data = xls_buffer.getvalue()
            
            # Provide Download Button
            download_placeholder.download_button(
                label="Download XLS",
                data=xls_data,
                file_name="bank_statement.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        #     )

if __name__ == "__main__":
    create_UI()
