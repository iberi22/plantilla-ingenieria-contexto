import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock dependencies
sys.modules['google.generativeai'] = MagicMock()
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.editor'] = MagicMock()
sys.modules['moviepy.audio.fx'] = MagicMock()
sys.modules['moviepy.video.fx'] = MagicMock()
sys.modules['edge_tts'] = MagicMock()
sys.modules['playwright.async_api'] = MagicMock()

from video_generator.reel_creator import ReelCreator

class TestEndToEnd(unittest.TestCase):

    @patch('video_generator.reel_creator.ReelCreator._create_section')
    @patch('video_generator.reel_creator.ReelCreator._create_intro')
    @patch('video_generator.reel_creator.ReelCreator._create_outro')
    @patch('moviepy.video.compositing.concatenate.concatenate_videoclips')
    def test_reel_creation_flow(self, mock_concat, mock_outro, mock_intro, mock_section):
        """
        Test the logical flow of creating a reel:
        Intro -> Problem -> Solution -> Architecture -> Outro
        """
        creator = ReelCreator(output_dir="tests/output")

        # Mock inputs
        script_data = {
            "hook": "Hook text",
            "solution": "Solution text",
            "architecture": "Arch text",
            "hook_highlights": ["Hook"],
            "solution_highlights": ["Solution"],
            "architecture_highlights": ["Arch"]
        }
        images = {
            "flow": "flow.png",
            "screenshot": "screen.png",
            "architecture": "arch.png"
        }

        # Mock moviepy clips
        mock_clip = MagicMock()
        mock_clip.duration = 5
        mock_intro.return_value = mock_clip
        mock_section.return_value = mock_clip
        mock_outro.return_value = mock_clip
        mock_concat.return_value = mock_clip # Final video

        # Run
        video_path = creator.create_reel("test-repo", script_data, images)

        # Assertions
        self.assertTrue(mock_intro.called)
        self.assertTrue(mock_outro.called)

        # Check section calls
        # Problem
        mock_section.assert_any_call(
            "The Problem", "Hook text", "flow.png", duration=5, highlights=["Hook"]
        )
        # Solution
        mock_section.assert_any_call(
            "The Solution", "Solution text", "screen.png", duration=5, highlights=["Solution"]
        )
        # Architecture
        mock_section.assert_any_call(
            "Architecture", "Arch text", "arch.png", duration=4, highlights=["Arch"]
        )

        self.assertTrue(mock_concat.called)

if __name__ == '__main__':
    unittest.main()
