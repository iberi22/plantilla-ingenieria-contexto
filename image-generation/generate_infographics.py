#!/usr/bin/env python3
"""
Professional Infographic Generator for Blog Posts
Generates 4K infographic images that visually explain repositories
without needing to read the article.

Uses Gemini Imagen 4 with detailed prompts for professional results.
"""

import os
import sys
import time
import logging
import re
import yaml
from pathlib import Path
from typing import Dict, Optional, List

from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# API KEY MANAGEMENT
# =============================================================================

API_KEYS: List[str] = []
CURRENT_KEY_INDEX = 0
CLIENT: genai.Client = None


def setup_gemini() -> bool:
    """Initialize Gemini with all available API keys."""
    global API_KEYS, CLIENT
    
    keys = []
    main_key = os.environ.get("GOOGLE_API_KEY")
    if main_key:
        keys.append(main_key)
    
    for i in range(2, 6):
        key = os.environ.get(f"GOOGLE_API_KEY_{i}")
        if key:
            keys.append(key)
    
    if not keys:
        logger.error("❌ No GOOGLE_API_KEYs found. Set GOOGLE_API_KEY, GOOGLE_API_KEY_2, etc.")
        return False
    
    API_KEYS = keys
    CLIENT = genai.Client(api_key=API_KEYS[0])
    logger.info(f"✅ Loaded {len(API_KEYS)} Gemini API keys for load balancing")
    return True


def rotate_key():
    """Rotate to next available API key."""
    global CURRENT_KEY_INDEX, CLIENT
    if len(API_KEYS) <= 1:
        return
    
    CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(API_KEYS)
    CLIENT = genai.Client(api_key=API_KEYS[CURRENT_KEY_INDEX])
    logger.info(f"🔄 Rotated to API key #{CURRENT_KEY_INDEX + 1}")


# =============================================================================
# BLOG POST PARSING
# =============================================================================

def parse_blog_post(md_file: Path) -> Optional[Dict]:
    """Extract all metadata and content from a blog post."""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        # Parse YAML frontmatter
        try:
            frontmatter = yaml.safe_load(parts[1])
        except:
            frontmatter = {}
        
        body = parts[2]
        
        # Extract sections from body
        sections = extract_sections(body)
        
        return {
            'title': frontmatter.get('title', ''),
            'description': frontmatter.get('description', ''),
            'repo': frontmatter.get('repo', ''),
            'language': frontmatter.get('language', 'Unknown'),
            'stars': frontmatter.get('stars', 0),
            'tags': frontmatter.get('tags', []),
            'category': frontmatter.get('category', 'General'),
            'repo_data': frontmatter.get('repo_data', {}),
            'insights': frontmatter.get('insights', {}),
            'sections': sections,
            'file_path': md_file
        }
    except Exception as e:
        logger.error(f"Error parsing {md_file}: {e}")
        return None


def extract_sections(body: str) -> Dict[str, str]:
    """Extract markdown sections from body."""
    sections = {
        'problem': '',
        'solution': '',
        'advantages': '',
        'considerations': '',
        'verdict': ''
    }
    
    # Extract problem section
    problem_match = re.search(r'##.*Problem.*?\n(.*?)(?=##|\Z)', body, re.DOTALL | re.IGNORECASE)
    if problem_match:
        sections['problem'] = clean_text(problem_match.group(1))
    
    # Extract solution section
    solution_match = re.search(r'##.*Solution.*?\n(.*?)(?=##|\Z)', body, re.DOTALL | re.IGNORECASE)
    if solution_match:
        sections['solution'] = clean_text(solution_match.group(1))
    
    # Extract advantages
    advantages_match = re.search(r'##.*Advantages.*?\n(.*?)(?=##|\Z)', body, re.DOTALL | re.IGNORECASE)
    if advantages_match:
        sections['advantages'] = clean_text(advantages_match.group(1))
    
    # Extract considerations/limitations
    considerations_match = re.search(r'##.*Considerations.*?\n(.*?)(?=##|\Z)', body, re.DOTALL | re.IGNORECASE)
    if considerations_match:
        sections['considerations'] = clean_text(considerations_match.group(1))
    
    # Extract verdict
    verdict_match = re.search(r'##.*Verdict.*?\n(.*?)(?=##|\Z)', body, re.DOTALL | re.IGNORECASE)
    if verdict_match:
        sections['verdict'] = clean_text(verdict_match.group(1))
    
    return sections


def clean_text(text: str) -> str:
    """Clean markdown text for prompt use."""
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Code
    text = re.sub(r'- ', '', text)  # List items
    text = re.sub(r'\n+', ' ', text)  # Newlines
    return text.strip()[:500]  # Limit length


# =============================================================================
# INFOGRAPHIC PROMPT GENERATION
# =============================================================================

def get_language_visual_theme(language: str) -> Dict[str, str]:
    """Get visual theme based on programming language."""
    themes = {
        'Python': {
            'colors': 'blue and yellow gradient, snake-like flowing elements',
            'style': 'clean, scientific, data-visualization focused',
            'icons': 'code brackets, data charts, neural network nodes'
        },
        'JavaScript': {
            'colors': 'yellow and black accents, electric energy',
            'style': 'dynamic, modern web aesthetic, interactive feel',
            'icons': 'browser windows, DOM trees, event bubbles'
        },
        'TypeScript': {
            'colors': 'blue professional gradient, structured geometric',
            'style': 'enterprise, type-safe, architectural',
            'icons': 'type definitions, interfaces, modular blocks'
        },
        'Rust': {
            'colors': 'orange and dark gray, metallic textures',
            'style': 'industrial, robust, memory-safe visualization',
            'icons': 'gears, locks, performance meters'
        },
        'Go': {
            'colors': 'cyan and white, minimalist',
            'style': 'simple, concurrent, efficient',
            'icons': 'goroutines as parallel streams, simple shapes'
        },
        'Java': {
            'colors': 'red and blue corporate, coffee brown accents',
            'style': 'enterprise, object-oriented hierarchy',
            'icons': 'coffee cups, class diagrams, JVM layers'
        },
        'C#': {
            'colors': 'purple and white, Windows aesthetic',
            'style': 'professional, .NET framework feel',
            'icons': 'windows, frameworks, enterprise patterns'
        },
        'Ruby': {
            'colors': 'red gem tones, elegant',
            'style': 'elegant, developer happiness, Rails-inspired',
            'icons': 'gems, rails tracks, MVC diagrams'
        },
        'PHP': {
            'colors': 'purple and blue, web server feel',
            'style': 'web-focused, server-side',
            'icons': 'servers, databases, web requests'
        },
        'Swift': {
            'colors': 'orange gradient, Apple aesthetic',
            'style': 'clean, iOS/macOS focused, modern',
            'icons': 'Apple devices, SwiftUI components'
        },
        'Kotlin': {
            'colors': 'purple and orange gradient',
            'style': 'modern Android, concise',
            'icons': 'Android devices, null-safety shields'
        }
    }
    
    return themes.get(language, {
        'colors': 'blue and purple tech gradient',
        'style': 'modern tech, professional',
        'icons': 'code symbols, tech elements, digital patterns'
    })


def get_category_visual_elements(category: str) -> str:
    """Get visual elements based on category."""
    elements = {
        'AI': 'neural network visualizations, brain imagery, data flowing through nodes, machine learning pipelines',
        'Web/UI': 'browser frames, responsive layouts, UI components, color palettes, design systems',
        'Development': 'code editors, git branches, CI/CD pipelines, terminal windows, debugging tools',
        'Systems': 'server racks, network topology, containers, infrastructure diagrams, monitoring dashboards',
        'General': 'workflow diagrams, process flows, integration arrows, ecosystem visualization'
    }
    return elements.get(category, elements['General'])


def create_infographic_prompt(data: Dict) -> str:
    """
    Create a detailed prompt for 4K professional infographic.
    The infographic should explain the repository visually without reading.
    """
    
    title = data.get('title', 'Project')
    description = data.get('description', '')
    language = data.get('language', 'Unknown')
    stars = data.get('stars', 0)
    category = data.get('category', 'General')
    tags = data.get('tags', [])
    sections = data.get('sections', {})
    
    # Get visual themes
    lang_theme = get_language_visual_theme(language)
    category_elements = get_category_visual_elements(category)
    
    # Build features list from advantages
    features = sections.get('advantages', description)[:300]
    solution = sections.get('solution', description)[:300]
    
    # Determine star tier visualization
    if stars > 1000:
        popularity = "highly popular (1000+ stars)"
    elif stars > 500:
        popularity = "growing popularity (500+ stars)"
    elif stars > 100:
        popularity = "emerging project (100+ stars)"
    else:
        popularity = "hidden gem discovery"
    
    prompt = f"""Create a professional 4K infographic (3840x2160) that visually explains the open-source project "{title}" without any text.

PROJECT OVERVIEW:
- Purpose: {description}
- Language: {language}
- Category: {category}
- Status: {popularity}

VISUAL STORYTELLING (show these concepts graphically):
1. MAIN CONCEPT (center): {solution}
2. KEY FEATURES (surrounding elements): {features}
3. TECHNOLOGY STACK: Visualize {language} with {lang_theme['icons']}

DESIGN SPECIFICATIONS:
- Color Palette: {lang_theme['colors']}
- Visual Style: {lang_theme['style']}
- Category Elements: {category_elements}

LAYOUT STRUCTURE:
- Central hero element showing the main functionality as a 3D isometric visualization
- Surrounding satellite elements showing key features as interconnected modules
- Flow arrows showing data/process flow
- Tech stack icons integrated naturally
- Subtle grid background suggesting technical precision

ARTISTIC DIRECTION:
- Ultra-high quality 4K rendering
- Photorealistic 3D elements with soft shadows
- Glass morphism and depth effects
- Professional tech company presentation style
- Clean composition with visual hierarchy
- Subtle glow effects on interactive elements
- Depth of field for focus on main elements

IMPORTANT:
- NO TEXT, NO LETTERS, NO NUMBERS, NO LABELS
- The infographic must be self-explanatory through visuals alone
- Each feature should be represented by a distinct 3D icon or visualization
- Use visual metaphors to explain technical concepts
- Professional enough for tech conference presentation
- Modern 2024 design trends (glassmorphism, 3D, gradients)

Tags for context: {', '.join(tags[:5]) if tags else 'open-source, developer-tools'}"""

    return prompt


# =============================================================================
# IMAGE GENERATION
# =============================================================================

def generate_infographic(prompt: str, output_path: Path, retries: int = 3) -> bool:
    """Generate infographic image using Gemini Imagen 4."""
    global CLIENT
    
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"🎨 Generating infographic (attempt {attempt}/{retries})...")
            logger.debug(f"Prompt: {prompt[:200]}...")
            
            response = CLIENT.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",
                    safety_filter_level="BLOCK_ONLY_HIGH",
                    person_generation="DONT_ALLOW"
                )
            )
            
            if response.generated_images:
                image = response.generated_images[0]
                output_path.parent.mkdir(parents=True, exist_ok=True)
                # Save the image data
                image.image.save(str(output_path))
                logger.info(f"✅ Infographic saved: {output_path}")
                rotate_key()
                return True
            else:
                logger.warning(f"⚠️ No images in response (attempt {attempt})")
                rotate_key()
                
        except Exception as e:
            logger.error(f"❌ Generation error (attempt {attempt}): {e}")
            rotate_key()
            if attempt < retries:
                time.sleep(2 ** attempt)
    
    return False


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_blog_infographics(
    blog_dir: Path = None,
    output_dir: Path = None,
    limit: int = None,
    force: bool = False
):
    """
    Process all blog posts and generate infographics.
    
    Args:
        blog_dir: Path to blog content directory
        output_dir: Where to save generated images (default: same as blog post)
        limit: Maximum images to generate
        force: Regenerate even if image exists
    """
    
    if not setup_gemini():
        return
    
    if blog_dir is None:
        blog_dir = Path("website/src/content/blog")
    else:
        blog_dir = Path(blog_dir)
    
    if not blog_dir.exists():
        logger.error(f"❌ Blog directory not found: {blog_dir}")
        return
    
    generated = 0
    skipped = 0
    failed = 0
    
    logger.info(f"📁 Scanning blog posts in: {blog_dir}")
    
    for md_file in sorted(blog_dir.rglob("index.md")):
        if limit and generated >= limit:
            logger.info(f"🛑 Reached limit of {limit} images")
            break
        
        # Determine output path
        if output_dir:
            relative = md_file.parent.relative_to(blog_dir)
            image_path = Path(output_dir) / relative / "header.png"
        else:
            image_path = md_file.parent / "header.png"
        
        # Skip if exists (unless force)
        if image_path.exists() and not force:
            logger.info(f"⏭️ Skipping (exists): {md_file.parent.name}")
            skipped += 1
            continue
        
        # Parse blog post
        data = parse_blog_post(md_file)
        if not data:
            logger.warning(f"⚠️ Could not parse: {md_file}")
            failed += 1
            continue
        
        if not data['title']:
            logger.warning(f"⚠️ No title in: {md_file}")
            failed += 1
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 Processing: {data['title']}")
        logger.info(f"   Repo: {data['repo']}")
        logger.info(f"   Language: {data['language']}")
        logger.info(f"   Category: {data['category']}")
        logger.info(f"   Stars: {data['stars']}")
        
        # Generate prompt
        prompt = create_infographic_prompt(data)
        
        # Generate image
        if generate_infographic(prompt, image_path):
            generated += 1
            logger.info(f"✅ Generated {generated} infographics")
            # Rate limiting
            time.sleep(5)
        else:
            failed += 1
            logger.error(f"❌ Failed to generate for: {data['title']}")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 INFOGRAPHIC GENERATION COMPLETE")
    logger.info(f"   ✅ Generated: {generated}")
    logger.info(f"   ⏭️ Skipped: {skipped}")
    logger.info(f"   ❌ Failed: {failed}")
    logger.info(f"{'='*60}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate professional 4K infographics for blog posts'
    )
    parser.add_argument(
        '--blog-dir', 
        type=str, 
        default='website/src/content/blog',
        help='Path to blog content directory'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (default: same as blog posts)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of infographics to generate'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate even if image exists'
    )
    
    args = parser.parse_args()
    
    process_blog_infographics(
        blog_dir=Path(args.blog_dir) if args.blog_dir else None,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        limit=args.limit,
        force=args.force
    )


if __name__ == "__main__":
    main()
