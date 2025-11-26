import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class LocalStore:
    """
    Manages persistence of investigations as Markdown files with YAML frontmatter.
    Acts as a file-based database for the repository.
    """

    def __init__(self, storage_dir: str = "investigations"):
        self.logger = logging.getLogger(__name__)
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, repo_full_name: str) -> Path:
        """Generates a safe filename from the repo name."""
        safe_name = repo_full_name.replace("/", "_").replace(" ", "-")
        return self.storage_dir / f"{safe_name}.md"

    def save_investigation(self, repo_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Saves the investigation to a markdown file.
        Updates existing file if it exists, preserving history if needed.
        """
        file_path = self._get_file_path(repo_data["full_name"])

        # Prepare metadata (Frontmatter)
        metadata = {
            "repo_name": repo_data["name"],
            "repo_full_name": repo_data["full_name"],
            "url": repo_data.get("html_url", f"https://github.com/{repo_data['full_name']}"),
            "last_updated": datetime.now().isoformat(),
            "created_at": repo_data.get("created_at"),
            "pushed_at": repo_data.get("pushed_at"),
            "stars": repo_data.get("stargazers_count"),
            "language": repo_data.get("language"),
            "topics": repo_data.get("topics", []),
            "latest_commit": repo_data.get("latest_commit_hash"), # Important for versioning
            "version": analysis.get("version", "1.0.0"),
            "status": "active"
        }

        # Prepare Content
        content = analysis.get("content", "")
        if not content:
            # Fallback if content is structured differently
            content = f"# Investigation: {repo_data['name']}\n\n"
            content += f"{repo_data.get('description', 'No description')}\n\n"
            content += "## Analysis\n\n"
            content += str(analysis)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(metadata, f, default_flow_style=False)
            f.write("---\n\n")
            f.write(content)

        self.logger.info(f"Saved investigation to {file_path}")
        return str(file_path)

    def get_investigation(self, repo_full_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves the investigation data including metadata."""
        file_path = self._get_file_path(repo_full_name)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Split frontmatter and content
                raw_content = f.read()

            if raw_content.startswith("---"):
                parts = raw_content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    content = parts[2]
                    return {"metadata": metadata, "content": content}

            return None
        except Exception as e:
            self.logger.error(f"Error reading investigation {repo_full_name}: {e}")
            return None

    def list_investigations(self) -> list:
        """Lists all stored investigations."""
        return [f.stem.replace("_", "/") for f in self.storage_dir.glob("*.md")]
