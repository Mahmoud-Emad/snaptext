import pytesseract
from PIL import Image

def extract_text(image_path: str) -> str:
    """Extract text from an image file using pytesseract."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text.strip()
