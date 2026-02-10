#!/usr/bin/env python3
import sys
import subprocess
import re
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
    print("Usage: python convert.py <input_file> [format] [output_dir]")
    print("Example: python convert.py myfile.md pdf")
    sys.exit(1)

input_file = sys.argv[1]
output_format = sys.argv[2] if len(sys.argv) > 2 else 'docx'

# Allow custom output directory as third argument
if len(sys.argv) > 3:
    OUTPUT_DIR = Path(sys.argv[3])

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# READ FILE & EXTRACT YAML (NO DEPENDENCIES)
# ============================================================
def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter without external libraries."""
    if not content.startswith('---'):
        return {}
    
    # Find the closing ---
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    yaml_block = parts[1].strip()
    metadata = {}
    
    # Parse line by line
    for line in yaml_block.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            # Remove Obsidian wiki-links [[ ]]
            value = re.sub(r'\[\[.*?\]\]', '', value).strip()
            
            # Remove templater syntax <% %>
            value = re.sub(r'<%.*?%>', '', value).strip()
            
            if value:  # Only add non-empty values
                metadata[key] = value
    
    return metadata

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

metadata = parse_yaml_frontmatter(content)

# ============================================================
# FILENAME LOGIC
# ============================================================
file_type = metadata.get('type', '')

if file_type == 'scene':
    # Scene format: "story Chxxx — chapter_title"
    story = metadata.get('story', 'Unknown_Story')
    chapter = metadata.get('chapter', 'X')
    chapter_title = metadata.get('chapter_title', 'Untitled')
    
    # Zero-pad chapter to 3 digits for proper sorting
    if chapter != 'X':
        try:
            chapter = str(int(chapter)).zfill(3)
        except (ValueError, TypeError):
            chapter = 'XXX'  # Fallback if chapter isn't a number
    
    filename = f"{story} Ch{chapter} — {chapter_title}"
else:
    # Default format: use title if available
    title = metadata.get('title', '').strip()
    
    if title:
        filename = title
    else:
        # Fallback: use the input file's name (without extension)
        filename = Path(input_file).stem
# ============================================================
# SANITIZE FILENAME
# ============================================================
# Remove invalid filename characters (including colon for Windows)
filename = re.sub(r'[<>:"/\\|?*]', '', filename)
# Keep spaces (do NOT replace with underscores)
# Strip leading/trailing whitespace
filename = filename.strip()

# Fallback if filename is empty
if not filename or filename == '_':
    filename = 'output'

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
