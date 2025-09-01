"""
Tests for core OCR functionality in core/tool.py
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np

from core.tool import (
    extract_text,
    get_text_confidence,
    preprocess_image,
    enhance_image_pil,
)


class TestExtractText:
    """Test the main extract_text function."""

    def test_extract_text_with_real_image(self, sample_images):
        """Test OCR with real sample images."""
        if not sample_images:
            pytest.skip("No sample images found in dataset")

        # Test with the first available image
        image_path = list(sample_images.values())[0]

        # Should not raise an exception
        result = extract_text(image_path)

        # Result should be a string
        assert isinstance(result, str)

        # Should not be None
        assert result is not None

    def test_extract_text_with_created_image(self, create_test_image, temp_dir):
        """Test OCR with a programmatically created image."""
        test_text = "HELLO WORLD"
        img = create_test_image(test_text, size=(300, 100))

        # Save to temporary file
        img_path = os.path.join(temp_dir, "test_image.png")
        img.save(img_path)

        # Extract text
        result = extract_text(img_path)

        # Should contain some of the original text (OCR might not be perfect)
        assert isinstance(result, str)
        # At least some characters should be recognized
        assert len(result.strip()) > 0

    def test_extract_text_nonexistent_file(self):
        """Test extract_text with non-existent file."""
        with pytest.raises(Exception):
            extract_text("/nonexistent/path/image.png")

    def test_extract_text_invalid_file(self, temp_dir):
        """Test extract_text with invalid image file."""
        # Create a text file instead of image
        invalid_path = os.path.join(temp_dir, "not_an_image.txt")
        with open(invalid_path, "w") as f:
            f.write("This is not an image")

        with pytest.raises(Exception):
            extract_text(invalid_path)

    @patch("core.tool.pytesseract.image_to_string")
    def test_extract_text_multiple_methods(
        self, mock_tesseract, create_test_image, temp_dir
    ):
        """Test that multiple OCR methods are tried."""
        # Mock different responses for different calls
        mock_tesseract.side_effect = [
            "Method 1 result",  # Enhanced PIL
            "Method 2 longer result",  # OpenCV (should be selected as best)
            "Method 3",  # Scaled
            "Method 4",  # PSM 8
        ]

        img = create_test_image("TEST")
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        result = extract_text(img_path)

        # Should return the longest result (Method 2)
        assert result == "Method 2 longer result"

        # Should have called tesseract multiple times
        assert mock_tesseract.call_count >= 2


class TestGetTextConfidence:
    """Test the get_text_confidence function."""

    def test_get_confidence_with_real_image(self, sample_images):
        """Test confidence scoring with real images."""
        if not sample_images:
            pytest.skip("No sample images found in dataset")

        image_path = list(sample_images.values())[0]
        result = get_text_confidence(image_path)

        # Should return a dictionary
        assert isinstance(result, dict)

        # Should not have error if image is valid
        if "error" not in result:
            assert "average_confidence" in result
            assert "word_count" in result
            assert isinstance(result["average_confidence"], (int, float))
            assert isinstance(result["word_count"], int)

    def test_get_confidence_invalid_file(self):
        """Test confidence with invalid file."""
        result = get_text_confidence("/nonexistent/file.png")

        # Should return error information
        assert isinstance(result, dict)
        assert "error" in result

    @patch("core.tool.pytesseract.image_to_data")
    def test_get_confidence_mock_data(
        self, mock_tesseract_data, create_test_image, temp_dir
    ):
        """Test confidence calculation with mocked tesseract data."""
        # Mock tesseract data response
        mock_tesseract_data.return_value = {
            "conf": ["95", "87", "92", "78", "0", "88"],
            "text": ["Hello", "World", "Test", "Text", "", "OCR"],
        }

        img = create_test_image("Hello World")
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        result = get_text_confidence(img_path)

        # Should calculate average confidence correctly
        # (95 + 87 + 92 + 78 + 88) / 5 = 88
        assert result["average_confidence"] == 88.0
        assert result["word_count"] == 5  # Non-empty text entries
        assert result["low_confidence_words"] == 1  # Only 78 is < 80


class TestImagePreprocessing:
    """Test image preprocessing functions."""

    def test_preprocess_image_basic(self, create_test_image):
        """Test basic image preprocessing."""
        img = create_test_image("TEST", size=(100, 50))

        processed = preprocess_image(img)

        # Should return a PIL Image
        assert isinstance(processed, Image.Image)

        # Should be grayscale
        assert processed.mode in ["L", "1"]  # Grayscale or binary

    def test_preprocess_image_grayscale_input(self, create_test_image):
        """Test preprocessing with grayscale input."""
        img = create_test_image("TEST").convert("L")

        processed = preprocess_image(img)

        assert isinstance(processed, Image.Image)
        assert processed.mode in ["L", "1"]

    def test_enhance_image_pil(self, create_test_image):
        """Test PIL image enhancement."""
        img = create_test_image("TEST", size=(100, 50))

        enhanced = enhance_image_pil(img)

        # Should return a PIL Image
        assert isinstance(enhanced, Image.Image)

        # Should be grayscale
        assert enhanced.mode == "L"

        # Should have same size
        assert enhanced.size == img.size

    def test_enhance_image_already_grayscale(self, create_test_image):
        """Test enhancement with already grayscale image."""
        img = create_test_image("TEST").convert("L")

        enhanced = enhance_image_pil(img)

        assert isinstance(enhanced, Image.Image)
        assert enhanced.mode == "L"


class TestErrorHandling:
    """Test error handling in OCR functions."""

    @patch("core.tool.pytesseract.image_to_string")
    def test_extract_text_all_methods_fail(
        self, mock_tesseract, create_test_image, temp_dir
    ):
        """Test when all OCR methods fail."""
        # Make all tesseract calls raise exceptions
        mock_tesseract.side_effect = Exception("Tesseract failed")

        img = create_test_image("TEST")
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        with pytest.raises(Exception, match="Failed to extract text"):
            extract_text(img_path)

    @patch("core.tool.pytesseract.image_to_string")
    def test_extract_text_partial_failure(
        self, mock_tesseract, create_test_image, temp_dir
    ):
        """Test when some OCR methods fail but others succeed."""
        # Make some calls fail, others succeed
        mock_tesseract.side_effect = [
            Exception("Method 1 failed"),
            "Success from method 2",
            Exception("Method 3 failed"),
            "Success from method 4",
        ]

        img = create_test_image("TEST")
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        result = extract_text(img_path)

        # Should return one of the successful results
        assert result in ["Success from method 2", "Success from method 4"]


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_ocr_pipeline(self, create_test_image, temp_dir):
        """Test the complete OCR pipeline."""
        test_text = "INTEGRATION TEST 123"
        img = create_test_image(test_text, size=(400, 100))
        img_path = os.path.join(temp_dir, "integration_test.png")
        img.save(img_path)

        # Extract text
        extracted_text = extract_text(img_path)

        # Get confidence
        confidence = get_text_confidence(img_path)

        # Verify results
        assert isinstance(extracted_text, str)
        assert isinstance(confidence, dict)

        if "error" not in confidence:
            assert "average_confidence" in confidence
            assert confidence["average_confidence"] >= 0
            assert confidence["average_confidence"] <= 100

    def test_empty_image_handling(self, temp_dir):
        """Test handling of empty/blank images."""
        # Create a blank white image
        img = Image.new("RGB", (200, 100), "white")
        img_path = os.path.join(temp_dir, "blank.png")
        img.save(img_path)

        # Should not crash
        result = extract_text(img_path)
        confidence = get_text_confidence(img_path)

        # Results should be valid even if empty
        assert isinstance(result, str)
        assert isinstance(confidence, dict)
