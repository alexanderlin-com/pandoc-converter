#!/usr/bin/env python3
import sys
import subprocess
import re
from pathlib import Path

# ============================================================
# OUTPUT DIRECTORY CONFIGURATION
# ============================================================
OUTPUT_DIR = Path.home() / "Dropbox" / "Pandoc"

# ============================================================
# YAML PARSER (NO DEPENDENCIES)
# ============================================================
def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter without external libraries."""
    if not content.startswith('---'):
        return {}
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    yaml_block = parts[1].strip()
    metadata = {}
    
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
            
            if value:
                metadata[key] = value
    
    return metadata

# ============================================================
# COMMAND-LINE ARGUMENTS
# ============================================================
if len(sys.argv) < 2:
    # No argument: convert all .md files in current directory
    input_path = Path.cwd()
    is_batch = True
else:
    input_path = Path(sys.argv[1])
    is_batch = input_path.is_dir()

output_format = sys.argv[2] if len(sys.argv) > 2 else 'docx'

# Allow custom output directory as third argument
if len(sys.argv) > 3:
    OUTPUT_DIR = Path(sys.argv[3])

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# COLLECT FILES TO CONVERT
# ============================================================
if is_batch:
    md_files = list(input_path.glob('*.md'))
    
    if not md_files:
        print(f"✗ No .md files found in {input_path}")
        sys.exit(1)
    
    print(f"Found {len(md_files)} markdown file(s) to convert...")
else:
    if not input_path.exists():
        print(f"✗ File not found: {input_path}")
        sys.exit(1)
    
    md_files = [input_path]

# ============================================================
# PROCESS EACH FILE
# ============================================================
converted_count = 0
failed_count = 0

for input_file in md_files:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata = parse_yaml_frontmatter(content)

        # ============================================================
        # FILENAME LOGIC
        # ============================================================
        file_type = metadata.get('type', '')

        if file_type == 'scene':
            story = metadata.get('story', 'Unknown_Story')
            chapter = metadata.get('chapter', 'X')
            chapter_title = metadata.get('chapter_title', 'Untitled')
            
            if chapter != 'X':
                try:
                    chapter = str(int(chapter)).zfill(3)
                except (ValueError, TypeError):
                    chapter = 'XXX'
            
            filename = f"{story} Ch{chapter} — {chapter_title}"
        else:
            title = metadata.get('title', '').strip()
            
            if title:
                filename = title
            else:
                filename = input_file.stem

        # ============================================================
        # SANITIZE FILENAME
        # ============================================================
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip()

        if not filename:
            filename = 'output'

        output_file = OUTPUT_DIR / f"{filename}.{output_format}"

        # ============================================================
        # RUN PANDOC
        # ============================================================
        subprocess.run(['pandoc', str(input_file), '-o', str(output_file)], check=True)
        print(f"✓ Converted: {input_file.name} → {output_file.name}")
        converted_count += 1

    except Exception as e:
        print(f"✗ Failed to convert {input_file.name}: {e}")
        failed_count += 1

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*60}")
print(f"Conversion complete:")
print(f"  ✓ Successful: {converted_count}")
if failed_count > 0:
    print(f"  ✗ Failed: {failed_count}")
print(f"  → Output directory: {OUTPUT_DIR}")
print(f"{'='*60}")