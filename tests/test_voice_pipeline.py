import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import shutil
from pathlib import Path

# Mock modules that might require heavy dependencies or external services
sys.modules['google.generativeai'] = MagicMock()
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()

# Mock Voice Pipeline dependencies
sys.modules['whisper'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['TTS.api'] = MagicMock()

class TestVoiceTranslationPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests/temp_voice_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('video_generator.voice_translation.VoiceTranslationPipeline')
    def test_pipeline_mock(self, MockPipeline):
        # This tests the interface structure rather than actual ML models
        # to ensure the API can call it correctly.

        pipeline = MockPipeline()

        # Mock return values
        pipeline.transcribe_audio.return_value = ("Hello World", "en")
        pipeline.translate_text.return_value = "Hola Mundo"
        pipeline.synthesize_speech.return_value = "path/to/audio.wav"

        # Test Transcription
        text, lang = pipeline.transcribe_audio("dummy.wav")
        self.assertEqual(text, "Hello World")
        self.assertEqual(lang, "en")

        # Test Translation
        trans = pipeline.translate_text("Hello World", "en", "es")
        self.assertEqual(trans, "Hola Mundo")

        # Test Synthesis
        audio = pipeline.synthesize_speech("Hola Mundo", "es", "dummy.wav")
        self.assertEqual(audio, "path/to/audio.wav")

if __name__ == '__main__':
    import sys
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    unittest.main()
