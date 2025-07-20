from pydantic import BaseModel, Field, field_validator, ValidationError
from datetime import date, datetime
from typing import Optional

class ReceiptData(BaseModel):
    """
    Needed:
    Vendor/Biller
    Date
    Amount
    Category (Optional)
    """
    vendor: str = Field(..., description="Name of the vendor or biller")
    transaction_date: date = Field(..., description="Date of the transaction or start of the billing cycle")
    amount: float = Field(gt=0, description="Total value of the transaction")
    category: Optional[str] = Field(None, description="Optional categories")
    raw_text: str = Field(..., description="Raw Extracted text")
    raw_data: bytes = Field(..., description="Raw Data of uploaded file")
    raw_data_extension: str = Field(..., description="Extension of the file uploaded")
    upload_timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp when the receipt was updated")

    @field_validator('raw_data_extension')
    @classmethod
    def has_valid_extentions(cls, v: str)->str:
        """
        Must have valid extensions
        """
        allowed_extensions = ('jpg', 'png', 'pdf', 'txt')
        if not v.lower() in allowed_extensions:
            raise ValueError(f"{v} is not valid. Valid extensions include: {", ".join(allowed_extensions)}")
        
        return v
    
    @field_validator('vendor')
    @classmethod
    def vender_must_not_be_a_number(cls, v:str)->str:
        """
        Vendors cannot be just a number
        """
        if v.isdigit():
            raise ValueError("Vendor cannot be just numbers")
        return v



print("--- Testing ReceiptData Model ---")

# Test Case 1: Valid Data
print("\n--- Test Case 1: Valid Data ---")
try:
    valid_receipt = ReceiptData(
        vendor="Grocery Store ABC",
        transaction_date="2024-07-19",
        amount=55.75,
        category="Groceries",
        raw_text="Total: 55.75",
        raw_data=b"some_image_bytes",
        raw_data_extension="jpg"
    )
    print("Valid Receipt created successfully:")
    print(valid_receipt.model_dump_json(indent=2))
except ValidationError as e:
    print("Validation Error (should not happen for valid data):")
    print(e)

# Test Case 2: Invalid raw_data_extension
print("\n--- Test Case 2: Invalid raw_data_extension ---")
try:
    invalid_extension_receipt = ReceiptData(
        vendor="Book Shop",
        transaction_date="2024-07-18",
        amount=25.00,
        raw_text="Book purchase",
        raw_data=b"some_pdf_bytes",
        raw_data_extension="doc" # Invalid extension
    )
except ValidationError as e:
    print("Validation Error caught as expected:")
    print(e)
    # Expected output will show error for 'raw_data_extension'

# Test Case 3: Vendor is all numbers
print("\n--- Test Case 3: Vendor is all numbers ---")
try:
    numeric_vendor_receipt = ReceiptData(
        vendor="12345", # Vendor is all numbers
        transaction_date="2024-07-17",
        amount=10.50,
        raw_text="Utility bill",
        raw_data=b"some_txt_bytes",
        raw_data_extension="txt"
    )
except ValidationError as e:
    print("Validation Error caught as expected:")
    print(e)
    # Expected output will show error for 'vendor'

# Test Case 4: Amount is not greater than 0
print("\n--- Test Case 4: Amount is not greater than 0 ---")
try:
    zero_amount_receipt = ReceiptData(
        vendor="Cafe",
        transaction_date="2024-07-16",
        amount=0.0, # Amount is 0, violates gt=0
        raw_text="Coffee",
        raw_data=b"some_png_bytes",
        raw_data_extension="png"
    )
except ValidationError as e:
    print("Validation Error caught as expected:")
    print(e)
    # Expected output will show error for 'amount'

# Test Case 5: Missing required field (e.g., raw_text)
print("\n--- Test Case 5: Missing required field (raw_text) ---")
try:
    missing_field_receipt = ReceiptData(
        vendor="Online Store",
        transaction_date="2024-07-15",
        amount=120.00,
        # raw_text is missing
        raw_data=b"some_data",
        raw_data_extension="pdf"
    )
except ValidationError as e:
    print("Validation Error caught as expected:")
    print(e)
    # Expected output will show error for 'raw_text'