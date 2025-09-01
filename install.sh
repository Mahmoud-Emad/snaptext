#!/usr/bin/env bash

set -e

echo "📦 Installing TextShot dependencies..."

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    CYGWIN*|MINGW*|MSYS*) PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Detected platform: $PLATFORM"

# Install system dependencies
if [ "$PLATFORM" = "Linux" ]; then
    echo "Installing Tesseract on Linux..."
    if command -v apt-get >/dev/null; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr libtesseract-dev python3-venv
    elif command -v dnf >/dev/null; then
        sudo dnf install -y tesseract tesseract-devel python3-venv
    elif command -v pacman >/dev/null; then
        sudo pacman -S --noconfirm tesseract tesseract-data python-virtualenv
    else
        echo "❌ Unsupported Linux distribution. Please install Tesseract manually."
    fi
elif [ "$PLATFORM" = "Mac" ]; then
    echo "Installing Tesseract on macOS..."
    if command -v brew >/dev/null; then
        brew install tesseract
    else
        echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh/"
        exit 1
    fi
elif [[ "$PLATFORM" == Windows* ]]; then
    echo "⚠️ Please install Tesseract manually on Windows:"
    echo "    https://github.com/UB-Mannheim/tesseract/wiki"
    echo "Then run: poetry install"
    exit 0
else
    echo "❌ Unsupported platform: $PLATFORM"
    exit 1
fi

# Install Poetry if not found
if ! command -v poetry >/dev/null 2>&1; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install project dependencies
echo "Installing project dependencies with Poetry..."
poetry install

echo "✅ Installation complete. You can now run:"
echo "   poetry run python server/server.py"
