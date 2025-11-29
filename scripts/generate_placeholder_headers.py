#!/usr/bin/env python3
"""
Generate placeholder header images for blog posts using SVG.
This creates visually appealing placeholders without needing an API.
"""
import hashlib
import re
from pathlib import Path

# Color palettes based on category/language
PALETTES = {
    'ai': ['#10b981', '#059669', '#047857'],       # Emerald
    'web-ui': ['#3b82f6', '#2563eb', '#1d4ed8'],   # Blue
    'development': ['#8b5cf6', '#7c3aed', '#6d28d9'],  # Purple
    'devops': ['#f59e0b', '#d97706', '#b45309'],   # Amber
    'systems': ['#ef4444', '#dc2626', '#b91c1c'],  # Red
    'general': ['#6366f1', '#4f46e5', '#4338ca'],  # Indigo
    'python': ['#3776ab', '#2563eb', '#1d4ed8'],   # Python blue
    'javascript': ['#f7df1e', '#d97706', '#b45309'], # JS yellow
    'typescript': ['#3178c6', '#2563eb', '#1d4ed8'], # TS blue
    'rust': ['#ce422b', '#dc2626', '#b91c1c'],     # Rust orange
    'go': ['#00add8', '#0891b2', '#0e7490'],       # Go cyan
    'default': ['#6366f1', '#4f46e5', '#4338ca']   # Indigo
}

def get_color_for_post(title: str, category: str, language: str) -> tuple:
    """Get a color palette based on post metadata."""
    # Try language first
    lang_key = language.lower() if language else ''
    if lang_key in PALETTES:
        return PALETTES[lang_key]
    
    # Try category
    cat_key = category.lower() if category else ''
    if cat_key in PALETTES:
        return PALETTES[cat_key]
    
    # Hash the title to get consistent but varied colors
    hash_val = int(hashlib.md5(title.encode()).hexdigest()[:8], 16)
    palette_keys = list(PALETTES.keys())
    return PALETTES[palette_keys[hash_val % len(palette_keys)]]

def create_svg_header(title: str, category: str, language: str, stars: int = 0) -> str:
    """Create an SVG header image for a blog post."""
    colors = get_color_for_post(title, category, language)
    
    # Truncate title if too long
    display_title = title[:40] + "..." if len(title) > 40 else title
    
    # Get emoji based on category
    emoji_map = {
        'ai': '🤖',
        'web-ui': '🎨',
        'development': '💻',
        'devops': '🔧',
        'systems': '⚙️',
        'general': '📦',
    }
    emoji = emoji_map.get(category.lower() if category else 'general', '📦')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0A0A0A"/>
      <stop offset="100%" style="stop-color:#1a1a2e"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{colors[0]}"/>
      <stop offset="100%" style="stop-color:{colors[1]}"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>
  
  <!-- Grid pattern -->
  <g opacity="0.05">
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#ffffff" stroke-width="0.5"/>
    </pattern>
    <rect width="1200" height="630" fill="url(#grid)"/>
  </g>
  
  <!-- Accent circles -->
  <circle cx="1050" cy="150" r="250" fill="{colors[0]}" opacity="0.1"/>
  <circle cx="150" cy="480" r="200" fill="{colors[1]}" opacity="0.08"/>
  
  <!-- Decorative lines -->
  <line x1="80" y1="400" x2="400" y2="400" stroke="url(#accent)" stroke-width="4" opacity="0.6"/>
  
  <!-- Category badge -->
  <rect x="80" y="100" width="180" height="40" rx="20" fill="{colors[0]}" opacity="0.2"/>
  <text x="170" y="127" font-family="system-ui, sans-serif" font-size="16" fill="{colors[0]}" text-anchor="middle" font-weight="bold">{category.upper() if category else 'OPEN SOURCE'}</text>
  
  <!-- Main content area -->
  <text x="80" y="250" font-family="system-ui, -apple-system, sans-serif" font-size="64" font-weight="bold" fill="#F5F5DC" filter="url(#glow)">
    {emoji}
  </text>
  
  <!-- Language badge -->
  {f'<rect x="80" y="450" width="120" height="35" rx="17" fill="{colors[1]}" opacity="0.3"/><text x="140" y="474" font-family="monospace" font-size="14" fill="{colors[0]}" text-anchor="middle" font-weight="bold">{language.upper()}</text>' if language else ''}
  
  <!-- Stars -->
  {f'<text x="1120" y="580" font-family="system-ui, sans-serif" font-size="20" fill="#F5F5DC" opacity="0.6" text-anchor="end">⭐ {stars:,}</text>' if stars else ''}
  
  <!-- BestOf branding -->
  <text x="80" y="580" font-family="monospace" font-size="16" fill="#F5F5DC" opacity="0.4">
    BestOf OpenSource
  </text>
</svg>'''
    
    return svg

def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown."""
    if not content.startswith('---'):
        return {}
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    data = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip().strip('"\'')
    
    return data

def generate_placeholders():
    """Generate SVG placeholders for all blog posts missing headers."""
    blog_dir = Path("website/src/content/blog")
    generated = 0
    
    for md_file in blog_dir.rglob("index.md"):
        header_path = md_file.parent / "header.png"
        header_svg = md_file.parent / "header.svg"
        
        # Skip if already has an image
        if header_path.exists() or header_svg.exists():
            continue
        
        # Parse frontmatter
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        meta = parse_frontmatter(content)
        title = meta.get('title', md_file.parent.name)
        category = meta.get('category', meta.get('categories', 'General'))
        if category.startswith('['):
            category = category.strip('[]"\' ').split(',')[0]
        language = meta.get('language', '')
        stars = int(meta.get('stars', 0)) if meta.get('stars', '').isdigit() else 0
        
        # Generate SVG
        svg_content = create_svg_header(title, category, language, stars)
        
        # Save as SVG
        with open(header_svg, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        # Update frontmatter
        if 'images:' not in content:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                new_frontmatter = parts[1].rstrip() + '\nimages:\n  screenshot: "./header.svg"\n'
                content = '---' + new_frontmatter + '---' + parts[2]
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        print(f"✅ Generated: {md_file.parent.name}")
        generated += 1
    
    print(f"\n🎉 Generated {generated} placeholder headers")

if __name__ == "__main__":
    generate_placeholders()
