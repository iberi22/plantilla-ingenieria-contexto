#!/usr/bin/env python3
"""
Generate high-quality blog header images using Gemini Imagen API.
Uses AI to create professional infographics for blog posts.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# API KEY MANAGEMENT (with rotation for rate limits)
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

    # Load additional keys for load balancing
    for i in range(2, 6):
        key = os.environ.get(f"GOOGLE_API_KEY_{i}")
        if key:
            keys.append(key)

    if not keys:
        logger.warning("⚠️ No GOOGLE_API_KEY found. Image generation will be skipped.")
        logger.info("💡 To enable: Set GOOGLE_API_KEY environment variable")
        return False

    API_KEYS = keys
    CLIENT = genai.Client(api_key=API_KEYS[0])
    logger.info(f"✅ Loaded {len(API_KEYS)} Gemini API key(s) for image generation")
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
# IMAGE GENERATION
# =============================================================================

def generate_image(prompt: str, output_path: Path, retries: int = 3) -> bool:
    """
    Generate an image using Gemini Imagen API.

    Args:
        prompt: Description of the image to generate
        output_path: Where to save the image
        retries: Number of retry attempts

    Returns:
        True if successful, False otherwise
    """
    global CLIENT

    if not CLIENT:
        logger.error("❌ Gemini client not initialized")
        return False

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"🎨 Generating image (attempt {attempt}/{retries})...")
            logger.debug(f"Prompt: {prompt[:150]}...")

            response = CLIENT.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",
                    safety_filter_level="block_low_and_above",
                    person_generation="DONT_ALLOW"  # Avoid person generation for tech content
                )
            )

            if response.generated_images:
                image = response.generated_images[0]
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.image.save(str(output_path))
                logger.info(f"✅ Image saved: {output_path}")
                rotate_key()  # Rotate after success to distribute load
                return True
            else:
                logger.warning("⚠️ No images returned in response")
                rotate_key()

        except Exception as e:
            error_msg = str(e).lower()

            # Check for quota/rate limit errors
            if "quota" in error_msg or "rate" in error_msg or "limit" in error_msg:
                logger.warning(f"⚠️ Rate limit hit on key #{CURRENT_KEY_INDEX + 1}, rotating...")
                rotate_key()
                if attempt < retries:
                    import time
                    time.sleep(2)  # Brief pause before retry
                    continue

            logger.error(f"❌ Error generating image: {e}")

            if attempt < retries:
                import time
                time.sleep(2)
                continue

    logger.error(f"❌ Failed to generate image after {retries} attempts")
    return False


# =============================================================================
# BLOG POST PROCESSING
# =============================================================================

def parse_frontmatter(content: str) -> Dict:
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
            data[key.strip()] = value.strip().strip('"\'[]')

    return data


def create_professional_prompt(title: str, description: str, language: str = "", category: str = "") -> str:
    """
    Create a detailed prompt for generating professional tech infographics.

    Args:
        title: Repository/project title
        description: Short description of the project
        language: Primary programming language
        category: Project category (ai, web, devops, etc.)

    Returns:
        Detailed prompt for Imagen API
    """
    # Base style directives
    base_style = (
        "Professional 4K tech infographic, isometric 3D design, "
        "modern minimal aesthetic, vibrant gradient colors, "
        "dramatic lighting, sharp focus, clean composition, "
        "tech blog header style, no text overlays"
    )

    # Language-specific visual elements
    lang_visuals = {
        'python': 'Python ecosystem with code editors and data pipelines',
        'javascript': 'JavaScript runtime with node clusters and web interfaces',
        'typescript': 'TypeScript development environment with type systems',
        'rust': 'Rust systems architecture with memory-safe components',
        'go': 'Go microservices with concurrent goroutines',
        'java': 'Java enterprise architecture with scalable services',
        'c++': 'C++ high-performance computing infrastructure',
        'ruby': 'Ruby web application stack with elegant frameworks',
    }

    # Category-specific visual themes
    category_themes = {
        'ai': 'neural networks, machine learning models, AI agents, data flows',
        'web': 'responsive interfaces, cloud services, API connections, web dashboards',
        'devops': 'CI/CD pipelines, container orchestration, monitoring dashboards, automation',
        'development': 'code editors, version control, testing frameworks, developer tools',
        'systems': 'server infrastructure, distributed systems, network topology, system architecture',
    }

    # Build contextual visual description
    lang_context = lang_visuals.get(language.lower(), 'modern software architecture')
    category_context = category_themes.get(category.lower(), 'technology infrastructure')

    # Construct final prompt
    prompt = (
        f"Create a stunning visualization for '{title}': {description}. "
        f"Show {lang_context} integrated with {category_context}. "
        f"Visual style: {base_style}. "
        f"Composition: Isometric view with floating UI elements, "
        f"glowing connections, depth of field, cinematic lighting. "
        f"Color palette: tech blues, cyber purples, neon accents. "
        f"16:9 aspect ratio, 4K resolution quality."
    )

    return prompt


def generate_images_for_blog_posts(blog_dir: Path = None, limit: int = None) -> int:
    """
    Generate images for blog posts that don't have them.

    Args:
        blog_dir: Path to blog directory (default: website/src/content/blog)
        limit: Maximum number of images to generate (default: all)

    Returns:
        Number of images successfully generated
    """
    if blog_dir is None:
        blog_dir = Path("website/src/content/blog")

    if not blog_dir.exists():
        logger.error(f"❌ Blog directory not found: {blog_dir}")
        return 0

    logger.info(f"📁 Scanning blog posts in: {blog_dir}")

    generated = 0
    processed = 0

    for md_file in blog_dir.rglob("index.md"):
        # Skip if already has an image
        header_png = md_file.parent / "header.png"
        header_svg = md_file.parent / "header.svg"

        if header_png.exists() or header_svg.exists():
            logger.debug(f"⏭️  Skipping {md_file.parent.name} (already has image)")
            continue

        # Check limit
        if limit and generated >= limit:
            logger.info(f"✋ Reached generation limit ({limit})")
            break

        processed += 1

        try:
            # Parse frontmatter
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            meta = parse_frontmatter(content)
            title = meta.get('title', md_file.parent.name)
            description = meta.get('description', '')
            language = meta.get('language', '')
            category = meta.get('category', meta.get('categories', ''))

            logger.info(f"\n{'='*60}")
            logger.info(f"📝 Processing: {title}")
            logger.info(f"   Language: {language or 'N/A'}")
            logger.info(f"   Category: {category or 'N/A'}")

            # Create prompt
            prompt = create_professional_prompt(title, description, language, category)

            # Generate image
            if generate_image(prompt, header_png):
                generated += 1
                logger.info(f"✅ Generated {generated}/{processed} images")
            else:
                logger.warning(f"⚠️ Failed to generate image for {title}")

        except Exception as e:
            logger.error(f"❌ Error processing {md_file.parent.name}: {e}")
            continue

    logger.info(f"\n{'='*60}")
    logger.info(f"🎉 Image generation complete!")
    logger.info(f"   Generated: {generated}")
    logger.info(f"   Processed: {processed}")
    logger.info(f"{'='*60}")

    return generated


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate professional blog header images using Gemini Imagen API'
    )
    parser.add_argument(
        '--blog-dir',
        type=Path,
        default=Path('website/src/content/blog'),
        help='Path to blog directory (default: website/src/content/blog)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of images to generate (default: unlimited)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("="*60)
    logger.info("🎨 Gemini Image Generator for Blog Posts")
    logger.info("="*60)

    # Setup Gemini API
    if not setup_gemini():
        logger.error("❌ Failed to initialize Gemini API")
        logger.info("💡 Falling back to SVG placeholders...")
        return 1

    # Generate images
    count = generate_images_for_blog_posts(args.blog_dir, args.limit)

    if count == 0:
        logger.warning("⚠️ No images were generated")
        return 1

    logger.info(f"✅ Successfully generated {count} image(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
