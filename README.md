# SnapText

A simple Python tool to extract text from screenshots using Tesseract OCR.  
Includes a small web GUI for uploading images.

## Features

- Upload a screenshot and extract text instantly
- CLI support
- Lightweight web server with static frontend
- Cross-platform installation script (`install.sh`)

## Requirements

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

## Installation

```bash
git clone https://github.com/yourname/snaptext.git
cd snaptext
./install.sh
poetry install
````

## Usage

### Start Web Server

```bash
poetry run python server/server.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### CLI

```bash
poetry run python cli/cli.py path/to/image.png
```
