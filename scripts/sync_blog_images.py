#!/usr/bin/env python3
"""
Sync header images (PNG and SVG) from blog content to public folder
and update frontmatter with correct public URLs.
"""
import os
import shutil
import re
from pathlib import Path

def sync_images():
    blog_dir = Path("website/src/content/blog")
    public_images_dir = Path("website/public/images/blog")
    public_images_dir.mkdir(parents=True, exist_ok=True)

    # Base URL for the website
    base_url = "/bestof-opensorce/images/blog"
    synced = 0

    for md_file in blog_dir.rglob("index.md"):
        slug = md_file.parent.name
        
        # Look for header images (PNG or SVG)
        src_png = md_file.parent / "header.png"
        src_svg = md_file.parent / "header.svg"
        
        src_image = None
        if src_png.exists():
            src_image = src_png
            dest_filename = f"{slug}-header.png"
        elif src_svg.exists():
            src_image = src_svg
            dest_filename = f"{slug}-header.svg"
        
        if not src_image:
            continue
            
        dest_path = public_images_dir / dest_filename
        
        # Copy file
        shutil.copy2(src_image, dest_path)
        
        # Public URL
        public_path = f"{base_url}/{dest_filename}"
        
        # Update frontmatter
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        original_content = content
        
        # Update or add screenshot field
        if 'screenshot:' in content:
            # Replace existing screenshot path
            content = re.sub(
                r'(screenshot:\s*)(["\']?)([^"\'\n]+)(["\']?)',
                f'\\1"{public_path}"',
                content
            )
        elif 'images:' in content:
            # Add screenshot to existing images section
            content = content.replace('images:\n', f'images:\n  screenshot: "{public_path}"\n')
        else:
            # Add new images section
            parts = content.split('---', 2)
            if len(parts) >= 3:
                new_frontmatter = parts[1].rstrip() + f'\nimages:\n  screenshot: "{public_path}"\n'
                content = '---' + new_frontmatter + '---' + parts[2]
        
        if content != original_content:
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(content)
        
        print(f"✅ {slug}")
        synced += 1
    
    print(f"\n🎉 Synced {synced} images to public folder")

if __name__ == "__main__":
    sync_images()
