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
    
    def redact_text_in_image(self, image_path: str, output_path: str, target_phrase: str = None, auto_redact: bool = False, debug: bool = False) -> int:
        """
        Redact sensitive text from an image.
        
        Args:
            image_path: Path to input image
            output_path: Path to save redacted image
            target_phrase: Specific phrase to redact (if provided)
            auto_redact: Whether to automatically redact sensitive data
            debug: Print debug information about OCR detection
            
        Returns:
            Number of redactions made
        """
        try:
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            redactions_made = 0
            
            # Perform OCR with bounding boxes - try multiple configurations for better detection
            ocr_configs = [
                '',  # Default config
                '--psm 6',  # Treat image as single uniform block
                '--psm 8',  # Treat image as single word
                '--psm 13',  # Raw line. Treat image as single text line
                '-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # Letters and numbers only
            ]
            
            all_ocr_data = []
            for config in ocr_configs:
                try:
                    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
                    all_ocr_data.append(data)
                    if debug and target_phrase:
                        valid_texts = [data['text'][i].strip() for i in range(len(data['text'])) if data['text'][i].strip()]
                        print(f"DEBUG: OCR config '{config}' found {len(valid_texts)} text elements")
                except:
                    continue
            
            # Use the first (default) configuration as primary
            ocr_data = all_ocr_data[0] if all_ocr_data else {'text': [], 'left': [], 'top': [], 'width': [], 'height': [], 'conf': []}
            
            # Combine results from all configurations for better coverage
            combined_texts = set()
            for data in all_ocr_data:
                for i in range(len(data['text'])):
                    text = data['text'][i].strip()
                    if text and len(text) > 2:  # Only include meaningful text
                        combined_texts.add(text.lower())
            
            # Filter out empty text elements
            valid_indices = []
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                if text:
                    valid_indices.append(i)
            
            if debug and target_phrase:
                print(f"\nDEBUG: OCR detected {len(valid_indices)} text elements:")
                for i in valid_indices:
                    text = ocr_data['text'][i].strip()
                    conf = ocr_data['conf'][i]
                    x, y = ocr_data['left'][i], ocr_data['top'][i]
                    print(f"  [{i}] '{text}' (conf: {conf}, pos: {x},{y})")
                print(f"\nDEBUG: Combined texts from all OCR configs: {sorted(combined_texts)}")
            
            # Track which elements to redact
            elements_to_redact = set()
            direct_redaction_areas = []  # List of (x, y, w, h) tuples for direct coordinate redaction
            
            if target_phrase:
                target_lower = target_phrase.lower()
                if debug:
                    print(f"\nDEBUG: Looking for phrase: '{target_phrase}' (lowercase: '{target_lower}')")
                
                # Check if phrase exists in any of the combined OCR results
                phrase_found_in_combined = any(target_lower in text for text in combined_texts)
                if debug and phrase_found_in_combined:
                    matching_texts = [text for text in combined_texts if target_lower in text]
                    print(f"DEBUG: Phrase found in combined OCR results: {matching_texts}")
                
                # First, try to find exact phrase matches in individual elements across ALL OCR configurations
                for data_idx, data in enumerate(all_ocr_data):
                    config_name = ocr_configs[data_idx] if data_idx < len(ocr_configs) else f"config_{data_idx}"
                    for i in range(len(data['text'])):
                        text = data['text'][i].strip().lower()
                        if text and target_lower in text:
                            # Found the phrase! Now find corresponding element in primary OCR data
                            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                            
                            # Find overlapping elements in primary OCR data
                            for j in valid_indices:
                                primary_x = ocr_data['left'][j]
                                primary_y = ocr_data['top'][j]
                                primary_w = ocr_data['width'][j]
                                primary_h = ocr_data['height'][j]
                                
                                # Check if bounding boxes overlap significantly
                                overlap_x = max(0, min(x + w, primary_x + primary_w) - max(x, primary_x))
                                overlap_y = max(0, min(y + h, primary_y + primary_h) - max(y, primary_y))
                                overlap_area = overlap_x * overlap_y
                                
                                # If there's significant overlap (at least 30% of either box)
                                area1 = w * h
                                area2 = primary_w * primary_h
                                if area1 > 0 and area2 > 0:
                                    overlap_ratio = overlap_area / min(area1, area2)
                                    if overlap_ratio >= 0.3:
                                        elements_to_redact.add(j)
                                        if debug:
                                            print(f"DEBUG: Found phrase in {config_name} at ({x},{y},{w},{h})")
                                            print(f"DEBUG: Mapped to primary element [{j}]: '{ocr_data['text'][j].strip()}' at ({primary_x},{primary_y})")
                            
                            # If no overlapping elements found, add direct redaction coordinates
                            if not any(True for _ in elements_to_redact):  # Check if no elements added yet for this phrase
                                direct_redaction_areas.append((x, y, w, h))
                                if debug:
                                    print(f"DEBUG: Added direct redaction area at ({x},{y},{w},{h})")
                
                # Also check primary OCR data elements
                for i in valid_indices:
                    text = ocr_data['text'][i].strip().lower()
                    if target_lower in text:
                        elements_to_redact.add(i)
                        if debug:
                            print(f"DEBUG: Found exact match in primary element [{i}]: '{ocr_data['text'][i].strip()}'")
                
                # If no exact matches found, try to find phrase across multiple elements
                if not elements_to_redact:
                    if debug:
                        print("DEBUG: No exact matches found, trying multi-element reconstruction...")
                    
                    # Build a reconstructed text with position mapping
                    reconstructed_text = ""
                    char_to_element = []
                    
                    for idx, i in enumerate(valid_indices):
                        text = ocr_data['text'][i].strip()
                        start_pos = len(reconstructed_text)
                        
                        # Add space if this isn't the first element and we're on same line roughly
                        if idx > 0:
                            prev_i = valid_indices[idx - 1]
                            # Check if elements are on roughly the same line (within 10 pixels)
                            if abs(ocr_data['top'][i] - ocr_data['top'][prev_i]) <= 10:
                                reconstructed_text += " "
                                char_to_element.append(None)  # Space doesn't belong to any element
                        
                        reconstructed_text += text
                        # Map each character to its OCR element index
                        for _ in range(len(text)):
                            char_to_element.append(i)
                    
                    if debug:
                        print(f"DEBUG: Reconstructed text: '{reconstructed_text}'")
                        print(f"DEBUG: Reconstructed lowercase: '{reconstructed_text.lower()}'")
                    
                    # Search for target phrase in reconstructed text
                    reconstructed_lower = reconstructed_text.lower()
                    phrase_start = reconstructed_lower.find(target_lower)
                    
                    if phrase_start != -1:
                        phrase_end = phrase_start + len(target_phrase)
                        if debug:
                            print(f"DEBUG: Found phrase at positions {phrase_start}-{phrase_end} in reconstructed text")
                        
                        # Find all OCR elements that contain part of the phrase
                        for char_pos in range(phrase_start, phrase_end):
                            if char_pos < len(char_to_element) and char_to_element[char_pos] is not None:
                                elements_to_redact.add(char_to_element[char_pos])
                                if debug:
                                    elem_idx = char_to_element[char_pos]
                                    print(f"DEBUG: Will redact element [{elem_idx}]: '{ocr_data['text'][elem_idx].strip()}'")
                    elif debug:
                        print(f"DEBUG: Phrase '{target_phrase}' not found in reconstructed text")
                
                if debug:
                    print(f"DEBUG: Total elements to redact: {len(elements_to_redact)}")
            
            # Only try aggressive approaches if phrase was not found at all
            phrase_found_anywhere = len(elements_to_redact) > 0 or len(direct_redaction_areas) > 0
            
            if target_phrase and not phrase_found_anywhere:
                if debug:
                    print("DEBUG: Phrase not found anywhere, trying fallback approaches...")
                
                # Try character-by-character fuzzy matching only as last resort
                if debug:
                    print("DEBUG: Trying character-by-character approach...")
                target_chars = set(target_phrase.lower().replace(" ", ""))
                for i in valid_indices:
                    text = ocr_data['text'][i].strip().lower().replace(" ", "")
                    # If this text element contains a significant portion of target phrase characters
                    matching_chars = len(target_chars.intersection(set(text)))
                    if len(text) >= 3 and matching_chars >= min(len(target_chars) * 0.6, len(text) * 0.8):
                        elements_to_redact.add(i)
                        if debug:
                            print(f"DEBUG: Fuzzy match in element [{i}]: '{ocr_data['text'][i].strip()}' (chars: {matching_chars}/{len(target_chars)})")
                
                # If still no matches and phrase found in combined results, try spatial approach
                if not elements_to_redact and phrase_found_in_combined:
                    if debug:
                        print("DEBUG: Phrase found in combined OCR but not in individual elements, using spatial approach...")
                    
                    # Look for text elements in the top area of the image where usernames typically appear
                    image_height = image.height
                    top_area_threshold = image_height * 0.15  # Top 15% of image
                    
                    for i in valid_indices:
                        y = ocr_data['top'][i]
                        if y <= top_area_threshold:
                            # This is in the top area, include it for redaction
                            elements_to_redact.add(i)
                            if debug:
                                print(f"DEBUG: Including top-area element [{i}]: '{ocr_data['text'][i].strip()}' at y={y}")
                
                # If still no matches, try to find any text that contains partial matches of the target phrase
                if not elements_to_redact:
                    if debug:
                        print("DEBUG: Trying partial substring matching...")
                    
                    # Try to find elements that contain substrings of the target phrase
                    target_parts = [target_phrase[i:i+4] for i in range(len(target_phrase)-3)]  # 4-char substrings
                    for part in target_parts:
                        part_lower = part.lower()
                        for i in valid_indices:
                            text = ocr_data['text'][i].strip().lower()
                            if part_lower in text:
                                elements_to_redact.add(i)
                                if debug:
                                    print(f"DEBUG: Partial match '{part}' in element [{i}]: '{ocr_data['text'][i].strip()}'")
            elif debug and target_phrase:
                print(f"DEBUG: Phrase found via direct coordinates, skipping fallback approaches")
            
            # Check for auto-redact patterns
            if auto_redact:
                for i in valid_indices:
                    text = ocr_data['text'][i].strip()
                    if self.is_sensitive_text(text):
                        elements_to_redact.add(i)
            
            # Redact marked elements
            for i in elements_to_redact:
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
            
            # Redact direct coordinate areas
            for x, y, w, h in direct_redaction_areas:
                # Add padding to ensure complete coverage
                padding = 2
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = w + (padding * 2)
                h = h + (padding * 2)
                
                # Draw black rectangle to redact text
                draw.rectangle([(x, y), (x + w, y + h)], fill="black")
                redactions_made += 1
                if debug:
                    print(f"DEBUG: Applied direct redaction at ({x},{y},{w},{h})")
            
            # Save redacted image
            image.save(output_path)
            
            if redactions_made > 0:
                print(f"Redacted {redactions_made} items in: {os.path.basename(image_path)} → {output_path}")
                if target_phrase:
                    print(f"  Target phrase: '{target_phrase}'")
                    if elements_to_redact:
                        print(f"  Element-based redactions: {len(elements_to_redact)}")
                    if direct_redaction_areas:
                        print(f"  Direct coordinate redactions: {len(direct_redaction_areas)}")
            else:
                print(f"No redactions needed: {os.path.basename(image_path)} → {output_path}")
                if target_phrase:
                    print(f"  Phrase '{target_phrase}' not found")
            
            return redactions_made
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return 0
    
    def redact_directory(self, input_dir: str, output_dir: str, target_phrase: str = None, auto_redact: bool = False, debug: bool = False) -> None:
        """
        Redact all images in a directory.
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save redacted images
            target_phrase: Specific phrase to redact (if provided)
            auto_redact: Whether to automatically redact sensitive data
            debug: Print debug information about OCR detection
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
                
                redactions = self.redact_text_in_image(input_path, output_path, target_phrase, auto_redact, debug)
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
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output showing OCR detection details'
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
        auto_redact=args.auto_redact,
        debug=args.debug
    )
    
    # Create redaction report
    redactor.create_redaction_report(args.output_dir)
    
    print("=" * 60)
    print("Image redaction complete!")


if __name__ == "__main__":
    main()
