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

from scanner.grok_reviewer import GrokReviewer


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
    
    # Initialize AI reviewer
    reviewer = GrokReviewer()
    
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
                
                # Prepare context for AI
                context = {
                    'repo': repo,
                    'stars': analysis['metadata']['stars'],
                    'language': analysis['metadata'].get('language'),
                    'description': analysis['metadata'].get('description', ''),
                    'readme_excerpt': analysis['metadata'].get('readme', '')[:2000]  # First 2000 chars
                }
                
                # Call AI review
                ai_scores = reviewer.review_repository(
                    owner=owner,
                    repo=name,
                    readme_content=context['readme_excerpt'],
                    language=context['language'],
                    stars=context['stars']
                )
                
                # Add AI scores to analysis
                analysis['ai_review'] = {
                    'architecture': ai_scores.get('architecture_score', 0),
                    'documentation': ai_scores.get('documentation_score', 0),
                    'testing': ai_scores.get('testing_score', 0),
                    'best_practices': ai_scores.get('best_practices_score', 0),
                    'innovation': ai_scores.get('innovation_score', 0),
                    'quality_score': ai_scores.get('quality_score', 0),
                    'reasoning': ai_scores.get('reasoning', ''),
                    'strengths': ai_scores.get('strengths', []),
                    'weaknesses': ai_scores.get('weaknesses', [])
                }
                
                print(f"  ✅ AI Review: {ai_scores.get('quality_score', 0):.1f}/100")
                print(f"     Architecture: {ai_scores.get('architecture_score', 0)}/10")
                print(f"     Documentation: {ai_scores.get('documentation_score', 0)}/10")
                print(f"     Testing: {ai_scores.get('testing_score', 0)}/10")
                
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
