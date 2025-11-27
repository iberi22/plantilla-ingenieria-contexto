"""
Markdown Writer for generating blog posts from repository data.

This module creates Jekyll-compatible Markdown posts with YAML frontmatter.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json


class MarkdownWriter:
    """
    Generates Markdown blog posts with YAML frontmatter.

    Creates Jekyll-compatible posts from repository and script data.
    """

    def __init__(self, output_dir: str = "website/src/content/blog"):
        """
        Initialize MarkdownWriter.

        Args:
            output_dir: Directory to save generated posts.
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_post(
        self,
        repo_data: Dict[str, Any],
        script_data: Dict[str, Any],
        images: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a complete blog post in Markdown.

        Args:
            repo_data: Repository metadata from GitHub.
            script_data: Script data from AI analysis.
            images: Dictionary of image paths (architecture, flow, screenshot).

        Returns:
            Path to the generated Markdown file.
        """
        try:
            # Generate filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            repo_name = repo_data.get("name", "unknown").lower().replace(" ", "-")
            filename = f"{date_str}-{repo_name}.md"
            filepath = self.output_dir / filename

            # Build frontmatter
            frontmatter = self._format_frontmatter(repo_data, script_data, images)

            # Build content
            content = self._format_content(script_data)

            # Combine and write
            full_content = f"{frontmatter}\n\n{content}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)

            self.logger.info(f"Created blog post: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Failed to create post: {e}")
            raise

    def _determine_categories(self, tags: List[str], language: str) -> List[str]:
        """
        Determine categories based on tags and language.

        Args:
            tags: List of repository tags/topics.
            language: Primary programming language.

        Returns:
            List of category strings.
        """
        categories = set()

        # Normalize inputs
        tags_lower = [t.lower() for t in tags]
        lang_lower = language.lower() if language else ""

        # Basic mapping
        if "security" in tags_lower or "hacking" in tags_lower:
            categories.add("Cybersecurity")

        if "ai" in tags_lower or "machine-learning" in tags_lower or "llm" in tags_lower:
            categories.add("AI Tools")

        if "react" in tags_lower or "vue" in tags_lower or "svelte" in tags_lower or "css" in tags_lower or "ui" in tags_lower:
            categories.add("UI/UX")

        if "database" in tags_lower or "sql" in tags_lower or "nosql" in tags_lower:
            categories.add("Databases")

        if "docker" in tags_lower or "kubernetes" in tags_lower or "devops" in tags_lower:
            categories.add("DevOps")

        if "python" in lang_lower:
            categories.add("Development")

        # Default
        if not categories:
            categories.add("Development")

        return list(categories)

    def _format_frontmatter(
        self,
        repo_data: Dict[str, Any],
        script_data: Dict[str, Any],
        images: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Format YAML frontmatter for Astro/Jekyll.

        Args:
            repo_data: Repository metadata.
            script_data: Script analysis data.
            images: Image paths.

        Returns:
            Formatted YAML frontmatter string.
        """
        # Extract data
        repo_full_name = repo_data.get("full_name", "unknown/unknown")
        repo_name = repo_data.get("name", "Unknown")
        description = repo_data.get("description", "")
        # Sanitize description for YAML
        if description:
            description = description.replace('"', '\\"').replace('\n', ' ')
        else:
            description = ""

        stars = repo_data.get("stargazers_count", 0)
        language = repo_data.get("language", "Unknown")
        if not language:
            language = "Unknown"

        # Create title from hook
        hook = script_data.get("hook", "")
        # Sanitize hook for title
        if hook:
             clean_hook = hook.replace('"', '\\"').replace('\n', ' ')
             title = f"{repo_name} - {clean_hook[:50]}..." if len(clean_hook) > 50 else f"{repo_name} - {clean_hook}"
        else:
            title = repo_name

        # Extract tags from topics or language
        topics = repo_data.get("topics", [])
        tags = topics[:5] if topics else [language.lower()] if language != "Unknown" else []

        # Ensure tags is a list of strings
        tags = [str(t) for t in tags]

        # Determine categories
        categories = self._determine_categories(tags, language)

        # Build frontmatter for Astro
        frontmatter = "---\n"
        frontmatter += f"title: \"{title}\"\n"
        frontmatter += f"date: {datetime.now().strftime('%Y-%m-%d')}\n"
        frontmatter += f"description: \"{description}\"\n"
        frontmatter += f"repo: {repo_full_name}\n"
        frontmatter += f"stars: {stars}\n"
        frontmatter += f"language: {language}\n"

        # Add tags
        if tags:
            frontmatter += f"tags: {json.dumps(tags)}\n"
        else:
            frontmatter += "tags: []\n"

        # Add categories
        if categories:
            frontmatter += f"categories: {json.dumps(categories)}\n"
            # Also add single category for backward compatibility (pick first)
            frontmatter += f"category: \"{categories[0]}\"\n"

        # Add repo_data (subset or full? Full is better for flexibility)
        # We need to serialize it safely.
        try:
            # Simple sanitization or just dump it if it's JSON serializable
            # We exclude 'owner' object if it has complex fields, but usually GitHub API dicts are fine.
            # However, to be safe, we can just pick important fields if needed,
            # but Astro schema says z.any(), so we can dump the whole thing.
            # But let's be careful about huge dumps.
            safe_repo_data = {
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "stargazers_count": repo_data.get("stargazers_count"),
                "language": repo_data.get("language"),
                "topics": repo_data.get("topics"),
                "updated_at": repo_data.get("updated_at"),
                "html_url": repo_data.get("html_url")
            }
            frontmatter += f"repo_data:\n"
            for k, v in safe_repo_data.items():
                if v is not None:
                    val_str = json.dumps(v)
                    frontmatter += f"  {k}: {val_str}\n"
        except Exception as e:
            self.logger.warning(f"Could not serialize repo_data: {e}")

        # Add images if provided
        if images:
            frontmatter += "images:\n"
            if images.get("architecture"):
                frontmatter += f"  architecture: {images['architecture']}\n"
            if images.get("flow"):
                frontmatter += f"  flow: {images['flow']}\n"
            if images.get("screenshot"):
                frontmatter += f"  screenshot: {images['screenshot']}\n"

        frontmatter += "---\n"

        return frontmatter

    def _format_content(self, script_data: Dict[str, Any]) -> str:
        """
        Format the main content of the post.

        Args:
            script_data: Script analysis data.

        Returns:
            Formatted Markdown content.
        """
        content = ""

        # Hook / Problem
        hook = script_data.get("hook", "")
        if hook:
            content += "## 🎯 The Problem\n\n"
            content += f"{hook}\n\n"

        # Solution
        solution = script_data.get("solution", "")
        if solution:
            content += "## 💡 The Solution\n\n"
            content += f"{solution}\n\n"

        # Pros
        pros = script_data.get("pros", [])
        if pros:
            content += "## ✅ Advantages\n\n"
            if isinstance(pros, list):
                for pro in pros:
                    content += f"- {pro}\n"
            else:
                content += f"{pros}\n"
            content += "\n"

        # Cons
        cons = script_data.get("cons", [])
        if cons:
            content += "## ⚠️ Considerations\n\n"
            if isinstance(cons, list):
                for con in cons:
                    content += f"- {con}\n"
            else:
                content += f"{cons}\n"
            content += "\n"

        # Verdict
        verdict = script_data.get("verdict", "")
        if verdict:
            content += "## 🎬 Verdict\n\n"
            content += f"{verdict}\n\n"

        # Narration (as a quote)
        narration = script_data.get("narration", "")
        if narration:
            content += "---\n\n"
            content += "### 📝 Full Narration\n\n"
            content += f"> {narration}\n\n"

        return content

    def validate_post(self, filepath: str) -> bool:
        """
        Validate that a generated post is well-formed.

        Args:
            filepath: Path to the Markdown file.

        Returns:
            True if valid, False otherwise.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for frontmatter
            if not content.startswith("---"):
                self.logger.error("Post missing frontmatter")
                return False

            # Check for required fields (Astro format)
            required_fields = ["title:", "date:", "repo:", "tags:"]
            for field in required_fields:
                if field not in content:
                    self.logger.error(f"Post missing required field: {field}")
                    return False

            self.logger.info(f"Post validation passed: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Post validation failed: {e}")
            return False
