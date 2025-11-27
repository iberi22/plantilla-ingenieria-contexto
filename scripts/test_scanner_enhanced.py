import os
import sys
import logging
from pathlib import Path
import json

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

    # Use a query that finds high quality repos
    query = "language:python stars:>5000 pushed:>2024-01-01"
    logging.info(f"Scanning with query: {query}")

    # scan_recent_repos now does the heavy lifting
    repos = scanner.scan_recent_repos(query=query, limit=5)

    logging.info(f"Scan returned {len(repos)} enriched repositories.")

    for i, repo in enumerate(repos):
        print(f"\n--- Repo {i+1}: {repo['full_name']} ---")
        print(f"Stars: {repo['stargazers_count']}")
        print(f"Description: {repo.get('description')}")

        if "insights" in repo:
            print("Insights:")
            print(json.dumps(repo["insights"], indent=2))

        if "analysis" in repo:
            print("Analysis:")
            print(json.dumps(repo["analysis"], indent=2))
        else:
            print("WARNING: No analysis found!")

if __name__ == "__main__":
    main()
