"""
Workflow script for generating blog posts.

This script is executed by GitHub Actions to:
1. Scan GitHub for quality repos
2. Generate analysis with Gemini
3. Generate images
4. Create blog post in Markdown
5. Commit files (PR is created by GitHub Actions)
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner.github_scanner import GitHubScanner
from agents.scriptwriter import ScriptWriter
from image_gen.image_generator import ImageGenerator
from blog_generator.markdown_writer import MarkdownWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main workflow function."""
    logger.info("="*60)
    logger.info("🚀 Starting Blog Generation Workflow")
    logger.info("="*60)

    # Get environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    gemini_api_key = os.getenv("GOOGLE_API_KEY")

    if not github_token:
        logger.error("GITHUB_TOKEN not found in environment")
        sys.exit(1)

    if not gemini_api_key:
        logger.error("GOOGLE_API_KEY not found in environment")
        sys.exit(1)

    try:
        # Step 1: Scan GitHub for repos
        logger.info("\n📦 Step 1: Scanning GitHub for quality repositories...")
        scanner = GitHubScanner(token=github_token)
        # scan_recent_repos signature is (query, limit)
        repos = scanner.scan_recent_repos(limit=10)

        if not repos:
            logger.warning("No repositories found")
            return

        logger.info(f"Found {len(repos)} repositories")

        # Step 2: Find a valid repo
        valid_repo = None
        for repo in repos:
            if scanner.validate_repo(repo):
                valid_repo = repo
                logger.info(f"✅ Selected repo: {repo['full_name']}")
                break

        if not valid_repo:
            logger.warning("No valid repositories found")
            return

        # Step 3: Generate analysis with Gemini
        logger.info("\n🤖 Step 2: Generating analysis with Gemini...")
        scriptwriter = ScriptWriter(
            api_key=gemini_api_key,
            provider="gemini",
            model_name="gemini-2.5-flash"
        )

        script_data = scriptwriter.generate_script(valid_repo)

        if not script_data:
            logger.error("Failed to generate script")
            return

        logger.info("✅ Analysis generated successfully")

        # Step 4: Generate images
        logger.info("\n🎨 Step 3: Generating images...")
        try:
            image_generator = ImageGenerator(
                model_name="nano-banana-2",
                output_dir="blog/assets/images"
            )

            repo_name = valid_repo['name'].lower()

            # Generate architecture diagram
            arch_img = image_generator.generate_architecture_diagram(
                valid_repo,
                script_data
            )

            # Generate flow diagram
            flow_img = image_generator.generate_problem_solution_flow(
                valid_repo,
                script_data
            )

            # Prepare image paths for blog post
            images = {}
            if arch_img:
                images['architecture'] = f"/assets/images/{repo_name}/architecture.png"
            if flow_img:
                images['flow'] = f"/assets/images/{repo_name}/flow.png"

            logger.info(f"✅ Generated {len(images)} images")

        except Exception as e:
            logger.warning(f"Image generation failed: {e}. Continuing without images.")
            images = {}

        # Step 5: Create blog post
        logger.info("\n📝 Step 4: Creating blog post...")
        markdown_writer = MarkdownWriter(output_dir="blog/_posts")

        post_path = markdown_writer.create_post(
            valid_repo,
            script_data,
            images if images else None
        )

        logger.info(f"✅ Blog post created: {post_path}")

        # Validate post
        if markdown_writer.validate_post(post_path):
            logger.info("✅ Post validation passed")
        else:
            logger.error("❌ Post validation failed")
            return

        # Step 6: Summary
        logger.info("\n" + "="*60)
        logger.info("✅ Blog Generation Workflow Completed Successfully!")
        logger.info("="*60)
        logger.info(f"Repository: {valid_repo['full_name']}")
        logger.info(f"Post: {post_path}")
        logger.info(f"Images: {len(images)}")
        logger.info("\n💡 Next: GitHub Actions will create a PR with these changes")

    except Exception as e:
        logger.error(f"\n❌ Workflow failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
