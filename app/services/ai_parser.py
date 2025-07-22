import torch
from PIL import Image
import io
import logging
from typing import Optional, Dict, Any, List
import gc
import json
from dataclasses import dataclass
import time

# --- Dependency Checks ---
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF (fitz) not installed. PDF processing will be disabled.")

try:
    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
    QWEN2VL_AVAILABLE = True
except ImportError:
    QWEN2VL_AVAILABLE = False
    logging.warning("Hugging Face transformers not installed. Qwen2-VL functionality will be disabled.")

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Data Structures (Structure Preserved) ---
@dataclass
class OCRResult:
    """Standardized OCR result with quality metrics"""
    text: str
    confidence_score: float
    engine_name: str
    processing_time: float
    character_count: int
    line_count: int
    has_amounts: bool
    has_dates: bool
    has_vendor_info: bool
    quality_score: float
    structured_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# --- Main Engine Class (Structure Preserved, Internals Fixed) ---
class Qwen2VLEngine:
    """
    Qwen2-VL vision-language engine optimized for RTX 4050 (6GB VRAM).
    Provides intelligent receipt parsing with structured JSON output.
    (This version has been corrected to use the standard Hugging Face workflow).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Qwen2VLEngine, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Initialize Qwen2-VL model with GPU optimization for RTX 4050."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        self._model_loaded = False
        
        self.receipt_prompt = """You are an AI assistant specialized in reading and parsing receipt images. Your task is to extract key information and return it in a specific JSON format.
Analyze the provided receipt image and extract the following information, with the JSON fields sorted in this exact order: date, category, vendor, amount, currency.
Guidelines: Your main goal is to fill in all fields. It is acceptable if a value is a best-guess and not 100% accurate, as a human will review it. If a field is completely missing or impossible to read, use null.
Return only the JSON object. Do not include any introductory text, explanations, or markdown code fences.
Example: {"date": "2025-07-22", "category": "grocery", "vendor": "City Market", "amount": 42.15, "currency": "USD"}
Now, analyze the attached receipt image and provide the response."""

        logging.info(f"Qwen2-VL Engine ready on {self.device}")
        if torch.cuda.is_available():
            logging.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logging.info("Qwen2-VL model will be loaded on first use (lazy loading).")

    def _ensure_model_loaded(self):
        """Load Qwen2-VL model only when first needed (lazy loading)."""
        if self._model_loaded:
            return True
        if not QWEN2VL_AVAILABLE:
            logging.error("Qwen2-VL not available - please install the 'transformers' library.")
            return False

        try:
            logging.info("Loading Qwen/Qwen2-VL-2B-Instruct model...")
            model_name = "Qwen/Qwen2-VL-2B-Instruct"
            
            # The AutoProcessor correctly handles all preprocessing.
            self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto", # Automatically handles moving the model to GPU
                trust_remote_code=True
            )
            
            self._model_loaded = True
            logging.info("✓ Qwen2-VL model loaded successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to load Qwen2-VL model: {e}", exc_info=True)
            return False

    def extract_receipt_data(self, image_bytes: bytes) -> OCRResult:
        """Extract structured receipt data using the corrected, standard Qwen2-VL workflow."""
        start_time = time.time()
        
        if not self._ensure_model_loaded():
            return OCRResult(
                text="", confidence_score=0.0, engine_name="qwen2vl",
                processing_time=time.time() - start_time, character_count=0,
                line_count=0, has_amounts=False, has_dates=False,
                has_vendor_info=False, quality_score=0.0,
                error_message="Qwen2-VL model not available"
            )
        
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # ** CORRECTED & SIMPLIFIED INPUT PREPARATION **
            # This is the standard Hugging Face method for vision-language models.
            messages = [{"role": "user", "content": [{"type": "text", "text": self.receipt_prompt}, {"type": "image"}]}]
            text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.processor(text, images=[image], return_tensors="pt").to(self.device)

            # Generate response
            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_new_tokens=512)

            # Decode and clean up the response
            generated_ids = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            output_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            logging.info(f"Qwen2-VL raw output: {output_text}")

            # Parse JSON from the model's text response
            structured_data = self._parse_json_response(output_text)
            
            # Populate the OCRResult dataclass as intended
            processing_time = time.time() - start_time
            character_count = len(output_text)
            line_count = len(output_text.split('\n'))
            has_amounts = self._has_amounts(structured_data, output_text)
            has_dates = self._has_dates(structured_data, output_text)
            has_vendor_info = self._has_vendor_info(structured_data, output_text)
            quality_score = self._calculate_quality_score(structured_data, has_amounts, has_dates, has_vendor_info)
            
            return OCRResult(
                text=output_text,
                confidence_score=0.9 if structured_data else 0.5,
                engine_name="qwen2vl",
                processing_time=processing_time,
                character_count=character_count,
                line_count=line_count,
                has_amounts=has_amounts,
                has_dates=has_dates,
                has_vendor_info=has_vendor_info,
                quality_score=quality_score,
                structured_data=structured_data
            )
            
        except Exception as e:
            logging.error(f"Error in Qwen2-VL processing: {e}", exc_info=True)
            return OCRResult(
                text="", confidence_score=0.0, engine_name="qwen2vl",
                processing_time=time.time() - start_time, character_count=0,
                line_count=0, has_amounts=False, has_dates=False,
                has_vendor_info=False, quality_score=0.0, error_message=str(e)
            )
        finally:
            # Clean up GPU memory
            if torch.cuda.is_available():
                gc.collect()
                torch.cuda.empty_cache()

    # --- Helper and Public Interface Methods (Structure Preserved) ---
    
    def get_text_from_image(self, image_bytes: bytes) -> str:
        """Legacy method for backward compatibility."""
        result = self.extract_receipt_data(image_bytes)
        return result.text

    def get_structured_data(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Get structured receipt data (vendor, category, date, amount, currency)."""
        result = self.extract_receipt_data(image_bytes)
        return result.structured_data

    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Safely finds and parses a JSON object from a string."""
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            logging.warning(f"Could not parse JSON from response: {response_text}")
        return None

    def _has_amounts(self, structured_data: Optional[Dict], raw_text: str) -> bool:
        return bool(structured_data and structured_data.get('amount'))

    def _has_dates(self, structured_data: Optional[Dict], raw_text: str) -> bool:
        return bool(structured_data and structured_data.get('date'))

    def _has_vendor_info(self, structured_data: Optional[Dict], raw_text: str) -> bool:
        return bool(structured_data and structured_data.get('vendor'))

    def _calculate_quality_score(self, structured_data: Optional[Dict], has_amounts: bool, has_dates: bool, has_vendor_info: bool) -> float:
        """Calculate overall quality score for the OCR result."""
        if not structured_data:
            return 0.1
        score = 0.4
        if has_vendor_info: score += 0.2
        if has_amounts: score += 0.2
        if has_dates: score += 0.1
        if 'category' in structured_data: score += 0.05
        if 'currency' in structured_data: score += 0.05
        return min(score, 1.0)

# --- Top-level API Functions (Structure Preserved) ---

def extract_structured_receipt_data(file_bytes: bytes, file_extension: str) -> Optional[Dict[str, Any]]:
    """Extracts structured receipt data from an image file."""
    engine = Qwen2VLEngine()
    if file_extension.lower() in ['jpg', 'png', 'jpeg', 'bmp', 'tiff']:
        result = engine.extract_receipt_data(file_bytes)
        return result.structured_data
    else:
        logging.error(f"Structured receipt extraction only supports image files, got: {file_extension}")
        return None


