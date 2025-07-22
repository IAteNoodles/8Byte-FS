# Algorithms Module

This module contains data processing algorithms for receipt analysis, search, sorting, and aggregation.

## Components

### 📊 aggregation.py
**Data aggregation and statistical analysis**

**Key Functions:**
- `calculate_total_spend(records)` - Calculate total expenditure
- `get_top_vendors(records, mode='spend', limit=10)` - Top vendors analysis
- `get_top_categories(records, mode='spend', limit=10)` - Category breakdown

**Features:**
- Spend vs frequency analysis
- Configurable result limits
- Currency-aware calculations
- Pandas-based efficient processing

**Usage:**
```python
from algorithms.aggregation import get_top_vendors, get_top_categories

# Top vendors by spending
top_vendors = get_top_vendors(records, mode='spend', limit=5)

# Top categories by frequency
top_categories = get_top_categories(records, mode='frequency', limit=10)
```

### 🔍 search.py
**Advanced search and filtering capabilities**

**Key Functions:**
- `search_by_keywords_concise(keywords, feature, records)` - Keyword search
- `search_by_range(records, feature, start_range, end_range)` - Range filtering
- `fuzzy_search_records(query, feature, records, score_cutoff=75)` - Fuzzy matching

**Features:**
- Multi-keyword search support
- Date and amount range filtering
- Fuzzy string matching with configurable thresholds
- Case-insensitive search
- Regex pattern support

**Usage:**
```python
from algorithms.search import search_by_keywords_concise, fuzzy_search_records

# Search for multiple vendors
results = search_by_keywords_concise(['Starbucks', 'Coffee'], 'vendor', records)

# Fuzzy search for similar names
results = fuzzy_search_records('Starbuks', 'vendor', records, score_cutoff=80)

# Date range filtering
from datetime import date
results = search_by_range(records, 'transaction_date', 
                         date(2024, 1, 1), date(2024, 12, 31))
```

### 🔄 sort.py
**Data sorting and ordering**

**Key Functions:**
- `sort_records(records, sort_by, reverse=False)` - Multi-field sorting

**Features:**
- Support for all record fields
- Ascending/descending order
- Type-aware sorting (dates, numbers, strings)
- Stable sorting algorithm

**Usage:**
```python
from algorithms.sort import sort_records

# Sort by date (newest first)
sorted_records = sort_records(records, 'transaction_date', reverse=True)

# Sort by amount (lowest first)
sorted_records = sort_records(records, 'amount', reverse=False)
```

## Data Structures

### Input Format
All algorithms expect records in the following format:
```python
record = {
    'id': 1,
    'vendor': 'Starbucks',
    'transaction_date': '2024-01-15',
    'amount': 4.50,
    'currency': 'USD',
    'category': 'restaurant',
    'amount_in_base': 4.50  # Added by currency converter
}
```

### Output Formats

**Aggregation Results:**
```python
# get_top_vendors/get_top_categories output
[
    ('Starbucks', 125.50),  # (name, total_spend) or (name, frequency)
    ('McDonald\'s', 89.25),
    ('Subway', 67.80)
]
```

**Search Results:**
```python
# Returns filtered list of records
[
    {'id': 1, 'vendor': 'Starbucks', 'amount': 4.50, ...},
    {'id': 5, 'vendor': 'Starbucks', 'amount': 3.25, ...}
]
```

## Performance Characteristics

### Time Complexity
- **Aggregation**: O(n) for basic stats, O(n log n) for top-k
- **Search**: O(n) for keyword search, O(n*m) for fuzzy search
- **Sort**: O(n log n) using Python's Timsort

### Memory Usage
- **Pandas Operations**: ~2-3x memory overhead for DataFrames
- **Fuzzy Search**: O(n*m) where m is query length
- **In-place Operations**: Minimal additional memory


## Testing

```bash
# Run algorithm tests
python -m pytest app/algorithms/test.py -v


## Dependencies

### Required
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical operations
- `thefuzz` - Fuzzy string matching

### Optional
- `python-Levenshtein` - Faster fuzzy matching
- `numba` - JIT compilation for numerical operations

## Future Enhancements

- [ ] Machine learning-based categorization
- [ ] Advanced statistical analysis
- [ ] Real-time streaming algorithms
- [ ] Distributed processing support
- [ ] Custom similarity metrics
- [ ] Caching for frequent operations