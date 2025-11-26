"""
Migration script to convert investigations/*.md to blog posts.

This script:
1. Reads all JSON files from opencut_projects/
2. Creates markdown blog posts in website/src/content/blog/
3. Preserves all metadata in frontmatter
4. Generates SEO-friendly slugs
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def generate_blog_post(project_data, output_dir):
    """
    Generate a blog post from project JSON data.

    Args:
        project_data: Dictionary with project information
        output_dir: Path to website/src/content/blog/
    """
    # Extract metadata
    repo_name = project_data.get('repo_data', {}).get('full_name', 'unknown')
    title = project_data.get('title', repo_name)
    date = project_data.get('updated_at', datetime.now().isoformat())

    # Parse date to ensure proper format
    try:
        date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
        date_str = date_obj.strftime('%Y-%m-%d')
    except:
        date_str = datetime.now().strftime('%Y-%m-%d')

    # Create slug
    slug = f"{date_str}-{slugify(title)}"

    # Generate frontmatter
    frontmatter = {
        'title': title,
        'date': date_str,
        'repo': repo_name,
        'description': project_data.get('short_description', ''),
        'stars': project_data.get('repo_data', {}).get('stars', 0),
        'language': project_data.get('repo_data', {}).get('language', ''),
        'repo_data': project_data.get('repo_data', {}),
        'categories': project_data.get('categories', []),
        'tags': project_data.get('tags', []),
        'images': project_data.get('images', {}),
        'video': project_data.get('video', ''),
        'production_metrics': project_data.get('production_metrics', {}),
        'critical_issues': project_data.get('critical_issues', [])
    }

    # Build markdown content
    content_sections = []

    # Problem section
    if project_data.get('problem'):
        content_sections.append(f"## 🎯 The Problem\n\n{project_data['problem']}")

    # Solution section
    if project_data.get('solution'):
        content_sections.append(f"## 💡 The Solution\n\n{project_data['solution']}")

    # Advantages section
    if project_data.get('advantages'):
        content_sections.append(f"## ✅ Advantages\n\n{project_data['advantages']}")

    # Considerations section
    if project_data.get('considerations'):
        content_sections.append(f"## ⚠️ Considerations\n\n{project_data['considerations']}")

    # Verdict section
    if project_data.get('verdict'):
        content_sections.append(f"## 🎬 Verdict\n\n{project_data['verdict']}")

    # Long content section
    if project_data.get('long_content'):
        content_sections.append(f"## 📚 Detailed Analysis\n\n{project_data['long_content']}")

    # Full narration section
    if project_data.get('full_narration'):
        content_sections.append(f"---\n\n### 📝 Full Narration\n\n> {project_data['full_narration']}")

    # Combine all sections
    markdown_body = '\n\n'.join(content_sections)

    # Build final markdown file
    frontmatter_yaml = "---\n"
    for key, value in frontmatter.items():
        if value:  # Only include non-empty values
            if isinstance(value, str):
                # Escape quotes in strings
                value = value.replace('"', '\\"')
                frontmatter_yaml += f'{key}: "{value}"\n'
            elif isinstance(value, (list, dict)):
                # For complex types, use JSON representation
                import json
                frontmatter_yaml += f'{key}: {json.dumps(value)}\n'
            else:
                frontmatter_yaml += f'{key}: {value}\n'
    frontmatter_yaml += "---\n\n"

    final_content = frontmatter_yaml + markdown_body

    # Write to file
    output_path = output_dir / f"{slug}.md"
    output_path.write_text(final_content, encoding='utf-8')

    print(f"✅ Created: {output_path.name}")
    return output_path


def main():
    """Main migration function."""
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    projects_dir = project_root / 'opencut_projects'
    blog_dir = project_root / 'website' / 'src' / 'content' / 'blog'

    # Create blog directory if it doesn't exist
    blog_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Starting migration of investigations to blog posts...")
    print(f"📂 Reading from: {projects_dir}")
    print(f"📝 Writing to: {blog_dir}")
    print()

    # Check if projects directory exists
    if not projects_dir.exists():
        print(f"❌ Error: Projects directory not found: {projects_dir}")
        return

    # Get all JSON files
    json_files = list(projects_dir.glob('*.json'))

    if not json_files:
        print(f"⚠️ No JSON files found in {projects_dir}")
        return

    print(f"📦 Found {len(json_files)} project files\n")

    # Process each file
    migrated = 0
    errors = 0

    for json_file in json_files:
        try:
            # Read JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # Generate blog post
            generate_blog_post(project_data, blog_dir)
            migrated += 1

        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            errors += 1

    # Summary
    print()
    print("=" * 50)
    print(f"✨ Migration complete!")
    print(f"✅ Successfully migrated: {migrated} posts")
    if errors > 0:
        print(f"❌ Errors: {errors}")
    print(f"📍 Blog posts location: {blog_dir}")
    print("=" * 50)


if __name__ == '__main__':
    main()
