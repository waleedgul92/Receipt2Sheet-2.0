import streamlit as st
import pandas as pd
from io import BytesIO
import os
from PIL import Image
from model import extract_info_img
from data_output import json_to_csv, json_to_xls
import time

def create_UI():
    st.set_page_config("Receipt2Sheet", initial_sidebar_state="collapsed")
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
            vertical-align: left;  /* Align items to the left */
        }

        .stFileUploader {
            width: 100%;  /* Make the file uploader full width */
            border-radius: 5px;  /* Rounded corners */
            text-align: center;  /* Center text */
        }

        [data-testid='stFileUploader'] section {
            padding: 0;
            float: left;
        }

        [data-testid='stFileUploader'] section > input + div {
            display: none;  /* Hide the default uploader text */
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

    st.markdown("<div class='welcome-message'>Welcome to Receipt2Sheet!</div>", unsafe_allow_html=True)
    
    st.sidebar.title("Settings")
    
    # Language selection dropdown
    language = st.sidebar.selectbox(
        "Select Language for Extraction",
        ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Hindi",'Urdu',"Arabic"],
        key="language_selection"
    )
    


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
        st.info(f"Processing image(s) with language: {language}...")
        json_output = extract_info_img(uploaded_files_images, language)  # Pass language to the function if supported

        if option == "CSV":
            csv_data = json_to_csv(json_output)
            download_placeholder.download_button(
                label="Download",
                data=csv_data,
                file_name="output.csv",
                mime="text/csv"
            )
        elif option == "XLS":
            xls_data = json_to_xls(json_output)
            download_placeholder.download_button(
                label="Download",
                data=xls_data.getvalue(),
                file_name="output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    create_UI()
