"""Quick test for GrokReviewer GitHub Models API"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scanner.grok_reviewer import GrokReviewer

print("=" * 50)
print("Testing GrokReviewer with GitHub Models API")
print("=" * 50)

reviewer = GrokReviewer(model="gpt-4o")

print(f"\n✅ Reviewer initialized")
print(f"   Available: {reviewer.available}")
print(f"   Model: {reviewer.model}")
print(f"   Endpoint: {reviewer.api_endpoint}")

if reviewer.github_token:
    print(f"   Token: {reviewer.github_token[:10]}...{reviewer.github_token[-10:]}")
else:
    print(f"   Token: None")

print("\n" + "=" * 50)
