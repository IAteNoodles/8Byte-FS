from typing import List, Dict, Any
# In algorithms/aggregation.py
import pandas as pd

def calculate_total_spend(records: List[Dict[str, Any]]) -> float:
    """
    Calculates the total spend by summing the 'amount' from a list of records.

    Args:
        records: A list of record dictionaries. Each dictionary is expected
                 to have an 'amount' key with a numerical value.

    Returns:
        The total spend as a float.
    """
    total = 0.0
    for record in records:
        # We use .get() to safely access the 'amount' and provide a default of 0
        # in case the key is missing from a record.
        amount = record.get('amount', 0)
        if isinstance(amount, (int, float)):
            total += amount
        # #TODO: Add more robust logging or error handling for records with invalid 'amount' types.
        
    return total

from typing import List, Dict, Any, Optional, Tuple

"""def get_top_vendors(records: List[Dict[str, Any]], mode: str = 'frequency', limit: Optional[int] = None) -> List[Tuple[str, float]]:
    
    Finds top vendors by transaction frequency or total spend.

    Args:
        records: A list of record dictionaries.
        mode: The method for aggregation. Can be 'frequency' (default) to count
              the number of transactions, or 'spend' to sum the 'amount'.
        limit: The number of top vendors to return. If None, all vendors are returned.

    Returns:
        A sorted list of tuples, where each tuple contains a vendor name and 
        their aggregated score (count or total spend), sorted in descending order.
    
    if mode not in ['frequency', 'spend']:
        raise ValueError("Mode must be either 'frequency' or 'spend'")

    vendor_summary = {}
    for record in records:
        vendor = record.get('vendor')
        if not vendor or not isinstance(vendor, str):
            continue  # Skip records without a valid vendor name

        if mode == 'frequency':
            vendor_summary[vendor] = vendor_summary.get(vendor, 0) + 1
        elif mode == 'spend':
            amount = record.get('amount', 0)
            if isinstance(amount, (int, float)):
                # #TODO: Consider currency conversion if multi-currency support is added.
                vendor_summary[vendor] = vendor_summary.get(vendor, 0) + amount

    # Sort the vendors by their aggregated value in descending order
    # #TODO: Implement a secondary sort by vendor name (alphabetical) for items with the same score.
    sorted_vendors = sorted(vendor_summary.items(), key=lambda item: item[1], reverse=True)

    if limit is not None:
        return sorted_vendors[:limit]
    
    return sorted_vendors"""



# In algorithms/aggregation.py

def get_top_vendors(records: list[dict], mode: str = 'spend', limit: int = 10, amount_field: str = 'amount') -> list:
    """
    Aggregates records to find top vendors by total spend or frequency.
    Now accepts a dynamic amount_field for currency conversion.
    """
    if not records:
        return []

    df = pd.DataFrame(records)
    if df.empty:
        return []

    if mode == 'spend':
        # Use the amount_field parameter here instead of a hardcoded 'amount'
        top_items = df.groupby('vendor')[amount_field].sum().nlargest(limit)
    else:  # mode == 'frequency'
        top_items = df['vendor'].value_counts().nlargest(limit)

    return list(top_items.items())




def get_top_categories(records: list[dict], mode: str = 'spend', limit: int = 10, amount_field: str = 'amount') -> list:
    """
    Aggregates records to find top categories by total spend or frequency.
    """
    if not records:
        return []

    # Use a DataFrame for efficient grouping
    df = pd.DataFrame(records)

    # Filter out records with no category
    df = df.dropna(subset=['category'])
    if df.empty:
        return []

    if mode == 'spend':
        # Group by category and sum the amounts, then get the top 'limit'
        top_items = df.groupby('category')[amount_field].sum().nlargest(limit)
    else: # mode == 'frequency'
        # Group by category and count occurrences, then get the top 'limit'
        top_items = df['category'].value_counts().nlargest(limit)

    return list(top_items.items())