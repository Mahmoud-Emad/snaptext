import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy.
    """
    # Convert PIL image to numpy array for OpenCV processing
    img_array = np.array(image)

    # Convert to grayscale if not already
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array

    # Apply noise reduction
    denoised = cv2.medianBlur(gray, 3)

    # Apply adaptive thresholding to handle varying lighting conditions
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Apply morphological operations to clean up the image
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

    # Convert back to PIL Image
    return Image.fromarray(cleaned)

def enhance_image_pil(image):
    """
    Enhance image using PIL operations.
    """
    # Convert to grayscale
    if image.mode != 'L':
        image = image.convert('L')

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)

    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)

    # Apply unsharp mask filter
    image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

    return image

def extract_text(image_path: str) -> str:
    """
    Extract text from an image file using enhanced OCR techniques.
    """
    try:
        logger.info(f"Starting OCR processing for: {image_path}")

        # Open and prepare the image
        original_img = Image.open(image_path)
        logger.info(f"Image loaded: {original_img.size}, mode: {original_img.mode}")

        # Try multiple OCR approaches and combine results
        results = []

        # Method 1: Original image with basic enhancement
        try:
            enhanced_img = enhance_image_pil(original_img.copy())
            text1 = pytesseract.image_to_string(
                enhanced_img,
                config='--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?@#$%^&*()_+-=[]{}|;:,.<>?'
            ).strip()
            if text1:
                results.append(("Enhanced PIL", text1))
                logger.info(f"Method 1 (Enhanced PIL) extracted {len(text1)} characters")
        except Exception as e:
            logger.warning(f"Method 1 failed: {e}")

        # Method 2: OpenCV preprocessing
        try:
            preprocessed_img = preprocess_image(original_img.copy())
            text2 = pytesseract.image_to_string(
                preprocessed_img,
                config='--oem 3 --psm 6'
            ).strip()
            if text2:
                results.append(("OpenCV Preprocessed", text2))
                logger.info(f"Method 2 (OpenCV) extracted {len(text2)} characters")
        except Exception as e:
            logger.warning(f"Method 2 failed: {e}")

        # Method 3: High DPI scaling
        try:
            # Scale up the image for better OCR
            scale_factor = 2
            width, height = original_img.size
            scaled_img = original_img.resize((width * scale_factor, height * scale_factor), Image.LANCZOS)
            scaled_img = enhance_image_pil(scaled_img)

            text3 = pytesseract.image_to_string(
                scaled_img,
                config='--oem 3 --psm 6 --dpi 300'
            ).strip()
            if text3:
                results.append(("Scaled", text3))
                logger.info(f"Method 3 (Scaled) extracted {len(text3)} characters")
        except Exception as e:
            logger.warning(f"Method 3 failed: {e}")

        # Method 4: Try different PSM modes for difficult images
        try:
            text4 = pytesseract.image_to_string(
                enhance_image_pil(original_img.copy()),
                config='--oem 3 --psm 8'  # Single word mode
            ).strip()
            if text4:
                results.append(("PSM 8", text4))
                logger.info(f"Method 4 (PSM 8) extracted {len(text4)} characters")
        except Exception as e:
            logger.warning(f"Method 4 failed: {e}")

        # Choose the best result (longest meaningful text)
        if not results:
            logger.warning("No text extracted by any method")
            return ""

        # Select the result with the most characters (usually more accurate)
        best_result = max(results, key=lambda x: len(x[1]))
        best_method, best_text = best_result

        logger.info(f"Best result from {best_method}: {len(best_text)} characters")
        logger.info(f"All results: {[(method, len(text)) for method, text in results]}")

        return best_text

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise Exception(f"Failed to extract text: {str(e)}")

def get_text_confidence(image_path: str) -> dict:
    """
    Get OCR confidence scores for debugging.
    """
    try:
        img = Image.open(image_path)
        enhanced_img = enhance_image_pil(img)

        # Get detailed OCR data with confidence scores
        data = pytesseract.image_to_data(enhanced_img, output_type=pytesseract.Output.DICT)

        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            'average_confidence': avg_confidence,
            'word_count': len([word for word in data['text'] if word.strip()]),
            'low_confidence_words': len([conf for conf in confidences if conf < 60])
        }
    except Exception as e:
        logger.error(f"Failed to get confidence scores: {e}")
        return {'error': str(e)}
