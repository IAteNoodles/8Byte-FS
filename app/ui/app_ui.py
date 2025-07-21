import streamlit as st
import requests
import pandas as pd
import base64
from datetime import datetime  # <-- ADD THIS IMPORT

# TODO: Make the base URL configurable
BACKEND_URL = "http://127.0.0.1:5000"

# --- Page Configuration ---
st.set_page_config(
    page_title="Receipt Processor",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Receipt and Bill Processor")

# --- File Uploader ---
st.header("1. Upload a Receipt")
uploaded_file = st.file_uploader(
    "Choose a receipt file",
    type=['jpg', 'png', 'pdf', 'txt'],
    key="uploader"
)

if uploaded_file is not None:
    # When a new file is uploaded, store its bytes and extension in the session state
    st.session_state.file_bytes = uploaded_file.getvalue()
    st.session_state.file_extension = uploaded_file.name.rsplit('.', 1)[1].lower()
    
    with st.spinner('Processing file...'):
        files = {'file': (uploaded_file.name, st.session_state.file_bytes, uploaded_file.type)}
        try:
            response = requests.post(f"{BACKEND_URL}/process-receipt", files=files)
            if response.status_code == 200:
                st.session_state.extracted_data = response.json()
                st.success("File processed! Please review and correct the data below.")
            else:
                st.error(f"Error processing file: {response.json().get('error')}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the backend.")

# --- Correction Form ---
# This section will only appear after data has been extracted
if 'extracted_data' in st.session_state:
    st.header("2. Review and Save")
    data = st.session_state.extracted_data

    with st.form(key="correction_form"):
        vendor = st.text_input("Vendor", value=data.get('vendor', ''))
        
        t_date = data.get('transaction_date')
        transaction_date = datetime.strptime(t_date, '%Y-%m-%d').date() if t_date else None
        transaction_date = st.date_input("Transaction Date", value=transaction_date)
        
        # --- THIS IS THE FIX ---
        # Handle the case where the extracted amount is None before converting to float
        extracted_amount = data.get('amount')
        amount_value = float(extracted_amount) if extracted_amount is not None else 0.0
        amount = st.number_input("Amount", value=amount_value, format="%.2f")
        # ---------------------

        category = st.text_input("Category", value=data.get('category', ''))
        
        submitted = st.form_submit_button("Save Receipt")

        if submitted:
            final_data = {
                "vendor": vendor,
                "transaction_date": transaction_date.isoformat() if transaction_date else None,
                "amount": amount,
                "category": category,
                "raw_text": data.get('raw_text'),
                "raw_data": base64.b64encode(st.session_state.file_bytes).decode('utf-8'),
                "raw_data_extension": st.session_state.file_extension
            }
            
            try:
                save_response = requests.post(f"{BACKEND_URL}/save-receipt", json=final_data)
                if save_response.status_code == 201:
                    st.success(f"Receipt saved successfully! Receipt ID: {save_response.json().get('receipt_id')}")
                    del st.session_state.extracted_data
                    del st.session_state.file_bytes
                    del st.session_state.file_extension
                else:
                    st.error(f"Validation Failed: {save_response.json().get('details')}")
            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not connect to the backend.")

# --- Display Receipts Table and Visualizations ---
st.header("Uploaded Receipts & Insights")
# --- Display Receipts Table (remains the same) ---

# --- Display Receipts Section ---
st.header("Uploaded Receipts")

# --- Interactive Controls for Search and Sort ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    search_feature = st.selectbox("Search In", options=['vendor', 'category', 'raw_text'], index=0)
with col2:
    search_keyword = st.text_input("Search Keyword", placeholder="e.g., Mart, Coffee")
with col3:
    sort_by = st.selectbox("Sort By", options=['transaction_date', 'amount', 'vendor'], index=0)
with col4:
    order = st.selectbox("Order", options=['desc', 'asc'], index=0)

# --- Dynamic API Call and Data Display ---
params = {
    'search_keyword': search_keyword,
    'search_feature': search_feature,
    'sort_by': sort_by,
    'order': order
}

try:
    active_params = {k: v for k, v in params.items() if v}
    response = requests.get(f"{BACKEND_URL}/receipts", params=active_params)
    
    if response.status_code == 200:
        receipts = response.json()
        if receipts:
            df = pd.DataFrame(receipts)
            display_cols = ['vendor', 'transaction_date', 'amount', 'category', 'id']
            df_display = df[[col for col in display_cols if col in df.columns]]
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No receipts found matching your criteria.")
    else:
        st.error("Failed to fetch receipts from the backend.")
except requests.exceptions.ConnectionError:
    st.error("Connection Error: Could not connect to the backend.")


# --- Visualizations Section ---
st.header("Spending Insights")
st.subheader("Top Vendors")

# --- Interactive Controls for Chart ---
chart_mode = st.selectbox(
    "View by:",
    options=['Spend', 'Frequency'],
    index=0
)

# --- Dynamic API Call for Chart Data ---
try:
    params = {'mode': chart_mode.lower()}
    response = requests.get(f"{BACKEND_URL}/insights/top-vendors", params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            df_chart = pd.DataFrame(data)
            df_chart.set_index('vendor', inplace=True)
            st.bar_chart(df_chart)
        else:
            st.info("Not enough data to display insights.")
except requests.exceptions.ConnectionError:
    st.error("Connection Error: Could not connect to the backend.")


# --- Time-Series Visualization ---
st.subheader("Spending Over Time")

try:
    response = requests.get(f"{BACKEND_URL}/insights/spending-over-time")
    if response.status_code == 200:
        data = response.json()
        if data:
            # Convert data to a pandas DataFrame suitable for st.line_chart
            df_time = pd.DataFrame(data)
            df_time['transaction_date'] = pd.to_datetime(df_time['transaction_date'])
            df_time.set_index('transaction_date', inplace=True)
            
            st.line_chart(df_time)
        else:
            st.info("Not enough data to display a time-series chart.")
            
except requests.exceptions.ConnectionError:
    st.error("Connection Error: Could not connect to the backend.")

# --- End of Script ---