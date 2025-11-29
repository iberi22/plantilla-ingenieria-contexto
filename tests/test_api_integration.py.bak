import unittest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os

# Mock dependencies before importing app
sys.modules['google.generativeai'] = MagicMock()
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.editor'] = MagicMock()
sys.modules['moviepy.audio.fx'] = MagicMock()
sys.modules['moviepy.video.fx'] = MagicMock()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

# Import app (will trigger mocks)
from multilingual_api import app

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('multilingual_api.VoiceTranslationPipeline')
    def test_transcribe_endpoint(self, MockPipeline):
        # Mock pipeline instance
        mock_instance = MockPipeline.return_value
        mock_instance.transcribe_audio.return_value = ("Test Text", "en")

        # Mock global getter
        with patch('multilingual_api.get_pipeline', return_value=mock_instance):
            # Create dummy file
            data = {
                'audio': (open('tests/test_voice_pipeline.py', 'rb'), 'test.wav') # Using self as dummy file
            }

            response = self.app.post('/api/transcribe', data=data, content_type='multipart/form-data')

            self.assertEqual(response.status_code, 200)
            json_data = json.loads(response.data)
            self.assertEqual(json_data['text'], "Test Text")
            self.assertEqual(json_data['language'], "en")

    @patch('multilingual_api.VoiceTranslationPipeline')
    def test_translate_endpoint(self, MockPipeline):
        mock_instance = MockPipeline.return_value
        mock_instance.translate_text.return_value = "Texto de prueba"

        with patch('multilingual_api.get_pipeline', return_value=mock_instance):
            data = {
                'text': "Test Text",
                'source_lang': "en",
                'target_langs': ["es"]
            }

            response = self.app.post('/api/translate', json=data)

            self.assertEqual(response.status_code, 200)
            json_data = json.loads(response.data)
            self.assertEqual(json_data['translations']['es'], "Texto de prueba")

    @patch('multilingual_api.ReelCreator')
    def test_generate_video_endpoint(self, MockReelCreator):
        mock_creator = MockReelCreator.return_value
        mock_creator.create_reel.return_value = "path/to/video.mp4"

        with patch('pathlib.Path.exists', return_value=True):
            data = {
                'audio_path': "dummy_audio.wav",
                'text_content': "Demo",
                'language': "es"
            }

            response = self.app.post('/api/generate-video', json=data)

            self.assertEqual(response.status_code, 200)
            json_data = json.loads(response.data)
            self.assertEqual(json_data['filename'], "video.mp4")

if __name__ == '__main__':
    unittest.main()
