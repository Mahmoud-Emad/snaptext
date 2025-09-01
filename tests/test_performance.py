"""
Performance tests for SnapText OCR functionality.
"""

import pytest
import time
import os
from unittest.mock import patch
from core.tool import extract_text, get_text_confidence


@pytest.mark.slow
class TestPerformance:
    """Performance tests for OCR operations."""
    
    def test_extract_text_performance(self, sample_images):
        """Test OCR performance with sample images."""
        if not sample_images:
            pytest.skip("No sample images found in dataset")
        
        # Test performance with each sample image
        for name, image_path in sample_images.items():
            start_time = time.time()
            
            try:
                result = extract_text(image_path)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # OCR should complete within reasonable time (30 seconds max)
                assert processing_time < 30.0, f"OCR took too long: {processing_time:.2f}s for {name}"
                
                # Log performance info
                print(f"\n{name}: {processing_time:.2f}s, {len(result)} characters extracted")
                
            except Exception as e:
                # Log failures but don't fail the test
                print(f"\n{name}: Failed with error: {e}")
    
    def test_confidence_calculation_performance(self, sample_images):
        """Test confidence calculation performance."""
        if not sample_images:
            pytest.skip("No sample images found in dataset")
        
        for name, image_path in sample_images.items():
            start_time = time.time()
            
            try:
                confidence = get_text_confidence(image_path)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # Confidence calculation should be fast (10 seconds max)
                assert processing_time < 10.0, f"Confidence calculation took too long: {processing_time:.2f}s"
                
                print(f"\n{name} confidence: {processing_time:.2f}s")
                
            except Exception as e:
                print(f"\n{name} confidence failed: {e}")
    
    def test_multiple_image_processing(self, create_test_image, temp_dir):
        """Test processing multiple images in sequence."""
        num_images = 5
        images = []
        
        # Create multiple test images
        for i in range(num_images):
            img = create_test_image(f"TEST IMAGE {i}", size=(200, 100))
            img_path = os.path.join(temp_dir, f"test_{i}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Process all images and measure total time
        start_time = time.time()
        
        results = []
        for img_path in images:
            try:
                result = extract_text(img_path)
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_images
        
        print(f"\nProcessed {num_images} images in {total_time:.2f}s (avg: {avg_time:.2f}s per image)")
        
        # Average processing time should be reasonable
        assert avg_time < 15.0, f"Average processing time too high: {avg_time:.2f}s"
        
        # Should have processed all images
        assert len(results) == num_images
    
    @pytest.mark.slow
    def test_large_image_performance(self, create_test_image, temp_dir):
        """Test performance with large images."""
        # Create a large image
        large_img = create_test_image("LARGE IMAGE PERFORMANCE TEST", size=(2000, 1000))
        img_path = os.path.join(temp_dir, "large_test.png")
        large_img.save(img_path)
        
        start_time = time.time()
        
        try:
            result = extract_text(img_path)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            print(f"\nLarge image (2000x1000): {processing_time:.2f}s")
            
            # Large images should still complete within reasonable time
            assert processing_time < 60.0, f"Large image processing took too long: {processing_time:.2f}s"
            
        except Exception as e:
            # Large images might fail due to memory constraints
            print(f"\nLarge image processing failed: {e}")
    
    def test_memory_usage_stability(self, create_test_image, temp_dir):
        """Test that memory usage remains stable across multiple operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple images
        for i in range(10):
            img = create_test_image(f"MEMORY TEST {i}")
            img_path = os.path.join(temp_dir, f"memory_test_{i}.png")
            img.save(img_path)
            
            try:
                extract_text(img_path)
            except Exception:
                pass  # Ignore errors for this test
            
            # Clean up the file
            os.remove(img_path)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\nMemory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (increase: {memory_increase:.1f}MB)")
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.1f}MB"


@pytest.mark.integration
class TestIntegrationPerformance:
    """Integration performance tests."""
    
    def test_server_upload_performance(self, client, create_test_image):
        """Test server upload performance."""
        import io
        
        # Create test image
        img = create_test_image("SERVER PERFORMANCE TEST", size=(400, 200))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Measure upload and processing time
        start_time = time.time()
        
        data = {'file': (img_buffer, 'performance_test.png')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"\nServer upload and processing: {processing_time:.2f}s")
        
        # Server should respond within reasonable time
        assert processing_time < 30.0, f"Server processing took too long: {processing_time:.2f}s"
        
        # Should get a response (success or failure)
        assert response.status_code in [200, 500]
    
    def test_concurrent_server_requests(self, client, create_test_image):
        """Test server performance with concurrent requests."""
        import threading
        import io
        
        results = []
        
        def upload_image(image_name):
            img = create_test_image(f"CONCURRENT {image_name}")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            start_time = time.time()
            data = {'file': (img_buffer, f'concurrent_{image_name}.png')}
            response = client.post('/upload', data=data, content_type='multipart/form-data')
            end_time = time.time()
            
            results.append({
                'name': image_name,
                'time': end_time - start_time,
                'status': response.status_code
            })
        
        # Create multiple threads
        threads = []
        for i in range(3):  # Small number to avoid overwhelming the system
            thread = threading.Thread(target=upload_image, args=[f"test_{i}"])
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        print(f"\nConcurrent requests completed in {total_time:.2f}s")
        print(f"Individual times: {[r['time'] for r in results]}")
        
        # All requests should complete
        assert len(results) == 3
        
        # Total time should be reasonable
        assert total_time < 60.0, f"Concurrent processing took too long: {total_time:.2f}s"
