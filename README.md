

# 🏦 Bank Statement Data Extractor  

A **Streamlit-based** application that extracts account details and transactions from bank statement images, processes the data, and exports it into **CSV or Excel** format.  

## ✨ Features  
✅ Extracts **account details** from bank statements  
✅ Identifies and categorizes **Paid In** and **Paid Out** transactions  
✅ Uses **Gemini AI** for intelligent data extraction  
✅ Translates extracted text using **Google Translate API**  
✅ Merges all data into a structured **DataFrame**  
✅ Exports the processed data as **CSV or Excel**  
✅ Provides an easy **download button** for the final file  

## 📌 Tech Stack  
- **Python** 🐍  
- **Streamlit** (for UI)  
- **Google Gemini AI** (for intelligent OCR and data extraction)  
- **Pandas** (for data processing)  
- **XlsxWriter** (for Excel exports)  
- **Pillow (PIL)** (for image handling)  
- **Dotenv** (for managing API keys)  

## 🚀 How to Run  
1. Clone the repository:  
   ```bash
   git clone https://github.com/your-username/bank-statement-extractor.git
   cd bank-statement-extractor
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `keys.env` file and add your **Google Gemini API Key** and **model_name**:  
   ```
   Gemini_key=your_api_key_here
   Model_name= model-name
   ```
4. Run the Streamlit app:  
   ```bash
   streamlit run app.py
   ```
5. Upload **bank statement images** and download the extracted data.  

## 📂 Output Example  
- **CSV**: Account details and transactions saved as a structured CSV file.  
- **Excel**: Two sheets: `Account Details` & `Transactions`.  

---
