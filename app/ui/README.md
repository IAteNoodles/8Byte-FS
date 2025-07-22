# UI Module

This module contains the Streamlit-based web interface for the receipt analysis system.

## Components

### 🖥️ app_ui.py
**Interactive web dashboard for receipt processing and analysis**

**Key Features:**
- File upload and processing interface
- Real-time receipt data extraction and correction
- Interactive analytics dashboard
- Data filtering and search capabilities
- Export functionality (CSV/JSON)
- Visual charts and insights

## Main Interface Sections

### 1. Upload & Process Section
**File upload and AI processing interface**

**Features:**
- Multi-format file support (JPG, PNG, PDF, TXT)
- File preview with modal dialogs
- AI-enhanced vs traditional OCR toggle
- Real-time processing status
- Error handling and user feedback

**Usage:**
```python
# File upload configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg'}
BACKEND_URL = "http://127.0.0.1:5000"

# File processing
if uploaded_file:
    files = {'file': (uploaded_file.name, file_bytes, uploaded_file.type)}
    form_data = {'use_ai': use_ai}
    response = requests.post(f"{BACKEND_URL}/process-receipt", files=files, data=form_data)
```

### 2. Review & Save Section
**Data correction and validation interface**

**Features:**
- Editable form fields for extracted data
- Currency selection with custom input
- Date picker for transaction dates
- Category assignment
- Validation feedback
- Save confirmation

**Form Fields:**
- Vendor name (text input)
- Transaction date (date picker)
- Amount (number input with decimal precision)
- Currency (dropdown with custom option)
- Category (text input)

### 3. Data Filtering Section
**Advanced search and filtering capabilities**

**Features:**
- Search by vendor or category
- Date range filtering
- Amount range filtering
- Currency conversion for display
- Real-time filter application

**Filter Options:**
```python
# Search filters
search_feature = ['vendor', 'category']
range_feature = ['transaction_date', 'amount']
display_currency = ['INR', 'USD', 'EUR', 'GBP']

# Date range example
date_range = st.date_input("Select date range", 
                          value=(date.today() - timedelta(days=90), date.today()))

# Amount range example
start_param, end_param = st.slider("Select amount range", 0.0, 10000.0, (0.0, 5000.0))
```

## Configuration

### Backend Connection
```python
BACKEND_URL = "http://127.0.0.1:5000"
CURRENCY_SYMBOLS = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£'}
```

### Page Setup
```python
st.set_page_config(
    page_title="Receipt Analyzer", 
    layout="wide", 
    page_icon="📊"
)
```

### Session State Management
```python
# File processing state
if 'extracted_data' in st.session_state:
    # Show correction form
    
if 'file_bytes' in st.session_state:
    # Process uploaded file
```

## Advanced Features

### File Preview System
**Multi-format file preview with modal dialogs**

**Image Files:**
```python
if file_extension in ['jpg', 'png', 'jpeg']:
    image = Image.open(uploaded_file)
    st.image(image, caption=f"Preview: {uploaded_file.name}")
```

**PDF Files:**
```python
if file_extension == 'pdf':
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    first_page = doc[0]
    pix = first_page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    img_data = pix.tobytes("png")
    st.image(img_data, caption=f"Page 1 of {len(doc)}")
```

**Text Files:**
```python
if file_extension == 'txt':
    text_content = uploaded_file.read().decode('utf-8')
    st.text_area("Preview (first 3 lines):", value=preview_text, height=100)
```

### Data Export System
**CSV and JSON export capabilities**


## User Experience Features

### Loading States
```python
with st.spinner('Processing file...'):
    # Long-running operation
    
with st.spinner("Loading receipt data..."):
    # Data fetching operation
```

### Progress Feedback
```python
# Success messages
st.success("✅ Receipt saved successfully!")

# Warning messages
st.warning("⚠️ Please select both start and end dates for the date range filter.")

# Info messages
st.info("📭 No receipts found matching your criteria.")

# Error messages
st.error("❌ Failed to load data: HTTP 500")
```

### Interactive Elements
```python
# Expandable sections
with st.expander("📄 File Preview", expanded=False):
    # Preview content

with st.expander("View Filtered Raw Data"):
    # Data table

# Popover dialogs
with st.popover("📄 Full Content", use_container_width=False):
    # Modal content

# Toggle switches
use_ai = st.toggle("AI-Enhanced Parser", 
                  help="Uses a more powerful model for potentially better accuracy.")
```


## Deployment

### Local Development
```bash
# Start the UI
cd app
streamlit run ui/app_ui.py

# Access at http://localhost:8501
```

## Future Enhancements

- [ ] Real-time data updates with WebSocket
- [ ] Drag-and-drop file upload
- [ ] Batch file processing
- [ ] Advanced chart customization
- [ ] Mobile-responsive design improvements
- [ ] Offline mode capabilities
- [ ] User authentication and sessions
- [ ] Custom dashboard layouts