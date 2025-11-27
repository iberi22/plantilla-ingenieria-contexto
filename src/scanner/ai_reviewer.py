"""
AI Code Reviewer using Google Gemini for hidden gems analysis
"""
import json
import logging
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AIReviewer:
    """Uses Gemini AI to perform code quality review"""

    def __init__(self, google_api_key: str):
        """Initialize with Gemini API key"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            # Using gemini-2.0-flash-exp for latest features
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.available = True
            logger.info("✅ Gemini AI reviewer initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.available = False

    def review_repository(self, repo, readme_content: str, recent_files: list) -> Optional[Dict]:
        """
        Perform AI-powered code review

        Args:
            repo: PyGithub Repository object
            readme_content: Full README text
            recent_files: List of recently modified files with content samples

        Returns:
            Dict with scores and analysis, or None if review fails
        """
        if not self.available:
            logger.warning("AI reviewer not available")
            return None

        try:
            # Build context for AI
            context = self._build_review_context(repo, readme_content, recent_files)

            # Generate prompt
            prompt = self._create_review_prompt(context)

            # Call Gemini with retry logic
            response = self._call_gemini_with_retry(prompt)

            if response:
                # Parse and validate response
                scores = self._parse_ai_response(response)
                return scores

            return None

        except Exception as e:
            logger.error(f"Error during AI review: {e}")
            return None

    def _build_review_context(self, repo, readme_content: str, recent_files: list) -> Dict:
        """Gather context information for AI review"""
        context = {
            "repo_name": repo.full_name,
            "description": repo.description or "No description",
            "language": repo.language or "Unknown",
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "readme": readme_content[:3000],  # First 3000 chars
            "topics": repo.get_topics(),
            "has_wiki": repo.has_wiki,
            "has_pages": repo.has_pages,
        }

        # Add file samples
        if recent_files:
            context["file_samples"] = recent_files[:5]  # Max 5 files

        # Get recent commit messages
        try:
            commits = list(repo.get_commits()[:10])
            context["recent_commits"] = [
                {
                    "message": c.commit.message[:200],
                    "author": c.commit.author.name if c.commit.author else "Unknown"
                }
                for c in commits
            ]
        except:
            context["recent_commits"] = []

        return context

    def _create_review_prompt(self, context: Dict) -> str:
        """Create the review prompt for Gemini"""

        file_samples = ""
        if context.get("file_samples"):
            file_samples = "\n\n## Code Samples\n"
            for file in context["file_samples"]:
                file_samples += f"\n### {file['path']}\n```{file.get('language', '')}\n{file['content'][:500]}\n```\n"

        commits = ""
        if context.get("recent_commits"):
            commits = "\n\n## Recent Commits\n"
            for commit in context["recent_commits"][:5]:
                commits += f"- {commit['message']} (by {commit['author']})\n"

        prompt = f"""You are an expert code reviewer analyzing a GitHub repository to determine if it's a "hidden gem" - a quality project that deserves more visibility.

## Repository Information
- **Name**: {context['repo_name']}
- **Description**: {context['description']}
- **Language**: {context['language']}
- **Stars**: {context['stars']} | **Forks**: {context['forks']}
- **Topics**: {', '.join(context.get('topics', []))}

## README (first 3000 chars)
{context['readme']}
{file_samples}
{commits}

## Your Task
Analyze this repository across 5 dimensions and provide scores from 1-10 for each:

1. **architecture_quality**: Code organization, separation of concerns, modularity, design patterns
2. **documentation_quality**: README clarity, code comments, API docs, examples, setup instructions
3. **testing_coverage**: Presence of tests, test quality, CI/CD integration
4. **best_practices**: Error handling, security practices, performance considerations, idiomatic code
5. **innovation_value**: Uniqueness, problem-solving approach, potential impact, novelty

## Scoring Guidelines
- **1-3**: Poor/Missing - Significant issues or completely absent
- **4-6**: Average - Present but with notable gaps or mediocrity
- **7-8**: Good - Well implemented with minor improvements possible
- **9-10**: Excellent - Exceptional quality, exemplary practices

## Output Format
Respond with ONLY a valid JSON object (no markdown, no explanations):

{{
  "architecture_quality": 8,
  "documentation_quality": 7,
  "testing_coverage": 6,
  "best_practices": 8,
  "innovation_value": 9,
  "summary": "Brief 2-3 sentence summary of key strengths and concerns",
  "recommendation": "APPROVE/REVIEW/REJECT",
  "key_strengths": ["strength 1", "strength 2", "strength 3"],
  "concerns": ["concern 1", "concern 2"]
}}

Analyze now and respond with JSON only:"""

        return prompt

    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Gemini API with retry logic"""

        for attempt in range(max_retries):
            try:
                logger.info(f"🤖 Calling Gemini AI (attempt {attempt + 1}/{max_retries})...")

                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.3,  # Lower temperature for more consistent scoring
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 1024,
                    }
                )

                if response and response.text:
                    logger.info("✅ Gemini response received")
                    return response.text

            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt + 1}): {e}")

                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached")

        return None

    def _parse_ai_response(self, response_text: str) -> Optional[Dict]:
        """Parse and validate AI response"""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            # Parse JSON
            data = json.loads(response_text)

            # Validate required fields
            required_scores = [
                "architecture_quality",
                "documentation_quality",
                "testing_coverage",
                "best_practices",
                "innovation_value"
            ]

            for field in required_scores:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return None

                score = data[field]
                if not isinstance(score, (int, float)) or score < 1 or score > 10:
                    logger.error(f"Invalid score for {field}: {score}")
                    return None

            # Calculate aggregate score
            total_score = sum(data[field] for field in required_scores)
            avg_score = total_score / len(required_scores)

            data["aggregate_score"] = round(avg_score, 2)
            data["total_score"] = round(total_score, 2)

            logger.info(f"✅ AI scores parsed: {avg_score:.2f}/10 average")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return None

    def calculate_quality_score(self, ai_scores: Dict) -> float:
        """
        Convert AI scores to 0-100 quality score for gem analyzer

        AI scores are 1-10, we normalize to 0-100 with weighting
        """
        if not ai_scores:
            return 0

        # Weights for different aspects
        weights = {
            "architecture_quality": 0.25,
            "documentation_quality": 0.20,
            "testing_coverage": 0.20,
            "best_practices": 0.20,
            "innovation_value": 0.15
        }

        total = 0
        for field, weight in weights.items():
            if field in ai_scores:
                # Normalize 1-10 to 0-100, then apply weight
                normalized = ((ai_scores[field] - 1) / 9) * 100
                total += normalized * weight

        return round(total, 2)
