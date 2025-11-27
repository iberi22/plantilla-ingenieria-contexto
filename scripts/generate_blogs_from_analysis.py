#!/usr/bin/env python3
"""
Generate Blog Posts from Analysis JSON
Consumes analysis with AI reviews and generates Astro blog posts.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from blog_generator.blog_post_generator import BlogPostGenerator


def create_blog_post(analysis, generator):
    """Create a blog post from analysis data."""
    
    repo = analysis['repo']
    metadata = analysis['metadata']
    scores = analysis['scores']
    ai_review = analysis.get('ai_review', {})
    
    print(f"\n📝 Generating blog post for {repo}...")
    
    # Prepare script data
    script_data = {
        'repo_name': repo,
        'repo_url': f"https://github.com/{repo}",
        'description': metadata.get('description', 'An interesting open source project'),
        'language': metadata.get('language', 'Unknown'),
        'stars': metadata['stars'],
        'forks': metadata['forks'],
        'open_issues': metadata.get('open_issues', 0),
        'total_score': analysis['total_score'],
        
        # Analysis scores
        'commit_activity_score': scores['commit_activity'],
        'code_quality_score': scores['code_quality'],
        'developer_engagement_score': scores['developer_engagement'],
        'project_maturity_score': scores['project_maturity'],
        
        # AI review scores (if available)
        'architecture_score': ai_review.get('architecture', 0) if ai_review else 0,
        'documentation_score': ai_review.get('documentation', 0) if ai_review else 0,
        'testing_score': ai_review.get('testing', 0) if ai_review else 0,
        'best_practices_score': ai_review.get('best_practices', 0) if ai_review else 0,
        'innovation_score': ai_review.get('innovation', 0) if ai_review else 0,
        
        # AI insights
        'ai_reasoning': ai_review.get('reasoning', '') if ai_review else '',
        'strengths': ai_review.get('strengths', []) if ai_review else [],
        'weaknesses': ai_review.get('weaknesses', []) if ai_review else [],
        
        # Metadata
        'readme_excerpt': metadata.get('readme', '')[:500],
        'topics': metadata.get('topics', []),
        'license': metadata.get('license', 'Unknown'),
        'created_at': metadata.get('created_at', ''),
        'updated_at': metadata.get('updated_at', ''),
    }
    
    # Generate blog post
    try:
        blog_content = generator.generate_blog_post(script_data)
        
        # Save to file
        blog_dir = Path(__file__).parent.parent / 'website' / 'src' / 'content' / 'blog'
        blog_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename from repo name
        repo_slug = repo.replace('/', '-').lower()
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"{timestamp}-{repo_slug}.md"
        
        filepath = blog_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(blog_content)
        
        print(f"  ✅ Blog post created: {filename}")
        return filepath
        
    except Exception as e:
        print(f"  ❌ Failed to generate blog post: {e}")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: generate_blogs_from_analysis.py <analysis_with_ai.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    print(f"📥 Loading analysis from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        analyses = json.load(f)
    
    # Filter approved repos
    approved = [a for a in analyses if a['recommendation'] == 'APPROVE']
    
    print(f"📊 Found {len(approved)} approved repositories")
    
    if not approved:
        print("ℹ️ No approved repositories to generate blog posts for")
        return
    
    # Initialize blog generator
    generator = BlogPostGenerator()
    
    # Generate blog posts
    generated = []
    for analysis in approved:
        filepath = create_blog_post(analysis, generator)
        if filepath:
            generated.append(filepath)
    
    # Summary
    print(f"\n✅ Blog Generation Complete:")
    print(f"   - Approved repositories: {len(approved)}")
    print(f"   - Blog posts generated: {len(generated)}")
    
    if generated:
        print(f"\n📁 Generated files:")
        for filepath in generated:
            print(f"   - {filepath.name}")


if __name__ == '__main__':
    main()
