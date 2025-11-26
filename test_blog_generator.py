"""
Test script for Blog Generator.

Tests the MarkdownWriter and BlogManager components.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from blog_generator.markdown_writer import MarkdownWriter


def test_markdown_writer():
    """Test MarkdownWriter functionality."""
    print("\n🧪 Testing MarkdownWriter...")

    # Mock data
    repo_data = {
        "name": "test-automation-tool",
        "full_name": "testuser/test-automation-tool",
        "description": "An amazing automation tool for developers",
        "stargazers_count": 567,
        "language": "Python",
        "topics": ["automation", "testing", "devops"]
    }

    script_data = {
        "hook": "Manual testing is slow and error-prone",
        "solution": "This tool automates your entire testing workflow with AI-powered test generation",
        "pros": [
            "Saves hours of manual testing time",
            "AI-powered test generation",
            "Integrates with popular CI/CD tools",
            "Easy to set up and use"
        ],
        "cons": [
            "Requires Python 3.8+",
            "Learning curve for advanced features"
        ],
        "verdict": "A game-changer for teams looking to improve their testing workflow",
        "narration": "Stop wasting time on manual testing. This AI-powered tool generates comprehensive tests automatically, integrates with your CI/CD pipeline, and catches bugs before they reach production."
    }

    images = {
        "architecture": "/assets/images/test-automation-tool/architecture.png",
        "flow": "/assets/images/test-automation-tool/flow.png",
        "screenshot": "/assets/images/test-automation-tool/screenshot.png"
    }

    try:
        # Create writer
        writer = MarkdownWriter(output_dir="website/src/content/blog")
        print("✅ MarkdownWriter initialized")

        # Generate post
        filepath = writer.create_post(repo_data, script_data, images)
        print(f"✅ Post created: {filepath}")

        # Validate post
        is_valid = writer.validate_post(filepath)
        if is_valid:
            print("✅ Post validation passed")
        else:
            print("❌ Post validation failed")
            return False

        # Show preview
        print("\n" + "="*60)
        print("📄 Post Preview:")
        print("="*60)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Show first 500 characters
            print(content[:500] + "...\n")
        print("="*60)

        print("\n✅ MarkdownWriter test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ MarkdownWriter test failed: {e}")
        return False


def main():
    print("="*60)
    print("🧪 Blog Generator Tests")
    print("="*60)

    results = {
        "markdown_writer": False
    }

    # Test MarkdownWriter
    results["markdown_writer"] = test_markdown_writer()

    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"MarkdownWriter: {'✅ PASS' if results['markdown_writer'] else '❌ FAIL'}")

    if all(results.values()):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

    print("\n💡 Next steps:")
    print("   1. Review the generated post in blog/_posts/")
    print("   2. Test BlogManager (requires Git setup)")
    print("   3. Create GitHub Workflow")


if __name__ == "__main__":
    main()
