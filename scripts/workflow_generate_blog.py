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
from scanner.rust_bridge import get_scanner, RustScanner
from agents.scriptwriter import ScriptWriter
from blog_generator.markdown_writer import MarkdownWriter

# Optional: Image generation (only in private repo)
try:
    from image_gen.image_generator import ImageGenerator
    IMAGE_GEN_AVAILABLE = True
except ImportError:
    IMAGE_GEN_AVAILABLE = False
    logging.warning("image_gen module not available - skipping image generation")

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
        logger.error("❌ GITHUB_TOKEN not found in environment")
        sys.exit(1)

    if not gemini_api_key:
        logger.error("❌ GOOGLE_API_KEY not found in environment")
        sys.exit(1)

    logger.info(f"✅ Environment variables loaded:")
    logger.info(f"   GITHUB_TOKEN: {'*' * 20}")
    logger.info(f"   GOOGLE_API_KEY: {'*' * 20}")

    try:
        # Step 1: Scan GitHub for repos (try Rust first for speed)
        logger.info("\n📦 Step 1: Scanning GitHub for quality repositories...")

        # Try Rust scanner first
        scanner = get_scanner(github_token, prefer_rust=True)

        valid_repo = None

        if isinstance(scanner, RustScanner) and scanner.is_available():
            # Use Rust scanner (much faster)
            logger.info("🦀 Using Rust scanner for improved performance...")
            valid_repo = scanner.scan_and_find_repo()

            if valid_repo:
                logger.info(f"✅ Rust scanner found: {valid_repo['full_name']}")

        # Fallback to Python scanner if Rust fails or not available
        # Fallback to Python scanner if Rust fails or not available
        if not valid_repo:
            logger.info("🐍 Using Python scanner (fallback)...")
            if isinstance(scanner, RustScanner):
                from scanner.github_scanner import GitHubScanner
                scanner = GitHubScanner(token=github_token)

            # Limit to 7 projects per run to avoid API saturation
            # 3 keys * 20 images/day = 60 images. 2 images/project = 30 projects/day.
            # 4 runs/day => 7.5 projects/run.
            MAX_PROJECTS = 7
            repos = scanner.scan_recent_repos(limit=20) # Scan more to filter

            if not repos:
                logger.warning("⚠️  No repositories found")
                return

            logger.info(f"Found {len(repos)} repositories")

            # Find valid repos
            valid_repos = []
            for repo in repos:
                if scanner.validate_repo(repo):
                    valid_repos.append(repo)
                    logger.info(f"✅ Selected repo: {repo['full_name']}")
                    if len(valid_repos) >= MAX_PROJECTS:
                        break

            if not valid_repos and not valid_repo:
                logger.warning("⚠️  No valid repositories found after validation")
                return

            # Process all valid repos
            processed_count = 0

            # If we found a single valid repo via Rust, add it to the list
            if valid_repo:
                valid_repos = [valid_repo]

            for repo in valid_repos:
                try:
                    logger.info(f"\n🔄 Processing {processed_count + 1}/{len(valid_repos)}: {repo['full_name']}")

                    # Step 3: Generate analysis with Gemini
                    logger.info("🤖 Generating analysis...")
                    scriptwriter = ScriptWriter(
                        api_key=gemini_api_key,
                        provider="gemini",
                        model_name="gemini-2.5-flash"
                    )

                    script_data = scriptwriter.generate_script(repo)

                    if not script_data:
                        logger.error(f"Failed to generate script for {repo['full_name']}")
                        continue

                    # Step 4: Generate images (optional)
                    images = {}
                    if IMAGE_GEN_AVAILABLE:
                        logger.info("🎨 Generating images...")
                        try:
                            image_generator = ImageGenerator(
                                model_name="nano-banana-2",
                                output_dir="website/public/images"
                            )

                            repo_name = repo['name'].lower()

                            # Generate architecture diagram
                            arch_img = image_generator.generate_architecture_diagram(
                                repo,
                                script_data
                            )

                            # Generate flow diagram
                            flow_img = image_generator.generate_problem_solution_flow(
                                repo,
                                script_data
                            )

                            # Prepare image paths
                            if arch_img:
                                images['architecture'] = f"/images/{repo_name}/architecture.png"
                            if flow_img:
                                images['flow'] = f"/images/{repo_name}/flow.png"

                        except Exception as e:
                            logger.warning(f"Image generation failed for {repo['full_name']}: {e}")
                            images = {}

                    # Step 5: Create blog post
                    logger.info("📝 Creating blog post...")
                    markdown_writer = MarkdownWriter(output_dir="website/src/content/blog")

                    post_path = markdown_writer.create_post(
                        repo,
                        script_data,
                        images if images else None
                    )

                    logger.info(f"✅ Blog post created: {post_path}")
                    processed_count += 1

                except Exception as e:
                    logger.error(f"❌ Error processing {repo['full_name']}: {e}")
                    continue

            logger.info("\n" + "="*60)
            logger.info(f"✅ Batch Completed! Processed {processed_count} projects.")
            logger.info("="*60)
            logger.info("\n💡 Next: GitHub Actions will create a PR with these changes")
            return # Exit main successfully

        # If we reached here without processing loop (should be covered above)
        if valid_repo and not valid_repos:
             # Handle single rust repo case if logic falls through
             pass


    except Exception as e:
        logger.error(f"\n❌ Workflow failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
