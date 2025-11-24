"""
Professional Voice Translation System.

Uses state-of-the-art models for direct voice-to-voice translation:
- Whisper for transcription
- MarianMT for text translation
- XTTS-v2 for voice synthesis in target language
- Voice conversion to maintain speaker characteristics
"""

import logging
import torch
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import numpy as np

# Whisper for transcription
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available. Install with: pip install openai-whisper")

# TTS for voice synthesis
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Translation
try:
    from transformers import MarianMTModel, MarianTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class VoiceTranslationPipeline:
    """
    Complete pipeline for voice-to-voice translation.

    Workflow:
    1. Transcribe original audio (Whisper)
    2. Translate text to target language (MarianMT)
    3. Synthesize speech in target language with original voice characteristics (XTTS-v2)
    """

    def __init__(
        self,
        whisper_model: str = "base",
        tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    ):
        """
        Initialize Voice Translation Pipeline.

        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large).
            tts_model: TTS model for synthesis.
        """
        self.logger = logging.getLogger(__name__)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initialize Whisper
        if not WHISPER_AVAILABLE:
            raise ImportError("Whisper is required. Install with: pip install openai-whisper")

        self.logger.info(f"Loading Whisper model: {whisper_model}")
        self.whisper_model = whisper.load_model(whisper_model, device=self.device)

        # Initialize TTS
        if not TTS_AVAILABLE:
            raise ImportError("TTS is required. Install with: pip install TTS")

        self.logger.info(f"Loading TTS model: {tts_model}")
        self.tts = TTS(tts_model).to(self.device)

        # Translation models (loaded on demand)
        self.translation_models = {}
        self.translation_tokenizers = {}

        # Language pairs for translation
        self.language_pairs = {
            "en-es": "Helsinki-NLP/opus-mt-en-es",
            "en-fr": "Helsinki-NLP/opus-mt-en-fr",
            "en-de": "Helsinki-NLP/opus-mt-en-de",
            "en-it": "Helsinki-NLP/opus-mt-en-it",
            "en-pt": "Helsinki-NLP/opus-mt-en-pt",
            "en-ru": "Helsinki-NLP/opus-mt-en-ru",
            "en-zh": "Helsinki-NLP/opus-mt-en-zh",
            "en-ja": "Helsinki-NLP/opus-mt-en-jap",
            "en-ar": "Helsinki-NLP/opus-mt-en-ar",
        }

    def transcribe_audio(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribe audio to text using Whisper.

        Args:
            audio_path: Path to audio file.

        Returns:
            Tuple of (transcribed_text, detected_language).
        """
        try:
            self.logger.info(f"Transcribing audio: {audio_path}")

            result = self.whisper_model.transcribe(
                audio_path,
                fp16=(self.device == "cuda")
            )

            text = result["text"].strip()
            language = result["language"]

            self.logger.info(f"Transcription complete. Language: {language}")
            self.logger.info(f"Text: {text[:100]}...")

            return text, language

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}", exc_info=True)
            return "", "unknown"

    def _load_translation_model(self, source_lang: str, target_lang: str) -> bool:
        """Load translation model for language pair."""
        pair_key = f"{source_lang}-{target_lang}"

        if pair_key in self.translation_models:
            return True

        if pair_key not in self.language_pairs:
            self.logger.error(f"Translation pair {pair_key} not supported")
            return False

        try:
            model_name = self.language_pairs[pair_key]
            self.logger.info(f"Loading translation model: {model_name}")

            self.translation_tokenizers[pair_key] = MarianTokenizer.from_pretrained(model_name)
            self.translation_models[pair_key] = MarianMTModel.from_pretrained(model_name).to(self.device)

            return True

        except Exception as e:
            self.logger.error(f"Failed to load translation model: {e}")
            return False

    def translate_text(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "es"
    ) -> Optional[str]:
        """
        Translate text from source to target language.

        Args:
            text: Text to translate.
            source_lang: Source language code.
            target_lang: Target language code.

        Returns:
            Translated text, or None if failed.
        """
        try:
            pair_key = f"{source_lang}-{target_lang}"

            if not self._load_translation_model(source_lang, target_lang):
                return None

            # Tokenize
            inputs = self.translation_tokenizers[pair_key](
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Translate
            with torch.no_grad():
                translated = self.translation_models[pair_key].generate(**inputs)

            translated_text = self.translation_tokenizers[pair_key].decode(
                translated[0],
                skip_special_tokens=True
            )

            self.logger.info(f"Translation ({source_lang} → {target_lang}): {translated_text[:100]}...")
            return translated_text

        except Exception as e:
            self.logger.error(f"Translation failed: {e}", exc_info=True)
            return None

    def synthesize_speech(
        self,
        text: str,
        reference_audio: str,
        output_path: str,
        language: str = "en"
    ) -> Optional[str]:
        """
        Synthesize speech using TTS with voice characteristics from reference.

        Args:
            text: Text to synthesize.
            reference_audio: Path to reference audio (original narration).
            output_path: Path to save synthesized audio.
            language: Target language code.

        Returns:
            Path to synthesized audio, or None if failed.
        """
        try:
            self.logger.info(f"Synthesizing speech in {language}...")

            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=reference_audio,
                language=language
            )

            self.logger.info(f"Speech synthesized: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Speech synthesis failed: {e}", exc_info=True)
            return None

    def translate_voice(
        self,
        original_audio: str,
        target_language: str,
        output_path: str,
        source_language: str = "en"
    ) -> Optional[Dict[str, str]]:
        """
        Complete voice-to-voice translation pipeline.

        Args:
            original_audio: Path to original narration audio.
            target_language: Target language code.
            output_path: Path to save translated audio.
            source_language: Source language code (auto-detected if not provided).

        Returns:
            Dictionary with translation info, or None if failed.
        """
        try:
            # Step 1: Transcribe original audio
            self.logger.info("=" * 60)
            self.logger.info("Step 1: Transcribing original audio...")
            transcribed_text, detected_lang = self.transcribe_audio(original_audio)

            if not transcribed_text:
                self.logger.error("Transcription failed")
                return None

            # Use detected language if not specified
            if source_language == "auto":
                source_language = detected_lang

            # Step 2: Translate text
            self.logger.info("Step 2: Translating text...")
            translated_text = self.translate_text(
                transcribed_text,
                source_language,
                target_language
            )

            if not translated_text:
                self.logger.error("Translation failed")
                return None

            # Step 3: Synthesize speech in target language
            self.logger.info("Step 3: Synthesizing speech...")
            synthesized_audio = self.synthesize_speech(
                translated_text,
                original_audio,
                output_path,
                target_language
            )

            if not synthesized_audio:
                self.logger.error("Speech synthesis failed")
                return None

            self.logger.info("=" * 60)
            self.logger.info("✅ Voice translation complete!")

            return {
                "original_text": transcribed_text,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "audio_path": synthesized_audio
            }

        except Exception as e:
            self.logger.error(f"Voice translation failed: {e}", exc_info=True)
            return None

    def batch_translate_voice(
        self,
        original_audio: str,
        target_languages: List[str],
        output_dir: str,
        base_filename: str = "narration"
    ) -> Dict[str, Dict[str, str]]:
        """
        Translate voice to multiple languages.

        Args:
            original_audio: Path to original narration.
            target_languages: List of target language codes.
            output_dir: Directory to save translated audio files.
            base_filename: Base name for output files.

        Returns:
            Dictionary mapping language code to translation info.
        """
        results = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for lang in target_languages:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Translating to {lang.upper()}...")
            self.logger.info(f"{'='*60}")

            output_file = output_path / f"{base_filename}_{lang}.wav"

            result = self.translate_voice(
                original_audio=original_audio,
                target_language=lang,
                output_path=str(output_file)
            )

            if result:
                results[lang] = result
                self.logger.info(f"✅ {lang}: Success")
            else:
                self.logger.error(f"❌ {lang}: Failed")

        return results
