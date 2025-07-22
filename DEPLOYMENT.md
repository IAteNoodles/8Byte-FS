# 🚀 Deployment Guide

This guide covers various deployment options for the AI-Powered Receipt Analysis System.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.9 or higher
- **Memory**: Minimum 8GB RAM (16GB recommended for AI processing)
- **Storage**: 10GB free space (for models and data)
- **GPU**: NVIDIA GPU with 6GB+ VRAM (optional, for AI acceleration)

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    python3-dev \
    build-essential

# CentOS/RHEL
sudo yum install -y \
    tesseract \
    poppler-utils \
    python3-devel \
    gcc \
    gcc-c++

# macOS
brew install tesseract poppler

# Windows
# Download and install Tesseract from:
# https://github.com/UB-Mannheim/tesseract/wiki
```

## 🏠 Local Development Setup

### 1. Clone and Setup
```bash
# Clone repository
git clone https://github.com/IAteNoodles/8Byte-FS.git
cd 8Byte-FS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
cd app
python -c "from database.database import initialize_database; initialize_database()"
```

### 2. Start Services
```bash
# Terminal 1: Start Flask API
cd app
python app.py

# Terminal 2: Start Streamlit UI
cd app
streamlit run ui/app_ui.py
```

### 3. Access Application
- **API**: http://localhost:5000
- **Web UI**: http://localhost:8501

