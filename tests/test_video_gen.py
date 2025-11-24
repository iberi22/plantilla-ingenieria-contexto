
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
from src.video_generator.screenshot_capturer import ScreenshotCapturer
from src.video_generator.reel_creator import ReelCreator

# Mock Playwright
@pytest.fixture
def mock_playwright():
    with patch('src.video_generator.screenshot_capturer.async_playwright') as p:
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        p.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        yield mock_page

# Mock MoviePy
@pytest.fixture
def mock_moviepy():
    with patch('src.video_generator.reel_creator.VideoFileClip') as vfc, \
         patch('src.video_generator.reel_creator.ImageClip') as ic, \
         patch('src.video_generator.reel_creator.TextClip') as tc, \
         patch('src.video_generator.reel_creator.CompositeVideoClip') as cvc, \
         patch('src.video_generator.reel_creator.concatenate_videoclips') as concat, \
         patch('src.video_generator.reel_creator.ColorClip') as cc, \
         patch('src.video_generator.reel_creator.AudioFileClip') as ac, \
         patch('src.video_generator.reel_creator.FadeIn') as fi, \
         patch('src.video_generator.reel_creator.FadeOut') as fo:

        # Setup basic mocks
        ic.return_value.with_duration.return_value = ic.return_value
        ic.return_value.with_effects.return_value = ic.return_value
        ic.return_value.with_position.return_value = ic.return_value
        ic.return_value.w = 1000
        ic.return_value.h = 1000

        tc.return_value.with_position.return_value = tc.return_value
        tc.return_value.with_duration.return_value = tc.return_value

        cc.return_value.with_opacity.return_value = cc.return_value
        cc.return_value.with_position.return_value = cc.return_value

        cvc.return_value.set_audio.return_value = cvc.return_value
        cvc.return_value.with_effects.return_value = cvc.return_value

        yield {
            'ImageClip': ic,
            'TextClip': tc,
            'CompositeVideoClip': cvc,
            'concatenate_videoclips': concat,
            'AudioFileClip': ac
        }

@pytest.mark.asyncio
async def test_capture_highlights(mock_playwright):
    capturer = ScreenshotCapturer(output_dir="tests/output")

    # Mock _remove_banners to avoid extra query_selector calls
    capturer._remove_banners = AsyncMock()

    # Setup mock element
    mock_element = AsyncMock()
    mock_playwright.query_selector.return_value = mock_element

    highlights = {
        'readme': 'article.markdown-body',
        'sidebar': '.Layout-sidebar'
    }

    results = await capturer.capture_highlights(
        "https://github.com/test/repo",
        "test-repo",
        highlights
    )

    # Verification
    assert mock_playwright.goto.called
    assert mock_playwright.query_selector.call_count == 2
    assert mock_element.screenshot.call_count == 2
    assert 'readme' in results
    assert 'sidebar' in results

def test_create_reel(mock_moviepy):
    creator = ReelCreator(output_dir="tests/output")

    repo_name = "Test Repo"
    script_data = {
        "hook": "This is a hook",
        "solution": "This is a solution"
    }
    images = {
        "flow": "path/to/flow.png",
        "screenshot": "path/to/screenshot.png",
        "architecture": "path/to/architecture.png"
    }

    # Mock os.path.exists to return True
    with patch('os.path.exists', return_value=True):
        output_path = creator.create_reel(repo_name, script_data, images)

    assert output_path is not None
    assert "test-repo-reel.mp4" in output_path

    # Verify MoviePy calls
    assert mock_moviepy['ImageClip'].call_count >= 3
    assert mock_moviepy['concatenate_videoclips'].called
    # final_video comes from concatenate_videoclips
    assert mock_moviepy['concatenate_videoclips'].return_value.write_videofile.called
