import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner.github_scanner import GitHubScanner

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logging.error("GITHUB_TOKEN environment variable is required.")
        sys.exit(1)

    scanner = GitHubScanner(token)

    logging.info("Scanning for recent repositories...")
    repos = scanner.scan_recent_repos(limit=20)
    logging.info(f"Found {len(repos)} candidates. Validating...")

    valid_repos = []
    for repo in repos:
        if scanner.validate_repo(repo):
            valid_repos.append(repo)
            logging.info(f"✅ Valid Repo: {repo['full_name']}")
        else:
            # logging.info(f"❌ Invalid Repo: {repo['full_name']}")
            pass

    logging.info(f"Scan complete. {len(valid_repos)} valid repositories found.")

    # In a real pipeline, we would pass these to the Blog Generator
    # for r in valid_repos: ...

if __name__ == "__main__":
    main()
