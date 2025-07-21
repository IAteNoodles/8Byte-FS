import pytesseract
from PIL import Image
import io
import re
from datetime import datetime
import fitz  # PyMuPDF
from thefuzz import fuzz
from dateutil import parser  # Added for flexible date parsing


#This DOESN"T EXISTSSSSS
# Make sure you have the ai_parser.py file we created earlier
#TODO
from .ai_parser import extract_with_ai
#----------------------VENDORS-----------------------

# In services/parsers.py

# ... (imports)

# Define a structured dictionary of known vendors by category

KNOWN_VENDORS = {
    'Electricity': {
        # Existing entries
        'bescom': 'BESCOM',  # Bangalore Electricity Supply Company (Government)[2][4]
        'tneb': 'TNEB',      # Tamil Nadu Electricity Board (Government)[2][4]
        'msedcl': 'MSEDCL',  # Maharashtra State Electricity Distribution Company Limited (Government)[2][4]
        'adani': 'Adani Electricity',  # Major private distributor in Mumbai and other areas[1][3][11]
        'ntpc': 'NTPC Limited',        # National Thermal Power Corporation (Government)[2][3][5]
        'tata power': 'Tata Power',    # Prominent private player in multiple states[2][3][11]
        'nhpc': 'NHPC Limited',        # Hydroelectric power (Government)[2][3][5]
        'power grid': 'Power Grid Corporation',  # Transmission and distribution (Government)[2][3][5]
        
        # Expanded entries: Government players
        'apspdcl': 'Southern Power Distribution Company of Andhra Pradesh Limited',  # Andhra Pradesh (Government)[4][11]
        'apeastern': 'Andhra Pradesh Eastern Power Distribution Company Limited',  # Andhra Pradesh (Government)[4][11]
        'assam pdcl': 'Assam Power Distribution Company Limited',  # Assam (Government)[5]
        'bwsb': 'Bangalore Water Supply and Sewerage Board',  # Related to utilities, but includes power aspects (Government)[4]
        'cesc': 'CESC Limited',  # West Bengal, semi-government roots but privatized[2][5]
        'cspdcl': 'Chhattisgarh State Power Distribution Company Limited',  # Chhattisgarh (Government)[4]
        'dnh power': 'DNH Power Distribution Corporation Limited',  # Dadra and Nagar Haveli (Government)[5][14]
        'dtl': 'Delhi Transco Limited',  # Delhi (Government)[5][14]
        'gujarat urja': 'Gujarat Urja Vikas Nigam Limited',  # Gujarat (Government)[4]
        'haryana power': 'Haryana Power Generation Corporation Limited',  # Haryana (Government)[2]
        'hpsebl': 'Himachal Pradesh State Electricity Board Limited',  # Himachal Pradesh (Government)[2]
        'jvvnl': 'Jaipur Vidyut Vitran Nigam Limited',  # Rajasthan (Government)[4]
        'jodhpur vvn': 'Jodhpur Vidyut Vitran Nigam Limited',  # Rajasthan (Government)[4]
        'kerala seb': 'Kerala State Electricity Board',  # Kerala (Government)[2]
        'mppgcl': 'Madhya Pradesh Power Generation Company Limited',  # Madhya Pradesh (Government)[2][4]
        'mptransco': 'Madhya Pradesh Power Transmission Company Limited',  # Madhya Pradesh (Government)[2]
        'mppkvvcl': 'Madhya Pradesh Poorv Kshetra Vidyut Vitaran Company Limited',  # Madhya Pradesh (Government)[2][4]
        'mpmkvvcl': 'Madhya Pradesh Madhya Kshetra Vidyut Vitaran Company Limited',  # Madhya Pradesh (Government)[2][4]
        'mppkvvcl indore': 'Madhya Pradesh Paschim Kshetra Vidyut Vitaran Company Limited',  # Madhya Pradesh (Government)[2][4]
        'mescom': 'Mangalore Electricity Supply Company Limited',  # Karnataka (Government)[4]
        'hesco': 'Hubli Electricity Supply Company Limited',  # Karnataka (Government)[4]
        'mahavitran': 'Maharashtra State Electricity Distribution Company Limited',  # Maharashtra (Government)[2][4]
        'mahatransco': 'Maharashtra State Electricity Transmission Company Limited',  # Maharashtra (Government)[2]
        'mahagenco': 'Maharashtra State Power Generation Company Limited',  # Maharashtra (Government)[2]
        'mizoram power': 'Mizoram Power and Electricity Department',  # Mizoram (Government)[2]
        'nagaland seb': 'Nagaland State Electricity Board',  # Nagaland (Government)[2]
        'ohpc': 'Odisha Hydro Power Corporation',  # Odisha (Government)[2]
        'opgc': 'Odisha Power Generation Corporation',  # Odisha (Government)[2]
        'optcl': 'Odisha Power Transmission Corporation Limited',  # Odisha (Government)[2]
        'cesu': 'Central Electricity Supply Utility of Odisha',  # Odisha (Government)[2]
        'wesco': 'Western Electricity Supply Company of Odisha',  # Odisha (Government)[2]
        'tp nodl': 'TP Northern Odisha Distribution Limited',  # Odisha (Government-affiliated)[2]
        'pspcl': 'Punjab State Power Corporation Limited',  # Punjab (Government)[2]
        'pstcl': 'Punjab State Transmission Corporation Limited',  # Punjab (Government)[2]
        'rrvunl': 'Rajasthan Rajya Vidyut Utpadan Nigam Limited',  # Rajasthan (Government)[2]
        'rrvpnl': 'Rajasthan Rajya Vidyut Prasaran Nigam Limited',  # Rajasthan (Government)[2]
        'avvnl': 'Ajmer Vidyut Vitran Nigam Limited',  # Rajasthan (Government)[4]
        'tangedco': 'Tamil Nadu Generation and Distribution Corporation Limited',  # Tamil Nadu (Government)[2][4]
        'tantransco': 'Tamil Nadu Transmission Corporation Limited',  # Tamil Nadu (Government)[2]
        'tsgenco': 'Telangana Power Generation Corporation',  # Telangana (Government)[2][4]
        'tstransco': 'Transmission Corporation of Telangana',  # Telangana (Government)[2]
        'tsnpdcl': 'Telangana Northern Power Distribution Company Limited',  # Telangana (Government)[2][4]
        'tspdcl': 'Telangana Southern Power Distribution Company Limited',  # Telangana (Government)[2][4]
        'thdc': 'THDC India Limited',  # Uttarakhand/Himachal (Government)[5][14]
        'uprvunl': 'Uttar Pradesh Rajya Vidyut Utpadan Nigam Limited',  # Uttar Pradesh (Government)[2]
        'uppcl': 'Uttar Pradesh Power Corporation Limited',  # Uttar Pradesh (Government)[2]
        'upptcl': 'UP Power Transmission Corporation Limited',  # Uttar Pradesh (Government)[2]
        'upjvnl': 'UP Jal Vidyut Nigam Limited',  # Uttar Pradesh (Government)[2]
        'upcl': 'Uttarakhand Power Corporation Limited',  # Uttarakhand (Government)[2]
        'wbpdcl': 'West Bengal Power Development Corporation Limited',  # West Bengal (Government)[2]
        'wbseb': 'West Bengal State Electricity Board',  # West Bengal (Government)[2]
        
        # Expanded entries: Non-government (private) players
        'reliance energy': 'Reliance Energy Limited',  # Private distributor[1][4]
        'torrent power': 'Torrent Power Limited',  # Private in Gujarat and others[3][4][11]
        'bajaj energy': 'Bajaj Energy Limited',  # Private generation[5]
        'adani green': 'Adani Green Energy Limited',  # Private renewable focus[3]
        'adani power': 'Adani Power Limited',  # Private generation[3]
        'jsw energy': 'JSW Energy Limited',  # Private[3]
        'renew power': 'ReNew Power',  # Private renewable[3]
        'india power': 'India Power Corporation Limited',  # Private[3][20]
        'ravindra energy': 'Ravindra Energy',  # Private[20]
        'orient green': 'Orient Green Power Company',  # Private[3]
        'pge': 'PG&E',              # Pacific Gas and Electric (US)
        'coned': 'Con Edison',      # Consolidated Edison (US)
        'duke': 'Duke Energy',      # Duke Energy (US)
        'fpl': 'Florida Power & Light',  # Florida Power & Light (US)
        'southern': 'Southern Company',  # Southern Company (US)

    },
    'Internet & Telecom': {
        # Existing entries
        'jio': 'Jio',                  # Private, leading subscribers[6][10][18]
        'airtel': 'Airtel',            # Private, broadband and mobile[6][10][18]
        'vodafone': 'Vodafone Idea (Vi)',  # Private, merged entity[6][10][18]
        'bsnl': 'BSNL',                # Government, Bharat Sanchar Nigam Limited[6][10][12]
        'mtnl': 'MTNL',                # Government, Mahanagar Telephone Nigam Limited[6][12]
        'act': 'ACT (Atria Convergence Technologies)',  # Private broadband[6][10][12]
        'hathway': 'Hathway',          # Private cable and broadband[6][10][12]
        'excitel': 'Excitel Broadband',  # Private ISP[6][10][12]
        
        # Expanded entries: Government players
        'railwire': 'RailWire (RailTel Corporation of India)',  # Government, railway-based ISP[12][15]
        
        # Expanded entries: Non-government (private) players
        'tata play fiber': 'Tata Play Fiber',  # Private, high-speed plans[6][12]
        'you broadband': 'YOU Broadband',  # Private, Vodafone subsidiary[6][12]
        'spectra': 'Spectra',  # Private, fiber optic[6][12]
        'tikona': 'Tikona Infinet',  # Private, wireless broadband[6][12]
        'den networks': 'DEN Networks',  # Private, cable and internet[12][18]
        'gtpl': 'GTPL Hathway',  # Private, broadband and cable[12][18]
        'siti broadband': 'Siti Broadband',  # Private[12]
        'alliance broadband': 'Alliance Broadband',  # Private, regional[12][18]
        'asianet broadband': 'Asianet Broadband',  # Private, Kerala focus[12]
        'comway': 'Comway Broadband',  # Private[12]
        'connect broadband': 'Connect Broadband',  # Private[12]
        'fusionnet': 'Fusionnet',  # Private[12]
        'gigatel': 'Gigatel Networks',  # Private[12]
        'ion': 'ION by Viacom18',  # Private[12]
        'joister': 'Joister Infoserve',  # Private[12]
        'kerala vision': 'Kerala Vision Broadband',  # Private[12]
        'meghbela': 'Meghbela Broadband',  # Private[12]
        'netplus': 'Netplus Broadband',  # Private[12]
        'nextra': 'Nextra Teleservices',  # Private[12]
        'oritel': 'Oritel Broadband',  # Private[12]
        'pioneer': 'Pioneer Elabs',  # Private[12]
        'readylink': 'Readylink Internet Services',  # Private[12]
        'shyam spectra': 'Shyam Spectra',  # Private[12]
        'smartlink': 'Smartlink Broadband Services',  # Private[12]
        'timbl': 'Timbl Broadband',  # Private[12]
        'comcast': 'Comcast',       # Comcast (US)
        'att': 'AT&T',              # AT&T (US)
        'verizon': 'Verizon',       # Verizon (US)
        'tmobile': 'T-Mobile',      # T-Mobile (US)
    },
    'Groceries': {
        # Existing entries
        'reliance fresh': 'Reliance Fresh',  # Private, Reliance Retail[7][10][16]
        'dmart': 'DMart',                    # Private, Avenue Supermarts[7][10][16]
        'more': 'More Supermarket',          # Private, Aditya Birla Retail[7][10][16]
        'spencer': "Spencer's Retail",       # Private, RPG Group[7][10][16]
        'big bazaar': 'Big Bazaar',          # Private, Future Group[7][10][16]
        'lulu': 'Lulu Hypermarket',          # Private, international chain[7][10][16]
        'hypercity': 'HyperCity',            # Private, K Raheja Corp[7][10][16]
        'heritage fresh': 'Heritage Fresh',  # Private, Heritage Foods[7][10]
        'star bazaar': 'Star Bazaar',        # Private, Tata and Tesco venture[7][10]
        
        # Expanded entries: Government players
        'supplyco': 'Kerala State Civil Supplies Corporation',  # Government, subsidized groceries[19]
        
        # Expanded entries: Non-government (private) players
        'easyday': 'Easyday',  # Private, Future Group[7][16]
        'natures basket': "Nature's Basket",  # Private, Godrej Group[7][16]
        'metro cash carry': 'Metro Cash & Carry',  # Private, wholesale focus[7][16]
        'hearty mart': 'Hearty Mart',  # Private, regional[19]
        'nilgiris': 'Nilgiris',  # Private, one of the oldest chains[13][19]
        'foodworld': 'Foodworld',  # Private[13]
        'bigbasket': 'BigBasket',  # Private, online and physical[10][16]
        'jiomart': 'JioMart',  # Private, Reliance[10][16]
        'amazon fresh': 'Amazon Fresh',  # Private, e-commerce[10]
        'grofers': 'Grofers (now Blinkit)',  # Private, quick commerce[10]
        'dunzo': 'Dunzo',  # Private, delivery-focused[10]
        '7eleven': '7-Eleven',  # Private, convenience stores[16]
        'ratnadeep': 'Ratnadeep Supermarket',  # Private, South India[16]
        'vijetha': 'Vijetha Supermarkets',  # Private[16]
        'qmart': 'Q-Mart',  # Private[16]
        'smart': 'Smart Bazaar',  # Private[16]
        'vishal mega mart': 'Vishal Mega Mart',  # Private[16]
        'max hypermarket': 'Max Hypermarket',  # Private[7]
        'foodhall': 'Foodhall',  # Private, premium[7]
        'walmart': 'Walmart',       # Walmart (US)
        'kroger': 'Kroger',         # Kroger (US)
        'costco': 'Costco',         # Costco (US)
        'target': 'Target',         # Target (US)
    }
    # TODO: Add more vendors and categories as needed
}



import re

def find_currency_and_amount(text: str) -> tuple[float | None, str | None]:
    """
    Scans text to find an amount and its currency based on common symbols.

    Args:
        text: The raw text from the receipt.

    Returns:
        A tuple containing the amount (float) and the currency code (str),
        or (None, None) if no currency-adorned amount is found.
    """
    # Define currency symbols and their corresponding ISO codes
    currency_map = {
        '₹': 'INR',
        'IN': 'INR',
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
    }

    # A robust regex for capturing numbers, including those with commas
    amount_pattern_str = r'(\d{1,3}(?:,?\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)'

    detected_amount = None
    detected_currency = None

    # Iterate through each currency symbol and look for a match
    for symbol, code in currency_map.items():
        # Regex to find: [symbol][optional space][amount] OR [amount][optional space][symbol]
        pattern = re.compile(
            f"(?:{re.escape(symbol)}\s*({amount_pattern_str}))"  # e.g., $1,234.56
            f"|"
            f"({amount_pattern_str})\s*{re.escape(symbol)}",    # e.g., 1,234.56 €
            re.IGNORECASE
        )
        
        for match in pattern.finditer(text):
            # The match object will have 3 groups:
            # group(1) is from the first part of the OR: symbol-amount
            # group(2) is from the second part: amount-symbol
            # group(0) is the full match
            amount_str = match.group(1) or match.group(2)
            if amount_str:
                amount_val = float(amount_str.replace(',', ''))
                # You might add logic here to find the "best" amount if multiple are found
                detected_amount = amount_val
                detected_currency = code
                # Return on first find for simplicity, or continue to find the largest/best amount
                return detected_amount, detected_currency

    return None, None # Fallback if no symbol-based amount is found


#------------------VENDORS-------------------

import re # Make sure 're' is imported

from thefuzz import fuzz

# In services/parsers.py

def find_vendor(text: str) -> tuple[str | None, str | None]:
    """Finds a vendor using a tiered heuristic and cleans the resulting name."""
    text_lower = text.lower()
    for category, vendors in KNOWN_VENDORS.items():
        for keyword, name in vendors.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                return name, category
    corporate_suffixes = ['ltd', 'pvt', 'limited', 'corp', 'corporation', 'inc']
    for line in text.split('\n')[:15]:
        clean_line = line.strip()
        line_lower = clean_line.lower()
        if any(suffix in line_lower for suffix in corporate_suffixes) and not any(char.isdigit() for char in clean_line):
            if len(clean_line) > 3:
                vendor_name = clean_line.split(',')[0].split('(')[0]
                cleaned_name = re.sub(r"[^a-zA-Z0-9 '\"_-]", "", vendor_name).strip()
                return cleaned_name, 'Uncategorized'
    if 'electricity' in text_lower: return 'Generic Electricity Provider', 'Electricity'
    if any(k in text_lower for k in ['telecom', 'internet']): return 'Generic Telecom Provider', 'Internet & Telecom'
    if 'groceries' in text_lower: return 'Generic Grocery Store', 'Groceries'
    return None, None

def find_date(text: str) -> str | None:
    """Finds all possible dates in the text and returns the earliest one."""
    date_pattern = r'(\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})'
    matches = re.findall(date_pattern, text)
    if not matches: return None
    parsed_dates = []
    for date_str in matches:
        try:
            parsed_dates.append(datetime.strptime(date_str.replace('/', '-'), '%d-%m-%Y'))
        except ValueError:
            try:
                parsed_dates.append(datetime.strptime(date_str.replace('/', '-'), '%Y-%m-%d'))
            except ValueError:
                continue
    if parsed_dates: return min(parsed_dates).strftime('%Y-%m-%d')
    return None

def find_amount(text: str) -> float | None:
    """Finds the total amount using a two-stage, bottom-up search."""
    currency_pattern = r'(¥|₹|Rs\.?|INR|rupees|\$|USD|€|EUR|£|GBP)'
    number_pattern = r'([\d,]+(?:\.\d{1,2})?)'
    amount_keywords = ["amount to be paid", "net amt due", "total amount due", "net amount payable", "grand total", "total", "amt", "due"]
    lines = text.split('\n')
    # Primary Method: Direct currency search
    for line in reversed(lines):
        if re.search(currency_pattern, line, re.IGNORECASE) and re.search(number_pattern, line):
            match = re.search(number_pattern, line)
            if match:
                try: return float(match.group(1).replace(',', '').replace(' ', ''))
                except (ValueError, AttributeError): continue
    # Fallback Method: Fuzzy keyword search
    for line in reversed(lines):
        if max(fuzz.token_set_ratio(k, line.lower()) for k in amount_keywords) >= 80:
            match = re.search(number_pattern, line)
            if match:
                try: return float(match.group(1).replace(',', '').replace(' ', ''))
                except (ValueError, AttributeError): continue
    return None

# --- Main Controller Function ---
def parse_and_extract_data(file_bytes: bytes, file_extension: str, use_ai: bool = False) -> dict:
    """
    Selects an OCR engine (Tesseract or AI), gets raw text, then applies fuzzy parsers.
    Now includes currency detection.
    """
    raw_text = ""
    # This entire OCR section remains unchanged
    if use_ai:
        print("Using AI-Enhanced OCR (PaddleOCR)...")
        raw_text = extract_with_ai(file_bytes, file_extension)
    else:
        print("Using Standard OCR (Tesseract)...")
        if file_extension in ['jpg', 'png', 'jpeg']:
            try: raw_text = pytesseract.image_to_string(Image.open(io.BytesIO(file_bytes)))
            except Exception as e: print(f"Error during Tesseract OCR: {e}")
        elif file_extension == 'pdf':
            try:
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    for page in doc:
                        text = page.get_text()
                        if not text.strip():
                            pix = page.get_pixmap()
                            raw_text += pytesseract.image_to_string(Image.open(io.BytesIO(pix.tobytes("png")))) + "\n"
                        else:
                            raw_text += text + "\n"
            except Exception as e: print(f"Error processing PDF with Tesseract: {e}")
        elif file_extension == 'txt':
            raw_text = file_bytes.decode('utf-8', errors='ignore')

    # --- MODIFIED PARSING LOGIC ---

    # 1. Parse vendor and date as you did before
    vendor, category = find_vendor(raw_text)
    transaction_date = find_date(raw_text)

    # 2. Use the new helper to find amount AND currency together
    amount, currency = find_currency_and_amount(raw_text)

    # 3. Fallback Logic: If no currency symbol was found, use your original method
    if amount is None:
        print("No currency symbol found. Using fallback amount parser.")
        amount = find_amount(raw_text)  # Your original amount-finding function
        currency = "INR"                 # Assign the default currency

    # 4. Return the dictionary, now with the new 'currency' field included
    return {
        "vendor": vendor,
        "transaction_date": transaction_date,
        "amount": amount,
        "currency": currency, # Add the new currency field to the response
        "raw_text": raw_text,
        "category": category
    }

