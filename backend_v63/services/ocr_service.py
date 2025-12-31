"""
OCR Service - Free Tesseract Implementation
Extract text from placa técnica images (brand, model, serial number)
"""
import re
from typing import Optional, Dict
from PIL import Image
import pytesseract
import cv2
import numpy as np

from schemas import OCRScanResponse


# ============================================================================
# OCR CONFIGURATION
# ============================================================================

# Windows: Set Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# ============================================================================
# IMAGE PREPROCESSING
# ============================================================================

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess image for better OCR accuracy
    - Convert to grayscale
    - Apply thresholding
    - Remove noise
    """
    # Read image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return denoised


# ============================================================================
# TEXT EXTRACTION
# ============================================================================

def extract_text(image_path: str, lang: str = 'spa') -> str:
    """
    Extract text from image using Tesseract OCR
    
    Args:
        image_path: Path to image file
        lang: Language ('spa' for Spanish, 'eng' for English)
    
    Returns:
        Raw text extracted from image
    """
    try:
        # Preprocess image
        processed_img = preprocess_image(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(processed_img, lang=lang)
        
        return text.strip()
    except Exception as e:
        print(f"Error in OCR: {e}")
        # Fallback to direct OCR without preprocessing
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=lang)
            return text.strip()
        except Exception as e2:
            print(f"Error in fallback OCR: {e2}")
            return ""


# ============================================================================
# DATA PARSING
# ============================================================================

def parse_placa_data(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Parse extracted text to find brand, model, and serial number
    
    Common patterns in placa técnica:
    - Brand/Marca: Usually first line or near "MARCA"
    - Model/Modelo: Near "MODELO" or "MODEL"
    - Serial/Serie: Near "SERIAL", "N°SERIE", "S/N"
    """
    result = {
        "brand": None,
        "model": None,
        "serial_number": None
    }
    
    lines = raw_text.split('\n')
    text_lower = raw_text.lower()
    
    # Extract Brand
    brand_patterns = [
        r'marca[:\s]+([a-zA-Z0-9\s]+)',
        r'brand[:\s]+([a-zA-Z0-9\s]+)',
        r'fabricante[:\s]+([a-zA-Z0-9\s]+)',
    ]
    for pattern in brand_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["brand"] = match.group(1).strip().upper()
            break
    
    # If no pattern match, try common brands
    common_brands = ['LG', 'SAMSUNG', 'WHIRLPOOL', 'MABE', 'FENSA', 'ELECTROLUX', 'HAIER', 'MIDEA']
    if not result["brand"]:
        for line in lines:
            for brand in common_brands:
                if brand.lower() in line.lower():
                    result["brand"] = brand
                    break
    
    # Extract Model
    model_patterns = [
        r'modelo[:\s]+([a-zA-Z0-9\-]+)',
        r'model[:\s]+([a-zA-Z0-9\-]+)',
        r'mod[\.:\s]+([a-zA-Z0-9\-]+)',
    ]
    for pattern in model_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["model"] = match.group(1).strip().upper()
            break
    
    # Extract Serial Number
    serial_patterns = [
        r'serial[:\s#]+([a-zA-Z0-9\-]+)',
        r'serie[:\s#]+([a-zA-Z0-9\-]+)',
        r's[/\\]n[:\s]+([a-zA-Z0-9\-]+)',
        r'n[°º\s]+serie[:\s]+([a-zA-Z0-9\-]+)',
    ]
    for pattern in serial_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["serial_number"] = match.group(1).strip().upper()
            break
    
    return result


# ============================================================================
# MAIN OCR FUNCTION
# ============================================================================

async def scan_placa_tecnica(image_path: str) -> OCRScanResponse:
    """
    Main function to scan placa técnica and extract structured data
    
    Args:
        image_path: Path to uploaded image file
    
    Returns:
        OCRScanResponse with extracted data
    """
    # Extract raw text
    raw_text = extract_text(image_path, lang='spa')
    
    # Parse structured data
    parsed_data = parse_placa_data(raw_text)
    
    # Calculate confidence based on how many fields we extracted
    fields_found = sum(1 for v in parsed_data.values() if v is not None)
    confidence = fields_found / 3.0  # 3 fields total
    
    return OCRScanResponse(
        brand=parsed_data["brand"],
        model=parsed_data["model"],
        serial_number=parsed_data["serial_number"],
        raw_text=raw_text,
        confidence=confidence
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_tesseract_installed() -> bool:
    """Check if Tesseract is installed and accessible"""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
