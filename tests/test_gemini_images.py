#!/usr/bin/env python3
"""
Quick test for Gemini Imagen API configuration.
Tests that API keys are properly configured and can generate images.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_api_keys():
    """Test that API keys are available."""
    print("="*60)
    print("🔑 Testing API Key Configuration")
    print("="*60)

    keys = []
    main_key = os.environ.get("GOOGLE_API_KEY")
    if main_key:
        keys.append(f"GOOGLE_API_KEY: {main_key[:20]}...")

    for i in range(2, 6):
        key = os.environ.get(f"GOOGLE_API_KEY_{i}")
        if key:
            keys.append(f"GOOGLE_API_KEY_{i}: {key[:20]}...")

    if not keys:
        print("❌ No API keys found!")
        print("\n💡 To fix:")
        print("   1. Create/edit .env file")
        print("   2. Add: GOOGLE_API_KEY=your_key_here")
        print("   3. Get key from: https://makersuite.google.com/app/apikey")
        return False

    print(f"✅ Found {len(keys)} API key(s):")
    for key in keys:
        print(f"   • {key}")

    return True


def test_image_generation():
    """Test a simple image generation."""
    print("\n" + "="*60)
    print("🎨 Testing Image Generation")
    print("="*60)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False

    try:
        client = genai.Client(api_key=api_key)
        print("✅ Client initialized")

        # Simple test prompt
        prompt = (
            "Professional tech infographic showing a Python project, "
            "isometric 3D design, modern colors, clean composition, "
            "16:9 aspect ratio, no text"
        )

        print(f"\n📝 Test Prompt: {prompt[:80]}...")
        print("⏳ Generating test image (this may take 10-30 seconds)...")

        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="block_low_and_above",
                person_generation="DONT_ALLOW"
            )
        )

        if response.generated_images:
            # Save test image
            test_output = Path("test_gemini_image.png")
            image = response.generated_images[0]
            image.image.save(str(test_output))

            print(f"✅ Image generated successfully!")
            print(f"   Saved to: {test_output.absolute()}")
            print(f"\n💡 You can view the test image to verify quality")
            return True
        else:
            print("⚠️ No images returned in response")
            return False

    except Exception as e:
        error_msg = str(e).lower()

        if "quota" in error_msg or "rate" in error_msg:
            print(f"⚠️ Rate limit or quota error: {e}")
            print("\n💡 Possible solutions:")
            print("   1. Wait a few minutes and try again")
            print("   2. Add more API keys (GOOGLE_API_KEY_2, etc.)")
            print("   3. Check billing at: https://console.cloud.google.com/billing")
        elif "permission" in error_msg or "api" in error_msg:
            print(f"❌ API access error: {e}")
            print("\n💡 Possible solutions:")
            print("   1. Verify API key is valid")
            print("   2. Enable 'Generative Language API' in Google Cloud Console")
            print("   3. Check project has billing enabled (if required)")
        else:
            print(f"❌ Unexpected error: {e}")

        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 Gemini Imagen API Test Suite")
    print("="*60)

    # Test 1: API Keys
    if not test_api_keys():
        return 1

    # Test 2: Image Generation
    if not test_image_generation():
        print("\n" + "="*60)
        print("❌ Image generation test failed")
        print("="*60)
        return 1

    # Success
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. Run full pipeline: .\\scripts\\run_full_rust_pipeline.ps1")
    print("   2. Or generate images only: python scripts/generate_blog_images.py --limit 3")
    print("   3. Check docs: docs/IMAGE_GENERATION_GUIDE.md")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
