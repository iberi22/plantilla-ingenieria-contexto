"""
Markdown Writer for generating blog posts from repository data.

This module creates Jekyll-compatible Markdown posts with YAML frontmatter.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


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

    def _format_frontmatter(
        self,
        repo_data: Dict[str, Any],
        script_data: Dict[str, Any],
        images: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Format YAML frontmatter for Jekyll.

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
        stars = repo_data.get("stargazers_count", 0)
        language = repo_data.get("language", "Unknown")

        # Create title from hook
        hook = script_data.get("hook", "")
        title = f"{repo_name} - {hook[:50]}..." if len(hook) > 50 else f"{repo_name} - {hook}"

        # Extract tags from topics or language
        topics = repo_data.get("topics", [])
        tags = topics[:5] if topics else [language.lower()] if language else []

        # Build frontmatter for Astro
        frontmatter = "---\n"
        frontmatter += f"title: \"{title}\"\n"
        frontmatter += f"date: {datetime.now().strftime('%Y-%m-%d')}\n"
        frontmatter += f"description: \"{description.replace('\"', '\\\"')}\"\n"
        frontmatter += f"repo: {repo_full_name}\n"
        frontmatter += f"stars: {stars}\n"
        frontmatter += f"language: {language}\n"

        # Astro Schema: repo_data object
        frontmatter += "repo_data:\n"
        frontmatter += f"  full_name: {repo_full_name}\n"
        frontmatter += f"  description: \"{description.replace('\"', '\\\"')}\"\n"
        frontmatter += f"  stars: {stars}\n"
        frontmatter += f"  language: {language}\n"
        frontmatter += f"  url: {repo_data.get('html_url', '')}\n"
        frontmatter += f"  owner: {repo_data.get('owner', {}).get('login', '')}\n"

        if tags:
            frontmatter += f"tags: [{', '.join(tags)}]\n"
            frontmatter += f"categories: [{', '.join(tags[:2])}]\n" # Use first 2 tags as categories

        # Add images if provided
        if images:
            frontmatter += "images:\n"
            if images.get("architecture"):
                frontmatter += f"  architecture: {images['architecture']}\n"
            if images.get("flow"):
                frontmatter += f"  flow: {images['flow']}\n"
            if images.get("screenshot"):
                frontmatter += f"  screenshot: {images['screenshot']}\n"

        # Add video placeholder (will be filled later)
        # frontmatter += f"video: /assets/videos/{repo_name.lower()}-reel.mp4\n"

        frontmatter += "---"

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
            required_fields = ["title:", "date:", "repo:"]
            for field in required_fields:
                if field not in content:
                    self.logger.error(f"Post missing required field: {field}")
                    return False

            self.logger.info(f"Post validation passed: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Post validation failed: {e}")
            return False
