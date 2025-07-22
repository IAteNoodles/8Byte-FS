# Receipt Analysis API

Flask REST API for AI-powered receipt processing and analysis.

## Quick Start

```bash
# Install dependencies
pip install -r ../requirements.txt

# Initialize database
python -c "from database.database import initialize_database; initialize_database()"

# Start API server
python app.py
```

Server runs on `http://localhost:5000`

## API Endpoints

### Process Receipt
```bash
POST /process-receipt
Content-Type: multipart/form-data

curl -X POST -F "file=@receipt.jpg" -F "use_ai=true" http://localhost:5000/process-receipt
```

### Save Receipt
```bash
POST /save-receipt
Content-Type: application/json

curl -X POST -H "Content-Type: application/json" -d '{
  "vendor": "Starbucks",
  "transaction_date": "2024-01-15",
  "amount": 4.50,
  "currency": "USD",
  "raw_text": "Receipt text...",
  "raw_data": "base64_encoded_data",
  "raw_data_extension": "jpg"
}' http://localhost:5000/save-receipt
```

### Get Receipts
```bash
GET /receipts?sort_by=transaction_date&order=desc
```

### Analytics
```bash
GET /insights/statistics?base_currency=USD
GET /insights/top-vendors?mode=spend
GET /insights/top-categories?mode=frequency
```

## Features

- **AI-Enhanced OCR**: Qwen2-VL vision-language model
- **Multi-format Support**: JPG, PNG, PDF, TXT files
- **Smart Fallback**: Traditional OCR when AI fails
- **Currency Conversion**: Real-time exchange rates
- **Advanced Analytics**: Spending insights and trends

## Web UI

Start the Streamlit interface:
```bash
streamlit run ui/app_ui.py
```

Access at `http://localhost:8501`