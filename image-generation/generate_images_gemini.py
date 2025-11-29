import os
import sys
import time
import random
import logging
from google import genai
from google.genai import types
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global list of available keys
API_KEYS = []
CURRENT_KEY_INDEX = 0
CLIENT: genai.Client = None

def setup_gemini():
    global API_KEYS, CLIENT

    # Collect all available keys
    keys = []
    main_key = os.environ.get("GOOGLE_API_KEY")
    if main_key:
        keys.append(main_key)

    # Check for additional keys (2 to 5)
    for i in range(2, 6):
        key = os.environ.get(f"GOOGLE_API_KEY_{i}")
        if key:
            keys.append(key)

    if not keys:
        logging.error("No GOOGLE_API_KEYs found in environment variables")
        return None

    API_KEYS = keys
    CLIENT = genai.Client(api_key=API_KEYS[0])
    logging.info(f"✅ Loaded {len(API_KEYS)} Gemini API keys for load balancing.")

    return True

def rotate_key():
    """Rotates to the next available API key."""
    global CURRENT_KEY_INDEX, CLIENT
    if len(API_KEYS) <= 1:
        return # No need to rotate

    CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(API_KEYS)
    CLIENT = genai.Client(api_key=API_KEYS[CURRENT_KEY_INDEX])
    logging.info(f"🔄 Rotated to API Key #{CURRENT_KEY_INDEX + 1}")

def generate_image_gemini(prompt, output_path):
    """Generates an image using Google Gemini (Imagen 4)."""
    global CLIENT
    
    try:
        model_name = 'imagen-4.0-generate-001'

        logging.info(f"🎨 Generating image with prompt: {prompt[:80]}...")

        try:
            response = CLIENT.models.generate_images(
                model=model_name,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",
                    safety_filter_level="block_low_and_above",
                    person_generation="ALLOW_ADULT"
                )
            )

            if response.generated_images:
                image = response.generated_images[0]
                image.image.save(str(output_path))
                logging.info(f"✅ Image saved to: {output_path}")
                # Rotate key after success to spread load
                rotate_key()
                return True
            else:
                logging.error("❌ No images returned in response")
                rotate_key() # Rotate on failure too
                return False

        except Exception as e:
            logging.error(f"❌ Error calling API: {e}")
            rotate_key() # Rotate on error
            return False

    except Exception as e:
        logging.error(f"❌ Critical error generating image: {e}")
        return False

def extract_frontmatter(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return None

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    return {
        'frontmatter': parts[1],
        'content': parts[2],
        'file': md_file
    }

def parse_metadata(frontmatter):
    lines = frontmatter.strip().split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip().strip('"\'')
    return data

def create_prompt(title, repo, language, description):
    return (
        f"Professional 3D infographic for '{title}', {description}. "
        f"Visualizing real-world application and solution architecture. "
        f"High-end digital art, isometric view, sleek modern design, "
        f"vibrant colors, professional lighting, sharp focus, 16:9 aspect ratio, "
        f"no text, clean composition, tech blog header style."
    )

def process_blog_posts(blog_dir: Path = None, limit: int = None):
    if not setup_gemini():
        return

    if blog_dir is None:
        blog_dir = Path("website/src/content/blog")
    else:
        blog_dir = Path(blog_dir)

    generated_count = 0

    for md_file in blog_dir.rglob("index.md"):
        # Check limit
        if limit and generated_count >= limit:
            logging.info(f"🛑 Reached limit of {limit} images, stopping.")
            break

        # Check if header.png exists
        image_path = md_file.parent / "header.png"
        if image_path.exists():
            continue

        logging.info(f"📝 Processing missing image for: {md_file.parent.name}")

        data = extract_frontmatter(md_file)
        if not data:
            continue

        meta = parse_metadata(data['frontmatter'])
        title = meta.get('title', '')
        repo = meta.get('repo', '')
        language = meta.get('language', '')
        description = meta.get('description', '')

        if not title:
            continue

        prompt = create_prompt(title, repo, language, description)

        if generate_image_gemini(prompt, image_path):
            generated_count += 1
            logging.info(f"✅ Generated {generated_count} images so far")
            # Wait to avoid rate limits
            time.sleep(5)
        else:
            logging.error(f"Failed to generate image for {title}")

    logging.info(f"🎉 Image generation complete! Generated {generated_count} new images.")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate blog header images using Gemini Imagen')
    parser.add_argument('--blog-dir', type=str, help='Path to blog directory')
    parser.add_argument('--limit', type=int, help='Maximum number of images to generate')

    args = parser.parse_args()

    process_blog_posts(blog_dir=args.blog_dir, limit=args.limit)

if __name__ == "__main__":
    main()
