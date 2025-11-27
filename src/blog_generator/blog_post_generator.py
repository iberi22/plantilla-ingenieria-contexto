"""
Blog Post Generator - Generates complete blog posts from analysis data.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from .markdown_writer import MarkdownWriter


class BlogPostGenerator:
    """
    High-level blog post generator that coordinates data transformation
    and markdown generation.
    """

    def __init__(self, output_dir: str = "website/src/content/blog"):
        """
        Initialize BlogPostGenerator.

        Args:
            output_dir: Directory to save generated posts.
        """
        self.logger = logging.getLogger(__name__)
        self.writer = MarkdownWriter(output_dir)

    def generate_blog_post(self, script_data: Dict[str, Any]) -> str:
        """
        Generate a blog post from script/analysis data.

        Args:
            script_data: Dictionary containing:
                - repo_name: Repository full name (owner/repo)
                - repo_url: GitHub URL
                - description: Short description
                - language: Programming language
                - stars: Star count
                - forks: Fork count
                - total_score: Overall score
                - commit_activity_score: Commit activity score
                - code_quality_score: Code quality score
                - developer_engagement_score: Developer engagement score
                - project_maturity_score: Project maturity score
                - architecture_score: AI architecture score (optional)
                - documentation_score: AI documentation score (optional)
                - testing_score: AI testing score (optional)
                - best_practices_score: AI best practices score (optional)
                - innovation_score: AI innovation score (optional)
                - ai_reasoning: AI review reasoning (optional)
                - strengths: List of strengths (optional)
                - weaknesses: List of weaknesses (optional)
                - readme_excerpt: Excerpt from README
                - topics: List of GitHub topics
                - license: License name
                - created_at: Creation date
                - updated_at: Last update date

        Returns:
            Markdown content string.
        """
        try:
            # Transform script_data into repo_data format
            repo_data = self._transform_to_repo_data(script_data)

            # Generate content sections from analysis
            content_script_data = self._generate_content_sections(script_data)

            # Use MarkdownWriter to create the post
            filepath = self.writer.create_post(
                repo_data=repo_data,
                script_data=content_script_data,
                images=None  # No images for now
            )

            # Read and return content
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            self.logger.error(f"Failed to generate blog post: {e}")
            raise

    def _transform_to_repo_data(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform script_data to repo_data format expected by MarkdownWriter.

        Args:
            script_data: Analysis data.

        Returns:
            Repository data dictionary.
        """
        repo_name = script_data.get('repo_name', 'unknown/unknown')
        parts = repo_name.split('/')
        owner = parts[0] if len(parts) > 0 else 'unknown'
        name = parts[1] if len(parts) > 1 else 'unknown'

        return {
            'full_name': repo_name,
            'name': name,
            'owner': {'login': owner},
            'description': script_data.get('description', ''),
            'stargazers_count': script_data.get('stars', 0),
            'forks_count': script_data.get('forks', 0),
            'open_issues_count': script_data.get('open_issues', 0),
            'language': script_data.get('language', 'Unknown'),
            'topics': script_data.get('topics', []),
            'license': {'name': script_data.get('license', 'Unknown')},
            'html_url': script_data.get('repo_url', f"https://github.com/{repo_name}"),
            'created_at': script_data.get('created_at', ''),
            'updated_at': script_data.get('updated_at', ''),
        }

    def _generate_content_sections(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content sections from analysis data.

        Args:
            script_data: Analysis data.

        Returns:
            Dictionary with content sections for MarkdownWriter.
        """
        repo_name = script_data.get('repo_name', 'Unknown Repository')
        total_score = script_data.get('total_score', 0)
        language = script_data.get('language', 'Unknown')

        # Generate hook
        hook = self._generate_hook(script_data)

        # Generate solution/overview
        solution = self._generate_solution(script_data)

        # Generate pros (strengths + high scores)
        pros = self._generate_pros(script_data)

        # Generate cons (weaknesses + low scores)
        cons = self._generate_cons(script_data)

        # Generate verdict
        verdict = self._generate_verdict(script_data)

        return {
            'hook': hook,
            'solution': solution,
            'pros': pros,
            'cons': cons,
            'verdict': verdict,
        }

    def _generate_hook(self, script_data: Dict[str, Any]) -> str:
        """Generate engaging hook from description and scores."""
        description = script_data.get('description', '')
        total_score = script_data.get('total_score', 0)
        stars = script_data.get('stars', 0)
        language = script_data.get('language', 'Unknown')

        if description:
            return (
                f"Looking for a high-quality {language} project? "
                f"With a score of {total_score:.1f}/100 and {stars:,} stars, "
                f"this repository delivers: {description}"
            )
        else:
            return (
                f"A {language} project scoring {total_score:.1f}/100 with {stars:,} stars. "
                f"Let's explore what makes it stand out."
            )

    def _generate_solution(self, script_data: Dict[str, Any]) -> str:
        """Generate solution/overview from README and analysis."""
        readme = script_data.get('readme_excerpt', '')
        ai_reasoning = script_data.get('ai_reasoning', '')

        sections = []

        if readme:
            sections.append(readme)

        if ai_reasoning:
            sections.append(f"\n**AI Analysis:** {ai_reasoning}")

        # Add score breakdown
        commit_score = script_data.get('commit_activity_score', 0)
        quality_score = script_data.get('code_quality_score', 0)
        engagement_score = script_data.get('developer_engagement_score', 0)
        maturity_score = script_data.get('project_maturity_score', 0)

        sections.append(
            f"\n**Score Breakdown:**\n"
            f"- Commit Activity: {commit_score:.1f}%\n"
            f"- Code Quality: {quality_score:.1f}%\n"
            f"- Developer Engagement: {engagement_score:.1f}%\n"
            f"- Project Maturity: {maturity_score:.1f}%"
        )

        return '\n'.join(sections)

    def _generate_pros(self, script_data: Dict[str, Any]) -> list:
        """Generate list of advantages/strengths."""
        pros = []

        # Add AI strengths
        strengths = script_data.get('strengths', [])
        pros.extend(strengths)

        # Add notable scores
        commit_score = script_data.get('commit_activity_score', 0)
        quality_score = script_data.get('code_quality_score', 0)
        engagement_score = script_data.get('developer_engagement_score', 0)
        maturity_score = script_data.get('project_maturity_score', 0)

        if commit_score >= 70:
            pros.append(f"🔥 Active development with {commit_score:.0f}% commit activity")

        if quality_score >= 70:
            pros.append(f"✨ High code quality ({quality_score:.0f}%) with proper documentation and tests")

        if engagement_score >= 70:
            pros.append(f"👥 Strong community engagement ({engagement_score:.0f}%)")

        if maturity_score >= 70:
            pros.append(f"🎯 Mature and stable project ({maturity_score:.0f}%)")

        # AI scores
        arch_score = script_data.get('architecture_score', 0)
        doc_score = script_data.get('documentation_score', 0)
        test_score = script_data.get('testing_score', 0)

        if arch_score >= 7:
            pros.append(f"🏗️ Excellent architecture (AI: {arch_score}/10)")

        if doc_score >= 7:
            pros.append(f"📚 Well documented (AI: {doc_score}/10)")

        if test_score >= 7:
            pros.append(f"🧪 Comprehensive testing (AI: {test_score}/10)")

        return pros if pros else ["Quality open source project"]

    def _generate_cons(self, script_data: Dict[str, Any]) -> list:
        """Generate list of considerations/weaknesses."""
        cons = []

        # Add AI weaknesses
        weaknesses = script_data.get('weaknesses', [])
        cons.extend(weaknesses)

        # Add notable low scores
        commit_score = script_data.get('commit_activity_score', 0)
        quality_score = script_data.get('code_quality_score', 0)
        engagement_score = script_data.get('developer_engagement_score', 0)

        if commit_score < 50:
            cons.append(f"⚠️ Low commit activity ({commit_score:.0f}%)")

        if quality_score < 50:
            cons.append(f"⚠️ Limited documentation or tests ({quality_score:.0f}%)")

        if engagement_score < 50:
            cons.append(f"⚠️ Limited community engagement ({engagement_score:.0f}%)")

        return cons if cons else ["No major concerns identified"]

    def _generate_verdict(self, script_data: Dict[str, Any]) -> str:
        """Generate final verdict/recommendation."""
        total_score = script_data.get('total_score', 0)
        repo_name = script_data.get('repo_name', 'This repository')
        repo_url = script_data.get('repo_url', '#')

        if total_score >= 80:
            verdict = (
                f"**Highly Recommended!** {repo_name} scores {total_score:.1f}/100, "
                f"demonstrating excellence across all metrics. A must-check for developers "
                f"looking for quality open source projects."
            )
        elif total_score >= 70:
            verdict = (
                f"**Recommended.** With a score of {total_score:.1f}/100, {repo_name} "
                f"shows strong potential and solid fundamentals. Worth exploring for your next project."
            )
        else:
            verdict = (
                f"**Worth Exploring.** Scoring {total_score:.1f}/100, {repo_name} "
                f"has potential but may need further evaluation based on your specific needs."
            )

        verdict += f"\n\n[🔗 View on GitHub]({repo_url})"

        return verdict
