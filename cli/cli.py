import sys
from core.tool import extract_text

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    text = extract_text(image_path)
    print("Extracted text:\n")
    print(text)

if __name__ == "__main__":
    main()
