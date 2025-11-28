import os
import sys
import re
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from scanner.insights_collector import InsightsCollector
except ImportError:
    # Fallback if running from root
    sys.path.insert(0, "src")
    from scanner.insights_collector import InsightsCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        logger.info(f"Loading .env from {env_path}")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        os.environ[key] = value.strip().strip('"').strip("'")
                    except ValueError:
                        pass

def update_frontmatter(content, insights):
    """Update the frontmatter with new insights data"""
    parts = content.split('---', 2)
    if len(parts) < 3:
        return content

    frontmatter = parts[1]

    # Remove existing insights block if present to avoid duplicates
    # We look for "insights:" and all following lines that are indented
    frontmatter = re.sub(r'\ninsights:\s*\n(\s+.*\n?)*', '\n', frontmatter)

    # Construct new insights block
    insights_yaml = "insights:\n"

    if "last_commit_date" in insights:
        insights_yaml += f"  last_commit_date: \"{insights['last_commit_date']}\"\n"

    if "open_issues_count" in insights:
        insights_yaml += f"  open_issues_count: {insights['open_issues_count']}\n"

    if "top_contributors" in insights:
        # Serialize list of dicts to JSON string as expected by the frontmatter parser/schema
        contributors_json = json.dumps(insights['top_contributors'])
        insights_yaml += f"  top_contributors: {contributors_json}\n"

    # Append to frontmatter
    new_frontmatter = frontmatter.rstrip() + "\n" + insights_yaml

    return f"---{new_frontmatter}---{parts[2]}"

def main():
    logger.info("🚀 Starting Insights Backfill Script")

    load_env()

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_PAT")
    if not token:
        logger.error("❌ No GITHUB_TOKEN or GH_PAT found in environment or .env file")
        return

    collector = InsightsCollector(token)

    # Find all blog posts
    blog_dir = Path("website/src/content/blog")
    files = list(blog_dir.rglob("*.md"))

    if not files:
        logger.warning("⚠️ No markdown files found in website/src/content/blog")
        return

    logger.info(f"Found {len(files)} blog posts to process")

    success_count = 0

    for i, file_path in enumerate(files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract repo name
            # Matches "repo: user/repo" or "repo: 'user/repo'"
            match = re.search(r'^repo:\s*["\']?([\w\-\.]+/[[\w\-\.]+)["\']?', content, re.MULTILINE)

            if not match:
                logger.warning(f"⚠️ Skipping {file_path.name}: No 'repo' field found in frontmatter")
                continue

            repo_full_name = match.group(1)
            logger.info(f"[{i+1}/{len(files)}] Processing {repo_full_name} ({file_path.name})...")

            # Collect insights
            insights = collector.collect_insights(repo_full_name)

            # Validate we got something useful
            if not insights.get('last_commit_date'):
                logger.warning(f"⚠️ Failed to fetch insights for {repo_full_name}")
                continue

            # Update file
            new_content = update_frontmatter(content, insights)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"✅ Updated {file_path.name} with {insights['open_issues_count']} issues, last commit: {insights['last_commit_date']}")
            success_count += 1

        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")

    logger.info("="*60)
    logger.info(f"🎉 Backfill complete! Updated {success_count}/{len(files)} files.")
    logger.info("="*60)

if __name__ == "__main__":
    main()
