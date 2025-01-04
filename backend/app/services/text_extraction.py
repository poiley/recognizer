import fitz  # PyMuPDF
from app.core.logging import logger

def process_pdf_page(page) -> str:
    """
    Process a single PDF page with PyMuPDF to extract text.
    
    Args:
        page: fitz.Page object
        
    Returns:
        str: Extracted text from the page
    """
    try:
        text = page.get_text()
        return text.strip()
    except Exception as e:
        logger.error(f"Error processing page with PyMuPDF: {str(e)}")
        return "" 