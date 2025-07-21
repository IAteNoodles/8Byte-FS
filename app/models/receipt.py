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
    currency: str = Field(default="INR", description="ISO 4217 currency code (e.g., INR, USD)")

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
