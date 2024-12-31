import pytesseract
from PIL import Image
from app.core.logging import logger

def process_image(image: Image) -> str:
    """
    Process a single image with OCR to extract text.
    
    Args:
        image: PIL Image object
        
    Returns:
        str: Extracted text from the image
    """
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"Error processing image with OCR: {str(e)}")
        return "" 