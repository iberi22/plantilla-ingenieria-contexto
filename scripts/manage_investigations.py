#!/usr/bin/env python3
"""
Investigation Management Script.
Handles the lifecycle of repository investigations:
- Adding new repositories.
- Checking for updates (Git commit changes).
- Updating the 'Repo as DB' (Markdown files).
- Triggering Blog updates.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner.github_scanner import GitHubScanner
from persistence.local_store import LocalStore
from agents.scriptwriter import ScriptWriter
from blog_generator.markdown_writer import MarkdownWriter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("InvestigationManager")

load_dotenv()

class InvestigationManager:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.google_key = os.getenv("GOOGLE_API_KEY")

        if not self.github_token:
            logger.error("GITHUB_TOKEN is required.")
            sys.exit(1)

        self.scanner = GitHubScanner(self.github_token)
        self.store = LocalStore()

        # Initialize AI Agent (ScriptWriter)
        # We use Gemini by default as per existing code
        if self.google_key:
            self.agent = ScriptWriter(api_key=self.google_key, provider="gemini")
        else:
            logger.warning("GOOGLE_API_KEY not found. AI Analysis will be mocked/skipped.")
            self.agent = None

    def check_updates(self):
        """Checks all stored investigations for updates on GitHub."""
        logger.info("🔍 Checking for updates...")
        investigations = self.store.list_investigations()

        for repo_full_name in investigations:
            data = self.store.get_investigation(repo_full_name)
            if not data:
                continue

            metadata = data["metadata"]
            stored_commit = metadata.get("latest_commit")

            # Fetch current commit
            current_commit = self.scanner.get_latest_commit(repo_full_name)

            if not current_commit:
                logger.warning(f"Could not fetch commit for {repo_full_name}")
                continue

            if stored_commit != current_commit:
                logger.info(f"🔄 Update detected for {repo_full_name}!")
                logger.info(f"   Old: {stored_commit[:7]} -> New: {current_commit[:7]}")
                self.update_investigation(repo_full_name, current_commit)
            else:
                logger.info(f"✅ {repo_full_name} is up to date.")

    def update_investigation(self, repo_full_name, current_commit):
        """Re-analyzes and updates the investigation file."""
        # 1. Fetch fresh repo data
        # We need a method to get full repo details by name in Scanner,
        # but for now we can assume we can get it via search or direct API if we add it.
        # Let's mock the "get_repo" call using the scanner's internal requests if possible
        # or just use the search for now.

        # Hack: Search for specific repo to get details
        repos = self.scanner.scan_recent_repos(query=f"repo:{repo_full_name}", limit=1)
        if not repos:
            logger.error(f"Could not find repo {repo_full_name} to update.")
            return

        repo_data = repos[0]
        repo_data["latest_commit_hash"] = current_commit # Ensure this is set

        # 2. Run Analysis
        analysis = self._run_analysis(repo_data)

        # 3. Save
        self.store.save_investigation(repo_data, analysis)
        logger.info(f"💾 Updated investigation for {repo_full_name}")

        # 4. Trigger Blog Update
        self._update_blog_post(repo_data, analysis)

    def add_repo(self, repo_url):
        """Adds a new repository to the system."""
        repo_name = repo_url.split("/")[-1]
        owner = repo_url.split("/")[-2] if "/" in repo_url else "unknown"
        full_name = f"{owner}/{repo_name}"

        logger.info(f"➕ Adding new repo: {full_name}")

        # Fetch details
        repos = self.scanner.scan_recent_repos(query=f"repo:{full_name}", limit=1)
        if not repos:
            logger.error(f"Could not find repo {full_name}")
            return

        repo_data = repos[0]

        # Get commit hash
        commit = self.scanner.get_latest_commit(full_name)
        repo_data["latest_commit_hash"] = commit

        # Run Analysis
        analysis = self._run_analysis(repo_data)

        # Save
        self.store.save_investigation(repo_data, analysis)

        # Blog
        self._update_blog_post(repo_data, analysis)

    def discover_new_repos(self, limit=5):
        """Scans for new trending repositories and adds them."""
        logger.info(f"🔭 Scanning for new repositories (limit={limit})...")

        # Use the scanner to find candidates
        # We can adjust the query to be more specific if needed
        candidates = self.scanner.scan_recent_repos(limit=limit * 2) # Fetch more to filter

        added_count = 0
        for repo in candidates:
            if added_count >= limit:
                break

            full_name = repo["full_name"]

            # Check if already exists
            if self.store.get_investigation(full_name):
                logger.info(f"⏭️  Skipping {full_name} (already exists)")
                continue

            # Validate (Scanner already does some validation, but we can double check)
            if not self.scanner.validate_repo(repo):
                continue

            logger.info(f"✨ Found new candidate: {full_name}")

            # Add it
            # We need to get the latest commit hash if it's not in the search result
            # (Search results usually don't have the latest commit hash)
            commit = self.scanner.get_latest_commit(full_name)
            repo["latest_commit_hash"] = commit

            analysis = self._run_analysis(repo)
            self.store.save_investigation(repo, analysis)
            self._update_blog_post(repo, analysis)

            added_count += 1

        logger.info(f"🏁 Discovery complete. Added {added_count} new repositories.")

    def _run_analysis(self, repo_data):
        """Runs the AI analysis."""
        if self.agent:
            logger.info(f"🤖 Running AI analysis for {repo_data['name']}...")
            # We might need to fetch README content here if it's not in repo_data
            # The scanner has _has_substantial_readme but doesn't return content.
            # For now, we pass what we have.
            return self.agent.generate_script(repo_data)
        else:
            return {
                "hook": "Manual analysis required.",
                "solution": "No AI agent configured.",
                "verdict": "Pending",
                "content": "AI Analysis unavailable. Please configure GOOGLE_API_KEY."
            }

    def _update_blog_post(self, repo_data, analysis):
        """
        Updates or creates the blog post.
        This should interface with BlogManager/MarkdownWriter.
        """
        logger.info(f"📝 Updating blog post for {repo_data['name']}...")
        
        try:
            # Output to Astro content directory
            writer = MarkdownWriter(output_dir="website/src/content/blog")
            # We pass empty images for now as we are focusing on text/data flow
            post_path = writer.create_post(repo_data, analysis, images={})
            logger.info(f"✅ Blog post generated at: {post_path}")
        except Exception as e:
            logger.error(f"Failed to generate blog post: {e}")def main():
    parser = argparse.ArgumentParser(description="Manage Investigations")
    parser.add_argument("--check", action="store_true", help="Check for updates")
    parser.add_argument("--add", help="Add a repo by URL")
    parser.add_argument("--discover", type=int, help="Discover N new repositories", const=5, nargs="?")

    args = parser.parse_args()

    manager = InvestigationManager()

    if args.add:
        manager.add_repo(args.add)
    elif args.discover:
        manager.discover_new_repos(limit=args.discover)
    elif args.check:
        manager.check_updates()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
