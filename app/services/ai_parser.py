import paddleocr
import fitz  # PyMuPDF
from PIL import Image
import io
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

class PpOcrEngine:
    """
    A singleton class to handle OCR using the PP-OCR model.
    The model is loaded only once for performance.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PpOcrEngine, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Loads the PP-OCR model."""
        logging.info("Initializing PP-OCR Engine: Loading model... (This may take a moment)")
        try:
            # Set use_gpu=False if you do not have a compatible GPU
            self.ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en')
            logging.info("PP-OCR model loaded successfully.")
        except Exception as e:
            logging.error(f"FATAL: Error loading PP-OCR model: {e}")
            self.ocr = None

    def get_text_from_image(self, image_bytes: bytes) -> str:
        """Performs OCR on a single image and returns the joined raw text."""
        if not self.ocr:
            logging.error("OCR model is not available.")
            return ""
        try:
            result = self.ocr.ocr(image_bytes)
            if result and result[0] is not None:
                return '\n'.join([line[1][0] for line in result[0]])
            return ""
        except Exception as e:
            logging.error(f"Error during PP-OCR processing: {e}")
            return ""

# Create a single, global instance of the OCR engine
ai_ocr_engine = PpOcrEngine()

def extract_with_ai(file_bytes: bytes, file_extension: str) -> str:
    """
    Main entry point for AI-based OCR. Handles different file types.
    """
    raw_text = ""
    if file_extension in ['jpg', 'png', 'jpeg']:
        return ai_ocr_engine.get_text_from_image(file_bytes)
            
    elif file_extension == 'pdf':
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                raw_text += ai_ocr_engine.get_text_from_image(img_bytes) + "\n\n"
            doc.close()
            return raw_text
        except Exception as e:
            logging.error(f"Error converting PDF to image for AI OCR: {e}")
            return ""
    
    logging.error(f"Unsupported file type for AI OCR: {file_extension}")
    return ""