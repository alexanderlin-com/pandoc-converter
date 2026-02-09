#!/usr/bin/env python3
import sys
import yaml
import subprocess
import re
import os
from pathlib import Path

# ============================================================
# OUTPUT DIRECTORY CONFIGURATION
# ============================================================
OUTPUT_DIR = Path.home() / "Dropbox" / "Pandoc"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# COMMAND-LINE ARGUMENTS
# ============================================================
if len(sys.argv) < 2:
    print("Usage: python convert.py <input_file> [format]")
    print("Example: python convert.py myfile.md pdf")
    sys.exit(1)

input_file = sys.argv[1]
output_format = sys.argv[2] if len(sys.argv) > 2 else 'docx'

# ============================================================
# READ FILE & EXTRACT YAML
# ============================================================
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if YAML frontmatter exists
if not content.startswith('---'):
    print("No YAML frontmatter found. Using default filename.")
    filename = "output"
else:
    # Extract YAML block (between first and second ---)
    yaml_block = content.split('---')[1]
    metadata = yaml.safe_load(yaml_block)

    # ============================================================
    # FILENAME LOGIC
    # ============================================================
    file_type = metadata.get('type', '')

    if file_type == 'scene':
        # Scene format: "[story] - Chapter [chapter] - [chapter_title]"
        story = metadata.get('story', 'Unknown_Story')
        chapter = metadata.get('chapter', 'X')
        chapter_title = metadata.get('chapter_title', 'Untitled')

        # Build filename
        filename = f"{story} - Chapter {chapter} - {chapter_title}"
    else:
        # Default format: just use title
        filename = metadata.get('title', 'output')

    # ============================================================
    # SANITIZE FILENAME
    # ============================================================
    # Remove invalid filename characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Strip leading/trailing whitespace
    filename = filename.strip()

# Build full output path
output_file = OUTPUT_DIR / f"{filename}.{output_format}"

# ============================================================
# RUN PANDOC
# ============================================================
try:
    subprocess.run(['pandoc', input_file, '-o', str(output_file)], check=True)
    print(f"✓ Converted to: {output_file}")
except subprocess.CalledProcessError as e:
    print(f"✗ Pandoc conversion failed: {e}")
    sys.exit(1)
except FileNotFoundError:
    print("✗ Pandoc not found. Is it installed and in your PATH?")
    sys.exit(1)