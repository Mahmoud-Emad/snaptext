# SnapText

[![Tests](https://github.com/Mahmoud-Emad/snaptext/workflows/Tests/badge.svg)](https://github.com/Mahmoud-Emad/snaptext/actions/workflows/test.yml)
[![Lint](https://github.com/Mahmoud-Emad/snaptext/workflows/Lint/badge.svg)](https://github.com/Mahmoud-Emad/snaptext/actions/workflows/lint.yml)
[![CI](https://github.com/Mahmoud-Emad/snaptext/workflows/CI/badge.svg)](https://github.com/Mahmoud-Emad/snaptext/actions/workflows/ci.yml)

A powerful OCR tool to extract text from images with enhanced accuracy and modern UI.

## Features

- **Enhanced OCR Accuracy**: Multiple preprocessing techniques for better text recognition
- **Modern Web Interface**: Google Material Design-inspired UI with image preview
- **Command Line Interface**: Full-featured CLI with confidence scoring
- **Image Preview**: See your uploaded images before processing
- **OCR Quality Metrics**: Real-time confidence scores and quality assessment
- **Copy to Clipboard**: One-click text copying
- **Responsive Design**: Works on desktop and mobile devices
- **Cross-platform**: Supports Linux, macOS, and Windows

## OCR Improvements

SnapText uses advanced image preprocessing techniques to improve text extraction accuracy:

- **Multiple OCR Methods**: Tries different approaches and selects the best result
- **Image Enhancement**: Contrast, sharpness, and noise reduction
- **Adaptive Thresholding**: Handles varying lighting conditions
- **Scale Optimization**: Automatically scales images for better recognition
- **Confidence Scoring**: Provides quality metrics for extracted text

## Requirements

- Python 3.11+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- OpenCV (automatically installed)
- NumPy (automatically installed)

## Quick Start

```bash
git clone https://github.com/yourname/snaptext.git
cd snaptext
make install    # Installs Python, Poetry, Tesseract, and dependencies
make runserver  # Start the web interface
```

## Installation

### Automatic Installation (Recommended)

```bash
make install
```

This will automatically install:

- Python 3.11+ (if not present)
- Poetry (if not present)
- Tesseract OCR
- All project dependencies

### Manual Installation

```bash
# Install Tesseract OCR first
# On macOS: brew install tesseract
# On Ubuntu: sudo apt-get install tesseract-ocr

# Install project dependencies
poetry install
```

## Usage

### Web Interface

```bash
make runserver
# or
poetry run python server/server.py

# For development with debug mode (not recommended for production)
FLASK_DEBUG=true poetry run python server/server.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

**Security Note**: Debug mode is disabled by default for security. Only enable it during development by setting the `FLASK_DEBUG=true` environment variable.

Features:

- Drag and drop image upload
- Image preview with metadata
- Real-time OCR quality assessment
- One-click text copying
- Responsive design

### Command Line Interface

```bash
# Basic usage
make runcli -- image.png

# With confidence information
make runcli -- image.png --confidence

# Save to file with verbose output
make runcli -- image.png --output extracted.txt --verbose

# Direct poetry commands
poetry run python cli/cli.py image.png --help
```

### Available Make Commands

```bash
make help        # Show all available commands
make install     # Install all dependencies
make runserver   # Start web server
make runcli      # Run CLI tool
make check-deps  # Check dependency status
make clean       # Clean temporary files

# Testing commands
make test              # Run all tests
make test-unit         # Run fast unit tests
make test-integration  # Run integration tests
make test-performance  # Run performance tests (slow)
make test-coverage     # Run tests with coverage report
make test-core         # Test core OCR functionality
make test-server       # Test Flask server
make test-cli          # Test CLI interface

# Code quality commands
make lint              # Run code linting
make format            # Format code with black and isort
make install-dev       # Install development dependencies
```

## CI/CD Workflows

SnapText includes comprehensive GitHub Actions workflows for continuous integration:

### 🔄 **Automated Testing** (`.github/workflows/test.yml`)

- **Multi-platform testing**: Ubuntu and macOS
- **Multi-version support**: Python 3.11, 3.12, 3.13
- **Comprehensive test suite**: Unit, integration, and performance tests
- **Coverage reporting**: Automatic coverage reports with Codecov
- **CLI and server integration testing**
- **Security scanning**: Safety and Bandit checks

### 🔍 **Code Quality** (`.github/workflows/lint.yml`)

- **Code formatting**: Black and isort validation
- **Linting**: Flake8 with custom rules
- **Type checking**: MyPy static analysis
- **Security scanning**: Automated security issue detection
- **Documentation checks**: Docstring validation
- **Complexity analysis**: Code complexity metrics
- **Pre-commit hooks validation**

### ⚡ **Pull Request CI** (`.github/workflows/ci.yml`)

- **Smart change detection**: Only runs relevant checks
- **Fast feedback**: Optimized for quick PR validation
- **Integration testing**: End-to-end workflow validation
- **Security validation**: Automated security checks
- **Documentation validation**: README and markdown link checking
