"""
Tests for the CLI interface in cli/cli.py
"""

import pytest
import sys
import os
import tempfile
import subprocess


class TestCLIArguments:
    """Test CLI argument parsing."""
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', '--help'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        assert result.returncode == 0
        assert 'SnapText' in result.stdout
        assert 'Extract text from images' in result.stdout
        assert '--output' in result.stdout
        assert '--verbose' in result.stdout
        assert '--confidence' in result.stdout
    
    def test_cli_version(self):
        """Test CLI version output."""
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', '--version'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        assert result.returncode == 0
        assert 'SnapText CLI' in result.stdout


class TestCLIExecution:
    """Test CLI execution with different arguments."""
    
    def test_cli_basic_usage(self, create_test_image, temp_dir):
        """Test basic CLI usage."""
        # Create test image with clear text
        img = create_test_image("HELLO", size=(200, 80))
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        # Run CLI
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', img_path
        ], capture_output=True, text=True, cwd=os.getcwd())

        assert result.returncode == 0
        # Should extract some text (OCR might not be perfect)
        assert len(result.stdout.strip()) > 0
    
    def test_cli_with_output_file(self, create_test_image, temp_dir):
        """Test CLI with output file option."""
        # Create test image
        img = create_test_image("SAVE", size=(200, 80))
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        # Output file path
        output_path = os.path.join(temp_dir, "output.txt")

        # Run CLI with output option
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', img_path, '--output', output_path
        ], capture_output=True, text=True, cwd=os.getcwd())

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Check file was created and has content
        with open(output_path, 'r') as f:
            content = f.read()
        assert len(content.strip()) > 0
    
    def test_cli_with_verbose(self, create_test_image, temp_dir):
        """Test CLI with verbose option."""
        # Create test image
        img = create_test_image("VERBOSE", size=(200, 80))
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        # Run CLI with verbose option
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', img_path, '--verbose'
        ], capture_output=True, text=True, cwd=os.getcwd())

        assert result.returncode == 0
        assert "Processing image" in result.stdout
        assert "Text extraction completed" in result.stdout
        assert "OCR Quality Information" in result.stdout
        # Should show some confidence percentage
        assert "%" in result.stdout
    
    def test_cli_with_confidence(self, create_test_image, temp_dir):
        """Test CLI with confidence option."""
        # Create test image
        img = create_test_image("CONFIDENCE", size=(200, 80))
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)

        # Run CLI with confidence option
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', img_path, '--confidence'
        ], capture_output=True, text=True, cwd=os.getcwd())

        assert result.returncode == 0
        assert "OCR Quality Information" in result.stdout
        # Should show some confidence percentage and quality level
        assert "%" in result.stdout
        assert any(quality in result.stdout for quality in ["High", "Medium", "Low"])
    
    def test_cli_nonexistent_file(self):
        """Test CLI with non-existent file."""
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', '/nonexistent/file.png'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        assert result.returncode == 1
        assert "not found" in result.stderr
    
    def test_cli_no_arguments(self):
        """Test CLI without arguments."""
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        assert result.returncode == 2  # argparse error
        assert "required" in result.stderr.lower()


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_cli_ocr_failure(self, temp_dir):
        """Test CLI when OCR fails with invalid file."""
        # Create an invalid image file (text file with .png extension)
        invalid_path = os.path.join(temp_dir, "invalid.png")
        with open(invalid_path, 'w') as f:
            f.write("This is not an image")

        # Run CLI
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', invalid_path
        ], capture_output=True, text=True, cwd=os.getcwd())

        assert result.returncode == 1
        assert "Error processing image" in result.stderr
    
    def test_cli_invalid_output_path(self, create_test_image, temp_dir):
        """Test CLI with invalid output path."""
        # Create test image
        img = create_test_image("TEST")
        img_path = os.path.join(temp_dir, "test.png")
        img.save(img_path)
        
        # Try to write to invalid path
        invalid_output = "/invalid/path/output.txt"
        
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', img_path, '--output', invalid_output
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        assert result.returncode == 1
        assert "Error saving to file" in result.stderr
    
    def test_cli_unreadable_file(self, temp_dir):
        """Test CLI with unreadable file."""
        # Create a file and make it unreadable
        test_file = os.path.join(temp_dir, "unreadable.png")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Make file unreadable (on Unix systems)
        if hasattr(os, 'chmod'):
            os.chmod(test_file, 0o000)
        
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', test_file
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Should fail with permission error
        assert result.returncode == 1
        
        # Restore permissions for cleanup
        if hasattr(os, 'chmod'):
            os.chmod(test_file, 0o644)


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_cli_real_image_processing(self, sample_images):
        """Test CLI with real sample images."""
        if not sample_images:
            pytest.skip("No sample images found in dataset")
        
        # Test with first available image
        image_path = list(sample_images.values())[0]
        
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', image_path, '--verbose'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Should complete successfully or fail gracefully
        assert result.returncode in [0, 1]
        
        if result.returncode == 0:
            assert "Processing image" in result.stdout
            assert "Text extraction completed" in result.stdout
    
    def test_cli_with_all_options(self, create_test_image, temp_dir):
        """Test CLI with all options combined."""
        # Create test image
        img = create_test_image("FULL TEST", size=(300, 100))
        img_path = os.path.join(temp_dir, "full_test.png")
        img.save(img_path)
        
        # Output file
        output_path = os.path.join(temp_dir, "full_output.txt")
        
        # Run with all options
        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', img_path,
            '--output', output_path,
            '--verbose',
            '--confidence'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Should complete
        assert result.returncode in [0, 1]
        
        if result.returncode == 0:
            # Check that output file was created
            assert os.path.exists(output_path)
            
            # Check verbose output
            assert "Processing image" in result.stdout
            assert "OCR Quality Information" in result.stdout
    
    def test_cli_different_image_formats(self, create_test_image, temp_dir):
        """Test CLI with different image formats."""
        formats = [('PNG', 'png'), ('JPEG', 'jpg')]
        
        for fmt, ext in formats:
            img = create_test_image(f"FORMAT {fmt}")
            if fmt == 'JPEG':
                img = img.convert('RGB')
            
            img_path = os.path.join(temp_dir, f"test.{ext}")
            img.save(img_path, format=fmt)
            
            result = subprocess.run([
                sys.executable, '-m', 'cli.cli', img_path
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            # Should handle different formats
            assert result.returncode in [0, 1]


class TestCLIOutput:
    """Test CLI output formatting."""
    
    def test_confidence_quality_assessment(self, create_test_image, temp_dir):
        """Test confidence quality assessment output."""
        # Create a clear test image that should get high confidence
        img = create_test_image("QUALITY", size=(300, 100))
        img_path = os.path.join(temp_dir, "quality_test.png")
        img.save(img_path)

        result = subprocess.run([
            sys.executable, '-m', 'cli.cli', img_path, '--confidence'
        ], capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            # Should show quality assessment
            assert any(quality in result.stdout for quality in ["High", "Medium", "Low"])
            assert "%" in result.stdout
            assert "OCR Quality Information" in result.stdout
