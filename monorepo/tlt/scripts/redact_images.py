#!/usr/bin/env python3
"""
TLT Image Redaction Script

This script redacts PII and sensitive information from images using OCR detection.
It automatically detects and redacts Discord IDs, UUIDs, API keys, timestamps,
and other sensitive data by covering them with black boxes.

Usage:
    python redact_images.py <input_dir> <output_dir> [--auto-redact]
    python redact_images.py <input_dir> <output_dir> --phrase "specific text"

Examples:
    python redact_images.py ./docs/assets ./docs/assets_redacted --auto-redact
    python redact_images.py ./screenshots ./redacted_screenshots --phrase "username"
"""

import os
import argparse
import re
from PIL import Image, ImageDraw
import pytesseract
from typing import List, Tuple, Pattern

SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')

class ImageRedactor:
    """Redacts PII and sensitive information from images using OCR."""
    
    def __init__(self):
        # Compile regex patterns for sensitive data detection
        self.sensitive_patterns = {
            'discord_id': re.compile(r'\b\d{17,19}\b'),  # Discord snowflake IDs
            'long_numeric_id': re.compile(r'\b\d{10,25}\b'),  # Long numeric IDs (event_id, user_id, etc.)
            'uuid': re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', re.IGNORECASE),
            'discord_token': re.compile(r'\bMT[A-Za-z0-9]{24}\.[A-Za-z0-9]{6}\.[A-Za-z0-9-_]{27,39}\b'),
            'openai_key': re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9]{20,}\b'),
            'timestamp': re.compile(r'\b\d{8}_\d{6}\b'),  # YYYYMMDD_HHMMSS format
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        }
        
        # Common sensitive keywords to redact
        self.sensitive_keywords = [
            'password', 'passwd', 'secret', 'token', 'key', 'api_key',
            'private', 'confidential', 'internal', 'admin', 'root',
            'username', 'login', 'auth', 'credential', 'bearer'
        ]
        
        self.redaction_count = 0
        self.total_images = 0
    
    def is_sensitive_text(self, text: str) -> bool:
        """Check if text contains sensitive information."""
        text_lower = text.lower()
        
        # Check regex patterns
        for pattern_name, pattern in self.sensitive_patterns.items():
            if pattern.search(text):
                # Special handling for long numeric IDs to avoid false positives
                if pattern_name == 'long_numeric_id':
                    # Skip if it's a common non-sensitive number (years, simple counts, etc.)
                    if self._is_likely_non_sensitive_number(text):
                        continue
                return True
        
        # Check sensitive keywords
        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def _is_likely_non_sensitive_number(self, text: str) -> bool:
        """Check if a number is likely non-sensitive (years, simple counts, etc.)."""
        try:
            num = int(text)
            
            # Skip common non-sensitive numbers
            if 1900 <= num <= 2100:  # Years
                return True
            if 1 <= num <= 1000:  # Simple counts, percentages, etc.
                return True
            if num in [0, 100, 200, 300, 400, 500, 1000, 2000, 3000, 5000, 10000]:  # Round numbers
                return True
            
            return False
        except ValueError:
            return False
    
    def redact_text_in_image(self, image_path: str, output_path: str, target_phrase: str = None, auto_redact: bool = False) -> int:
        """
        Redact sensitive text from an image.
        
        Args:
            image_path: Path to input image
            output_path: Path to save redacted image
            target_phrase: Specific phrase to redact (if provided)
            auto_redact: Whether to automatically redact sensitive data
            
        Returns:
            Number of redactions made
        """
        try:
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            redactions_made = 0
            
            # Perform OCR with bounding boxes
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                
                # Skip empty text
                if not text:
                    continue
                
                should_redact = False
                
                if target_phrase:
                    # Redact specific phrase
                    if target_phrase.lower() in text.lower():
                        should_redact = True
                
                if auto_redact:
                    # Auto-redact sensitive information
                    if self.is_sensitive_text(text):
                        should_redact = True
                
                if should_redact:
                    x, y, w, h = (
                        ocr_data['left'][i],
                        ocr_data['top'][i],
                        ocr_data['width'][i],
                        ocr_data['height'][i]
                    )
                    
                    # Add padding to ensure complete coverage
                    padding = 2
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = w + (padding * 2)
                    h = h + (padding * 2)
                    
                    # Draw black rectangle to redact text
                    draw.rectangle([(x, y), (x + w, y + h)], fill="black")
                    redactions_made += 1
            
            # Save redacted image
            image.save(output_path)
            
            if redactions_made > 0:
                print(f"Redacted {redactions_made} items in: {os.path.basename(image_path)} → {output_path}")
            else:
                print(f"No redactions needed: {os.path.basename(image_path)} → {output_path}")
            
            return redactions_made
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return 0
    
    def redact_directory(self, input_dir: str, output_dir: str, target_phrase: str = None, auto_redact: bool = False) -> None:
        """
        Redact all images in a directory.
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save redacted images
            target_phrase: Specific phrase to redact (if provided)
            auto_redact: Whether to automatically redact sensitive data
        """
        if not os.path.exists(input_dir):
            print(f"Error: Input directory does not exist: {input_dir}")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process all supported image files
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(SUPPORTED_EXTENSIONS):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, filename)
                
                redactions = self.redact_text_in_image(input_path, output_path, target_phrase, auto_redact)
                self.redaction_count += redactions
                self.total_images += 1
        
        # Print summary
        print(f"\nRedaction Summary:")
        print(f"Images processed: {self.total_images}")
        print(f"Total redactions: {self.redaction_count}")
        print(f"Average redactions per image: {self.redaction_count / max(1, self.total_images):.1f}")
    
    def create_redaction_report(self, output_dir: str) -> None:
        """Create a report of redactions performed."""
        report_path = os.path.join(output_dir, 'IMAGE_REDACTION_REPORT.md')
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# TLT Image Redaction Report\n\n")
                f.write("This directory contains redacted images with PII and sensitive information removed.\n\n")
                f.write("## Redaction Summary\n\n")
                f.write(f"- **Images processed**: {self.total_images}\n")
                f.write(f"- **Total redactions**: {self.redaction_count}\n")
                f.write(f"- **Average redactions per image**: {self.redaction_count / max(1, self.total_images):.1f}\n\n")
                f.write("## Redaction Types\n\n")
                f.write("The following types of sensitive information were automatically detected and redacted:\n\n")
                f.write("### Automatically Detected Patterns\n")
                f.write("- **Discord IDs**: 17-19 digit snowflake identifiers\n")
                f.write("- **Long Numeric IDs**: 10-25 digit identifiers (event_id, user_id, etc.)\n")
                f.write("- **UUIDs**: 8-4-4-4-12 hex character identifiers\n")
                f.write("- **Discord Tokens**: MT... format tokens\n")
                f.write("- **OpenAI API Keys**: sk-... format keys\n")
                f.write("- **Timestamps**: YYYYMMDD_HHMMSS format\n")
                f.write("- **Email Addresses**: Standard email formats\n")
                f.write("- **Phone Numbers**: US phone number formats\n")
                f.write("- **IP Addresses**: IPv4 addresses\n")
                f.write("- **Credit Card Numbers**: Standard credit card formats\n")
                f.write("- **SSNs**: XXX-XX-XXXX format\n\n")
                f.write("### Sensitive Keywords\n")
                f.write("- password, secret, token, key, api_key\n")
                f.write("- private, confidential, internal, admin\n")
                f.write("- username, login, auth, credential, bearer\n\n")
                f.write("## Processing Method\n\n")
                f.write("1. **OCR Detection**: Tesseract OCR used to extract text from images\n")
                f.write("2. **Pattern Matching**: Regex patterns identify sensitive data types\n")
                f.write("3. **Smart Filtering**: Long numeric IDs filtered to avoid false positives\n")
                f.write("4. **Keyword Filtering**: Common sensitive keywords detected\n")
                f.write("5. **Black Box Redaction**: Sensitive areas covered with black rectangles\n")
                f.write("6. **Padding Applied**: 2-pixel padding ensures complete coverage\n\n")
                f.write("### False Positive Prevention\n")
                f.write("Long numeric IDs are filtered to exclude common non-sensitive numbers:\n")
                f.write("- Years (1900-2100)\n")
                f.write("- Simple counts (1-1000)\n")
                f.write("- Round numbers (100, 500, 1000, etc.)\n\n")
                f.write("---\n")
                f.write("Generated by TLT Image Redaction Script\n")
            
            print(f"Redaction report created: {report_path}")
            
        except Exception as e:
            print(f"Error creating redaction report: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Redact PII and sensitive information from images using OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Auto-redact sensitive information
    python redact_images.py ./docs/assets ./docs/assets_redacted --auto-redact
    
    # Redact specific phrase
    python redact_images.py ./screenshots ./redacted --phrase "username"
    
    # Redact both auto and specific
    python redact_images.py ./images ./redacted --auto-redact --phrase "confidential"
        """
    )
    
    parser.add_argument(
        'input_dir',
        help='Directory containing input images'
    )
    
    parser.add_argument(
        'output_dir',
        help='Directory to save redacted images'
    )
    
    parser.add_argument(
        '--phrase',
        help='Specific phrase or word to redact (quoted if contains spaces)'
    )
    
    parser.add_argument(
        '--auto-redact',
        action='store_true',
        help='Automatically redact sensitive information (Discord IDs, UUIDs, API keys, etc.)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.phrase and not args.auto_redact:
        print("Error: Either --phrase or --auto-redact must be specified")
        parser.print_help()
        return
    
    # Initialize redactor
    redactor = ImageRedactor()
    
    print(f"Redacting images from {args.input_dir} to {args.output_dir}")
    if args.auto_redact:
        print("Auto-redacting sensitive information...")
    if args.phrase:
        print(f"Redacting phrase: '{args.phrase}'")
    print("=" * 60)
    
    # Perform redaction
    redactor.redact_directory(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        target_phrase=args.phrase,
        auto_redact=args.auto_redact
    )
    
    # Create redaction report
    redactor.create_redaction_report(args.output_dir)
    
    print("=" * 60)
    print("Image redaction complete!")


if __name__ == "__main__":
    main()
