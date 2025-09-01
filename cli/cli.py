#!/usr/bin/env python3
"""
SnapText CLI - Command-line interface for screenshot OCR
"""

import argparse
import os
import sys
from pathlib import Path

from core.tool import extract_text, get_text_confidence


def main():
    parser = argparse.ArgumentParser(
        description="SnapText - Extract text from images using OCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.png
  %(prog)s screenshot.jpg --output extracted.txt
  %(prog)s photo.png --verbose
        """,
    )

    parser.add_argument("image_path", help="Path to the image file to process")

    parser.add_argument(
        "-o",
        "--output",
        help="Output file to save extracted text (default: print to stdout)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--confidence", action="store_true", help="Show OCR confidence information"
    )

    parser.add_argument("--version", action="version", version="SnapText CLI 1.0.0")

    args = parser.parse_args()

    # Check if image file exists
    if not os.path.exists(args.image_path):
        print(f"❌ Error: Image file '{args.image_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Check if file is readable
    if not os.access(args.image_path, os.R_OK):
        print(f"❌ Error: Cannot read image file '{args.image_path}'.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"📸 Processing image: {args.image_path}")

    try:
        # Extract text from image
        text = extract_text(args.image_path)

        if args.verbose:
            print(f"✅ Text extraction completed. Found {len(text)} characters.")

        # Get confidence information if requested
        if args.confidence or args.verbose:
            confidence_info = get_text_confidence(args.image_path)
            if not confidence_info.get("error"):
                avg_conf = confidence_info.get("average_confidence", 0)
                word_count = confidence_info.get("word_count", 0)
                low_conf_words = confidence_info.get("low_confidence_words", 0)

                print("\n📊 OCR Quality Information:")
                print(f"   Average confidence: {avg_conf:.1f}%")
                print(f"   Words detected: {word_count}")
                if low_conf_words > 0:
                    print(f"   Low confidence words: {low_conf_words}")

                # Quality assessment
                if avg_conf >= 80:
                    print("   Quality: ✅ High")
                elif avg_conf >= 60:
                    print("   Quality: ⚠️ Medium")
                else:
                    print("   Quality: ❌ Low - Consider improving image quality")

        # Output results
        if args.output:
            # Save to file
            output_path = Path(args.output)
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                if args.verbose:
                    print(f"\n💾 Text saved to: {output_path}")
                else:
                    print(f"Text saved to: {output_path}")
            except IOError as e:
                print(f"❌ Error saving to file '{output_path}': {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Print to stdout
            if args.verbose or args.confidence:
                print("\n📄 Extracted text:")
                print("-" * 40)
            print(text)

    except Exception as e:
        print(f"❌ Error processing image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
