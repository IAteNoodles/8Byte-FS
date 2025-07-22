import unittest
from datetime import date

# TODO: Make sure to import your actual functions from their file.
# Assuming your functions are in a file named 'algorithms.py'
from .search import search_by_keywords_concise
from .sort import sort_records
from .aggregation import calculate_total_spend, get_top_vendors

class TestCoreAlgorithms(unittest.TestCase):

    def setUp(self):
        """Set up a sample dataset that runs before each test."""
        self.records = [
            {'vendor': 'Starbucks', 'transaction_date': date(2025, 7, 19), 'amount': 7.50, 'category': 'Coffee'},
            {'vendor': 'Grocery Mart', 'transaction_date': date(2025, 7, 18), 'amount': 120.00, 'category': 'Groceries'},
            {'vendor': 'Starbucks', 'transaction_date': date(2025, 7, 20), 'amount': 12.50, 'category': 'Coffee'},
            {'vendor': 'Amazon', 'transaction_date': date(2025, 7, 15), 'amount': 45.50}, # Missing category
            {'vendor': 'Grocery Mart', 'transaction_date': date(2025, 7, 20), 'amount': 75.00, 'category': 'Groceries'},
            {'vendor': 'Shell', 'transaction_date': date(2025, 7, 17), 'amount': 65.00, 'category': 'Gas'},
        ]
        self.empty_records = []
        self.malformed_records = [
            {'vendor': 'Test', 'transaction_date': date(2025, 1, 1), 'amount': 100},
            {'vendor': 'Test 2'}, # Missing amount
            {'vendor': 'Test 3', 'amount': 'not-a-number'} # Invalid amount type
        ]

    # -- Sorting Tests --
    def test_sort_records_by_amount_asc(self):
        sorted_data = sort_records(self.records, sort_by='amount')
        self.assertEqual(sorted_data[0]['vendor'], 'Starbucks')
        self.assertEqual(sorted_data[0]['amount'], 7.50)
        self.assertEqual(sorted_data[-1]['vendor'], 'Grocery Mart')
        self.assertEqual(sorted_data[-1]['amount'], 120.00)

    def test_sort_records_by_vendor_desc(self):
        sorted_data = sort_records(self.records, sort_by='vendor', reverse=True)
        self.assertEqual(sorted_data[0]['vendor'], 'Starbucks')
        self.assertEqual(sorted_data[-1]['vendor'], 'Amazon')

    def test_sort_records_by_date(self):
        sorted_data = sort_records(self.records, sort_by='transaction_date')
        self.assertEqual(sorted_data[0]['vendor'], 'Amazon')
        self.assertEqual(sorted_data[-1]['transaction_date'], date(2025, 7, 20))

    # -- Search Tests --
    def test_search_by_keywords_found(self):
        results = search_by_keywords_concise('star', 'vendor', self.records)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['vendor'], 'Starbucks')

    def test_search_by_keywords_not_found(self):
        results = search_by_keywords_concise('nonexistent', 'vendor', self.records)
        self.assertEqual(len(results), 0)
        
    def test_search_by_keywords_on_non_string_feature(self):
        results = search_by_keywords_concise('120', 'amount', self.records)
        self.assertEqual(len(results), 0)

    # -- Aggregation Tests --
    def test_calculate_total_spend(self):
        total = calculate_total_spend(self.records)
        self.assertAlmostEqual(total, 325.50)
        
    def test_calculate_total_spend_empty(self):
        total = calculate_total_spend(self.empty_records)
        self.assertEqual(total, 0.0)

    def test_calculate_total_spend_malformed(self):
        # Should skip missing and invalid amounts, not crash
        total = calculate_total_spend(self.malformed_records)
        self.assertEqual(total, 100)

    def test_get_top_vendors_by_frequency(self):
        top = get_top_vendors(self.records, mode='frequency')
        self.assertEqual(len(top), 4)
        self.assertEqual(top[0], ('Starbucks', 2))
        self.assertEqual(top[1], ('Grocery Mart', 2))

    def test_get_top_vendors_by_spend(self):
        top = get_top_vendors(self.records, mode='spend')
        self.assertEqual(len(top), 4)
        self.assertEqual(top[0], ('Grocery Mart', 195.00))
        self.assertEqual(top[1], ('Shell', 65.00))
        
    def test_get_top_vendors_with_limit(self):
        top = get_top_vendors(self.records, mode='spend', limit=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], 'Grocery Mart')
        self.assertEqual(top[1][0], 'Shell')


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)