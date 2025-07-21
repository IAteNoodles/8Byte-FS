import streamlit as st
import requests
import pandas as pd
import base64
from datetime import datetime, date, timedelta
import altair as alt

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:5000"
CURRENCY_SYMBOLS = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£'}

# --- Page Setup ---
st.set_page_config(page_title="Receipt Analyzer", layout="wide", page_icon="📊")
st.title("📊 Receipt Analysis Dashboard")


# ==============================================================================
# 1. UPLOAD SECTION
# ==============================================================================
with st.expander("1. Upload & Process a New Receipt"):
    st.header("Upload")
    use_ai = st.toggle("AI-Enhanced Parser", help="Uses a more powerful model for potentially better accuracy.")
    uploaded_file = st.file_uploader("Upload a receipt file", type=['jpg', 'png', 'pdf', 'txt'])

    if uploaded_file:
        if st.button("Process File", use_container_width=True, key="process_btn"):
            st.session_state.file_bytes = uploaded_file.getvalue()
            st.session_state.file_extension = uploaded_file.name.rsplit('.', 1)[1].lower()
            with st.spinner('Processing file...'):
                files = {'file': (uploaded_file.name, st.session_state.file_bytes, uploaded_file.type)}
                form_data = {'use_ai': use_ai}
                try:
                    response = requests.post(f"{BACKEND_URL}/process-receipt", files=files, data=form_data)
                    st.session_state.extracted_data = response.json() if response.status_code == 200 else {"error": "Processing failed"}
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error.")

    import time # Add this import at the top of your script

# --- 2. Correction Form Section ---
if 'extracted_data' in st.session_state and st.session_state.extracted_data:
    
    # Create a placeholder container
    form_container = st.empty()

    with form_container.container():
        st.header("2. Review and Save")
        with st.form(key="correction_form"):
            data = st.session_state.extracted_data
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            vendor = c1.text_input("Vendor", value=data.get('vendor') or '')
            t_date = datetime.strptime(data.get('transaction_date'), '%Y-%m-%d').date() if data.get('transaction_date') else None
            transaction_date = c2.date_input("Transaction Date", value=t_date)
            amount = c3.number_input("Amount", value=float(data.get('amount') or 0.0), format="%.2f")
            currency = c4.text_input("Currency", value=data.get('currency') or 'INR')
            category = st.text_input("Category", value=data.get('category') or '')

            if st.form_submit_button("Save Receipt", use_container_width=True):
                final_data = {
                    "vendor": vendor, "transaction_date": transaction_date.isoformat() if transaction_date else None,
                    "amount": amount, "currency": currency.upper(), "category": category,
                    "raw_text": data.get('raw_text'),
                    "raw_data": base64.b64encode(st.session_state.file_bytes).decode('utf-8'),
                    "raw_data_extension": st.session_state.file_extension
                }
                try:
                    response = requests.post(f"{BACKEND_URL}/save-receipt", json=final_data)
                    if response.status_code == 201:
                        # --- MODIFIED SUCCESS LOGIC ---
                        # 1. Clear the form from the screen and show a success message
                        form_container.success("✅ Receipt saved successfully!")
                        # 2. Clear the data from the session state
                        st.session_state.extracted_data = None
                        # 3. Wait for a moment so the user can see the message
                        time.sleep(1.5)
                        # 4. Rerun the script to get a clean page
                        st.rerun()
                    else:
                        st.error(f"Failed to save: {response.json().get('error', 'Unknown backend error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error: Could not connect to the backend.")

# ==============================================================================
# 2. FILTER DATA SECTION (Now always visible)
# ==============================================================================
st.subheader("Filter Data")
filter_cols = st.columns(4)
search_feature = filter_cols[0].selectbox("Search In", options=['vendor', 'category', 'raw_text'], key='search_in')
search_keyword = filter_cols[1].text_input("Search Keyword", placeholder="e.g., Starbucks", key='search_kw')
range_feature = filter_cols[2].selectbox("Filter by Range", options=["(None)", "transaction_date", "amount"], key='range_feature')
display_currency = filter_cols[3].selectbox("Display Currency", options=['INR', 'USD', 'EUR', 'GBP'], key='display_curr')

start_param, end_param = None, None
if range_feature == "transaction_date":
    start_param, end_param = st.date_input("Select date range", value=(date.today() - timedelta(days=90), date.today()))
    start_param, end_param = start_param.isoformat(), end_param.isoformat()
elif range_feature == "amount":
    start_param, end_param = st.slider("Select amount range", 0.0, 10000.0, (0.0, 5000.0))

active_filter_params = {k: v for k, v in {
    'search_keyword': search_keyword, 'search_feature': search_feature,
    'range_feature': range_feature if range_feature != "(None)" else None,
    'start': start_param, 'end': end_param, 'base_currency': display_currency
}.items() if v}

st.divider()

with st.expander("View Filtered Raw Data"):
    try:
        table_params = active_filter_params.copy()
        table_params['sort_by'] = 'transaction_date'
        table_params['order'] = 'desc'
        response = requests.get(f"{BACKEND_URL}/receipts", params=table_params)
        if response.status_code == 200:
            receipts = response.json()
            if receipts:
                df = pd.DataFrame(receipts)
                st.download_button("📥 Export as CSV", df.to_csv(index=False).encode('utf-8'),
                                   'filtered_receipts.csv', 'text/csv', key='download-csv')
                display_cols = ['vendor', 'transaction_date', 'amount', 'currency', 'category']
                st.dataframe(df[[col for col in display_cols if col in df.columns]], use_container_width=True)
            else:
                st.info("No receipts found matching your criteria.")
    except Exception as e:
        st.warning(f"Could not connect to backend to load table data: {e}")

st.divider()

# ==============================================================================
# 3. VISUALIZATIONS SECTION
# ==============================================================================
st.header(f"Visualizations ({display_currency})")

# --- Key Metrics (KPIs) ---
try:
    stats_response = requests.get(f"{BACKEND_URL}/insights/statistics", params=active_filter_params)
    stats = stats_response.json() if stats_response.status_code == 200 else {}
    symbol = CURRENCY_SYMBOLS.get(display_currency, '')
    
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Spend", f"{symbol}{stats.get('total', 0):,.2f}")
    kpi_cols[1].metric("Mean Transaction", f"{symbol}{stats.get('mean', 0):,.2f}")
    kpi_cols[2].metric("Median Transaction", f"{symbol}{stats.get('median', 0):,.2f}")
    
    vendor_params = active_filter_params.copy()
    vendor_params['mode'] = 'spend'
    top_vendor_response = requests.get(f"{BACKEND_URL}/insights/top-vendors", params=vendor_params)
    top_vendor = top_vendor_response.json()[0]['vendor'] if top_vendor_response.status_code == 200 and top_vendor_response.json() else "N/A"
    kpi_cols[3].metric("Top Vendor by Spend", top_vendor)
except Exception as e:
    st.warning(f"Could not load key metrics. Error: {e}")

st.divider()

# --- Main Visualization Columns ---
viz_cols = st.columns(3)

# Column 1: Vendor Analysis
with viz_cols[0]:
    st.subheader("By Vendor")
    vendor_mode = st.selectbox("Mode", options=['Spend', 'Frequency'], key="vendor_mode")
    vendor_params = active_filter_params.copy()
    vendor_params['mode'] = vendor_mode.lower()
    try:
        response = requests.get(f"{BACKEND_URL}/insights/top-vendors", params=vendor_params)
        response.raise_for_status() # This will raise an error for bad responses (like 4xx or 5xx)
        data = response.json()
        if data:
            st.bar_chart(pd.DataFrame(data).set_index('vendor'))
        else:
            st.info("No vendor data to display for the current filters.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error fetching vendor data: {e.response.status_code} {e.response.reason}")
        st.json(e.response.json()) # Show the actual error from the backend
    except Exception as e:
        st.error(f"An error occurred: {e}")


# Column 2: Category Analysis
with viz_cols[1]:
    st.subheader("By Category")
    category_mode = st.selectbox("Mode", options=['Spend', 'Frequency'], key="category_mode")
    category_params = active_filter_params.copy()
    category_params['mode'] = category_mode.lower()
    try:
        response = requests.get(f"{BACKEND_URL}/insights/top-categories", params=category_params)
        response.raise_for_status()
        data = response.json()
        if data:
            st.bar_chart(pd.DataFrame(data).set_index('category'))
        else:
            st.info("No category data to display for the current filters.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error fetching category data: {e.response.status_code} {e.response.reason}")
        st.json(e.response.json())
    except Exception as e:
        st.error(f"An error occurred: {e}")


# Column 3: Time-Series Analysis
with viz_cols[2]:
    st.subheader("Over Time")
    time_mode = st.selectbox("Plot", options=['Total Spend', 'Mean Spend', 'By Vendor', 'By Category'], key="time_mode")
    time_params = active_filter_params.copy()
    time_params['mode'] = time_mode.lower() # Pass the selected mode to the backend
    try:
        response = requests.get(f"{BACKEND_URL}/insights/spending-over-time", params=time_params)
        response.raise_for_status()
        data = response.json()
        if data:
            df = pd.DataFrame(data).set_index('transaction_date')
            st.line_chart(df)
        else:
            st.info("No time-series data to display for the current filters.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Error fetching time-series data: {e.response.status_code} {e.response.reason}")
        st.json(e.response.json())
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.divider()

