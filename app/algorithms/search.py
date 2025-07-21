from typing import List, Dict, Any

import pandas as pd
import re

def search_by_keywords_concise(keywords: list[str], feature: str, records: list[dict]) -> list[dict]:
    """
    Filters records where the feature contains ANY of the provided keywords.
    Keywords are treated as a comma-separated list.
    """
    if not keywords or not keywords[0]:
        return records

    df = pd.DataFrame(records)
    if feature not in df.columns:
        return []

    # Create a regex pattern like 'word1|word2|word3' to search for any keyword
    # re.escape handles special characters safely
    search_pattern = '|'.join(map(re.escape, keywords))
    
    # Filter where the feature column contains any of the keywords, case-insensitive
    mask = df[feature].str.contains(search_pattern, case=False, na=False)
    return df[mask].to_dict('records')
from datetime import datetime

def search_by_range(records: list[dict], feature: str, start_range, end_range) -> list[dict]:
    """
    Filters records to find items where a specific feature's value is within a given range.
    """
    results = []
    is_date_range = 'date' in feature.lower()

    for record in records:
        value = record.get(feature)
        if value is None:
            continue

        try:
            # Convert values to a comparable type (date or float)
            if is_date_range:
                record_value = datetime.strptime(str(value), '%Y-%m-%d').date()
                start = datetime.strptime(str(start_range), '%Y-%m-%d').date()
                end = datetime.strptime(str(end_range), '%Y-%m-%d').date()
            else:
                record_value = float(value)
                start = float(start_range)
                end = float(end_range)

            # Check if the value is within the range
            if start <= record_value <= end:
                results.append(record)
        except (ValueError, TypeError) as e:
            # Silently skip records that can't be converted (e.g., malformed date)
            print(f"Skipping record due to conversion error: {e}")
            continue
            
    return results

from thefuzz import fuzz
from typing import List, Dict, Any

def fuzzy_search_records(query: str, feature: str, records: List[Dict[str, Any]], score_cutoff: int = 75) -> List[Dict[str, Any]]:
    """
    Searches records using a fuzzy matching algorithm.
    """
    results = []
    for record in records:
        value_to_check = record.get(feature)
        if isinstance(value_to_check, str):
            score = fuzz.partial_ratio(query.lower(), value_to_check.lower())
            if score >= score_cutoff:
                results.append(record)
    return results