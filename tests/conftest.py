"""
Pytest configuration and shared fixtures for SnapText tests.
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont


@pytest.fixture
def test_data_dir():
    """Return the path to the test dataset directory."""
    return Path(__file__).parent / "dataset"


@pytest.fixture
def sample_images(test_data_dir):
    """Return paths to sample test images."""
    images = {}
    # Check for common image extensions
    extensions = [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.gif",
        "*.bmp",
        "*.JPG",
        "*.JPEG",
        "*.PNG",
    ]
    for pattern in extensions:
        for img_file in test_data_dir.glob(pattern):
            images[img_file.stem] = str(img_file)
    return images


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def create_test_image():
    """Factory fixture to create test images with specific text."""

    def _create_image(
        text="Test Text", size=(200, 100), bg_color="white", text_color="black"
    ):
        """Create a simple test image with text."""
        img = Image.new("RGB", size, bg_color)
        draw = ImageDraw.Draw(img)

        # Try to use a default font, fallback to basic if not available
        try:
            # Try to load a better font
            font = ImageFont.truetype("Arial.ttf", 20)
        except (OSError, IOError):
            try:
                font = ImageFont.load_default()
            except (OSError, IOError):
                font = None

        # Calculate text position (center)
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            # Rough estimation if no font available
            text_width = len(text) * 10
            text_height = 15

        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2

        draw.text((x, y), text, fill=text_color, font=font)
        return img

    return _create_image


@pytest.fixture
def mock_tesseract_response():
    """Mock tesseract response for testing."""
    return "Sample extracted text from image"


@pytest.fixture
def flask_app():
    """Create a Flask app instance for testing."""
    from server.server import app

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask app."""
    return flask_app.test_client()


@pytest.fixture
def runner(flask_app):
    """Create a test runner for the Flask app."""
    return flask_app.test_cli_runner()


# Test data constants
EXPECTED_TEXT_SAMPLES = {
    "simple": "Hello World",
    "multiline": "Line 1\nLine 2\nLine 3",
    "numbers": "123 456 789",
    "mixed": "Text with 123 numbers and symbols!@#",
    "empty": "",
}

CONFIDENCE_THRESHOLDS = {
    "high": 80,
    "medium": 60,
    "low": 40,
}
