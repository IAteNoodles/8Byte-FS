# 📊 AI-Powered Receipt Analysis System

A comprehensive receipt processing and analysis system that combines traditional OCR with advanced AI vision-language models for intelligent document parsing and financial insights.

---

**🌐 Try it online:**  
The project is hosted at [https://simpleocr.streamlit.app/](https://simpleocr.streamlit.app/)  
No installation required—just visit the link for a live demo!

---

## 🚀 Features

### Core Functionality
- **Multi-format Support:** Process JPG, PNG, PDF, and TXT files
- **AI-Enhanced OCR:** Qwen2-VL vision-language model for intelligent parsing
- **Structured Data Extraction:** Vendor, date, amount, currency, and category detection
- **Fallback Processing:** Traditional OCR when AI parsing fails
- **Quality Comparison:** Automatic selection of best extraction method

### Analytics & Insights
- **Financial Statistics:** Total spend, averages, medians
- **Vendor Analysis:** Top vendors by spend and frequency
- **Category Breakdown:** Spending patterns by category
- **Time Series Analysis:** Spending trends over time
- **Currency Conversion:** Multi-currency support with real-time rates
- **Advanced Filtering:** Search, date ranges, amount ranges

### User Interface
- **Web Dashboard:** Streamlit-based interactive UI ([Try it online](https://simpleocr.streamlit.app/))
- **REST API:** Flask backend for programmatic access
- **Real-time Processing:** Live file upload and processing
- **Data Export:** CSV and JSON export capabilities
- **Visual Analytics:** Charts and graphs for insights

---

## 🏗️ Architecture

```
├── app/
│   ├── algorithms/          # Data processing algorithms
│   ├── database/           # SQLite database management
│   ├── models/             # Data models and validation
│   ├── services/           # Core processing services
│   ├── ui/                 # Streamlit web interface
│   ├── utils/              # Utilities and logging
│   └── app.py              # Flask API server
├── docs/                   # Module documentation
└── requirements.txt        # Python dependencies
```

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9+
- CUDA-compatible GPU (optional, for AI acceleration)
- System dependencies:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr tesseract-ocr-eng poppler-utils

  # macOS
  brew install tesseract poppler

  # Windows
  # Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
  ```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/IAteNoodles/8Byte-FS.git 
   cd 8Byte-FS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   cd app
   python -c "from database.database import initialize_database; initialize_database()"
   ```

---

## 🚀 Usage

### Starting the Application

1. **Start the Flask API server**
   ```bash
   cd app
   python app.py
   ```
   Server will run on `http://localhost:5000`

2. **Start the Streamlit UI** (in a new terminal)
   ```bash
   cd app
   streamlit run ui/app_ui.py
   ```
   UI will be available at `http://localhost:8501`

### Using the System

1. **Upload Receipt:** Use the web interface to upload receipt files
2. **AI Processing:** Toggle AI-enhanced parsing for better accuracy
3. **Review & Correct:** Verify and edit extracted data
4. **Save:** Store processed receipts in the database
5. **Analyze:** Use the dashboard for insights and analytics

### OCR Engines

- **Tesseract:** Traditional OCR engine
- **PyMuPDF:** PDF text extraction
- **Quality Comparison:** Automatic best-result selection
- **Qwen-VL:** Fallback AI parser (Use With Caution)

---

## 🌐 API Quick Start & Endpoints

### Quick Start

```bash
# Install dependencies
pip install -r ../requirements.txt

# Initialize database
python -c "from database.database import initialize_database; initialize_database()"

# Start API server
python app.py
```

API runs on `http://localhost:5000`

### API Endpoints

- **Process Receipt**
  ```bash
  POST /process-receipt
  Content-Type: multipart/form-data

  curl -X POST -F "file=@receipt.jpg" -F "use_ai=true" http://localhost:5000/process-receipt
  ```

- **Save Receipt**
  ```bash
  POST /save-receipt
  Content-Type: application/json

  curl -X POST -H "Content-Type: application/json" -d '{ ... }' http://localhost:5000/save-receipt
  ```

- **Get Receipts**
  ```bash
  GET /receipts?sort_by=transaction_date&order=desc
  ```

- **Analytics**
  ```bash
  GET /insights/statistics?base_currency=USD
  GET /insights/top-vendors?mode=spend
  GET /insights/top-categories?mode=frequency
  ```

---

## 📦 Algorithms Module

- **Aggregation:** Data aggregation and statistical analysis (`aggregation.py`)
- **Search:** Advanced search and filtering (`search.py`)
- **Sort:** Data sorting and ordering (`sort.py`)
- **Input Format:**
  ```python
  record = {
      'id': 1,
      'vendor': 'Starbucks',
      'transaction_date': '2024-01-15',
      'amount': 4.50,
      'currency': 'USD',
      'category': 'restaurant',
      'amount_in_base': 4.50  # Added by currency converter
  }
  ```
- **Dependencies:** pandas, numpy, thefuzz (and optionally python-Levenshtein, numba)

---

## 📊 Data Models

### Receipt Data Structure

```python
{
    "vendor": "Store Name",
    "transaction_date": "2024-01-15",
    "amount": 42.50,
    "currency": "USD",
    "category": "grocery",
    "raw_text": "Original extracted text",
}
```

---

## 🔮 Future Enhancements

- [ ] Multi-language receipt support
- [ ] Batch processing capabilities
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Cloud deployment options
- [ ] Custom model training pipeline

---

## 💬 Contributing

Issues and pull requests are welcome! Please check the [issues](https://github.com/IAteNoodles/8Byte-FS/issues) page and contribute with new features or bugfixes.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for more details.
