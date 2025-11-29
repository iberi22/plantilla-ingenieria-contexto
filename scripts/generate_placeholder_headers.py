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
    """Create a professional SVG header image for a blog post with 3D-style graphics."""
    colors = get_color_for_post(title, category, language)

    # Truncate title if too long
    display_title = title[:35] + "..." if len(title) > 35 else title

    # Get icon based on category
    icon_map = {
        'ai': ('🤖', 'neural-network'),
        'web-ui': ('🎨', 'web-interface'),
        'development': ('💻', 'code-editor'),
        'devops': ('🔧', 'infrastructure'),
        'systems': ('⚙️', 'system'),
        'databases': ('🗄️', 'database'),
        'general': ('📦', 'package'),
    }
    emoji, icon_type = icon_map.get(category.lower() if category else 'general', ('📦', 'package'))

    # Language-specific secondary color
    lang_colors = {
        'python': '#3776ab',
        'javascript': '#f7df1e',
        'typescript': '#3178c6',
        'rust': '#ce422b',
        'go': '#00add8',
        'java': '#007396',
        'kotlin': '#7f52ff',
        'php': '#777bb4',
        'ruby': '#cc342d',
        'c++': '#00599c',
        'c#': '#239120',
        'shell': '#89e051',
    }
    lang_accent = lang_colors.get(language.lower() if language else '', colors[1])

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <!-- Main background gradient -->
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d0d1a"/>
      <stop offset="50%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#16213e"/>
    </linearGradient>

    <!-- Accent gradients -->
    <linearGradient id="accent1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors[0]}"/>
      <stop offset="100%" style="stop-color:{colors[1]}"/>
    </linearGradient>
    <linearGradient id="accent2" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{lang_accent}"/>
      <stop offset="100%" style="stop-color:{colors[0]}"/>
    </linearGradient>

    <!-- Glow effects -->
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="softGlow">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- 3D cube pattern -->
    <pattern id="cubePattern" width="60" height="52" patternUnits="userSpaceOnUse">
      <path d="M30 0 L60 15 L60 45 L30 52 L0 45 L0 15 Z" fill="none" stroke="{colors[0]}" stroke-width="0.5" opacity="0.15"/>
      <path d="M30 22 L30 52 M0 15 L30 22 L60 15" fill="none" stroke="{colors[0]}" stroke-width="0.5" opacity="0.1"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>

  <!-- Cube pattern overlay -->
  <rect width="1200" height="630" fill="url(#cubePattern)" opacity="0.3"/>

  <!-- Decorative floating orbs -->
  <circle cx="1000" cy="120" r="180" fill="{colors[0]}" opacity="0.08" filter="url(#softGlow)"/>
  <circle cx="1100" cy="400" r="120" fill="{lang_accent}" opacity="0.06" filter="url(#softGlow)"/>
  <circle cx="100" cy="500" r="150" fill="{colors[1]}" opacity="0.05" filter="url(#softGlow)"/>
  <circle cx="600" cy="600" r="200" fill="{colors[0]}" opacity="0.04"/>

  <!-- Isometric 3D element (right side) -->
  <g transform="translate(850, 200)" opacity="0.9">
    <!-- Back face -->
    <path d="M0 80 L100 30 L200 80 L200 180 L100 230 L0 180 Z" fill="{colors[1]}" opacity="0.3"/>
    <!-- Top face -->
    <path d="M0 80 L100 30 L200 80 L100 130 Z" fill="{colors[0]}" opacity="0.5"/>
    <!-- Front face -->
    <path d="M0 80 L100 130 L100 230 L0 180 Z" fill="{colors[0]}" opacity="0.7"/>
    <!-- Right face -->
    <path d="M100 130 L200 80 L200 180 L100 230 Z" fill="{colors[1]}" opacity="0.4"/>
    <!-- Inner glow line -->
    <path d="M100 30 L100 130 M0 80 L100 130 L200 80" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.3"/>
  </g>

  <!-- Second smaller cube -->
  <g transform="translate(750, 350) scale(0.6)" opacity="0.7">
    <path d="M0 80 L100 30 L200 80 L200 180 L100 230 L0 180 Z" fill="{lang_accent}" opacity="0.3"/>
    <path d="M0 80 L100 30 L200 80 L100 130 Z" fill="{lang_accent}" opacity="0.5"/>
    <path d="M0 80 L100 130 L100 230 L0 180 Z" fill="{lang_accent}" opacity="0.6"/>
    <path d="M100 130 L200 80 L200 180 L100 230 Z" fill="{colors[0]}" opacity="0.4"/>
  </g>

  <!-- Floating particles -->
  <circle cx="700" cy="150" r="4" fill="{colors[0]}" opacity="0.6"/>
  <circle cx="950" cy="280" r="3" fill="#ffffff" opacity="0.4"/>
  <circle cx="800" cy="500" r="5" fill="{lang_accent}" opacity="0.5"/>
  <circle cx="650" cy="400" r="3" fill="{colors[1]}" opacity="0.5"/>
  <circle cx="1100" cy="200" r="4" fill="#ffffff" opacity="0.3"/>

  <!-- Category badge with glass effect -->
  <rect x="60" y="80" width="160" height="36" rx="18" fill="{colors[0]}" opacity="0.15"/>
  <rect x="60" y="80" width="160" height="36" rx="18" fill="none" stroke="{colors[0]}" stroke-width="1" opacity="0.4"/>
  <text x="140" y="104" font-family="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" font-size="13" fill="{colors[0]}" text-anchor="middle" font-weight="600" letter-spacing="1">{category.upper() if category else 'OPEN SOURCE'}</text>

  <!-- Main emoji icon -->
  <text x="60" y="220" font-family="system-ui, sans-serif" font-size="72" filter="url(#glow)">{emoji}</text>

  <!-- Title with gradient effect -->
  <text x="60" y="310" font-family="system-ui, -apple-system, BlinkMacSystemFont, sans-serif" font-size="52" font-weight="700" fill="#ffffff" letter-spacing="-1">
    {display_title}
  </text>

  <!-- Accent line under title -->
  <rect x="60" y="330" width="300" height="4" rx="2" fill="url(#accent1)" opacity="0.8"/>

  <!-- Language badge -->
  {f'''<g transform="translate(60, 420)">
    <rect width="100" height="32" rx="16" fill="{lang_accent}" opacity="0.2"/>
    <rect width="100" height="32" rx="16" fill="none" stroke="{lang_accent}" stroke-width="1" opacity="0.5"/>
    <text x="50" y="21" font-family="ui-monospace, monospace" font-size="12" fill="{lang_accent}" text-anchor="middle" font-weight="600">{language.upper()}</text>
  </g>''' if language else ''}

  <!-- Stars badge -->
  {f'''<g transform="translate(60, 470)">
    <text font-family="system-ui, sans-serif" font-size="16" fill="#fbbf24" opacity="0.9">⭐</text>
    <text x="24" y="0" font-family="system-ui, sans-serif" font-size="14" fill="#ffffff" opacity="0.7">{stars:,}</text>
  </g>''' if stars else ''}

  <!-- Bottom branding -->
  <g transform="translate(60, 580)">
    <rect width="180" height="28" rx="14" fill="#ffffff" opacity="0.05"/>
    <text x="90" y="19" font-family="ui-monospace, monospace" font-size="11" fill="#ffffff" opacity="0.4" text-anchor="middle" letter-spacing="1">BESTOF OPENSOURCE</text>
  </g>

  <!-- Corner accent -->
  <path d="M1200 0 L1200 100 L1100 0 Z" fill="url(#accent1)" opacity="0.3"/>
  <path d="M0 630 L0 530 L100 630 Z" fill="url(#accent2)" opacity="0.2"/>
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
