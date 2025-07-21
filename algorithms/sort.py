from typing import List, Dict, Any
from datetime import date

def sort_records(records: List[Dict[str, Any]], sort_by: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Sorts a list of records by a specified feature.

    Args:
        records: A list of dictionaries to sort.
        sort_by: The dictionary key to sort the records by (e.g., 'amount', 'transaction_date').
        reverse: If True, sorts in descending order. Defaults to False (ascending).

    Returns:
        A new list containing the sorted records.
        
    Raises:
        KeyError: If the sort_by key is not found in a record, which can cause inconsistent sorting.
        TypeError: If records have incompatible types for the sort_by key (e.g., mixing str and int).
    """

    try:
        return sorted(records, key=lambda record: record[sort_by], reverse=reverse)
    except KeyError:
        #TODO
        print(f"Error: The sort key '{sort_by}' was not found in at least one record.")
        return records # Return original list on error
    except TypeError:
        #TODO
        print(f"Error: The records have incompatible data types for the sort key '{sort_by}'.")
        return records # Return original list on error