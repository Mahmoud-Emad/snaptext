#!/usr/bin/env bash

set -e

echo "📦 Installing SnapText dependencies..."

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    CYGWIN*|MINGW*|MSYS*) PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Detected platform: $PLATFORM"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python on different platforms
install_python() {
    echo "🐍 Installing Python..."

    if [ "$PLATFORM" = "Linux" ]; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv python3-dev
        elif command_exists dnf; then
            sudo dnf install -y python3 python3-pip python3-venv python3-devel
        elif command_exists pacman; then
            sudo pacman -S --noconfirm python python-pip python-virtualenv
        elif command_exists zypper; then
            sudo zypper install -y python3 python3-pip python3-venv python3-devel
        else
            echo "❌ Unsupported Linux distribution. Please install Python 3.8+ manually."
            exit 1
        fi
    elif [ "$PLATFORM" = "Mac" ]; then
        if command_exists brew; then
            brew install python@3.11
        else
            echo "❌ Homebrew not found. Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            brew install python@3.11
        fi
    elif [[ "$PLATFORM" == Windows* ]]; then
        echo "⚠️ Please install Python manually on Windows:"
        echo "    https://www.python.org/downloads/windows/"
        echo "    Make sure to check 'Add Python to PATH' during installation"
        exit 1
    fi
}

# Function to install Poetry
install_poetry() {
    echo "📝 Installing Poetry..."

    if [ "$PLATFORM" = "Windows" ]; then
        echo "⚠️ Please install Poetry manually on Windows:"
        echo "    https://python-poetry.org/docs/#installation"
        exit 1
    else
        curl -sSL https://install.python-poetry.org | python3 -

        # Add Poetry to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"

        # Add Poetry to shell profile
        if [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        fi
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi

        echo "✅ Poetry installed. You may need to restart your terminal or run:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

# Check and install Python if needed
if ! command_exists python3; then
    echo "❌ Python 3 not found."
    install_python
else
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.8"

    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        echo "❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION+ is required."
        install_python
    else
        echo "✅ Python $PYTHON_VERSION found."
    fi
fi

# Check and install Poetry if needed
if ! command_exists poetry; then
    echo "❌ Poetry not found."
    install_poetry
else
    echo "✅ Poetry found: $(poetry --version)"
fi

# Install system dependencies (Tesseract OCR)
echo "🔍 Installing Tesseract OCR..."
if [ "$PLATFORM" = "Linux" ]; then
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr libtesseract-dev
    elif command_exists dnf; then
        sudo dnf install -y tesseract tesseract-devel
    elif command_exists pacman; then
        sudo pacman -S --noconfirm tesseract tesseract-data-eng
    elif command_exists zypper; then
        sudo zypper install -y tesseract-ocr tesseract-ocr-devel
    else
        echo "❌ Unsupported Linux distribution. Please install Tesseract manually."
        exit 1
    fi
elif [ "$PLATFORM" = "Mac" ]; then
    if command_exists brew; then
        brew install tesseract
    else
        echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh/"
        exit 1
    fi
elif [[ "$PLATFORM" == Windows* ]]; then
    echo "⚠️ Please install Tesseract manually on Windows:"
    echo "    https://github.com/UB-Mannheim/tesseract/wiki"
    echo "    Make sure to add Tesseract to your PATH"
    exit 0
else
    echo "❌ Unsupported platform: $PLATFORM"
    exit 1
fi

# Verify Tesseract installation
if command_exists tesseract; then
    echo "✅ Tesseract OCR installed: $(tesseract --version | head -n1)"
else
    echo "❌ Tesseract installation failed or not in PATH"
    exit 1
fi

# Install project dependencies with Poetry
echo "📦 Installing project dependencies with Poetry..."
poetry install

echo ""
echo "🎉 Installation complete!"
echo ""
echo "You can now run:"
echo "  make runserver    # Start the web server"
echo "  make runcli       # Run the CLI tool"
echo "  poetry run python server/server.py  # Start server directly"
echo "  poetry run python cli/cli.py --help # CLI help"
echo ""
