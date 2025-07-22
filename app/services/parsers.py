import pytesseract
from PIL import Image
import io
import re
from datetime import datetime
import fitz  # PyMuPDF
from thefuzz import fuzz

# Try to import AI parser, fallback gracefully if not available
try:
    from ai_parser import extract_with_ai, extract_structured_receipt_data
    AI_PARSER_AVAILABLE = True
except ImportError:
    try:
        # Try relative import as fallback
        from .ai_parser import extract_with_ai, extract_structured_receipt_data
        AI_PARSER_AVAILABLE = True
    except ImportError:
        AI_PARSER_AVAILABLE = False
        print("AI parser not available. Using standard OCR only.")

#----------------------VENDORS-----------------------

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
    },
    'Restaurant': {
        'mcdonalds': "McDonald's",
        'kfc': 'KFC',
        'pizza hut': 'Pizza Hut',
        'dominos': "Domino's Pizza",
        'subway': 'Subway',
        'starbucks': 'Starbucks',
        'cafe coffee day': 'Cafe Coffee Day',
        'barista': 'Barista',
        'burger king': 'Burger King',
        'taco bell': 'Taco Bell',
        'restaurant': 'Restaurant',
        'cafe': 'Cafe',
        'hotel': 'Hotel Restaurant',
        'dhaba': 'Dhaba',
        'food court': 'Food Court',
    },
    'Transportation': {
        'uber': 'Uber',
        'ola': 'Ola',
        'rapido': 'Rapido',
        'auto': 'Auto Rickshaw',
        'taxi': 'Taxi',
        'metro': 'Metro',
        'bus': 'Bus',
        'train': 'Train',
        'petrol pump': 'Petrol Pump',
        'fuel': 'Fuel Station',
        'hp': 'HP Petrol Pump',
        'iocl': 'Indian Oil',
        'bpcl': 'BPCL',
        'shell': 'Shell',
        'essar': 'Essar Oil',
        'reliance petrol': 'Reliance Petrol',
    },
    'Healthcare': {
        'hospital': 'Hospital',
        'clinic': 'Clinic',
        'pharmacy': 'Pharmacy',
        'medical': 'Medical Center',
        'apollo': 'Apollo Hospital',
        'fortis': 'Fortis Hospital',
        'max': 'Max Hospital',
        'aiims': 'AIIMS',
        'medplus': 'MedPlus',
        'apollo pharmacy': 'Apollo Pharmacy',
        'guardian': 'Guardian Pharmacy',
        'wellness': 'Wellness Center',
        'diagnostic': 'Diagnostic Center',
        'lab': 'Laboratory',
    },
    'Shopping': {
        'mall': 'Shopping Mall',
        'shop': 'Shop',
        'store': 'Store',
        'retail': 'Retail Store',
        'fashion': 'Fashion Store',
        'clothing': 'Clothing Store',
        'electronics': 'Electronics Store',
        'mobile': 'Mobile Store',
        'book': 'Book Store',
        'gift': 'Gift Shop',
        'jewellery': 'Jewellery Store',
        'footwear': 'Footwear Store',
    },
    'Banking': {
        'sbi': 'State Bank of India',
        'hdfc': 'HDFC Bank',
        'icici': 'ICICI Bank',
        'axis': 'Axis Bank',
        'pnb': 'Punjab National Bank',
        'bank': 'Bank',
        'atm': 'ATM',
        'branch': 'Bank Branch',
        'cooperative': 'Cooperative Bank',
    },
    'Education': {
        'school': 'School',
        'college': 'College',
        'university': 'University',
        'institute': 'Institute',
        'academy': 'Academy',
        'coaching': 'Coaching Center',
        'tuition': 'Tuition Center',
        'library': 'Library',
        'bookstore': 'Book Store',
    }
}
# ==============================================================================
# ENHANCED PARSING FUNCTIONS
# ==============================================================================

def find_vendor(text: str) -> tuple[str | None, str | None]:
    """
    Enhanced vendor detection with category-first approach:
    1. First scan for category keywords (electricity, internet, groceries, etc.)
    2. If category found, only match vendors from that category
    3. If no category found, match all vendors
    4. Fallback to business suffix heuristics
    """
    text_lower = text.lower()
    lines = text.split('\n')
    
    # Step 1: Detect category from document content first
    category_keywords = {
        'Electricity': ['electricity', 'electric', 'power', 'energy', 'utility', 'bescom', 'tneb', 'msedcl'],
        'Internet & Telecom': ['internet', 'broadband', 'telecom', 'mobile', 'phone', 'wifi', 'data'],
        'Groceries': ['grocery', 'supermarket', 'fresh', 'mart', 'food'],
        'Restaurant': ['restaurant', 'cafe', 'hotel', 'dining', 'food court'],
        'Transportation': ['taxi', 'uber', 'ola', 'fuel', 'petrol', 'gas', 'transport'],
        'Healthcare': ['hospital', 'clinic', 'medical', 'pharmacy', 'health'],
        'Shopping': ['mall', 'shop', 'retail', 'store', 'fashion'],
        'Banking': ['bank', 'atm', 'financial', 'credit', 'debit']
    }
    
    detected_category = None
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if fuzz.partial_ratio(keyword, text_lower) >= 85:
                detected_category = category
                print(f"Category detected: {category} (keyword: '{keyword}')")
                break
        if detected_category:
            break
    
    # Step 2: Search for vendors based on detected category
    if detected_category:
        # Only search within the detected category
        vendors_to_search = {detected_category: KNOWN_VENDORS[detected_category]}
        print(f"Searching only in {detected_category} category")
    else:
        # Search all categories
        vendors_to_search = KNOWN_VENDORS
        print("No specific category detected, searching all categories")
    
    # Fuzzy search within the selected vendor categories
    best_match_score = 0
    best_vendor_name = None
    best_vendor_category = None
    
    for category, vendors in vendors_to_search.items():
        for keyword, name in vendors.items():
            # Skip very short keywords to avoid false matches
            if len(keyword) < 4:
                continue
                
            # Use multiple fuzzy matching approaches
            partial_score = fuzz.partial_ratio(keyword.lower(), text_lower)
            token_score = fuzz.token_sort_ratio(keyword.lower(), text_lower)
            ratio_score = fuzz.ratio(keyword.lower(), text_lower)
            
            # Take the best score but require higher threshold for short keywords
            score = max(partial_score, token_score, ratio_score)
            min_threshold = 90 if len(keyword) < 6 else 85
            
            if score > best_match_score and score >= min_threshold:
                # Additional check: keyword should appear as a meaningful part
                if keyword.lower() in text_lower or any(word in text_lower for word in keyword.lower().split()):
                    best_match_score = score
                    best_vendor_name = name
                    best_vendor_category = category
    
    if best_vendor_name:
        print(f"Vendor found by fuzzy search: {best_vendor_name} (Score: {best_match_score})")
        return best_vendor_name, best_vendor_category

    # Step 3: Fallback to business suffix heuristics
    business_suffixes = ['ltd', 'limited', 'pvt', 'private', 'corp', 'corporation', 
                        'inc', 'incorporated', 'llc', 'llp', 'co', 'company']
    
    for i, line in enumerate(lines[:15]):  # Check top 15 lines
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        # Skip lines that are too short or contain obvious non-vendor info
        if len(line_clean) < 5:
            continue
        if re.search(r'^\d+$|total|amount|₹|\$|invoice|bill|date.*\d{4}|account|number|rr\s+number|tariff|reading', line_clean, re.IGNORECASE):
            continue
            
        # Check for business suffixes - require word boundaries for precision
        suffix_pattern = r'\b(?:' + '|'.join(business_suffixes) + r')\b'
        if re.search(suffix_pattern, line_lower):
            print(f"Found business suffix in line: '{line_clean}'")
            
            # Extract vendor name - handle various formats
            cleaned_line = re.sub(r'[(),]', ' ', line_clean)  # Remove parentheses and commas
            
            # Split by suffix and take the first part
            for suffix in business_suffixes:
                if suffix in line_lower:
                    parts = re.split(suffix, cleaned_line, flags=re.IGNORECASE)
                    if parts and len(parts[0].strip()) >= 3:
                        vendor_name = parts[0].strip()
                        vendor_name = re.sub(r'[^\w\s&-]', '', vendor_name).strip()
                        
                        if len(vendor_name) >= 3:
                            # Use detected category if available, otherwise determine from name
                            if detected_category:
                                category = detected_category
                            else:
                                vendor_name_lower = vendor_name.lower()
                                category = "Business"  # Default
                                
                                if any(word in vendor_name_lower for word in ['petroleum', 'oil', 'fuel', 'gas']):
                                    category = "Transportation"
                                elif any(word in vendor_name_lower for word in ['electric', 'power', 'energy']):
                                    category = "Electricity"
                                elif any(word in vendor_name_lower for word in ['bank', 'financial']):
                                    category = "Banking"
                                elif any(word in vendor_name_lower for word in ['hospital', 'medical', 'health']):
                                    category = "Healthcare"
                            
                            print(f"Vendor found by business suffix: {vendor_name} ({category})")
                            return vendor_name, category
                    break

    # Step 4: Final fallback - generic category provider
    if detected_category:
        print(f"Using detected category as fallback: {detected_category}")
        return f"Generic {detected_category} Provider", detected_category

    return None, None


def find_date(text: str) -> str | None:
    """
    Enhanced date detection starting from top:
    1. Look for 'date:' labels with fuzzy search
    2. Look for YYYY-MM-DD or similar patterns with punctuation
    3. Apply fuzzy search for date-related keywords
    """
    lines = text.split('\n')
    
    # Step 1: Look for explicit date labels (start from top)
    date_keywords = ['date:', 'date', 'dated', 'bill date', 'invoice date', 'order date', 'transaction date']
    
    for i, line in enumerate(lines[:15]):  # Check top 15 lines
        line_lower = line.lower().strip()
        
        # Check for date keywords with fuzzy matching (lower threshold for OCR errors)
        for keyword in date_keywords:
            if fuzz.partial_ratio(keyword, line_lower) >= 70:  # Lower threshold for OCR errors
                # Search this line and next 2 lines for date patterns
                search_area = " ".join(lines[i:i+3])
                date_found = _extract_date_from_text(search_area)
                if date_found:
                    print(f"Date found near keyword '{keyword}': {date_found}")
                    return date_found

    # Step 2: Look for standard date patterns (YYYY-MM-DD, DD/MM/YYYY, etc.)
    for line in lines[:20]:  # Check top 20 lines
        # Look for structured date patterns
        date_patterns = [
            r'\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{4}\b',  # DD/MM/YYYY or MM/DD/YYYY
            r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2}\b',  # DD/MM/YY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                parsed_date = _parse_date_string(match)
                if parsed_date:
                    formatted_date = parsed_date.strftime('%Y-%m-%d')
                    print(f"Date found by pattern matching: {formatted_date}")
                    return formatted_date

    # Step 3: Fuzzy search for month names and dates
    month_pattern = r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{2,4}\b'
    for line in lines[:20]:
        matches = re.findall(month_pattern, line, re.IGNORECASE)
        for match in matches:
            parsed_date = _parse_date_string(match)
            if parsed_date:
                formatted_date = parsed_date.strftime('%Y-%m-%d')
                print(f"Date found by month pattern: {formatted_date}")
                return formatted_date

    return None


def find_currency_and_amount(text: str) -> tuple[float | None, str | None]:
    """
    Enhanced amount detection starting from bottom:
    1. Look for amount keywords (total, amount, to be paid) with fuzzy search
    2. When found, look at the number and check 2 lines up and around
    3. Look for separators (---, ===) and check amounts below them
    4. Return the most likely final amount
    """
    lines = text.split('\n')
    amount_keywords = ["total", "grand total", "amount", "to pay", "amount to be paid", "balance", 
                      "net amount", "final amount", "payable", "due", "subtotal", "bill amount",
                      "invoice amount", "payment due", "amount due", "total due", "total payable",
                      "total amount", "sum total", "net total", "gross amount", "charge", "fee",
                      "price", "cost", "payment", "outstanding", "balance due", "to be paid"]
    currency_map = {'₹': 'INR', '¥': 'INR', 'rs': 'INR', 'inr': 'INR', '$': 'USD', '€': 'EUR', '£': 'GBP'}
    
    # Improved amount pattern to catch various formats
    amount_pattern = r'(?:rs\.?\s*|₹\s*|¥\s*|inr\s*|\$\s*|€\s*|£\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)'
    candidates = []

    # Step 0: High priority scan for currency symbols directly next to numbers
    currency_adjacent_pattern = r'([₹¥$€£])\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    for line in lines:
        matches = re.finditer(currency_adjacent_pattern, line, re.IGNORECASE)
        for match in matches:
            symbol, amount_str = match.groups()
            try:
                clean_amount = amount_str.replace(',', '')
                amount_val = float(clean_amount)
                
                if amount_val < 1:
                    continue
                
                # Skip date-like numbers (years)
                if 1900 <= amount_val <= 2100:
                    continue
                
                # Map currency symbol
                currency_found = currency_map.get(symbol, 'INR')
                
                # VERY HIGH priority for currency symbols directly adjacent to numbers
                priority = 500  # Highest priority
                candidates.append((amount_val, currency_found, priority))
                print(f"Found currency-adjacent amount: {symbol} {amount_val} (priority: {priority})")
                
            except ValueError:
                continue

    # Start from bottom - check last 25 lines
    for i in range(len(lines) - 1, max(0, len(lines) - 25), -1):
        line = lines[i].strip()
        line_lower = line.lower()
        
        if not line:
            continue
            
        # Step 1: Look for amount keywords with fuzzy search
        best_keyword_score = 0
        matched_keyword = ""
        
        # Define keyword priorities (higher = more specific/important)
        keyword_priorities = {
            "amount to be paid": 100,
            "total amount": 95,
            "grand total": 95,
            "total": 90,
            "amount due": 85,
            "total due": 85,
            "net amount": 80,
            "balance": 75,
            "due": 70,
            "amount": 65,
            "payable": 60,
            "payment": 55,
            "cost": 50,
            "price": 50,
            "fee": 45,
            "charge": 45
        }
        
        for keyword in amount_keywords:
            score = fuzz.partial_ratio(keyword, line_lower)
            if score >= 80:  # Only consider good matches
                # Apply keyword priority bonus
                priority_bonus = keyword_priorities.get(keyword, 50)
                adjusted_score = score + priority_bonus
                
                if adjusted_score > best_keyword_score:
                    best_keyword_score = adjusted_score
                    matched_keyword = keyword
                    
        # Debug output
        if best_keyword_score >= 80:
            print(f"Found keyword '{matched_keyword}' in line: '{line}' (score: {best_keyword_score})")
        
        # Step 2: Check if previous lines have separators
        has_separator_above = False
        if i > 0:
            prev_line = lines[i-1].strip()
            if re.match(r'^[-=_*\.]{3,}$', prev_line):
                has_separator_above = True
        
        # Step 3: If we found keywords or separators, extract amounts
        if best_keyword_score >= 130 or has_separator_above:  # Higher threshold due to priority bonus
            # For keyword matches, focus on the current line first
            if best_keyword_score >= 80:
                # Find amounts on the same line as the keyword
                amount_matches = re.findall(amount_pattern, line, re.IGNORECASE)
                
                same_line_amounts = []
                for amount_str in amount_matches:
                    try:
                        clean_amount = amount_str.replace(',', '')
                        amount_val = float(clean_amount)
                        
                        if amount_val < 1:
                            continue
                        
                        # Skip date-like numbers (years)
                        if 1900 <= amount_val <= 2100:
                            continue
                        
                        # Detect currency
                        currency_found = 'INR'
                        for symbol, code in currency_map.items():
                            if symbol in line.lower():
                                currency_found = code
                                break
                        
                        # Very high priority for amounts on same line as keywords
                        priority = best_keyword_score + 200
                        same_line_amounts.append((amount_val, currency_found, priority))
                        print(f"Found amount {amount_val} on same line as '{matched_keyword}' (priority: {priority})")
                        
                    except ValueError:
                        continue
                
                # If we found amounts on the same line as keywords, use them and skip nearby lines
                if same_line_amounts:
                    candidates.extend(same_line_amounts)
                else:
                    # Only look at nearby lines if no amount found on keyword line
                    search_start = max(0, i - 2)
                    search_end = min(len(lines), i + 3)
                    
                    for j in range(search_start, search_end):
                        if j == i or not lines[j].strip():
                            continue
                            
                        amount_matches = re.findall(amount_pattern, lines[j], re.IGNORECASE)
                        
                        for amount_str in amount_matches:
                            try:
                                clean_amount = amount_str.replace(',', '')
                                amount_val = float(clean_amount)
                                
                                if amount_val < 1:
                                    continue
                                
                                # Skip date-like numbers (years)
                                if 1900 <= amount_val <= 2100:
                                    continue
                                
                                currency_found = 'INR'
                                for symbol, code in currency_map.items():
                                    if symbol in lines[j].lower():
                                        currency_found = code
                                        break
                                
                                # Lower priority for nearby lines
                                priority = best_keyword_score + 50
                                candidates.append((amount_val, currency_found, priority))
                                
                            except ValueError:
                                continue
            
            # For separator matches, look in nearby lines
            elif has_separator_above:
                search_start = max(0, i - 1)
                search_end = min(len(lines), i + 2)
                
                for j in range(search_start, search_end):
                    if j == i or not lines[j].strip():
                        continue
                        
                    amount_matches = re.findall(amount_pattern, lines[j], re.IGNORECASE)
                    
                    for amount_str in amount_matches:
                        try:
                            clean_amount = amount_str.replace(',', '')
                            amount_val = float(clean_amount)
                            
                            if amount_val < 1:
                                continue
                            
                            # Skip date-like numbers (years)
                            if 1900 <= amount_val <= 2100:
                                continue
                            
                            currency_found = 'INR'
                            for symbol, code in currency_map.items():
                                if symbol in lines[j].lower():
                                    currency_found = code
                                    break
                            
                            priority = 75  # Medium priority for separator context
                            candidates.append((amount_val, currency_found, priority))
                            
                        except ValueError:
                            continue

    if not candidates:
        # Fallback: look for any large amounts in bottom 10 lines
        for line in lines[-10:]:
            amounts = re.findall(amount_pattern, line, re.IGNORECASE)
            for amount_str in amounts:
                try:
                    clean_amount = amount_str.replace(',', '')
                    amount_val = float(clean_amount)
                    if amount_val >= 10:  # Reasonable minimum for a receipt total
                        currency_found = 'INR'
                        for symbol, code in currency_map.items():
                            if symbol in line.lower():
                                currency_found = code
                                break
                        candidates.append((amount_val, currency_found, 10))  # Low priority
                except ValueError:
                    continue

    if candidates:
        # Sort by priority first, then by amount (largest)
        best_candidate = max(candidates, key=lambda x: (x[2], x[0]))
        amount, currency, _ = best_candidate
        print(f"Amount found: {currency} {amount}")
        return amount, currency

    return None, None


# --- Helper functions for Date Parsing ---
def _extract_date_from_text(text: str) -> str | None:
    """Finds all possible dates in a block of text and returns the best one."""
    date_patterns = [
        r'\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b',  # YYYY-MM-DD
        r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{4}\b',  # DD/MM/YYYY or MM/DD/YYYY
        r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2}\b',  # DD/MM/YY
        r'\b\d{8}\b',  # YYYYMMDD (compact format)
        r'\b\d{1,2}[-/.\s]+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[-/.\s]+\d{2,4}\b'  # DD Month YYYY with various separators
    ]
    
    found_dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for date_str in matches:
            parsed_date = _parse_date_string(date_str.strip())
            if parsed_date:
                found_dates.append(parsed_date)

    if not found_dates:
        return None

    # Return the most recent valid date (not in future)
    today = datetime.now()
    valid_dates = [d for d in found_dates if d <= today]
    
    if valid_dates:
        return max(valid_dates).strftime('%Y-%m-%d')
    else:
        # If all dates are in future, return the earliest one
        return min(found_dates).strftime('%Y-%m-%d')

def _parse_date_string(date_str: str) -> datetime | None:
    """Parse date string with multiple format attempts."""
    if not date_str:
        return None
        
    # Clean up the date string
    date_str = date_str.strip()
    
    # Try compact format first with original string (no normalization)
    if re.match(r'^\d{8}$', date_str):
        try:
            parsed = datetime.strptime(date_str, '%Y%m%d')
            return parsed
        except ValueError:
            pass
    
    # Handle different separators for other formats
    normalized_date = re.sub(r'[/.\s]+', '-', date_str)
    
    # Try different date formats with normalized string
    formats_to_try = [
        '%Y-%m-%d',     # 2024-01-15
        '%d-%m-%Y',     # 15-01-2024
        '%m-%d-%Y',     # 01-15-2024
        '%d-%m-%y',     # 15-01-24
        '%m-%d-%y',     # 01-15-24
        '%d-%b-%Y',     # 15-Jan-2024
        '%b-%d-%Y',     # Jan-15-2024
        '%B-%d-%Y',     # January-15-2024
    ]
    
    for fmt in formats_to_try:
        try:
            parsed = datetime.strptime(normalized_date, fmt)
            # Handle 2-digit years
            if parsed.year < 1950:
                parsed = parsed.replace(year=parsed.year + 2000)
            return parsed
        except ValueError:
            continue
    
    # Try original string for month names
    try:
        # Handle formats like "15 Jan 2024"
        parts = date_str.split()
        if len(parts) == 3:
            day, month, year = parts
            month_names = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month_num = month_names.get(month.lower()[:3])
            if month_num:
                return datetime(int(year), month_num, int(day))
    except (ValueError, IndexError):
        pass
    
    return None


# ==============================================================================
# MAIN CONTROLLER FUNCTION
# ==============================================================================
def parse_and_extract_data(file_bytes: bytes, file_extension: str, use_ai: bool = False) -> dict:
    """
    Main function to orchestrate OCR and parsing with enhanced logic.
    """
    raw_text = ""
    
    try:
        if use_ai and AI_PARSER_AVAILABLE:
            print("Using AI-Enhanced OCR...")
            
            # Step 1: Get AI response (could be JSON or text)
            ai_response = extract_with_ai(file_bytes, file_extension)
            
            # Step 2: Try to parse as JSON first

            print(ai_response)
            
            try:
                import json
                # Try to find JSON in the response
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    structured_data = json.loads(json_str)
                    
                    # Validate it has the expected fields
                    expected_fields = ['vendor', 'category', 'date', 'amount', 'currency']
                    if any(field in structured_data for field in expected_fields):
                        print("✓ Valid JSON found in AI response, using structured data")
                        return {
                            "vendor": structured_data.get('vendor'),
                            "transaction_date": structured_data.get('date'),
                            "amount": structured_data.get('amount'),
                            "currency": structured_data.get('currency', 'INR'),
                            "raw_text": ai_response,
                            "category": structured_data.get('category'),
                            "source": "ai_json"
                        }
                
                print("✗ No valid JSON found in AI response, comparing with traditional OCR")
                
                # Get traditional OCR text for comparison
                traditional_text = _extract_text_with_ocr(file_bytes, file_extension)
                
                # Compare quality: use length and content richness as metrics
                ai_length = len(ai_response.strip()) if ai_response else 0
                traditional_length = len(traditional_text.strip()) if traditional_text else 0
                
                print(f"AI text length: {ai_length} chars")
                print(f"Traditional OCR length: {traditional_length} chars")
                
                # Use AI text only if it's significantly better than traditional
                if ai_length > traditional_length * 0.8:  # AI should be at least 80% as good
                    print("✓ Using AI text (better or comparable quality)")
                    raw_text = ai_response
                else:
                    print("✓ Using traditional OCR text (better quality)")
                    raw_text = traditional_text
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"✗ JSON parsing failed: {e}, comparing AI text with traditional OCR")
                
                # Get traditional OCR text for comparison
                traditional_text = _extract_text_with_ocr(file_bytes, file_extension)
                
                # Compare quality: use length and content richness as metrics
                ai_length = len(ai_response.strip()) if ai_response else 0
                traditional_length = len(traditional_text.strip()) if traditional_text else 0
                
                print(f"AI text length: {ai_length} chars")
                print(f"Traditional OCR length: {traditional_length} chars")
                
                # Use AI text only if it's significantly better than traditional
                if ai_length > traditional_length * 0.8:  # AI should be at least 80% as good
                    print("✓ Using AI text (better or comparable quality)")
                    raw_text = ai_response
                else:
                    print("✓ Using traditional OCR text (better quality)")
                    raw_text = traditional_text
                
        else:
            print("Using Standard OCR...")
            raw_text = _extract_text_with_ocr(file_bytes, file_extension)

        # Print raw text for debugging
        print("=" * 50)
        print("RAW TEXT EXTRACTED FROM OCR:")
        print("=" * 50)
        print(raw_text)
        print("=" * 50)
        print(f"Text length: {len(raw_text) if raw_text else 0} characters")
        print("=" * 50)

        if not raw_text or len(raw_text.strip()) < 10:
            print("Warning: OCR extracted very little text")
            return {
                "vendor": None,
                "transaction_date": None,
                "amount": None,
                "currency": "INR",
                "raw_text": raw_text,
                "category": None,
                "error": "Insufficient text extracted from document"
            }

        # Apply enhanced parsing functions
        vendor, category = find_vendor(raw_text)
        transaction_date = find_date(raw_text)
        amount, currency = find_currency_and_amount(raw_text)
        
        return {
            "vendor": vendor,
            "transaction_date": transaction_date,
            "amount": amount,
            "currency": currency or "INR",
            "raw_text": raw_text,
            "category": category
        }
        
    except Exception as e:
        print(f"Error in parse_and_extract_data: {str(e)}")
        return {
            "vendor": None,
            "transaction_date": None,
            "amount": None,
            "currency": "INR",
            "raw_text": raw_text,
            "category": None,
            "error": str(e)
        }


def _extract_text_with_ocr(file_bytes: bytes, file_extension: str) -> str:
    """Extract text using standard OCR methods."""
    try:
        print(f"Starting text extraction for file type: {file_extension}")
        print(f"File size: {len(file_bytes)} bytes")
        
        # Handle text files directly (no OCR needed)
        file_ext_clean = file_extension.lower().strip()
        print(f"Cleaned file extension: '{file_ext_clean}'")
        
        if file_ext_clean in ['txt', 'text', 'log', 'csv', 'tsv', 'dat']:
            print(f"Processing text file directly (extension: {file_ext_clean})...")
            try:
                # Try UTF-8 first, then fallback to other encodings
                text = file_bytes.decode('utf-8')
                print(f"Successfully decoded text file: {len(text)} characters")
                return text
            except UnicodeDecodeError:
                try:
                    text = file_bytes.decode('latin-1')
                    print(f"Successfully decoded text file with latin-1: {len(text)} characters")
                    return text
                except UnicodeDecodeError:
                    try:
                        text = file_bytes.decode('cp1252')
                        print(f"Successfully decoded text file with cp1252: {len(text)} characters")
                        return text
                    except UnicodeDecodeError:
                        print("Failed to decode text file with common encodings, treating as binary")
                        return str(file_bytes)
        
        elif file_extension.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            # Image OCR
            print("Processing image file...")
            image = Image.open(io.BytesIO(file_bytes))
            print(f"Image size: {image.size}, Mode: {image.mode}")
            
            # Try multiple OCR configurations for better results
            ocr_configs = [
                '--psm 6',  # Uniform block of text
                '--psm 4',  # Single column of text
                '--psm 3',  # Fully automatic page segmentation
                '--psm 1',  # Automatic page segmentation with OSD
            ]
            
            best_text = ""
            for config in ocr_configs:
                try:
                    print(f"Trying OCR with config: {config}")
                    text = pytesseract.image_to_string(image, config=config)
                    if len(text.strip()) > len(best_text.strip()):
                        best_text = text
                        print(f"Better result with {config}: {len(text)} chars")
                except Exception as e:
                    print(f"OCR config {config} failed: {e}")
                    continue
            
            return best_text
            
        elif file_extension.lower() == 'pdf':
            # PDF OCR
            print("Processing PDF file...")
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = ""
            
            print(f"PDF has {len(doc)} pages")
            
            for page_num in range(len(doc)):
                print(f"Processing page {page_num + 1}...")
                page = doc.load_page(page_num)
                
                # Try to extract text directly first
                text = page.get_text()
                if text.strip():
                    print(f"Extracted {len(text)} chars directly from page {page_num + 1}")
                    full_text += text + "\n"
                else:
                    print(f"No direct text on page {page_num + 1}, using OCR...")
                    # If no text, use OCR on page image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Try multiple OCR configs for PDF pages too
                    ocr_configs = ['--psm 6', '--psm 4', '--psm 3']
                    best_ocr_text = ""
                    
                    for config in ocr_configs:
                        try:
                            ocr_text = pytesseract.image_to_string(image, config=config)
                            if len(ocr_text.strip()) > len(best_ocr_text.strip()):
                                best_ocr_text = ocr_text
                        except:
                            continue
                    
                    full_text += best_ocr_text + "\n"
                    print(f"OCR extracted {len(best_ocr_text)} chars from page {page_num + 1}")
            
            doc.close()
            return full_text
            
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
            
    except Exception as e:
        print(f"OCR extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""
