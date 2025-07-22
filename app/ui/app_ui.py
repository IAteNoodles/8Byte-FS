import streamlit as st
import requests
import pandas as pd
import base64
import time
import json
from datetime import datetime, date, timedelta
import altair as alt
from PIL import Image
import io
import fitz  # PyMuPDF for PDF handling

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
        # File preview section - containerized
        with st.expander("📄 File Preview", expanded=False):
            file_extension = uploaded_file.name.rsplit('.', 1)[1].lower()
            
            # Create a container for the preview with fixed dimensions
            preview_container = st.container()
            with preview_container:
                if file_extension in ['jpg', 'png', 'jpeg']:
                    # Display actual image file
                    try:
                        image = Image.open(uploaded_file)
                        uploaded_file.seek(0)  # Reset file pointer
                        
                        st.info(f"🖼️ Image File: {uploaded_file.name} ({image.width}x{image.height} pixels)")
                        
                        # Show original image without scaling
                        st.image(image, caption=f"Preview: {uploaded_file.name}")
                            
                    except Exception as e:
                        st.error(f"Could not display image preview: {e}")
                        
                elif file_extension == 'txt':
                    # Display text file with modal preview
                    try:
                        text_content = uploaded_file.read().decode('utf-8')
                        uploaded_file.seek(0)  # Reset file pointer
                        
                        st.info(f"📄 Text File: {uploaded_file.name} ({len(text_content)} characters)")
                        
                        # Show preview of first few lines
                        preview_lines = text_content.split('\n')[:3]
                        preview_text = '\n'.join(preview_lines)
                        if len(preview_lines) < len(text_content.split('\n')):
                            preview_text += "\n..."
                        
                        st.text_area(
                            "Preview (first 3 lines):", 
                            value=preview_text, 
                            height=100, 
                            disabled=True
                        )
                        
                        # Modal dialog for full content
                        with st.popover("📄 Full Content", use_container_width=False):
                            st.text_area(
                                "Complete File Content:", 
                                value=text_content, 
                                height=400, 
                                disabled=True,
                                help="This is the complete content of your text file"
                            )
                            
                    except Exception as e:
                        st.error(f"Could not display text preview: {e}")
                        
                elif file_extension == 'pdf':
                    # Display PDF with modal preview
                    try:
                        pdf_bytes = uploaded_file.read()
                        uploaded_file.seek(0)  # Reset file pointer
                        
                        st.info(f"📄 PDF File: {uploaded_file.name} ({uploaded_file.size} bytes)")
                        
                        # Try to render first page as image for preview
                        try:
                            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            if len(doc) > 0:
                                # Convert first page to small thumbnail
                                first_page = doc[0]
                                pix_small = first_page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # Small preview
                                img_data_small = pix_small.tobytes("png")
                                
                                # Display small thumbnail
                                col1, col2, col3 = st.columns([1, 1, 2])
                                with col1:
                                    st.image(img_data_small, caption="Click to expand", use_container_width=True)
                                
                                # Modal dialog for full preview
                                with st.popover("📄 Full PDF Preview", use_container_width=False):
                                    # Convert first page to larger image for modal
                                    pix_large = first_page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # High quality
                                    img_data_large = pix_large.tobytes("png")
                                    
                                    st.image(img_data_large, caption=f"Page 1 of {len(doc)}", use_container_width=True)
                                    st.write(f"PDF has {len(doc)} page(s)")
                                    
                            doc.close()
                        except Exception as img_e:
                            st.write("Could not generate PDF preview")
                            
                    except Exception as e:
                        st.error(f"Could not display PDF preview: {e}")
                
                else:
                    st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Reset file pointer after preview
        uploaded_file.seek(0)
        if st.button("Process File", use_container_width=True, key="process_btn"):
            st.session_state.file_bytes = uploaded_file.getvalue()
            st.session_state.file_extension = uploaded_file.name.rsplit('.', 1)[1].lower()
            with st.spinner('Processing file...'):
                files = {'file': (uploaded_file.name, st.session_state.file_bytes, uploaded_file.type)}
                form_data = {'use_ai': use_ai}
                try:
                    response = requests.post(f"{BACKEND_URL}/process-receipt", files=files, data=form_data)
                    if response.status_code == 200:
                        response_data = response.json()
                        st.session_state.extracted_data = response_data.get('data', {})
                    else:
                        st.session_state.extracted_data = {"error": "Processing failed"}
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error: Could not connect to the backend server.")
                except Exception as e:
                    st.error(f"Processing Error: {str(e)}")
            
            # Show processing status
            if response.status_code == 200:
                st.success("✅ File processed successfully!")
            else:
                st.error("❌ File processing failed. Please try again.")

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
            
            # Currency dropdown with common currencies and "Other" option
            currency_options = ['INR', 'USD', 'EUR', 'GBP', 'Other']
            current_currency = data.get('currency') or 'INR'
            if current_currency not in currency_options[:-1]:  # If not in predefined list
                currency_choice = c4.selectbox("Currency", options=currency_options, index=len(currency_options)-1)
                if currency_choice == 'Other':
                    currency = st.text_input("Enter Currency Code", value=current_currency, placeholder="e.g., JPY, CAD")
                else:
                    currency = currency_choice
            else:
                currency_choice = c4.selectbox("Currency", options=currency_options, index=currency_options.index(current_currency))
                if currency_choice == 'Other':
                    currency = st.text_input("Enter Currency Code", value='', placeholder="e.g., JPY, CAD")
                else:
                    currency = currency_choice
            category = st.text_input("Category", value=data.get('category') or '')

            if st.form_submit_button("Save Receipt", use_container_width=True):
                final_data = {
                    "vendor": vendor, "transaction_date": transaction_date.isoformat() if transaction_date else None,
                    "amount": amount, "currency": currency.upper(), "category": category,
                    "raw_text": data.get('raw_text'),
                    "raw_data": base64.b64encode(st.session_state.file_bytes).decode('utf-8'),
                    "raw_data_extension": st.session_state.file_extension
                }
                with st.spinner("Saving receipt..."):
                    try:
                        response = requests.post(f"{BACKEND_URL}/save-receipt", json=final_data)
                        if response.status_code == 201:
                            # Clear the form data and show success message
                            st.success("✅ Receipt saved successfully!")
                            # Clear the session state data
                            if 'extracted_data' in st.session_state:
                                del st.session_state.extracted_data
                            if 'file_bytes' in st.session_state:
                                del st.session_state.file_bytes
                            if 'file_extension' in st.session_state:
                                del st.session_state.file_extension
                            # Rerun to refresh the page
                            st.rerun()
                        else:
                            error_msg = "Unknown error"
                            try:
                                error_data = response.json()
                                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                            except:
                                error_msg = f'HTTP {response.status_code}'
                            st.error(f"❌ Failed to save receipt: {error_msg}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Connection Error: Could not connect to the backend server.")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Timeout Error: The request took too long. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Unexpected Error: {str(e)}")

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
        with st.spinner("Loading receipt data..."):
            table_params = active_filter_params.copy()
            table_params['sort_by'] = 'transaction_date'
            table_params['order'] = 'desc'
            response = requests.get(f"{BACKEND_URL}/receipts", params=table_params, timeout=10)
            
        if response.status_code == 200:
            response_data = response.json()
            receipts = response_data.get('data', [])
            if receipts:
                df = pd.DataFrame(receipts)
                
                # Prepare clean data for export (remove binary/unnecessary fields)
                export_data = []
                for receipt in receipts:
                    clean_receipt = {k: v for k, v in receipt.items() 
                                   if k not in ['raw_data', 'raw_data_extension', 'upload_timestamp']}
                    export_data.append(clean_receipt)
                
                export_df = pd.DataFrame(export_data)
                
                # Export options
                export_cols = st.columns(2)
                with export_cols[0]:
                    st.download_button("📥 Export as CSV", export_df.to_csv(index=False).encode('utf-8'),
                                       'filtered_receipts.csv', 'text/csv', key='download-csv')
                with export_cols[1]:
                    json_data = json.dumps(export_data, indent=2, default=str)
                    st.download_button("📥 Export as JSON", json_data.encode('utf-8'),
                                       'filtered_receipts.json', 'application/json', key='download-json')
                
                display_cols = ['vendor', 'transaction_date', 'amount', 'currency', 'category']
                available_cols = [col for col in display_cols if col in df.columns]
                st.dataframe(df[available_cols], use_container_width=True)
                st.caption(f"Showing {len(receipts)} receipt(s)")
            else:
                st.info("📭 No receipts found matching your criteria.")
        else:
            st.error(f"❌ Failed to load data: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection Error: Could not connect to the backend server.")
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout Error: Request took too long. Please try again.")
    except Exception as e:
        st.error(f"❌ Error loading receipt data: {str(e)}")

st.divider()

# ==============================================================================
# 3. INSIGHTS SECTION
# ==============================================================================
st.header(f"📊 Insights ({display_currency})")

try:
    # Get basic statistics
    stats_response = requests.get(f"{BACKEND_URL}/insights/statistics", params=active_filter_params)
    stats = stats_response.json().get('data', {}) if stats_response.status_code == 200 else {}
    
    # Get top vendors by spend and frequency
    vendor_spend_params = active_filter_params.copy()
    vendor_spend_params['mode'] = 'spend'
    vendor_freq_params = active_filter_params.copy()
    vendor_freq_params['mode'] = 'frequency'
    
    top_vendors_spend = requests.get(f"{BACKEND_URL}/insights/top-vendors", params=vendor_spend_params)
    top_vendors_freq = requests.get(f"{BACKEND_URL}/insights/top-vendors", params=vendor_freq_params)
    
    # Get top categories by spend and frequency
    cat_spend_params = active_filter_params.copy()
    cat_spend_params['mode'] = 'spend'
    cat_freq_params = active_filter_params.copy()
    cat_freq_params['mode'] = 'frequency'
    
    top_categories_spend = requests.get(f"{BACKEND_URL}/insights/top-categories", params=cat_spend_params)
    top_categories_freq = requests.get(f"{BACKEND_URL}/insights/top-categories", params=cat_freq_params)
    
    symbol = CURRENCY_SYMBOLS.get(display_currency, '')
    
    # Key Metrics Row
    metrics_cols = st.columns(4)
    metrics_cols[0].metric("💰 Total Spend", f"{symbol}{stats.get('total', 0):,.2f}")
    metrics_cols[1].metric("📊 Avg Transaction", f"{symbol}{stats.get('mean', 0):,.2f}")
    metrics_cols[2].metric("📈 Total Transactions", stats.get('record_count', 0))
    metrics_cols[3].metric("💱 Currency", display_currency)
    
    st.markdown("---")
    
    # Comprehensive Insights Filter
    st.markdown("#### 📊 Comprehensive Insights")
    
    # Interactive controls
    analysis_cols = st.columns(3)
    with analysis_cols[0]:
        view_type = st.selectbox("View", ["Vendor", "Category"], key="insight_type")
    with analysis_cols[1]:
        view_metric = st.selectbox("Metric", ["Sales", "Frequency"], key="insight_metric")
    with analysis_cols[2]:
        view_rank = st.selectbox("Rank", ["Top", "Bottom"], key="insight_rank")
    
    # Get appropriate data based on selections
    if view_type == "Vendor" and view_metric == "Sales":
        data_source = top_vendors_spend.json().get('data', []) if top_vendors_spend.status_code == 200 else []
    elif view_type == "Vendor" and view_metric == "Frequency":
        data_source = top_vendors_freq.json().get('data', []) if top_vendors_freq.status_code == 200 else []
    elif view_type == "Category" and view_metric == "Sales":
        data_source = top_categories_spend.json().get('data', []) if top_categories_spend.status_code == 200 else []
    else:  # Category + Frequency
        data_source = top_categories_freq.json().get('data', []) if top_categories_freq.status_code == 200 else []
    
    # Display results based on selection
    if data_source:
        if view_rank == "Top":
            display_data = data_source[:3]  # Top 3
        else:
            display_data = data_source[-3:]  # Bottom 3
        
        # Show results
        for i, item in enumerate(display_data, 1):
            # Use ordinal numbers instead of emojis
            if view_rank == "Top":
                rank_text = f"{i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'}"
            else:
                # For bottom, show as bottom 1st, 2nd, 3rd
                rank_text = f"Bottom {i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'}"
            
            name_key = 'vendor' if view_type == 'Vendor' else 'category'
            name = item[name_key]
            
            if view_metric == "Sales":
                value = f"{symbol}{item['value']:,.2f}"
            else:
                value = f"{int(item['value'])} times"
            
            st.write(f"{rank_text}: **{name}** - {value}")
    else:
        st.info("No data available for selected criteria")

except Exception as e:
    st.error(f"Could not load insights: {e}")

st.divider()

# ==============================================================================
# 4. VISUALIZATIONS SECTION
# ==============================================================================
st.header(f"📈 Visualizations ({display_currency})")



# --- Main Visualization Columns ---
viz_cols = st.columns(2)

# Column 1: Combined Vendor & Category Analysis
with viz_cols[0]:
    st.subheader("Breakdown Analysis")
    
    # Choose between vendor or category analysis
    analysis_type = st.selectbox("Analyze By", options=['Vendor', 'Category'], key="breakdown_type")
    analysis_mode = st.selectbox("Mode", options=['Spend', 'Frequency'], key="breakdown_mode")
    
    # Add filters for the first graph
    if analysis_type == 'Vendor':
        # Get available vendors for filtering
        try:
            table_params = active_filter_params.copy()
            response = requests.get(f"{BACKEND_URL}/receipts", params=table_params, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                all_receipts = response_data.get('data', [])
                if all_receipts:
                    df_all = pd.DataFrame(all_receipts)
                    available_vendors = sorted(df_all['vendor'].dropna().unique().tolist())
                    if available_vendors:
                        selected_vendors_breakdown = st.multiselect(
                            "Select Vendors to Display:",
                            options=available_vendors,
                            default=available_vendors[:5] if len(available_vendors) > 5 else available_vendors,
                            key="selected_vendors_breakdown"
                        )
                    else:
                        selected_vendors_breakdown = []
                else:
                    selected_vendors_breakdown = []
            else:
                selected_vendors_breakdown = []
        except:
            selected_vendors_breakdown = []
    else:  # Category
        # Get available categories for filtering
        try:
            table_params = active_filter_params.copy()
            response = requests.get(f"{BACKEND_URL}/receipts", params=table_params, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                all_receipts = response_data.get('data', [])
                if all_receipts:
                    df_all = pd.DataFrame(all_receipts)
                    available_categories = sorted(df_all['category'].dropna().unique().tolist())
                    if available_categories:
                        selected_categories_breakdown = st.multiselect(
                            "Select Categories to Display:",
                            options=available_categories,
                            default=available_categories[:5] if len(available_categories) > 5 else available_categories,
                            key="selected_categories_breakdown"
                        )
                    else:
                        selected_categories_breakdown = []
                else:
                    selected_categories_breakdown = []
            else:
                selected_categories_breakdown = []
        except:
            selected_categories_breakdown = []
    
    # Prepare parameters
    analysis_params = active_filter_params.copy()
    analysis_params['mode'] = analysis_mode.lower()
    
    try:
        if analysis_type == 'Vendor':
            if 'selected_vendors_breakdown' in locals() and selected_vendors_breakdown:
                response = requests.get(f"{BACKEND_URL}/insights/top-vendors", params=analysis_params)
                chart_title = f"Selected Vendors by {analysis_mode}"
                index_col = 'vendor'
                
                response.raise_for_status()
                response_data = response.json()
                all_data = response_data.get('data', [])
                
                # Filter data to only show selected vendors
                data = [item for item in all_data if item['vendor'] in selected_vendors_breakdown]
            else:
                st.info("Please select at least one vendor to display.")
                data = []
        else:  # Category
            if 'selected_categories_breakdown' in locals() and selected_categories_breakdown:
                response = requests.get(f"{BACKEND_URL}/insights/top-categories", params=analysis_params)
                chart_title = f"Selected Categories by {analysis_mode}"
                index_col = 'category'
                
                response.raise_for_status()
                response_data = response.json()
                all_data = response_data.get('data', [])
                
                # Filter data to only show selected categories
                data = [item for item in all_data if item['category'] in selected_categories_breakdown]
            else:
                st.info("Please select at least one category to display.")
                data = []
        
        if data:
            st.write(f"**{chart_title}**")
            st.bar_chart(pd.DataFrame(data).set_index(index_col))
        elif analysis_type == 'Vendor' and 'selected_vendors_breakdown' in locals() and selected_vendors_breakdown:
            st.info(f"No data available for selected vendors.")
        elif analysis_type == 'Category' and 'selected_categories_breakdown' in locals() and selected_categories_breakdown:
            st.info(f"No data available for selected categories.")
            
    except requests.exceptions.HTTPError as e:
        st.error(f"Error fetching {analysis_type.lower()} data: {e.response.status_code} {e.response.reason}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Column 2: Time-Series Analysis with Selection
with viz_cols[1]:
    st.subheader("Time Series Analysis")
    
    # Choose what to analyze over time
    time_analysis_type = st.selectbox("Analyze Over Time", 
                                     options=['By Vendor', 'By Category'], 
                                     key="time_analysis_type")
    
    # Choose metric
    time_metric = st.selectbox("Metric", options=['Spend', 'Frequency'], key="time_metric")
    
    try:
        # Get all receipts to extract available vendors/categories
        table_params = active_filter_params.copy()
        response = requests.get(f"{BACKEND_URL}/receipts", params=table_params, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            all_receipts = response_data.get('data', [])
            
            if all_receipts:
                df_all = pd.DataFrame(all_receipts)
                
                if time_analysis_type == 'By Vendor':
                    # Get unique vendors
                    available_vendors = sorted(df_all['vendor'].dropna().unique().tolist())
                    if available_vendors:
                        selected_vendors = st.multiselect(
                            "Select Vendors to Display:",
                            options=available_vendors,
                            default=available_vendors[:5] if len(available_vendors) > 5 else available_vendors,
                            key="selected_vendors"
                        )
                        
                        if selected_vendors:
                            # Filter data for selected vendors
                            filtered_df = df_all[df_all['vendor'].isin(selected_vendors)].copy()
                            filtered_df['transaction_date'] = pd.to_datetime(filtered_df['transaction_date'])
                            
                            if time_metric == 'Spend':
                                # Convert currency if needed
                                if 'amount_in_base' not in filtered_df.columns:
                                    # Use original amount if no conversion available
                                    filtered_df['amount_in_base'] = filtered_df['amount']
                                
                                # Group by date and vendor, sum amounts
                                time_series = filtered_df.groupby([filtered_df['transaction_date'].dt.date, 'vendor'])['amount_in_base'].sum().unstack(fill_value=0)
                            else:  # Frequency
                                # Group by date and vendor, count transactions
                                time_series = filtered_df.groupby([filtered_df['transaction_date'].dt.date, 'vendor']).size().unstack(fill_value=0)
                            
                            if not time_series.empty:
                                st.line_chart(time_series)
                            else:
                                st.info("No data available for selected vendors.")
                        else:
                            st.info("Please select at least one vendor to display.")
                    else:
                        st.info("No vendors found in the current data.")
                
                elif time_analysis_type == 'By Category':
                    # Get unique categories
                    available_categories = sorted(df_all['category'].dropna().unique().tolist())
                    if available_categories:
                        selected_categories = st.multiselect(
                            "Select Categories to Display:",
                            options=available_categories,
                            default=available_categories[:5] if len(available_categories) > 5 else available_categories,
                            key="selected_categories"
                        )
                        
                        if selected_categories:
                            # Filter data for selected categories
                            filtered_df = df_all[df_all['category'].isin(selected_categories)].copy()
                            filtered_df['transaction_date'] = pd.to_datetime(filtered_df['transaction_date'])
                            
                            if time_metric == 'Spend':
                                # Convert currency if needed
                                if 'amount_in_base' not in filtered_df.columns:
                                    # Use original amount if no conversion available
                                    filtered_df['amount_in_base'] = filtered_df['amount']
                                
                                # Group by date and category, sum amounts
                                time_series = filtered_df.groupby([filtered_df['transaction_date'].dt.date, 'category'])['amount_in_base'].sum().unstack(fill_value=0)
                            else:  # Frequency
                                # Group by date and category, count transactions
                                time_series = filtered_df.groupby([filtered_df['transaction_date'].dt.date, 'category']).size().unstack(fill_value=0)
                            
                            if not time_series.empty:
                                st.line_chart(time_series)
                            else:
                                st.info("No data available for selected categories.")
                        else:
                            st.info("Please select at least one category to display.")
                    else:
                        st.info("No categories found in the current data.")
            else:
                st.info("No data available for time-series analysis.")
        else:
            st.error(f"❌ Failed to load data: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection Error: Could not connect to the backend server.")
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout Error: Request took too long. Please try again.")
    except Exception as e:
        st.error(f"❌ Error in time-series analysis: {str(e)}")

st.divider()

