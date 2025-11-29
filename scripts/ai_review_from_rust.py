#!/usr/bin/env python3
"""
AI Review from Rust Analysis
Consumes Rust analysis JSON and adds AI reviews using GitHub Models API.
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scanner.gemini_reviewer import GeminiReviewer


class MockRepo:
    """Mock PyGithub Repository object for use with GrokReviewer"""
    def __init__(self, name: str, description: str, language: str, stars: int, 
                 forks: int = 0, topics: list = None, has_license: bool = True, has_wiki: bool = False):
        self.name = name
        self.description = description or ""
        self.language = language or "Unknown"
        self.stargazers_count = stars
        self.forks_count = forks
        self._topics = topics or []
        self.license = has_license
        self.has_wiki = has_wiki
    
    def get_topics(self):
        return self._topics


def main():
    if len(sys.argv) != 3:
        print("Usage: ai_review_from_rust.py <rust_results.json> <output.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"📥 Loading Rust analysis from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        analyses = json.load(f)
    
    print(f"📊 Found {len(analyses)} repositories to review")
    
    # Initialize AI reviewer with Gemini (high quality reviews)
    reviewer = GeminiReviewer(model="gemini-2.0-flash")
    
    # Add AI reviews to approved repos
    reviewed = []
    for idx, analysis in enumerate(analyses, 1):
        repo = analysis['repo']
        recommendation = analysis['recommendation']
        
        print(f"\n[{idx}/{len(analyses)}] {repo} - {recommendation}")
        
        # Only do AI review for APPROVE/REVIEW candidates
        if recommendation in ['APPROVE', 'REVIEW']:
            try:
                print(f"  🤖 Running AI review...")
                
                # Get repository details
                owner, name = repo.split('/')
                
                # Create mock repo object for GrokReviewer
                mock_repo = MockRepo(
                    name=name,
                    description=analysis['metadata'].get('description', ''),
                    language=analysis['metadata'].get('language'),
                    stars=analysis['metadata']['stars'],
                    forks=analysis['metadata'].get('forks', 0),
                    topics=analysis['metadata'].get('topics', [])
                )
                
                readme_content = analysis['metadata'].get('readme', '')[:3000]
                
                # Call AI review with proper parameters
                ai_scores = reviewer.review_repository(
                    mock_repo,
                    readme_content,
                    []  # recent_files - not available from Rust scan
                )
                
                # Add AI scores to analysis
                if ai_scores:
                    analysis['ai_review'] = {
                        'architecture': ai_scores.get('architecture', 0),
                        'documentation': ai_scores.get('documentation', 0),
                        'testing': ai_scores.get('testing', 0),
                        'best_practices': ai_scores.get('practices', 0),
                        'innovation': ai_scores.get('innovation', 0),
                        'quality_score': reviewer.calculate_quality_score(ai_scores),
                        'reasoning': ai_scores.get('assessment', ''),
                        'strengths': ai_scores.get('key_strengths', []),
                        'weaknesses': ai_scores.get('improvements', [])
                    }
                    
                    print(f"  ✅ AI Review: {analysis['ai_review']['quality_score']:.1f}/100")
                    print(f"     Architecture: {ai_scores.get('architecture', 0)}/10")
                    print(f"     Documentation: {ai_scores.get('documentation', 0)}/10")
                    print(f"     Testing: {ai_scores.get('testing', 0)}/10")
                else:
                    print(f"  ⚠️ AI review returned no scores")
                    analysis['ai_review'] = None
                
            except Exception as e:
                print(f"  ⚠️ AI review failed: {e}")
                analysis['ai_review'] = {
                    'error': str(e),
                    'quality_score': 0
                }
        else:
            print(f"  ⏭️ Skipping AI review (status: {recommendation})")
            analysis['ai_review'] = None
        
        reviewed.append(analysis)
    
    # Save results
    print(f"\n💾 Saving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reviewed, f, indent=2, ensure_ascii=False)
    
    # Summary
    approved = sum(1 for a in reviewed if a['recommendation'] == 'APPROVE')
    with_ai = sum(1 for a in reviewed if a.get('ai_review') and not a['ai_review'].get('error'))
    
    print(f"\n✅ AI Review Complete:")
    print(f"   - Total analyzed: {len(reviewed)}")
    print(f"   - Approved: {approved}")
    print(f"   - With AI review: {with_ai}")


if __name__ == '__main__':
    main()
