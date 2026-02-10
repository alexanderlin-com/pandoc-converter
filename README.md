# pandoc-converter

A Python script that converts Markdown files to DOCX/PDF with dynamic filenames based on YAML frontmatter.

## What It Does

- Converts `.md` files to `.docx` or `.pdf` using pandoc
- Generates filenames automatically from YAML frontmatter
- Supports batch conversion (single file or entire folders)
- Zero external dependencies (pure Python stdlib)

## How It Works

The script reads YAML frontmatter and applies one of three naming rules:

1. **Scene files** (`type: scene`): `Story Ch001 — Chapter Title`
2. **Files with `title` field**: Uses that title
3. **Everything else**: Uses the markdown filename

All outputs default to `~/Dropbox/Pandoc/` unless specified otherwise.

## Installation

### macOS
```bash
# Make executable
chmod +x convert.py

# Symlink to PATH
sudo ln -s ~/path/to/convert.py /usr/local/bin/mdconvert
```

### Windows
Create `mdconvert.bat`:
```bat
@echo off
python "C:\path\to\convert.py" %*
```
Add the folder to your system PATH.

## Usage
```bash
# Convert single file
mdconvert myfile.md docx

# Convert all .md files in current directory
mdconvert

# Convert specific folder
mdconvert ~/Documents/MyNotes pdf

# Custom output directory
mdconvert ~/Documents/MyNotes pdf ~/Desktop
```

## YAML Assumptions

This script is built for my personal writing workflow and assumes the following YAML structure:

### For story scenes:
```yaml
---
story: "Story Title"
type: scene
chapter: 1
chapter_title: "Chapter Name"
---
```

### For other documents:
```yaml
---
title: "Document Title"
type: "Journal"
---
```

**Note:** The script strips Obsidian wiki-links (`[[...]]`) and Templater syntax (`<% %>`) automatically.

You can (and should) customize the filename logic in the script to match your own YAML structure.

## Requirements

- Python 3.6+
- [pandoc](https://pandoc.org/installing.html) installed and in PATH

## License

Do whatever you want with it. It's a script.
