# SnapText - Screenshot OCR Tool
# Makefile for common development tasks

.PHONY: help install runserver runcli test clean lint format check-deps

# Default target
help:
	@echo "📸 SnapText - Screenshot OCR Tool"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install all dependencies (Python, Poetry, Tesseract, project deps)"
	@echo "  make runserver   - Start the web server"
	@echo "  make runcli      - Run the CLI tool interactively"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run code linting"
	@echo "  make format      - Format code"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make check-deps  - Check if all dependencies are installed"
	@echo ""
	@echo "Examples:"
	@echo "  make install && make runserver"
	@echo "  make runcli -- --help"
	@echo "  make runcli -- image.png"
	@echo ""

# Install all dependencies
install:
	@echo "🚀 Installing SnapText dependencies..."
	@chmod +x scripts/install.sh
	@./scripts/install.sh
	@echo "✅ Installation complete!"

# Start the web server
runserver:
	@echo "🌐 Starting SnapText web server..."
	@echo "Server will be available at: http://127.0.0.1:5000"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	poetry run python server/server.py

# Run the CLI tool
runcli:
	@echo "💻 Running SnapText CLI..."
	@if [ "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		poetry run python cli/cli.py $(filter-out $@,$(MAKECMDGOALS)); \
	else \
		echo "Usage examples:"; \
		echo "  make runcli -- --help"; \
		echo "  make runcli -- image.png"; \
		echo "  make runcli -- image.png --output text.txt"; \
		echo ""; \
		echo "Available options:"; \
		poetry run python cli/cli.py --help; \
	fi

# Run tests
test:
	@echo "🧪 Running all tests..."
	poetry run pytest tests/ -v

# Run only unit tests (fast)
test-unit:
	@echo "⚡ Running unit tests..."
	poetry run pytest tests/ -v -m "not slow and not integration"

# Run integration tests
test-integration:
	@echo "🔗 Running integration tests..."
	poetry run pytest tests/ -v -m "integration"

# Run performance tests (slow)
test-performance:
	@echo "🏃 Running performance tests..."
	poetry run pytest tests/ -v -m "slow"

# Run tests with coverage
test-coverage:
	@echo "📊 Running tests with coverage..."
	poetry run pytest tests/ --cov=core --cov=server --cov=cli --cov-report=html --cov-report=term

# Run specific test file
test-core:
	@echo "🔍 Testing core OCR functionality..."
	poetry run pytest tests/test_core_ocr.py -v

test-server:
	@echo "🌐 Testing server functionality..."
	poetry run pytest tests/test_server.py -v

test-cli:
	@echo "💻 Testing CLI functionality..."
	poetry run pytest tests/test_cli.py -v

# Lint code
lint:
	@echo "🔍 Running code linting..."
	@if poetry show flake8 >/dev/null 2>&1; then \
		poetry run flake8 server/ cli/ core/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8 not installed. Run: poetry add --group dev flake8"; \
	fi

# Format code
format:
	@echo "✨ Formatting code..."
	@if poetry show black >/dev/null 2>&1; then \
		poetry run black server/ cli/ core/ --line-length=88; \
	else \
		echo "black not installed. Run: poetry add --group dev black"; \
	fi
	@if poetry show isort >/dev/null 2>&1; then \
		poetry run isort server/ cli/ core/ --profile black; \
	else \
		echo "isort not installed. Run: poetry add --group dev isort"; \
	fi

# Clean up temporary files
clean:
	@echo "🧹 Cleaning up temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Check if all dependencies are installed
check-deps:
	@echo "🔍 Checking dependencies..."
	@echo -n "Python 3: "
	@if command -v python3 >/dev/null 2>&1; then \
		echo "✅ $(shell python3 --version)"; \
	else \
		echo "❌ Not found"; \
	fi
	@echo -n "Poetry: "
	@if command -v poetry >/dev/null 2>&1; then \
		echo "✅ $(shell poetry --version)"; \
	else \
		echo "❌ Not found"; \
	fi
	@echo -n "Tesseract: "
	@if command -v tesseract >/dev/null 2>&1; then \
		echo "✅ $(shell tesseract --version | head -n1)"; \
	else \
		echo "❌ Not found"; \
	fi
	@echo -n "Project dependencies: "
	@if [ -f "poetry.lock" ] && poetry check >/dev/null 2>&1; then \
		echo "✅ Installed"; \
	else \
		echo "❌ Not installed or outdated"; \
	fi

# Development server with auto-reload
dev:
	@echo "🔧 Starting development server with auto-reload..."
	@echo "Server will restart automatically when files change"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	poetry run python -m flask --app server.server run --debug --host=127.0.0.1 --port=5000

# Install development dependencies
install-dev:
	@echo "🛠️ Installing development dependencies..."
	poetry add --group dev black flake8 isort pytest pytest-cov pytest-mock mypy safety bandit radon
	@echo "✅ Development dependencies installed!"

# Show project info
info:
	@echo "📸 SnapText - Screenshot OCR Tool"
	@echo ""
	@echo "Project structure:"
	@echo "  server/     - Web server and UI"
	@echo "  cli/        - Command-line interface"
	@echo "  core/       - Core OCR functionality"
	@echo "  scripts/    - Installation and utility scripts"
	@echo ""
	@echo "Configuration files:"
	@echo "  pyproject.toml - Poetry configuration"
	@echo "  Makefile       - Build automation"
	@echo ""

# Prevent make from treating CLI arguments as targets
%:
	@:
