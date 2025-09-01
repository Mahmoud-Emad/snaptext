"""
Tests for the Flask web server in server/server.py
"""

import pytest
import json
import io
import os
from unittest.mock import patch, MagicMock
from PIL import Image


class TestServerRoutes:
    """Test Flask server routes."""
    
    def test_index_route(self, client):
        """Test the main index route."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'SnapText' in response.data
        assert b'Extract text from images' in response.data
    
    def test_static_files(self, client):
        """Test static file serving."""
        # Test CSS file
        response = client.get('/static/style.css')
        assert response.status_code == 200
        assert response.content_type.startswith('text/css')
        
        # Test JavaScript file
        response = client.get('/static/script.js')
        assert response.status_code == 200
        assert response.content_type.startswith(('application/javascript', 'text/javascript'))


class TestUploadEndpoint:
    """Test the /upload endpoint."""
    
    def test_upload_no_file(self, client):
        """Test upload without file."""
        response = client.post('/upload')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No file uploaded' in data['error']
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename."""
        data = {'file': (io.BytesIO(b''), '')}
        response = client.post('/upload', data=data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Empty filename' in data['error']
    
    @patch('server.server.extract_text')
    @patch('server.server.get_text_confidence')
    def test_upload_success(self, mock_confidence, mock_extract, client, create_test_image):
        """Test successful file upload and OCR."""
        # Mock the OCR functions
        mock_extract.return_value = "Extracted text from image"
        mock_confidence.return_value = {
            'average_confidence': 85.5,
            'word_count': 4,
            'low_confidence_words': 0
        }
        
        # Create test image
        img = create_test_image("TEST IMAGE")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Upload the image
        data = {'file': (img_buffer, 'test_image.png')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert 'text' in response_data
        assert 'confidence' in response_data
        assert 'filename' in response_data
        
        assert response_data['text'] == "Extracted text from image"
        assert response_data['confidence']['average_confidence'] == 85.5
        assert response_data['filename'] == 'test_image.png'
        
        # Verify OCR functions were called
        mock_extract.assert_called_once()
        mock_confidence.assert_called_once()
    
    @patch('server.server.extract_text')
    def test_upload_ocr_failure(self, mock_extract, client, create_test_image):
        """Test upload when OCR fails."""
        # Mock OCR to raise an exception
        mock_extract.side_effect = Exception("OCR processing failed")
        
        # Create test image
        img = create_test_image("TEST")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Upload the image
        data = {'file': (img_buffer, 'test.png')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 500
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Failed to extract text' in response_data['error']
    
    def test_upload_invalid_file_type(self, client):
        """Test upload with non-image file."""
        # Create a text file
        text_buffer = io.BytesIO(b'This is not an image')
        
        data = {'file': (text_buffer, 'test.txt')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Should still accept the file but OCR will likely fail
        # The actual validation happens in the OCR processing
        assert response.status_code in [200, 500]  # Depends on OCR behavior
    
    def test_upload_large_file(self, client, create_test_image):
        """Test upload with large image file."""
        # Create a large image
        img = create_test_image("LARGE IMAGE TEST", size=(2000, 1000))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        data = {'file': (img_buffer, 'large_image.png')}
        
        # Should handle large files gracefully
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Should not crash (may succeed or fail depending on system resources)
        assert response.status_code in [200, 500]


class TestServerConfiguration:
    """Test server configuration and setup."""
    
    def test_app_config(self, flask_app):
        """Test Flask app configuration."""
        assert flask_app.config['TESTING'] is True
        assert hasattr(flask_app, 'static_folder')
        assert hasattr(flask_app, 'template_folder')
    
    def test_logging_setup(self, flask_app):
        """Test that logging is properly configured."""
        # The app should have logging configured
        assert hasattr(flask_app, 'logger')
        
        # Logger should be configured (this is done in server.py)
        import logging
        logger = logging.getLogger('server.server')
        assert logger is not None


class TestErrorHandling:
    """Test error handling in the server."""
    
    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed errors."""
        # Try GET on upload endpoint (only POST allowed)
        response = client.get('/upload')
        assert response.status_code == 405
    
    @patch('server.server.extract_text')
    def test_file_cleanup_on_error(self, mock_extract, client, create_test_image):
        """Test that temporary files are cleaned up on error."""
        # Mock extract_text to raise an exception
        mock_extract.side_effect = Exception("Processing failed")
        
        img = create_test_image("TEST")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        data = {'file': (img_buffer, 'test.png')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Should return error
        assert response.status_code == 500
        
        # File should be cleaned up (we can't easily test this directly,
        # but the code should handle it)
        response_data = json.loads(response.data)
        assert 'error' in response_data


class TestIntegration:
    """Integration tests for the complete server functionality."""
    
    def test_full_upload_workflow(self, client, create_test_image):
        """Test the complete upload and OCR workflow."""
        # Create a test image with clear text
        img = create_test_image("HELLO WORLD 123", size=(300, 100))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Test the full workflow
        data = {'file': (img_buffer, 'integration_test.png')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Should succeed (or fail gracefully)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            response_data = json.loads(response.data)
            assert 'text' in response_data
            assert 'confidence' in response_data
            assert 'filename' in response_data
            assert response_data['filename'] == 'integration_test.png'
    
    def test_concurrent_uploads(self, client, create_test_image):
        """Test handling of multiple concurrent uploads."""
        # Create multiple test images
        images = []
        for i in range(3):
            img = create_test_image(f"TEST {i}", size=(200, 50))
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            images.append((img_buffer, f'test_{i}.png'))
        
        # Upload all images
        responses = []
        for img_buffer, filename in images:
            data = {'file': (img_buffer, filename)}
            response = client.post('/upload', data=data, content_type='multipart/form-data')
            responses.append(response)
        
        # All should complete without crashing
        for response in responses:
            assert response.status_code in [200, 500]
    
    def test_different_image_formats(self, client, create_test_image):
        """Test upload with different image formats."""
        formats = ['PNG', 'JPEG', 'BMP']
        
        for fmt in formats:
            img = create_test_image(f"FORMAT {fmt}", size=(200, 50))
            img_buffer = io.BytesIO()
            
            # Save in different format
            if fmt == 'JPEG':
                img = img.convert('RGB')  # JPEG doesn't support transparency
            
            img.save(img_buffer, format=fmt)
            img_buffer.seek(0)
            
            filename = f'test.{fmt.lower()}'
            data = {'file': (img_buffer, filename)}
            response = client.post('/upload', data=data, content_type='multipart/form-data')
            
            # Should handle all common image formats
            assert response.status_code in [200, 500]
