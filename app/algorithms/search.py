from typing import List, Dict, Any

def search_by_keywords_concise(keyword: str, feature: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Searches a list of records for a keyword in a specific feature field (concise version).
    
    Args:
        keyword: The substring to search for.
        feature: The dictionary key whose value should be searched.
        records: A list of dictionaries to search through.

    Returns:
        A list of records that match the search criteria.
    """
    lower_keyword = keyword.lower()
    return [
        record for record in records
        if isinstance(record.get(feature), str) and lower_keyword in record.get(feature, "").lower()
    ]