#!/usr/bin/env python3
"""
Script to fix existing blog posts that have header.png but missing images.screenshot in frontmatter.
"""
import os
import re
from pathlib import Path

def fix_missing_image_frontmatter():
    """Scans all blog posts and adds images.screenshot if header.png exists but frontmatter is missing."""
    blog_dir = Path("website/src/content/blog")
    fixed_count = 0
    
    for md_file in blog_dir.rglob("index.md"):
        header_image = md_file.parent / "header.png"
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if header.png exists
        has_header = header_image.exists()
        
        # Check if images.screenshot already in frontmatter
        has_screenshot_field = 'screenshot:' in content
        
        if has_header and not has_screenshot_field:
            # Add images section with screenshot
            if 'images:' in content:
                # Add screenshot to existing images section
                content = content.replace('images:\n', 'images:\n  screenshot: "./header.png"\n')
            else:
                # Add new images section before the closing ---
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    new_frontmatter = parts[1].rstrip() + '\nimages:\n  screenshot: "./header.png"\n'
                    content = '---' + new_frontmatter + '---' + parts[2]
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed: {md_file.parent.name}")
            fixed_count += 1
        
        elif not has_header:
            print(f"⚠️ Missing header.png: {md_file.parent.name}")
    
    print(f"\n🎉 Fixed {fixed_count} posts with missing image frontmatter")

if __name__ == "__main__":
    fix_missing_image_frontmatter()
