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
            # Determine category for folder structure
            categories = self._determine_categories(
                repo_data.get("topics", []),
                repo_data.get("language", "Unknown")
            )
            primary_category = categories[0].lower().replace(" ", "-") if categories else "general"

            # Generate filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            repo_name = repo_data.get("name", "unknown").lower().replace(" ", "-")
            filename = f"{date_str}-{repo_name}.md"

            # Create category directory
            category_dir = self.output_dir / primary_category
            category_dir.mkdir(parents=True, exist_ok=True)

            filepath = category_dir / filename

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
            List of category strings. First one is primary.
        """
        categories = []
        tags_lower = [t.lower() for t in tags]
        lang_lower = language.lower() if language else ""

        # AI & ML
        if any(k in tags_lower for k in ["ai", "machine-learning", "llm", "gpt", "openai", "finetuning", "rag", "model"]):
            categories.append("AI")

        # MCP (Model Context Protocol)
        if "mcp" in tags_lower or "model-context-protocol" in tags_lower:
            categories.append("MCP")

        # Cybersecurity
        if any(k in tags_lower for k in ["security", "hacking", "pentesting", "malware", "encryption", "auth"]):
            categories.append("Cybersecurity")

        # Web UI
        if any(k in tags_lower for k in ["react", "vue", "svelte", "css", "ui", "frontend", "web", "html", "tailwind"]):
            categories.append("Web UI")

        # Mobile
        if any(k in tags_lower for k in ["mobile", "android", "ios", "flutter", "react-native", "swift", "kotlin"]):
            categories.append("Mobile")

        # DevOps & Cloud
        if any(k in tags_lower for k in ["docker", "kubernetes", "devops", "cloud", "aws", "azure", "terraform"]):
            categories.append("DevOps")

        # Fallback based on language
        if not categories:
            if "python" in lang_lower:
                categories.append("Development")
            elif "javascript" in lang_lower or "typescript" in lang_lower:
                categories.append("Web UI")
            elif "rust" in lang_lower or "go" in lang_lower:
                categories.append("Systems")
            else:
                categories.append("General")

        return categories

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

        # Use Cases
        use_cases = script_data.get("use_cases", [])
        if use_cases:
            content += "## 🚀 Use Cases\n\n"
            if isinstance(use_cases, list):
                for case in use_cases:
                    content += f"- {case}\n"
            else:
                content += f"{use_cases}\n"
            content += "\n"

        # Evaluation Method
        content += "## 📊 Evaluation Method\n\n"
        content += "Our analysis engine evaluates open source projects on four key dimensions:\n\n"
        content += "1.  **Commit Activity:** Frequency and consistency of updates.\n"
        content += "2.  **Code Quality:** Adherence to best practices, documentation, and testing.\n"
        content += "3.  **Developer Engagement:** Community interaction, issues, and PR management.\n"
        content += "4.  **Project Maturity:** Stability, longevity, and release history.\n\n"

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

        # Cons / Improvements
        cons = script_data.get("cons", [])
        if cons:
            content += "## ⚠️ Areas for Improvement\n\n"
            if isinstance(cons, list):
                for con in cons:
                    content += f"- {con}\n"
            else:
                content += f"{cons}\n"
            content += "\n"

        # Similar Projects
        similar = script_data.get("similar_projects", [])
        if similar:
            content += "## 🔄 Similar Projects\n\n"
            content += "Here are some other projects we've scanned that solve similar problems:\n\n"
            for sim in similar:
                name = sim.get('name', 'Unknown')
                url = sim.get('url', '#')
                desc = sim.get('description', '')
                content += f"- **[{name}]({url})**: {desc}\n"
            content += "\n"

        # Verdict
        verdict = script_data.get("verdict", "")
        if verdict:
            content += "## 🎬 Verdict\n\n"
            content += f"{verdict}\n\n"

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
