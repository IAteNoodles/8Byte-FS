from flask import Flask, request, jsonify
from pydantic import BaseModel, Field, field_validator, ValidationError
from datetime import date, datetime
from typing import Optional



# TODO: Import the parser and database modules.
from services.parsers import parse_and_extract_data
# from database import save_receipt
from database.database import save_receipt, get_all_receipts
from algorithms.sort import sort_records
from algorithms.search import search_by_keywords_concise
from algorithms.aggregation import calculate_total_spend, get_top_vendors

from models.receipt import ReceiptData

app = Flask(__name__)



# --- File Handling Logic ---
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg'}

def is_allowed_file(filename: str) -> bool:
    """Checks if the file has one of the allowed extensions."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Flask Endpoint ---
@app.route('/', methods=['GET'])
def hello():
    return "hello"
@app.route('/upload', methods=['POST'])
def upload_receipt():
    """Endpoint to upload, parse, and validate a receipt file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '' or not is_allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    try:
        file_bytes = file.read()
        file_extension = file.filename.rsplit('.', 1)[1].lower()

        # 1. Parse data using the parsing module
        extracted_data = parse_and_extract_data(file_bytes, file_extension)

        # 2. Prepare the full data payload for validation
        full_data = {
            **extracted_data,
            "raw_data": file_bytes,
            "raw_data_extension": file_extension
        }

        # 3. Validate data using the Pydantic model
        receipt = ReceiptData(**full_data)

        # 4. TODO: Save the validated receipt object to the SQLite database.
        receipt_id = save_receipt(receipt)
        
        # Return the validated data (excluding raw bytes) as confirmation
        return jsonify({
            "message": "File processed and validated successfully.",
            "data": receipt.dict(exclude={'raw_data'})
        }), 200

    except ValidationError as e:
        # Return detailed validation errors from Pydantic
        return jsonify({"error": "Validation failed", "details": e.errors()}), 422
    except Exception as e:
        # TODO: Implement more specific exception handling and logging.
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
@app.route('/receipts', methods=['GET'])
def get_receipts():
    """
    Retrieves, searches, and sorts receipts based on query parameters.
    Examples:
    - /receipts
    - /receipts?search_keyword=mart&search_feature=vendor
    - /receipts?sort_by=amount&order=desc
    """
    try:
        # 1. Fetch all records from the database
        records = get_all_receipts()

        # 2. Apply search if parameters are provided
        search_keyword = request.args.get('search_keyword')
        search_feature = request.args.get('search_feature')
        if search_keyword and search_feature:
            records = search_by_keywords_concise(search_keyword, search_feature, records)

        # 3. Apply sorting if parameters are provided
        sort_by = request.args.get('sort_by')
        if sort_by:
            order = request.args.get('order', 'asc') # Default to ascending
            is_desc = order.lower() == 'desc'
            print(is_desc)
            records = sort_records(records, sort_by=sort_by, reverse=is_desc)
        
        # #TODO: Implement pagination for large datasets.
        
        return jsonify(records), 200

    except Exception as e:
        # TODO: Implement more specific exception handling and logging.
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/insights/top-vendors', methods=['GET'])
def get_vendor_summary():
    """
    Provides aggregated data on vendors by spend or frequency.
    Query Params:
    - mode: 'spend' or 'frequency' (default: 'spend')
    - limit: integer (default: 10)
    """
    try:
        mode = request.args.get('mode', 'spend')
        limit = int(request.args.get('limit', 10))
        
        records = get_all_receipts()
        if not records:
            return jsonify([]), 200

        # Use the aggregation function we already built
        top_vendors_data = get_top_vendors(records, mode=mode, limit=limit)
        
        # Convert list of tuples to a format suitable for charting
        # e.g., [{'vendor': 'Walmart', 'value': 500}]
        results = [{"vendor": vendor, "value": value} for vendor, value in top_vendors_data]
        
        return jsonify(results), 200

    except Exception as e:
        # TODO: Add more specific error handling
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

import pandas as pd
# ... other imports

# ... (all other endpoints)

# --- New endpoint for time-series insights ---
@app.route('/insights/spending-over-time', methods=['GET'])
def get_spending_trend():
    """
    Provides aggregated data on total spending per day.
    """
    try:
        records = get_all_receipts()
        if not records:
            return jsonify([]), 200

        # Use pandas to easily manipulate the time-series data
        df = pd.DataFrame(records)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Group by date and sum the amounts, then reset index to make 'transaction_date' a column again
        daily_spend = df.groupby('transaction_date')['amount'].sum().reset_index()
        
        # Convert to a JSON-friendly list of dictionaries
        result = daily_spend.to_dict('records')
        
        return jsonify(result), 200

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/process-receipt', methods=['POST'])
def process_receipt_file():
    """
    Receives a file, runs parsing, and returns the extracted fields without saving.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '' or not is_allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    file_bytes = file.read()
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    
    # Run the parser but don't save to DB yet
    extracted_data = parse_and_extract_data(file_bytes, file_extension)
    
    # Also include the raw file data needed for the final save
    extracted_data['raw_data_extension'] = file_extension
    
    # Return the parsed data for the user to review
    return jsonify(extracted_data), 200


# In app.py
import base64
from pydantic import ValidationError

@app.route('/save-receipt', methods=['POST'])
def save_corrected_receipt():
    """
    Receives final, user-corrected JSON data, validates it, and saves it to the database.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be a valid JSON."}), 400

    # --- Add this check for required fields ---
    required_fields = ['vendor', 'transaction_date', 'amount', 'raw_data', 'raw_data_extension']
    for field in required_fields:
        if data.get(field) is None:
            return jsonify({"error": f"Validation failed: The '{field}' field cannot be empty."}), 422
    # -------------------------------------------

    try:
        if isinstance(data.get('raw_data'), str):
            data['raw_data'] = base64.b64decode(data['raw_data'])
        
        receipt = ReceiptData(**data)
        receipt_id = save_receipt(receipt)
        
        return jsonify({ "message": "Receipt saved successfully.", "receipt_id": receipt_id }), 201

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 422
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)