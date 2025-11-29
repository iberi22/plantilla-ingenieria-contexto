"""
AI Code Reviewer using Google Gemini API
Uses multiple API keys for load balancing and better rate limits
"""
import json
import logging
import os
import time
from typing import Dict, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiReviewer:
    """Uses Google Gemini API to perform code quality review with key rotation"""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """
        Initialize with Gemini API keys
        
        Args:
            model: Model to use. Options: 'gemini-2.0-flash', 'gemini-1.5-pro', etc.
        """
        self.model_name = model
        self.api_keys = self._collect_api_keys()
        self.current_key_index = 0
        self.available = len(self.api_keys) > 0
        
        if self.available:
            self._configure_current_key()
            logger.info(f"✅ Gemini reviewer initialized with {len(self.api_keys)} API keys (model: {self.model_name})")
        else:
            logger.warning("⚠️ No Gemini API keys found, AI reviewer disabled")
            logger.info("💡 Set GOOGLE_API_KEY, GOOGLE_API_KEY_2, GOOGLE_API_KEY_3 environment variables")

    def _collect_api_keys(self) -> List[str]:
        """Collect all available API keys from environment"""
        keys = []
        
        # Main key
        main_key = os.environ.get("GOOGLE_API_KEY")
        if main_key:
            keys.append(main_key)
        
        # Additional keys (2-5)
        for i in range(2, 6):
            key = os.environ.get(f"GOOGLE_API_KEY_{i}")
            if key:
                keys.append(key)
        
        return keys

    def _configure_current_key(self):
        """Configure Gemini with the current API key"""
        if self.api_keys:
            genai.configure(api_key=self.api_keys[self.current_key_index])

    def _rotate_key(self):
        """Rotate to the next available API key"""
        if len(self.api_keys) <= 1:
            return
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self._configure_current_key()
        logger.info(f"🔄 Rotated to Gemini API key #{self.current_key_index + 1}")

    def review_repository(self, repo, readme_content: str, recent_files: list) -> Optional[Dict]:
        """
        Perform AI-powered code review using Gemini

        Args:
            repo: Repository object with name, description, language, etc.
            readme_content: Full README text
            recent_files: List of recently modified files (not used currently)

        Returns:
            Dictionary with review scores and insights, or None if failed
        """
        if not self.available:
            return None

        try:
            # Build context
            context = self._build_context(repo, readme_content)
            
            # Create prompt
            prompt = self._create_review_prompt(context)
            
            # Call Gemini API with retry and key rotation
            response = self._call_gemini_with_retry(prompt)
            
            if response:
                scores = self._parse_ai_response(response)
                return scores
            
            return None

        except Exception as e:
            logger.error(f"Error during AI review: {e}")
            return None

    def _build_context(self, repo, readme_content: str) -> Dict:
        """Build context dictionary for AI"""
        # Handle both PyGithub objects and mock objects
        topics = []
        if hasattr(repo, 'get_topics'):
            try:
                topics = repo.get_topics()[:5]
            except:
                topics = getattr(repo, '_topics', [])[:5]
        
        return {
            "name": repo.name,
            "description": repo.description or "",
            "language": repo.language or "Unknown",
            "stars": getattr(repo, 'stargazers_count', 0),
            "forks": getattr(repo, 'forks_count', 0),
            "topics": ", ".join(topics) if topics else "None",
            "readme": readme_content[:4000],  # First 4000 chars for Gemini
            "has_license": bool(getattr(repo, 'license', False)),
        }

    def _create_review_prompt(self, context: Dict) -> str:
        """Create the review prompt for Gemini"""
        return f"""You are an expert code reviewer analyzing open source projects. Provide a quality assessment for this GitHub repository.

## Repository Information
- **Name**: {context['name']}
- **Description**: {context['description']}
- **Primary Language**: {context['language']}
- **Stars**: {context['stars']} | **Forks**: {context['forks']}
- **Topics**: {context['topics']}
- **Has License**: {'Yes' if context['has_license'] else 'No'}

## README Content
```
{context['readme']}
```

## Evaluation Criteria
Evaluate this project on these 5 dimensions (score 1-10 each):

1. **Architecture** (1-10): Code structure, modularity, design patterns, scalability
2. **Documentation** (1-10): README quality, code comments, API docs, examples
3. **Testing** (1-10): Test coverage indicators, CI/CD presence, quality assurance
4. **Best Practices** (1-10): Code style, security considerations, performance awareness
5. **Innovation** (1-10): Uniqueness, creative problem-solving, value proposition

Also provide:
- 3 key strengths of the project
- 3 areas for improvement
- A one-sentence overall assessment

## Response Format
Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "architecture_score": <1-10>,
  "documentation_score": <1-10>,
  "testing_score": <1-10>,
  "practices_score": <1-10>,
  "innovation_score": <1-10>,
  "key_strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "assessment": "one sentence overall assessment"
}}"""

    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Gemini API with retry and key rotation"""
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🤖 Calling Gemini API (attempt {attempt}/{max_retries}, key #{self.current_key_index + 1})...")
                
                model = genai.GenerativeModel(self.model_name)
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=1000,
                    )
                )
                
                if response and response.text:
                    logger.info("✅ Gemini API call successful")
                    # Rotate key after success to distribute load
                    self._rotate_key()
                    return response.text
                else:
                    logger.warning("Gemini returned empty response")
                    self._rotate_key()
                    
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Gemini API error (attempt {attempt}): {error_msg}")
                
                # Rotate key on error
                self._rotate_key()
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        logger.error("Max retries reached for Gemini API")
        return None

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI JSON response"""
        try:
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
            
            # Find JSON object
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
            
            data = json.loads(response_text)
            
            # Validate and normalize scores
            required = ['architecture_score', 'documentation_score', 'testing_score',
                       'practices_score', 'innovation_score']
            
            for field in required:
                if field not in data:
                    data[field] = 5  # Default score
                else:
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
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            return self._default_scores()
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
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
        """Calculate overall quality score (0-100) from individual scores"""
        if not ai_scores:
            return 50.0
        
        scores = [
            ai_scores.get('architecture', 5),
            ai_scores.get('documentation', 5),
            ai_scores.get('testing', 5),
            ai_scores.get('practices', 5),
            ai_scores.get('innovation', 5)
        ]
        
        return (sum(scores) / len(scores)) * 10.0
