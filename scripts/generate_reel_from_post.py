"""
End-to-end script to generate a video reel from a blog post.

Usage:
    python scripts/generate_reel_from_post.py <post_path>
"""

import sys
import asyncio
import logging
from pathlib import Path
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_generator.screenshot_capturer import ScreenshotCapturer
from video_generator.reel_creator import ReelCreator
from video_generator.narration_generator import NarrationGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_frontmatter(post_path: Path) -> dict:
    """
    Parse YAML frontmatter from a markdown post.

    Args:
        post_path: Path to the markdown file.

    Returns:
        Dictionary containing frontmatter data.
    """
    with open(post_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter between --- markers
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            return frontmatter

    return {}


async def generate_reel(post_path: str):
    """
    Generate a video reel from a blog post.

    Args:
        post_path: Path to the markdown blog post.
    """
    post_path = Path(post_path)

    if not post_path.exists():
        logger.error(f"Post not found: {post_path}")
        return

    logger.info(f"Processing post: {post_path}")

    # Parse frontmatter
    metadata = parse_frontmatter(post_path)

    repo_name = metadata.get('repo', 'unknown-repo')
    repo_url = f"https://github.com/{repo_name}"
    title = metadata.get('title', 'Unknown Project')

    logger.info(f"Repository: {repo_name}")
    logger.info(f"Title: {title}")

    # Extract images from metadata
    images = metadata.get('images', {})

    # If screenshot is not available, capture it
    if 'screenshot' not in images or not Path(images['screenshot']).exists():
        logger.info("Capturing screenshot...")
        capturer = ScreenshotCapturer()
        screenshot_path = await capturer.capture_repo_page(repo_url, repo_name)
        if screenshot_path:
            images['screenshot'] = screenshot_path

    # Check if we have all required images
    required_images = ['architecture', 'flow', 'screenshot']
    missing = [img for img in required_images if img not in images]

    if missing:
        logger.warning(f"Missing images: {missing}")
        logger.warning("Reel will be created with available images only")

    # Generate narration
    narration_text = metadata.get('narration_20s', metadata.get('hook', ''))

    if not narration_text:
        logger.error("No narration text found in post metadata")
        return

    logger.info("Generating narration audio...")
    narrator = NarrationGenerator()
    audio_path = await narrator.generate_20s_narration(narration_text, repo_name)

    if not audio_path:
        logger.error("Failed to generate narration")
        return

    # Prepare script data
    script_data = {
        'hook': metadata.get('hook', ''),
        'solution': metadata.get('solution', ''),
        'verdict': metadata.get('verdict', '')
    }

    # Create reel
    logger.info("Creating video reel...")
    creator = ReelCreator()
    video_path = creator.create_reel(
        repo_name=title,
        script_data=script_data,
        images=images,
        audio_path=audio_path
    )

    if video_path:
        logger.info(f"✅ Reel created successfully: {video_path}")

        # Update post metadata with video path
        if 'video' not in metadata:
            logger.info("Updating post with video path...")
            # Note: In a real implementation, we would update the frontmatter here
            logger.info(f"Video path: {video_path}")
    else:
        logger.error("❌ Failed to create reel")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_reel_from_post.py <post_path>")
        print("\nExample:")
        print("  python scripts/generate_reel_from_post.py blog/_posts/2025-11-23-awesome-project.md")
        sys.exit(1)

    post_path = sys.argv[1]
    asyncio.run(generate_reel(post_path))


if __name__ == "__main__":
    main()
