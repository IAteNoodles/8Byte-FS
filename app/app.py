import base64
import statistics
import traceback
import pandas as pd
from datetime import date, datetime
from typing import Optional

from flask import Flask, jsonify, request
from pydantic import ValidationError

# Assuming your project structure is now modular
# --- IMPORT THE NEW AGGREGATION FUNCTION ---
from algorithms.aggregation import get_top_vendors, get_top_categories
from algorithms.search import fuzzy_search_records, search_by_keywords_concise, search_by_range
from algorithms.sort import sort_records
from database.database import get_all_receipts, save_receipt
from models.receipt import ReceiptData
from services.parsers import parse_and_extract_data
from services.currency_converter import convert_to_base_currency
from flask_cors import CORS

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg'}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Helper Function for Dynamic Filtering ---
def get_filtered_receipts(args):
    records = get_all_receipts()
    range_feature = args.get('range_feature')
    start_range = args.get('start')
    end_range = args.get('end')
    if range_feature and start_range and end_range:
        records = search_by_range(records, range_feature, start_range, end_range)
    search_keyword = args.get('search_keyword')
    search_feature = args.get('search_feature')
    if search_keyword and search_feature:
        # Split the comma-separated string from the UI into a list
        keywords = [k.strip() for k in search_keyword.split(',')]
        
        # The fuzzy search logic would also need to be updated to handle lists,
        # but for the default exact search, this works perfectly.
        search_mode = args.get('search_mode', 'exact')
        if search_mode == 'fuzzy':
            # For now, fuzzy search will only use the first keyword
            records = fuzzy_search_records(keywords[0], search_feature, records)
        else:
            records = search_by_keywords_concise(keywords, search_feature, records)
    # --- End of modification ---

    return records

# --- Core API Endpoints (Unchanged) ---
@app.route('/process-receipt', methods=['POST'])
def process_receipt_file():
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if not file.filename or not is_allowed_file(file.filename): return jsonify({"error": "Invalid file"}), 400
    file_bytes = file.read()
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    use_ai = request.form.get('use_ai', 'false').lower() == 'true'
    extracted_data = parse_and_extract_data(file_bytes, file_extension, use_ai=use_ai)
    return jsonify(extracted_data), 200

@app.route('/save-receipt', methods=['POST'])
def save_corrected_receipt():
    data = request.get_json()
    if not data: return jsonify({"error": "Invalid JSON"}), 400
    try:
        if isinstance(data.get('raw_data'), str): data['raw_data'] = base64.b64decode(data['raw_data'])
        receipt = ReceiptData(**data)
        receipt_id = save_receipt(receipt)
        return jsonify({"message": "Receipt saved", "receipt_id": receipt_id}), 201
    except ValidationError as e: return jsonify({"error": "Validation failed", "details": e.errors()}), 422
    except Exception as e: return jsonify({"error": f"Unexpected error: {e}"}), 500

@app.route('/receipts', methods=['GET'])
def get_receipts():
    try:
        records = get_filtered_receipts(request.args)
        sort_by = request.args.get('sort_by')
        if sort_by:
            order = request.args.get('order', 'asc')
            records = sort_records(records, sort_by=sort_by, reverse=(order.lower() == 'desc'))
        return jsonify(records), 200
    except Exception as e: return jsonify({"error": f"Unexpected error: {e}"}), 500

# --- Insight Endpoints ---

@app.route('/insights/statistics', methods=['GET'])
def get_expenditure_stats():
    try:
        records = get_filtered_receipts(request.args)
        if not records: return jsonify({"total": 0, "mean": 0, "median": 0}), 200
        base_currency = request.args.get('base_currency', 'INR')
        records = convert_to_base_currency(records, base_currency)
        amounts = [r['amount_in_base'] for r in records if r.get('amount_in_base') is not None]
        if not amounts: return jsonify({"total": 0, "mean": 0, "median": 0}), 200
        stats = {
            "total": round(sum(amounts), 2),
            "mean": round(statistics.mean(amounts), 2),
            "median": round(statistics.median(amounts), 2),
        }
        return jsonify(stats), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {e}"}), 500

@app.route('/insights/top-vendors', methods=['GET'])
def get_vendor_summary():
    try:
        records = get_filtered_receipts(request.args)
        if not records: return jsonify([]), 200
        mode = request.args.get('mode', 'spend')
        if mode == 'spend':
            base_currency = request.args.get('base_currency', 'INR')
            records = convert_to_base_currency(records, base_currency)
        top_vendors_data = get_top_vendors(records, mode=mode, amount_field='amount_in_base')
        results = [{"vendor": vendor, "value": value} for vendor, value in top_vendors_data]
        return jsonify(results), 200
    except Exception as e: return jsonify({"error": f"Unexpected error: {e}"}), 500

"""# --- NEW ENDPOINT FOR CATEGORY ANALYSIS ---
@app.route('/insights/top-categories', methods=['GET'])
def get_category_summary():
    Provides top category data based on the filtered dataset.
    try:
        records = get_filtered_receipts(request.args)
        if not records: return jsonify([]), 200
        mode = request.args.get('mode', 'spend')
        if mode == 'spend':
            base_currency = request.args.get('base_currency', 'INR')
            records = convert_to_base_currency(records, base_currency)
        # Use the new aggregation function
        top_categories_data = get_top_categories(records, mode=mode, amount_field='amount_in_base')
        results = [{"category": category, "value": value} for category, value in top_categories_data]
        return jsonify(results), 200
    except Exception as e: return jsonify({"error": f"Unexpected error: {e}"}), 500"""

# --- ENHANCED ENDPOINT FOR TIME-SERIES ANALYSIS ---

@app.route('/insights/spending-over-time', methods=['GET'])
def get_spending_trend():
    """Provides time-series data based on different modes (total, mean, by vendor, by category)."""
    try:
        records = get_filtered_receipts(request.args)
        if not records: return jsonify([]), 200
        
        base_currency = request.args.get('base_currency', 'INR')
        records = convert_to_base_currency(records, base_currency)
        
        df = pd.DataFrame(records)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        mode = request.args.get('mode', 'total spend').lower()
        
        # Resample daily to ensure all dates are present
        df = df.set_index('transaction_date')

        if mode == 'by vendor':
            # Group by date and vendor, sum amounts, then pivot vendors into columns
            result_df = df.groupby([pd.Grouper(freq='D'), 'vendor'])['amount_in_base'].sum().unstack(level='vendor').fillna(0)
        elif mode == 'by category':
            # Group by date and category, sum amounts, then pivot categories into columns
            result_df = df.groupby([pd.Grouper(freq='D'), 'category'])['amount_in_base'].sum().unstack(level='category').fillna(0)
        elif mode == 'mean spend':
            # Group by date and calculate the mean spend per day
            result_df = df.resample('D')['amount_in_base'].mean().fillna(0).to_frame(name="Mean Spend")
        else: # Default to 'total spend'
            # Group by date and calculate the total spend per day
            result_df = df.resample('D')['amount_in_base'].sum().fillna(0).to_frame(name="Total Spend")

        result = result_df.reset_index().to_dict('records')
        return jsonify(result), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {e}"}), 500



# --- NEW ENDPOINT FOR CATEGORY ANALYSIS ---
@app.route('/insights/top-categories', methods=['GET'])
def get_category_summary():
    """Provides top category data based on the filtered dataset."""
    try:
        records = get_filtered_receipts(request.args)
        if not records: return jsonify([]), 200
        mode = request.args.get('mode', 'spend')
        if mode == 'spend':
            base_currency = request.args.get('base_currency', 'INR')
            records = convert_to_base_currency(records, base_currency)
        # Use the new aggregation function
        top_categories_data = get_top_categories(records, mode=mode, amount_field='amount_in_base')
        results = [{"category": category, "value": value} for category, value in top_categories_data]
        return jsonify(results), 200
    except Exception as e: return jsonify({"error": f"Unexpected error: {e}"}), 500




CORS(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)