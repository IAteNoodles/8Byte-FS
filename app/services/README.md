# Services Module

This module contains the core processing services for receipt analysis and data extraction.

## Components

### 📄 parsers.py
**Main OCR and parsing orchestrator**

**Key Functions:**
- `parse_and_extract_data(file_bytes, file_extension, use_ai=False)` - Main parsing function
- `find_vendor(text)` - Vendor detection with fuzzy matching
- `find_date(text)` - Date extraction with multiple formats
- `find_currency_and_amount(text)` - Amount and currency detection

**Features:**
- Multi-format support (JPG, PNG, PDF, TXT)
- AI vs Traditional OCR quality comparison
- Extensive vendor database with categories
- Fuzzy matching for vendor recognition
- Multiple OCR configuration attempts

**Usage:**
```python
from services.parsers import parse_and_extract_data

# Process with AI enhancement [Experimental]
result = parse_and_extract_data(file_bytes, 'jpg', use_ai=True)

# Traditional OCR only [Fallback/Stable]
result = parse_and_extract_data(file_bytes, 'pdf', use_ai=False)
```

**Usage:**
```python
from services.ai_parser import extract_with_ai, extract_structured_receipt_data

# Get raw text
text = extract_with_ai(image_bytes, 'jpg')

# Get structured data
data = extract_structured_receipt_data(image_bytes, 'jpg')
```

### 💱 currency_converter.py
**Multi-currency conversion service**

**Key Functions:**
- `convert_to_base_currency(records, base_currency)` - Batch currency conversion

**Features:**
- Real-time exchange rates via Frankfurter API
- Session-based rate caching
- Automatic fallback for conversion failures
- Historical rate support

**Usage:**
```python
from services.currency_converter import convert_to_base_currency

records = convert_to_base_currency(receipt_list, 'USD')
```

### Model Settings
```python
# AI Parser Configuration
QWEN_MODEL = "Qwen/Qwen2-VL-2B-Instruct"
MAX_TOKENS = 512
TEMPERATURE = 0.1

# OCR Configuration
TESSERACT_CONFIGS = ['--psm 6', '--psm 4', '--psm 3', '--psm 1']
```

## Error Handling

All services implement comprehensive error handling:
- Graceful fallbacks for missing dependencies
- Timeout protection for long-running operations
- Memory cleanup after processing
- Detailed error logging

## Performance Optimization

### AI Parser
- Lazy model loading (loaded on first use)
- GPU memory management
- FP16 precision for memory efficiency
- Automatic CPU fallback

### Traditional OCR
- Tesseract
- Quality-based result selection
- Parallel processing support
- Image preprocessing optimization


## Dependencies

### Required
- `torch` - AI model inference
- `transformers` - Hugging Face models
- `pytesseract` - OCR engine
- `Pillow` - Image processing
- `PyMuPDF` - PDF processing
- `thefuzz` - Fuzzy string matching

### Optional
- `opencv-python` - Advanced image preprocessing
- `easyocr` - Alternative OCR engine
- `paddleocr` - Alternative OCR engine
