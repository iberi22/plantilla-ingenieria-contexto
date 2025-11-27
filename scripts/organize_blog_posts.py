#!/usr/bin/env python3
"""
Organize Blog Posts into Categories
Moves existing markdown files in website/src/content/blog into subdirectories based on their content.
"""

import os
import sys
import shutil
import json
from pathlib import Path

# Add src to path to import MarkdownWriter logic
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from blog_generator.markdown_writer import MarkdownWriter

def parse_frontmatter(content):
    """Simple manual frontmatter parser."""
    if not content.startswith("---"):
        return {}

    try:
        _, fm, _ = content.split("---", 2)
        metadata = {}
        for line in fm.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                # Handle basic types
                if value.startswith("[") and value.endswith("]"):
                    try:
                        value = json.loads(value)
                    except:
                        pass
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                metadata[key] = value
        return metadata
    except Exception:
        return {}

def organize_posts():
    blog_dir = Path(__file__).parent.parent / 'website' / 'src' / 'content' / 'blog'
    writer = MarkdownWriter()

    print(f"📂 Organizing posts in {blog_dir}...")

    # Get all .md files in the root of blog_dir
    md_files = [f for f in blog_dir.glob("*.md") if f.is_file()]

    if not md_files:
        print("ℹ️ No files to organize in the root directory.")
        return

    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = parse_frontmatter(content)
            tags = metadata.get('tags', [])
            if isinstance(tags, str): # Handle if parsing failed to convert list
                tags = []

            language = metadata.get('language', 'Unknown')

            # Use MarkdownWriter's logic
            categories = writer._determine_categories(tags, language)
            primary_category = categories[0].lower().replace(" ", "-") if categories else "general"

            # Create target directory
            target_dir = blog_dir / primary_category
            target_dir.mkdir(parents=True, exist_ok=True)

            # Move file
            target_path = target_dir / file_path.name
            shutil.move(str(file_path), str(target_path))

            print(f"  ✅ Moved {file_path.name} -> {primary_category}/")

        except Exception as e:
            print(f"  ❌ Failed to process {file_path.name}: {e}")

    print("\n✨ Organization complete!")

if __name__ == "__main__":
    organize_posts()
