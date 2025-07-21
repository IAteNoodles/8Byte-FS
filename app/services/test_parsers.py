import unittest
from datetime import datetime

# TODO: Make sure to import your actual functions from services/parsers.py
from parsers import find_vendor, find_date, find_amount, KNOWN_VENDORS

# We must define the KNOWN_VENDORS dictionary here as well so the test can run independently.
# This should mirror the one in your parsers.py file.
KNOWN_VENDORS = {
    'Electricity': {
        'bescom': 'BESCOM',
        'tneb': 'TNEB',
    },
    'Internet & Telecom': {
        'jio': 'Jio',
        'airtel': 'Airtel',
    },
    'Groceries': {
        'dmart': 'DMart',
        'more': 'More Supermarket',
    }
}

# This is a bit of a workaround to make the KNOWN_VENDORS available to the find_vendor function
# without changing its signature.


class TestParsingLogic(unittest.TestCase):

    def setUp(self):
        """Set up sample text blocks simulating OCR output from Indian bills."""
        self.grocery_text = """
        DMART
        Some Address, Bengaluru
        Date: 19/07/2025 Time: 19:40
        ...
        Grand Total   Rs. 1,250.50
        """
        
        self.electricity_text = """
        BESCOM
        Bangalore Electricity Supply Company Ltd
        Bill Date: 20-06-2025
        Due Date: 15-07-2025
        ...
        Net Amount Payable : ₹ 2345.00
        """
        
        self.internet_text = """
        Welcome to Airtel
        Invoice Date : 01-07-2025
        ...
        Total Amount Due 999.00
        """
        
        self.unknown_vendor_text = """
        Krishna Bhavan
        South Indian Food Joint
        ...
        Total: 450.00
        """

    def test_find_vendor(self):
        self.assertEqual(find_vendor(self.grocery_text), ('DMart', 'Groceries'))
        self.assertEqual(find_vendor(self.electricity_text), ('BESCOM', 'Electricity'))
        self.assertEqual(find_vendor(self.internet_text), ('Airtel', 'Internet & Telecom'))
        # Test the fallback heuristic
        self.assertEqual(find_vendor(self.unknown_vendor_text), ('Krishna Bhavan', 'Uncategorized'))

    def test_find_date(self):
        # Test prioritizing "Bill Date" and DD-MM-YYYY format
        self.assertEqual(find_date(self.electricity_text), '2025-06-20')
        # Test "Invoice Date" and DD/MM/YYYY format
        self.assertEqual(find_date(self.internet_text), '2025-07-01')
        # Test finding a date without a keyword
        self.assertEqual(find_date(self.grocery_text), '2025-07-19')
        # Test no date found
        self.assertIsNone(find_date("Some text without a date."))

    def test_find_amount(self):
        self.assertEqual(find_amount(self.grocery_text), 1250.50)
        self.assertEqual(find_amount(self.electricity_text), 2345.00)
        self.assertEqual(find_amount(self.internet_text), 999.00)
        # Test no amount found
        self.assertIsNone(find_amount("Some text without a total."))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)