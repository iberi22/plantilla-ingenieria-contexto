#!/usr/bin/env python3
"""
Bridge Rust Output to AI Review Input
Transforms the raw JSON output from the Rust Hidden Gems Scanner into the format
expected by the AI Review script.
"""

import json
import sys
from datetime import datetime

def calculate_scores(repo):
    """Calculate basic scores based on available metadata."""
    # This is a simplified scoring since we don't have all the deep analysis data from Python scanner
    # But we can approximate based on what Rust gave us.

    # Engagement: Stars, Forks, Issues
    stars = repo.get('stargazers_count', 0)
    forks = repo.get('forks_count', 0)
    engagement_score = min(100, (stars / 100) * 10 + (forks / 10) * 5)

    # Maturity: Age, Size
    created_at = repo.get('created_at', '')
    try:
        created_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        age_days = (datetime.now() - created_dt).days
        maturity_score = min(100, age_days / 10) # 1000 days = 100 score
    except:
        maturity_score = 50

    # Quality: Size, Description, Topics
    desc = repo.get('description', '')
    topics = repo.get('topics', [])
    quality_score = 50
    if len(desc) > 50: quality_score += 10
    if len(topics) > 0: quality_score += 10
    if repo.get('has_wiki'): quality_score += 10
    if repo.get('has_pages'): quality_score += 10
    if repo.get('license'): quality_score += 10

    # Activity: Pushed At
    pushed_at = repo.get('pushed_at', '')
    try:
        pushed_dt = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ")
        days_since_push = (datetime.now() - pushed_dt).days
        activity_score = max(0, 100 - days_since_push) # 0 days = 100, 100 days = 0
    except:
        activity_score = 50

    return {
        "commit_activity": activity_score,
        "code_quality": quality_score,
        "developer_engagement": engagement_score,
        "project_maturity": maturity_score
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: bridge_rust_to_ai.py <rust_output.json> <bridge_output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"🌉 Bridging {input_file} -> {output_file}...")

    with open(input_file, 'r', encoding='utf-8') as f:
        repos = json.load(f)

    transformed = []
    for repo in repos:
        scores = calculate_scores(repo)
        total_score = sum(scores.values()) / 4

        # Determine recommendation
        recommendation = "APPROVE" if total_score > 60 else "REJECT"

        transformed.append({
            "repo": repo['full_name'],
            "recommendation": recommendation,
            "total_score": total_score,
            "scores": scores,
            "metadata": {
                "description": repo.get('description', ''),
                "stars": repo.get('stargazers_count', 0),
                "forks": repo.get('forks_count', 0),
                "language": repo.get('language', 'Unknown'),
                "topics": repo.get('topics', []),
                "license": repo.get('license', {}).get('name', 'Unknown'),
                "created_at": repo.get('created_at'),
                "updated_at": repo.get('updated_at'),
                "pushed_at": repo.get('pushed_at'),
                "readme": "" # Rust scanner doesn't fetch README content yet, AI reviewer will need to fetch it or we skip it
            }
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed, f, indent=2)

    print(f"✅ Transformed {len(transformed)} repositories.")

if __name__ == "__main__":
    main()
