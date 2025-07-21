# In services/currency_converter.py
import requests
from datetime import date

# A simple cache to store fetched exchange rates for the session
RATES_CACHE = {}

def convert_to_base_currency(records: list[dict], base_currency: str) -> list[dict]:
    """
    Converts amounts in a list of records to a specified base currency.
    """
    print(f"Converting {len(records)} records to base currency: {base_currency}")
    
    for record in records:
        original_amount = record.get('amount')
        # --- THIS IS THE CORRECTED LINE ---
        # If a record has no currency, assume it's INR, not the base_currency.
        original_currency = record.get('currency', 'INR')
        transaction_date = record.get('transaction_date')

        if not original_amount or not transaction_date:
            record['amount_in_base'] = 0
            continue

        if original_currency == base_currency:
            record['amount_in_base'] = original_amount
            continue

        try:
            cache_key = (transaction_date, original_currency, base_currency)
            if cache_key in RATES_CACHE:
                rate = RATES_CACHE[cache_key]
            else:
                response = requests.get(
                    f"https://api.frankfurter.app/{transaction_date}",
                    params={"from": original_currency, "to": base_currency}
                )
                response.raise_for_status()
                rate = response.json()['rates'][base_currency]
                RATES_CACHE[cache_key] = rate

            converted_amount = original_amount * rate
            record['amount_in_base'] = round(converted_amount, 2)
        except Exception as e:
            print(f"Could not get conversion rate for {original_currency} on {transaction_date}: {e}")
            record['amount_in_base'] = original_amount

    return records