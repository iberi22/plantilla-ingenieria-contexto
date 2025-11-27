"""
AI Code Reviewer using GitHub Models API (via GitHub Copilot subscription)
Uses the official GitHub Models REST API endpoint
"""
import json
import logging
import subprocess
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class GrokReviewer:
    """Uses GitHub Models API to perform code quality review"""

    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize with GitHub authentication

        Args:
            model: Model to use. Options: 'gpt-4o', 'gpt-4o-mini', 'claude-3.5-sonnet', 'o1', etc.
        """
        self.model = model
        self.api_endpoint = "https://models.inference.ai.azure.com/chat/completions"
        self.github_token = self._get_github_token()
        self.available = bool(self.github_token)

        if self.available:
            logger.info(f"✅ GitHub Models reviewer initialized (model: {self.model})")
        else:
            logger.warning("⚠️ GitHub token not available, AI reviewer disabled")
            logger.info("💡 Make sure GITHUB_TOKEN is set or gh CLI is authenticated")

    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from environment or gh CLI"""
        import os

        # Try environment variable first
        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token

        # Try gh CLI
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Failed to get token from gh CLI: {e}")

        return None

    def review_repository(self, repo, readme_content: str, recent_files: list) -> Optional[Dict]:
        """
        Perform AI-powered code review using GitHub Models

        Args:
            repo: PyGithub Repository object
            readme_content: Full README text
            recent_files: List of recently modified files with content samples

        Returns:
            Dictionary with review scores and insights, or None if failed
        """
        if not self.available:
            return None

        try:
            # Build context
            context = self._build_context(repo, readme_content, recent_files)

            # Create prompt
            prompt = self._create_review_prompt(context)

            # Call GitHub Models API with retry
            response = self._call_model_with_retry(prompt)

            if response:
                # Parse response
                scores = self._parse_ai_response(response)
                return scores

            return None

        except Exception as e:
            logger.error(f"Error during AI review: {e}")
            return None

    def _build_context(self, repo, readme_content: str, recent_files: list) -> Dict:
        """Build context dictionary for AI"""
        return {
            "name": repo.name,
            "description": repo.description or "",
            "language": repo.language,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "topics": ", ".join(repo.get_topics()[:5]),
            "readme": readme_content[:3000],  # First 3000 chars
            "recent_files": recent_files[:3],  # Top 3 files
            "has_license": bool(repo.license),
            "has_wiki": repo.has_wiki,
        }

    def _create_review_prompt(self, context: Dict) -> str:
        """Create the review prompt for AI"""
        return f"""Analyze this GitHub repository and provide a quality assessment.

Repository: {context['name']}
Description: {context['description']}
Language: {context['language']}
Stars: {context['stars']} | Forks: {context['forks']}
Topics: {context['topics']}
License: {'Yes' if context['has_license'] else 'No'}

README excerpt:
{context['readme']}

Evaluate the project on these 5 dimensions (score 1-10 each):
1. Architecture: Code structure, modularity, design patterns
2. Documentation: README quality, comments, guides
3. Testing: Test coverage, CI/CD, quality assurance
4. Best Practices: Code style, security, performance
5. Innovation: Uniqueness, problem-solving approach

Also provide:
- 3 key strengths
- 3 areas for improvement
- Overall assessment (1 sentence)

Respond ONLY with valid JSON:
{{
  "architecture_score": <1-10>,
  "documentation_score": <1-10>,
  "testing_score": <1-10>,
  "practices_score": <1-10>,
  "innovation_score": <1-10>,
  "key_strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "assessment": "one sentence summary"
}}"""

    def _call_model_with_retry(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """Call GitHub Models API with retry"""
        import requests

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🤖 Calling GitHub Models API (attempt {attempt}/{max_retries})...")

                headers = {
                    "Authorization": f"Bearer {self.github_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a code review expert. Respond only with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": self.model,
                    "temperature": 0.3,
                    "max_tokens": 800
                }

                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    logger.info("✅ GitHub Models API call successful")
                    return content
                else:
                    error_msg = response.text
                    logger.warning(f"GitHub Models API error {response.status_code}: {error_msg}")

                    if attempt < max_retries:
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)

            except requests.exceptions.Timeout:
                logger.warning(f"GitHub Models API timeout (attempt {attempt})")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.warning(f"GitHub Models API call failed (attempt {attempt}): {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)

        logger.error("Max retries reached for GitHub Models API")
        return None

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI JSON response"""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip() in ['```json', '```']:
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                response_text = '\n'.join(json_lines)

            # Try to find JSON object in text
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]

            # Parse JSON
            data = json.loads(response_text)

            # Validate required fields
            required = ['architecture_score', 'documentation_score', 'testing_score',
                       'practices_score', 'innovation_score']

            if not all(field in data for field in required):
                logger.error("Missing required fields in AI response")
                return self._default_scores()

            # Ensure scores are in range 1-10
            for field in required:
                data[field] = max(1, min(10, int(data[field])))

            return {
                'architecture': data['architecture_score'],
                'documentation': data['documentation_score'],
                'testing': data['testing_score'],
                'practices': data['practices_score'],
                'innovation': data['innovation_score'],
                'key_strengths': data.get('key_strengths', [])[:3],
                'improvements': data.get('improvements', [])[:3],
                'assessment': data.get('assessment', '')
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            return self._default_scores()
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._default_scores()

    def _default_scores(self) -> Dict:
        """Return default scores when AI fails"""
        return {
            'architecture': 5,
            'documentation': 5,
            'testing': 5,
            'practices': 5,
            'innovation': 5,
            'key_strengths': [],
            'improvements': [],
            'assessment': 'Unable to complete AI review'
        }

    def calculate_quality_score(self, ai_scores: Dict) -> float:
        """
        Calculate overall quality score from AI review scores
        
        Args:
            ai_scores: Dictionary with individual scores
            
        Returns:
            Overall quality score (0-100)
        """
        if not ai_scores:
            return 50.0
        
        # Average the 5 scores (each 1-10) and convert to 0-100
        scores = [
            ai_scores.get('architecture', 5),
            ai_scores.get('documentation', 5),
            ai_scores.get('testing', 5),
            ai_scores.get('practices', 5),
            ai_scores.get('innovation', 5)
        ]
        
        avg_score = sum(scores) / len(scores)
        return (avg_score / 10.0) * 100.0
