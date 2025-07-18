#!/usr/bin/env python3
"""
TLT Guild Data Redaction Script

This script redacts PII (Personally Identifiable Information) from TLT guild data
by replacing Discord IDs, UUIDs, and other sensitive identifiers with placeholder
values suitable for documentation and public sharing.

Usage:
    # Redact guild data directory
    python guild_data_redact.py <input_dir> <output_dir>
    
    # Redact GUILD_DATA.md file
    python guild_data_redact.py --guild-data-md [input_file] [output_file]

Examples:
    python guild_data_redact.py ./guild_data ./guild_data_redacted
    python guild_data_redact.py --guild-data-md GUILD_DATA.md GUILD_DATA_REDACTED.md
    python guild_data_redact.py --guild-data-md  # Uses default GUILD_DATA.md -> GUILD_DATA_REDACTED.md
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Set
import uuid


class GuildDataRedactor:
    """Redacts PII from TLT guild data structures."""
    
    def __init__(self):
        # Discord snowflake pattern: 17-19 digit numbers
        self.discord_id_pattern = re.compile(r'\b\d{17,19}\b')
        
        # UUID pattern: 8-4-4-4-12 hex characters
        self.uuid_pattern = re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', re.IGNORECASE)
        
        # File timestamp pattern: YYYYMMDD_HHMMSS
        self.timestamp_pattern = re.compile(r'\b\d{8}_\d{6}\b')
        
        # Discord token pattern: MTxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx
        self.discord_token_pattern = re.compile(r'\bMT[A-Za-z0-9]{24}\.[A-Za-z0-9]{6}\.[A-Za-z0-9-_]{27,39}\b')
        
        # OpenAI API key pattern: sk-proj-xxxxxxxxx or sk-xxxxxxxxx
        self.openai_key_pattern = re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9]{20,}\b')
        
        # Mapping of original IDs to placeholder names
        self.id_mappings: Dict[str, str] = {}
        self.id_counter = 1
    
    def get_placeholder_id(self, original_id: str, id_type: str) -> str:
        """Get or create a placeholder for an ID."""
        if original_id in self.id_mappings:
            return self.id_mappings[original_id]
        
        # Create placeholder based on type
        if id_type == 'discord':
            placeholder = f"{{guild_id}}" if self.id_counter == 1 else f"{{discord_id_{self.id_counter}}}"
        elif id_type == 'uuid':
            placeholder = f"{{uuid_{self.id_counter}}}"
        elif id_type == 'timestamp':
            placeholder = f"{{timestamp_{self.id_counter}}}"
        else:
            placeholder = f"{{{id_type}_{self.id_counter}}}"
        
        self.id_mappings[original_id] = placeholder
        self.id_counter += 1
        return placeholder
    
    def redact_discord_token(self, content: str) -> str:
        """Redact Discord tokens."""
        return self.discord_token_pattern.sub('{DISCORD_TOKEN}', content)
    
    def redact_openai_key(self, content: str) -> str:
        """Redact OpenAI API keys."""
        return self.openai_key_pattern.sub('{OPENAI_API_KEY}', content)
    
    def redact_discord_ids(self, content: str) -> str:
        """Redact Discord snowflake IDs."""
        def replace_id(match):
            original_id = match.group(0)
            return self.get_placeholder_id(original_id, 'discord')
        
        return self.discord_id_pattern.sub(replace_id, content)
    
    def redact_uuids(self, content: str) -> str:
        """Redact UUIDs."""
        def replace_uuid(match):
            original_uuid = match.group(0)
            return self.get_placeholder_id(original_uuid, 'uuid')
        
        return self.uuid_pattern.sub(replace_uuid, content)
    
    def redact_timestamps(self, content: str) -> str:
        """Redact file timestamps."""
        def replace_timestamp(match):
            original_timestamp = match.group(0)
            return self.get_placeholder_id(original_timestamp, 'timestamp')
        
        return self.timestamp_pattern.sub(replace_timestamp, content)
    
    def redact_content(self, content: str) -> str:
        """Apply all redactions to content."""
        # Apply redactions in order
        content = self.redact_discord_token(content)
        content = self.redact_openai_key(content)
        content = self.redact_discord_ids(content)
        content = self.redact_uuids(content)
        content = self.redact_timestamps(content)
        return content
    
    def redact_json_file(self, input_path: Path, output_path: Path) -> None:
        """Redact a JSON file."""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply redactions
            redacted_content = self.redact_content(content)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write redacted content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(redacted_content)
            
            print(f"Redacted: {input_path} -> {output_path}")
            
        except Exception as e:
            print(f"Error redacting {input_path}: {e}")
    
    def redact_text_file(self, input_path: Path, output_path: Path) -> None:
        """Redact a text file."""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply redactions
            redacted_content = self.redact_content(content)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write redacted content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(redacted_content)
            
            print(f"Redacted: {input_path} -> {output_path}")
            
        except Exception as e:
            print(f"Error redacting {input_path}: {e}")
    
    def copy_binary_file(self, input_path: Path, output_path: Path) -> None:
        """Copy binary files without redaction."""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(input_path, output_path)
            print(f"Copied: {input_path} -> {output_path}")
            
        except Exception as e:
            print(f"Error copying {input_path}: {e}")
    
    def redact_directory_structure(self, input_dir: Path, output_dir: Path) -> None:
        """Redact directory structure by renaming paths with IDs."""
        for item in input_dir.rglob('*'):
            # Calculate relative path from input directory
            relative_path = item.relative_to(input_dir)
            
            # Redact the path components
            redacted_path_str = str(relative_path)
            redacted_path_str = self.redact_content(redacted_path_str)
            
            # Create output path
            output_path = output_dir / redacted_path_str
            
            if item.is_file():
                # Process files based on extension
                if item.suffix.lower() in ['.json']:
                    self.redact_json_file(item, output_path)
                elif item.suffix.lower() in ['.txt', '.md', '.py', '.sh', '.conf', '.log', '.env']:
                    self.redact_text_file(item, output_path)
                elif item.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    # Copy image files as-is (no text content to redact)
                    self.copy_binary_file(item, output_path)
                else:
                    # Copy other files as-is
                    self.copy_binary_file(item, output_path)
            elif item.is_dir():
                # Create directory structure
                output_path.mkdir(parents=True, exist_ok=True)
    
    def create_redaction_report(self, output_dir: Path) -> None:
        """Create a report of redactions performed."""
        report_path = output_dir / 'REDACTION_REPORT.md'
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# TLT Guild Data Redaction Report\n\n")
                f.write("This directory contains redacted guild data with PII removed.\n\n")
                f.write("## Redactions Applied\n\n")
                f.write("### ID Mappings\n")
                f.write("| Original ID | Placeholder | Type |\n")
                f.write("|-------------|-------------|------|\n")
                
                for original_id, placeholder in self.id_mappings.items():
                    id_type = "Unknown"
                    if re.match(r'\d{17,19}', original_id):
                        id_type = "Discord ID"
                    elif re.match(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', original_id, re.IGNORECASE):
                        id_type = "UUID"
                    elif re.match(r'\d{8}_\d{6}', original_id):
                        id_type = "Timestamp"
                    
                    f.write(f"| `{original_id}` | `{placeholder}` | {id_type} |\n")
                
                f.write("\n### Security Redactions\n")
                f.write("- Discord tokens replaced with `{DISCORD_TOKEN}`\n")
                f.write("- OpenAI API keys replaced with `{OPENAI_API_KEY}`\n")
                f.write("- Discord snowflake IDs replaced with `{guild_id}`, `{discord_id_N}`, etc.\n")
                f.write("- UUIDs replaced with `{uuid_N}`\n")
                f.write("- File timestamps replaced with `{timestamp_N}`\n")
                f.write("\n### Files Processed\n")
                f.write("- JSON files: Content redacted\n")
                f.write("- Text files: Content redacted\n")
                f.write("- Image files: Copied as-is\n")
                f.write("- Directory structure: Path components redacted\n")
                f.write("\n---\n")
                f.write("Generated by TLT Guild Data Redaction Script\n")
            
            print(f"Redaction report created: {report_path}")
            
        except Exception as e:
            print(f"Error creating redaction report: {e}")
    
    def redact_guild_data_md(self, input_file: Path, output_file: Path) -> None:
        """Redact GUILD_DATA.md file specifically."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"Processing {input_file}...")
            
            # Apply redactions
            redacted_content = self.redact_content(content)
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write redacted content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(redacted_content)
            
            print(f"Redacted documentation: {input_file} -> {output_file}")
            
            # Create a simple redaction summary
            summary_path = output_file.parent / f"{output_file.stem}_REDACTION_SUMMARY.md"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("# GUILD_DATA.md Redaction Summary\n\n")
                f.write(f"Original file: `{input_file}`\n")
                f.write(f"Redacted file: `{output_file}`\n\n")
                f.write("## Redactions Applied\n\n")
                f.write("### ID Mappings\n")
                f.write("| Original ID | Placeholder | Type |\n")
                f.write("|-------------|-------------|------|\n")
                
                for original_id, placeholder in self.id_mappings.items():
                    id_type = "Unknown"
                    if re.match(r'\d{17,19}', original_id):
                        id_type = "Discord ID"
                    elif re.match(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', original_id, re.IGNORECASE):
                        id_type = "UUID"
                    elif re.match(r'\d{8}_\d{6}', original_id):
                        id_type = "Timestamp"
                    
                    f.write(f"| `{original_id}` | `{placeholder}` | {id_type} |\n")
                
                f.write("\n### Security Redactions\n")
                f.write("- Discord tokens replaced with `{DISCORD_TOKEN}`\n")
                f.write("- OpenAI API keys replaced with `{OPENAI_API_KEY}`\n")
                f.write("- Discord snowflake IDs replaced with `{guild_id}`, `{discord_id_N}`, etc.\n")
                f.write("- UUIDs replaced with `{uuid_N}`\n")
                f.write("- File timestamps replaced with `{timestamp_N}`\n")
                f.write("\n---\n")
                f.write("Generated by TLT Guild Data Redaction Script\n")
            
            print(f"Redaction summary created: {summary_path}")
            
        except Exception as e:
            print(f"Error redacting {input_file}: {e}")
            raise


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Redact PII from TLT guild data directories and documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Redact guild data directory
    python guild_data_redact.py ./guild_data ./guild_data_redacted
    python guild_data_redact.py /path/to/guild_data /path/to/redacted_output
    
    # Redact GUILD_DATA.md file
    python guild_data_redact.py --guild-data-md GUILD_DATA.md GUILD_DATA_REDACTED.md
    python guild_data_redact.py --guild-data-md  # Uses defaults
        """
    )
    
    parser.add_argument(
        '--guild-data-md',
        action='store_true',
        help='Redact GUILD_DATA.md file instead of directory structure'
    )
    
    parser.add_argument(
        'input_path',
        nargs='?',
        help='Input directory or file to redact (optional for --guild-data-md)'
    )
    
    parser.add_argument(
        'output_path',
        nargs='?',
        help='Output directory or file for redacted content (optional for --guild-data-md)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Initialize redactor
    redactor = GuildDataRedactor()
    
    if args.guild_data_md:
        # Handle GUILD_DATA.md redaction mode
        if args.input_path:
            input_file = Path(args.input_path)
        else:
            input_file = Path('GUILD_DATA.md')
        
        if args.output_path:
            output_file = Path(args.output_path)
        else:
            output_file = Path('GUILD_DATA_REDACTED.md')
        
        # Validate input file
        if not input_file.exists():
            print(f"Error: Input file does not exist: {input_file}")
            sys.exit(1)
        
        if not input_file.is_file():
            print(f"Error: Input path is not a file: {input_file}")
            sys.exit(1)
        
        # Check if output file exists
        if output_file.exists():
            response = input(f"Output file {output_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                sys.exit(1)
        
        print(f"Redacting documentation file: {input_file} -> {output_file}")
        print("=" * 60)
        
        # Perform redaction
        redactor.redact_guild_data_md(input_file, output_file)
        
        print("=" * 60)
        print(f"Documentation redaction complete!")
        print(f"Input:  {input_file}")
        print(f"Output: {output_file}")
        print(f"IDs redacted: {len(redactor.id_mappings)}")
        
    else:
        # Handle directory redaction mode (original functionality)
        if not args.input_path or not args.output_path:
            print("Error: Both input_path and output_path are required for directory redaction mode")
            parser.print_help()
            sys.exit(1)
        
        # Validate input directory
        input_dir = Path(args.input_path)
        if not input_dir.exists():
            print(f"Error: Input directory does not exist: {input_dir}")
            sys.exit(1)
        
        if not input_dir.is_dir():
            print(f"Error: Input path is not a directory: {input_dir}")
            sys.exit(1)
        
        # Validate output directory
        output_dir = Path(args.output_path)
        if output_dir.exists():
            response = input(f"Output directory {output_dir} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                sys.exit(1)
            shutil.rmtree(output_dir)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Redacting guild data from {input_dir} to {output_dir}")
        print("=" * 60)
        
        # Perform redaction
        redactor.redact_directory_structure(input_dir, output_dir)
        
        # Create redaction report
        redactor.create_redaction_report(output_dir)
        
        print("=" * 60)
        print(f"Redaction complete!")
        print(f"Input:  {input_dir}")
        print(f"Output: {output_dir}")
        print(f"IDs redacted: {len(redactor.id_mappings)}")


if __name__ == '__main__':
    main()