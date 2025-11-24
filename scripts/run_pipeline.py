#!/usr/bin/env python3
"""
End-to-End Automation Pipeline Script.
Orchestrates the entire flow: Repo -> Blog Post -> Video -> YouTube Upload.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import core components
# Note: In a real scenario, we would import the Agent/Scanner classes.
# For this sprint, we will focus on connecting the Video+Upload part
# given a blog post or repo info.

from video_generator.reel_creator import ReelCreator
# from blog_generator.markdown_writer import MarkdownWriter # Placeholder
# from agents.github_scanner import GitHubScanner # Placeholder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Pipeline")

def main():
    parser = argparse.ArgumentParser(description="Run the Video Generator Pipeline")
    parser.add_argument("--repo", help="GitHub repository URL", required=True)
    parser.add_argument("--blog-post", help="Path to existing blog post (markdown)", required=False)
    parser.add_argument("--upload", action="store_true", help="Enable YouTube upload")

    args = parser.parse_args()

    repo_url = args.repo
    repo_name = repo_url.split("/")[-1]

    logger.info(f"🚀 Starting pipeline for {repo_name}...")

    # Step 1: Blog Generation (Placeholder for now, assuming we have data)
    # In a full run, this would call GitHubScanner -> Gemini -> MarkdownWriter
    logger.info("📝 Step 1: Blog Generation")
    if not args.blog_post:
        logger.info("No blog post provided. Simulating generation...")
        # Simulate script data
        script_data = {
            "hook": f"Discover {repo_name}, the ultimate tool for developers.",
            "solution": f"{repo_name} solves complex problems with simple APIs.",
            "architecture": "Built with Python and React.",
            "hook_highlights": ["ultimate tool"],
            "solution_highlights": ["solves complex"],
            "architecture_highlights": ["Python", "React"]
        }
        # Simulate images
        images = {
            "architecture": "blog/assets/images/placeholder/architecture.png",
            "flow": "blog/assets/images/placeholder/flow.png",
            "screenshot": "blog/assets/images/placeholder/screenshot.png"
        }
    else:
        logger.info(f"Using existing blog post: {args.blog_post}")
        # Parse markdown (simplified)
        script_data = {
            "hook": f"Deep dive into {repo_name}.",
            "solution": "Automated solution.",
            "architecture": "Modern stack."
        }
        images = {} # Should parse from frontmatter

    # Step 2: Video Generation
    logger.info("🎬 Step 2: Video Generation")
    output_dir = "blog/assets/videos"

    reel_creator = ReelCreator(output_dir=output_dir, enable_upload=args.upload)

    # Generate Video
    # Note: In production, we would generate audio here first using VoiceTranslationPipeline
    # For this script, we'll assume ReelCreator handles it or we pass None for silent/music-only

    video_path = reel_creator.create_reel(
        repo_name=repo_name,
        script_data=script_data,
        images=images,
        audio_path=None, # Or path to synthesized audio
        durations={'intro':3, 'problem':5, 'solution':5, 'architecture':4, 'outro':3}
    )

    if video_path:
        logger.info(f"✅ Video generated at: {video_path}")

        # Step 3: Upload (Handled by ReelCreator if enable_upload=True)
        if args.upload:
            logger.info("📤 Step 3: Uploading to YouTube (via ReelCreator)...")
            # Logic is inside ReelCreator._handle_upload
        else:
            logger.info("⏭️  Skipping upload (use --upload to enable)")

    else:
        logger.error("❌ Video generation failed.")
        sys.exit(1)

    logger.info("🎉 Pipeline completed successfully!")

if __name__ == "__main__":
    main()
