"""
Tests for the VoiceTranslationPipeline.

Note: These tests are designed to be lightweight and focus on the pipeline's
structure and orchestration. They mock the heavy AI models to avoid
requiring a GPU or long run times in a CI environment.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import sys
import torch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_generator.voice_translation import VoiceTranslationPipeline

@pytest.fixture
def mock_audio_file(tmp_path):
    """Create a dummy audio file for testing."""
    audio_path = tmp_path / "test.wav"
    audio_path.touch()
    return str(audio_path)

@patch('video_generator.voice_translation.WHISPER_AVAILABLE', True)
@patch('video_generator.voice_translation.TTS_AVAILABLE', True)
@patch('video_generator.voice_translation.TRANSFORMERS_AVAILABLE', True)
def test_pipeline_initialization():
    """Test that the VoiceTranslationPipeline can be initialized."""
    with patch('video_generator.voice_translation.whisper.load_model') as mock_whisper, \
         patch('video_generator.voice_translation.TTS') as mock_tts:
        # Setup mock returns
        mock_whisper_model = Mock()
        mock_whisper.return_value = mock_whisper_model
        
        mock_tts_instance = Mock()
        mock_tts_instance.to.return_value = mock_tts_instance
        mock_tts.return_value = mock_tts_instance

        pipeline = VoiceTranslationPipeline()
        assert pipeline is not None
        assert pipeline.whisper_model is not None
        assert pipeline.tts is not None
        mock_whisper.assert_called_once()
        mock_tts.assert_called_once()

@patch('video_generator.voice_translation.WHISPER_AVAILABLE', True)
@patch('video_generator.voice_translation.TTS_AVAILABLE', True)
def test_transcribe_audio(mock_audio_file):
    """Test the transcription step, mocking the model."""
    with patch('whisper.load_model') as mock_whisper, \
         patch('TTS.api.TTS') as mock_tts:
        mock_tts_instance = Mock()
        mock_tts.return_value.to.return_value = mock_tts_instance

        # Arrange
        pipeline = VoiceTranslationPipeline()
        mock_transcribe_result = {'text': 'This is a test.', 'language': 'en'}
        pipeline.whisper_model.transcribe = MagicMock(return_value=mock_transcribe_result)

    # Act
    text, lang = pipeline.transcribe_audio(mock_audio_file)

    # Assert
    assert text == 'This is a test.'
    assert lang == 'en'
    pipeline.whisper_model.transcribe.assert_called_once_with(mock_audio_file, fp16=False)


@patch('video_generator.voice_translation.WHISPER_AVAILABLE', True)
@patch('video_generator.voice_translation.TTS_AVAILABLE', True)
@patch('video_generator.voice_translation.TRANSFORMERS_AVAILABLE', True)
def test_translate_text():
    """Test the text translation step, mocking the models."""
    with patch('video_generator.voice_translation.whisper.load_model') as mock_whisper, \
         patch('video_generator.voice_translation.TTS') as mock_tts, \
         patch('video_generator.voice_translation.MarianMTModel') as mock_marian, \
         patch('video_generator.voice_translation.MarianTokenizer') as mock_tokenizer:
        
        # Setup Whisper mock
        mock_whisper_model = Mock()
        mock_whisper.return_value = mock_whisper_model
        
        # Setup TTS mock
        mock_tts_instance = Mock()
        mock_tts_instance.to.return_value = mock_tts_instance
        mock_tts.return_value = mock_tts_instance

        # Setup Translation mocks
        mock_tensor = Mock()
        mock_tensor.to.return_value = mock_tensor
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.return_value = {
            "input_ids": mock_tensor,
            "attention_mask": mock_tensor
        }
        mock_tokenizer_instance.decode.return_value = "Ceci est un test."
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model_instance.generate.return_value = torch.tensor([[1, 2, 3]])
        mock_model_instance.to.return_value = mock_model_instance
        mock_marian.from_pretrained.return_value = mock_model_instance

        # Arrange
        pipeline = VoiceTranslationPipeline()

        # Act
        translated_text = pipeline.translate_text("This is a test.", source_lang="en", target_lang="fr")

        # Assert
        assert translated_text == "Ceci est un test."
        mock_marian.from_pretrained.assert_called_once_with("Helsinki-NLP/opus-mt-en-fr")
        mock_tokenizer.from_pretrained.assert_called_once_with("Helsinki-NLP/opus-mt-en-fr")


@patch('video_generator.voice_translation.WHISPER_AVAILABLE', True)
@patch('video_generator.voice_translation.TTS_AVAILABLE', True)
def test_synthesize_speech(mock_audio_file, tmp_path):
    """Test the speech synthesis step, mocking the TTS model."""
    with patch('whisper.load_model') as mock_whisper, \
         patch('TTS.api.TTS') as mock_tts:
        mock_tts_instance = Mock()
        mock_tts.return_value.to.return_value = mock_tts_instance

        # Arrange
        pipeline = VoiceTranslationPipeline()
        mock_tts_instance = pipeline.tts
        output_path = tmp_path / "output.wav"

    # Act
    result_path = pipeline.synthesize_speech("Ceci est un test.", mock_audio_file, str(output_path), language="fr")

    # Assert
    assert result_path == str(output_path)
    mock_tts_instance.tts_to_file.assert_called_once_with(
        text="Ceci est un test.",
        file_path=str(output_path),
        speaker_wav=mock_audio_file,
        language="fr"
    )

@patch('video_generator.voice_translation.WHISPER_AVAILABLE', True)
@patch('video_generator.voice_translation.TTS_AVAILABLE', True)
@patch('video_generator.voice_translation.VoiceTranslationPipeline.transcribe_audio')
@patch('video_generator.voice_translation.VoiceTranslationPipeline.translate_text')
@patch('video_generator.voice_translation.VoiceTranslationPipeline.synthesize_speech')
def test_full_voice_translation_pipeline(mock_synthesize, mock_translate, mock_transcribe):
    """Test the end-to-end voice translation pipeline by mocking each step."""
    with patch('whisper.load_model'), \
         patch('TTS.api.TTS') as mock_tts:
        mock_tts_instance = Mock()
        mock_tts.return_value.to.return_value = mock_tts_instance

        # Arrange
        pipeline = VoiceTranslationPipeline()

    mock_audio = "/path/to/audio.wav"
    output_path = "/path/to/output.wav"

    mock_transcribe.return_value = ("This is a test", "en")
    mock_translate.return_value = "Ceci est un test"
    mock_synthesize.return_value = output_path

    # Act
    result = pipeline.translate_voice(mock_audio, "fr", output_path)

    # Assert
    mock_transcribe.assert_called_once_with(mock_audio)
    mock_translate.assert_called_once_with("This is a test", "en", "fr")
    mock_synthesize.assert_called_once_with("Ceci est un test", mock_audio, output_path, "fr")

    assert result is not None
    assert result["original_text"] == "This is a test"
    assert result["translated_text"] == "Ceci est un test"
    assert result["audio_path"] == output_path

