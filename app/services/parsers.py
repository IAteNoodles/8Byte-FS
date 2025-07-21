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
#from ai_parser import extract_with_ai 
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


def extract_with_ai(blah):
    pass
#------------------VENDORS-------------------

def find_vendor(text: str, score_cutoff: int = 85) -> tuple[str | None, str | None]:
    """Finds a vendor using fuzzy matching against a known list."""
    text_lower = text.lower()
    best_match_score, best_match_vendor, best_match_category = 0, None, None
    for category, vendors in KNOWN_VENDORS.items():
        for keyword, name in vendors.items():
            score = fuzz.partial_ratio(keyword, text_lower)
            if score > best_match_score:
                best_match_score, best_match_vendor, best_match_category = score, name, category
    if best_match_score >= score_cutoff:
        return best_match_vendor, best_match_category
    if 'electricity' in text_lower:
        return 'Electricity Provider', 'Electricity'
    return None, None

def find_date(text: str) -> str | None:
    """Finds all possible dates in the text and returns the earliest one."""
    date_pattern = r'(\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})'
    matches = re.findall(date_pattern, text)
    if not matches:
        return None
    parsed_dates = []
    for date_str in matches:
        try:
            parsed_dates.append(datetime.strptime(date_str.replace('/', '-'), '%d-%m-%Y'))
        except ValueError:
            try:
                parsed_dates.append(datetime.strptime(date_str.replace('/', '-'), '%Y-%m-%d'))
            except ValueError:
                continue
    if parsed_dates:
        return min(parsed_dates).strftime('%Y-%m-%d')
    return None

def find_amount(text: str) -> float | None:
    """Finds the final total amount using a "bottom-up" search with a dynamic confidence score."""
    amount_keywords = [
        "amount to be paid", "net amt due", "total amount due", "net amount payable", "bill amount",
        "invoice amount", "final amount", "net amount", "grand total", "total", "amt", "due", "payable"
    ]
    currency_pattern = r'(¥|₹|Rs\.?|INR|\$|USD|€|EUR|£|GBP)'
    number_pattern = r'([\d,]+(?:\.\d{1,2})?)'
    min_cutoff, max_cutoff = 70, 95
    lines = text.split('\n')
    for i, line in enumerate(reversed(lines)):
        if not line.strip():
            continue
        if re.search(currency_pattern, line, re.IGNORECASE) and re.search(number_pattern, line):
            current_cutoff = min(max_cutoff, min_cutoff + i)
            line_lower = line.lower()
            keyword_score = max(fuzz.token_set_ratio(keyword, line_lower) for keyword in amount_keywords)
            if keyword_score >= current_cutoff:
                amount_match = re.search(number_pattern, line)
                if amount_match:
                    try:
                        amount_str = amount_match.group(1).replace(',', '').replace(' ', '')
                        return float(amount_str)
                    except (ValueError, AttributeError):
                        continue
    return None

def parse_and_extract_data(file_bytes: bytes, file_extension: str) -> dict:
    """Extracts text and parses it using a primary fuzzy logic method with an AI fallback."""
    raw_text = ""
    if file_extension in ['jpg', 'png']:
        try:
            raw_text = pytesseract.image_to_string(Image.open(io.BytesIO(file_bytes)))
        except Exception as e:
            print(f"Error processing image with Tesseract: {e}")
    elif file_extension == 'pdf':
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text = page.get_text()
                    if not text.strip():
                        pix = page.get_pixmap()
                        img_bytes = pix.tobytes("png")
                        raw_text += pytesseract.image_to_string(Image.open(io.BytesIO(img_bytes))) + "\n"
                    else:
                        raw_text += text + "\n"
        except Exception as e:
            print(f"Error processing PDF file: {e}")
    elif file_extension == 'txt':
        raw_text = file_bytes.decode('utf-8', errors='ignore')

    vendor, category = find_vendor(raw_text)
    transaction_date = find_date(raw_text)
    amount = find_amount(raw_text)

    print(raw_text)

    print("-----------Extracted")

    print(vendor, transaction_date, amount)

    if not all([vendor, transaction_date, amount]):
        print("Primary method failed. Triggering AI fallback...")
        ai_data = extract_with_ai(raw_text)
        if ai_data:
            return {
                "vendor": ai_data.get("vendor"), "transaction_date": ai_data.get("transaction_date"),
                "amount": ai_data.get("amount"), "raw_text": raw_text, "category": category 
            }

    return {
        "vendor": vendor, "transaction_date": transaction_date,
        "amount": amount, "raw_text": raw_text, "category": category 
    }