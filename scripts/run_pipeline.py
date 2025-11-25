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
from blog_generator.markdown_writer import MarkdownWriter
from scanner.github_scanner import GitHubScanner
from agents.scriptwriter import ScriptWriter
from image_gen.image_generator import ImageGenerator
from persistence.firebase_store import FirebaseStore

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

    # Initialize Persistence
    firebase_store = None
    try:
        firebase_store = FirebaseStore()
        logging.info("Firebase persistence enabled")
        repo_full_name = f"unknown/{repo_name}" # Placeholder until scan
        # firebase_store.save_repo(repo_full_name, {"name": repo_name}, status="pending")
    except Exception as e:
        logging.warning(f"Firebase not available: {e}")

    # Step 1: Blog Generation
    logger.info("📝 Step 1: Blog Generation")

    script_data = {}
    images = {}

    if args.blog_post:
        logger.info(f"Using existing blog post: {args.blog_post}")
        # Simplified parsing - in a real app we'd parse frontmatter properly
        script_data = {
            "hook": f"Deep dive into {repo_name}.",
            "solution": "Automated solution.",
            "architecture": "Modern stack."
        }
        # Assume images are already generated if blog post exists
        # images = ... (would need to parse frontmatter)
    else:
        logger.info("Generating content from scratch...")

        # 1a. Scan/Get Repo Details
        # For this script, since we have the URL, we can just 'validate' it or get metadata
        # We need a token for this
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            scanner = GitHubScanner(token=github_token)
            # We can't easily "get" a single repo with scan_recent_repos, but let's assume we have data
            # For now, we mock the repo metadata object or fetch it if we implemented `get_repo`
            repo_data = {
                "name": repo_name,
                "full_name": f"owner/{repo_name}",
                "description": "Automated analysis.",
                "stargazers_count": 100,
                "language": "Python",
                "topics": ["ai", "automation"]
            }
        else:
            logger.warning("GITHUB_TOKEN not found. Using mock repo data.")
            repo_data = {"name": repo_name, "full_name": f"unknown/{repo_name}", "description": "Mock description"}

        if firebase_store:
            firebase_store.save_repo(repo_data["full_name"], repo_data, status="processing")

        # 1b. Generate Analysis
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            writer = ScriptWriter(api_key=google_key, provider="gemini")
            script_data = writer.generate_script(repo_data)
        else:
            logger.warning("GOOGLE_API_KEY not found. Using mock script.")
            script_data = {
                "hook": f"Discover {repo_name}, the ultimate tool.",
                "solution": "Solves problems efficiently.",
                "architecture": "Modular design.",
                "pros": ["Fast", "Secure"],
                "cons": ["Complex setup"],
                "verdict": "Highly recommended."
            }

        # 1c. Generate Images
        try:
            img_gen = ImageGenerator(model_name="nano-banana-2", output_dir=f"blog/assets/images/{repo_name.lower()}")

            arch_img = img_gen.generate_architecture_diagram(repo_data, script_data)
            flow_img = img_gen.generate_problem_solution_flow(repo_data, script_data)

            if arch_img: images['architecture'] = arch_img
            if flow_img: images['flow'] = flow_img

            # Placeholder for screenshot (ScreenshotCapturer would handle this in ReelCreator or here)
            # images['screenshot'] = ...

        except Exception as e:
            logger.warning(f"Image generation skipped: {e}")

        # 1d. Write Blog Post
        md_writer = MarkdownWriter(output_dir="blog/_posts")
        post_path = md_writer.create_post(repo_data, script_data, images)
        logger.info(f"✅ Blog post created at: {post_path}")

        # If we want ReelCreator to capture the blog, we might need to serve it or point to file
        # For now, ReelCreator uses raw images if passed

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

        if firebase_store:
            firebase_store.update_status(repo_data.get("full_name", repo_name), status="completed")

    else:
        logger.error("❌ Video generation failed.")
        if firebase_store:
            firebase_store.update_status(repo_data.get("full_name", repo_name), status="failed", error_message="Video generation failed")
        sys.exit(1)

    logger.info("🎉 Pipeline completed successfully!")

if __name__ == "__main__":
    main()
