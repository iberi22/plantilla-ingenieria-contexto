"""Test real GitHub Models API call"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scanner.grok_reviewer import GrokReviewer

print("=" * 60)
print("Testing GitHub Models API - Real Call")
print("=" * 60)

reviewer = GrokReviewer(model="gpt-4o")

if not reviewer.available:
    print("❌ Reviewer not available - check authentication")
    sys.exit(1)

# Create a simple test prompt
test_prompt = """Analyze this GitHub repository and provide a quality assessment.

Repository: test-repo
Description: A simple Python CLI tool
Language: Python
Stars: 100 | Forks: 20
Topics: python, cli, tool
License: Yes

README excerpt:
# Test Repo
A Python command-line tool for testing purposes.

## Features
- Simple CLI interface
- Well documented
- Active development

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
{
  "architecture_score": <1-10>,
  "documentation_score": <1-10>,
  "testing_score": <1-10>,
  "practices_score": <1-10>,
  "innovation_score": <1-10>,
  "key_strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "assessment": "one sentence summary"
}"""

print("\n📡 Making API call to GitHub Models...")
response = reviewer._call_model_with_retry(test_prompt, max_retries=1)

if response:
    print("\n✅ API call successful!")
    print("\n📄 Raw response:")
    print("-" * 60)
    print(response[:500] + ("..." if len(response) > 500 else ""))
    print("-" * 60)

    print("\n🔍 Parsing response...")
    scores = reviewer._parse_ai_response(response)

    print("\n📊 Parsed scores:")
    print(f"   Architecture: {scores['architecture']}/10")
    print(f"   Documentation: {scores['documentation']}/10")
    print(f"   Testing: {scores['testing']}/10")
    print(f"   Practices: {scores['practices']}/10")
    print(f"   Innovation: {scores['innovation']}/10")

    if scores.get('key_strengths'):
        print(f"\n✅ Strengths: {len(scores['key_strengths'])}")
        for s in scores['key_strengths']:
            print(f"   - {s}")

    if scores.get('assessment'):
        print(f"\n💬 Assessment: {scores['assessment']}")
else:
    print("\n❌ API call failed")

print("\n" + "=" * 60)
