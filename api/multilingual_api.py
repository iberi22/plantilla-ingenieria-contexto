"""
Flask API for professional multilingual reel generation.

Uses voice translation pipeline:
1. User records narration in their voice
2. System transcribes and translates to target languages
3. System synthesizes speech in target languages with user's voice characteristics
4. System generates video reels for each language

Endpoints:
- POST /api/generate-multilingual-reels - Generate reels in multiple languages
- GET /api/languages - Get supported languages
- GET /api/download/<lang>/<filename> - Download generated file
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import sys
from pathlib import Path
import json
from werkzeug.utils import secure_filename

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_generator.voice_translation import VoiceTranslationPipeline
from video_generator.reel_creator import ReelCreator

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('blog/assets/videos')
AUDIO_FOLDER = Path('blog/assets/audio/multilingual')

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
AUDIO_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'webm', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages for translation."""
    try:
        # Supported languages for voice translation
        languages = [
            {"code": "en", "name": "English", "flag": "🇺🇸"},
            {"code": "es", "name": "Español", "flag": "🇪🇸"},
            {"code": "fr", "name": "Français", "flag": "🇫🇷"},
            {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
            {"code": "it", "name": "Italiano", "flag": "🇮🇹"},
            {"code": "pt", "name": "Português", "flag": "🇵🇹"},
            {"code": "ru", "name": "Русский", "flag": "🇷🇺"},
            {"code": "zh", "name": "中文", "flag": "🇨🇳"},
            {"code": "ja", "name": "日本語", "flag": "🇯🇵"},
            {"code": "ar", "name": "العربية", "flag": "🇸🇦"},
        ]

        return jsonify({"languages": languages})

    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-multilingual-reels', methods=['POST'])
def generate_multilingual_reels():
    """
    Generate video reels in multiple languages from original narration.

    Expected form data:
    - audio: Audio file (user's narration in original language)
    - languages: JSON array of target language codes
    - repo_name: (optional) Repository name
    """
    try:
        # Validate request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        languages_json = request.form.get('languages', '["en"]')
        repo_name = request.form.get('repo_name', 'demo-project')

        # Parse languages
        try:
            target_languages = json.loads(languages_json)
        except:
            target_languages = ["en"]

        # Validate audio file
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400

        if not allowed_file(audio_file.filename):
            return jsonify({"error": "Invalid audio file format"}), 400

        # Save original narration
        filename = secure_filename(audio_file.filename)
        original_audio_path = UPLOAD_FOLDER / f"original_{filename}"
        audio_file.save(str(original_audio_path))

        logger.info(f"Generating reels for {len(target_languages)} languages")
        logger.info(f"Original narration: {original_audio_path}")

        # Initialize voice translation pipeline
        pipeline = VoiceTranslationPipeline(
            whisper_model="base",  # or "small" for better accuracy
            tts_model="tts_models/multilingual/multi-dataset/xtts_v2"
        )

        # Translate voice to multiple languages
        translation_results = pipeline.batch_translate_voice(
            original_audio=str(original_audio_path),
            target_languages=target_languages,
            output_dir=str(AUDIO_FOLDER),
            base_filename=repo_name
        )

        if not translation_results:
            return jsonify({"error": "Failed to translate voice"}), 500

        # Extract audio paths and transcriptions
        audio_results = {}
        transcriptions = {}

        for lang, result in translation_results.items():
            audio_results[lang] = result["audio_path"]
            transcriptions[lang] = {
                "original": result["original_text"],
                "translated": result["translated_text"]
            }

        # Generate video reels for each language
        video_results = {}
        reel_creator = ReelCreator(output_dir=str(OUTPUT_FOLDER))

        # Placeholder images (in real scenario, these would come from the blog post)
        placeholder_images = {
            'architecture': 'blog/assets/images/placeholder/architecture.png',
            'flow': 'blog/assets/images/placeholder/flow.png',
            'screenshot': 'blog/assets/images/placeholder/screenshot.png'
        }

        for lang, audio_path in audio_results.items():
            try:
                # Use translated text for script data
                translated_text = transcriptions[lang]["translated"]

                script_data = {
                    'hook': translated_text[:100],
                    'solution': translated_text,
                    'verdict': 'Check it out!'
                }

                video_path = reel_creator.create_reel(
                    repo_name=f"{repo_name}-{lang}",
                    script_data=script_data,
                    images=placeholder_images,
                    audio_path=audio_path
                )

                if video_path:
                    video_results[lang] = Path(video_path).name
                    logger.info(f"✅ Video created for {lang}: {video_path}")

            except Exception as e:
                logger.error(f"Failed to create video for {lang}: {e}")

        # Cleanup original audio
        try:
            original_audio_path.unlink()
        except:
            pass

        return jsonify({
            "success": True,
            "message": f"Generated {len(video_results)} reels",
            "audio_files": audio_results,
            "video_files": video_results,
            "transcriptions": transcriptions,
            "languages": list(video_results.keys())
        })

    except Exception as e:
        logger.error(f"Error generating reels: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated video file."""
    try:
        file_path = OUTPUT_FOLDER / filename

        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "multilingual-reel-api",
        "features": [
            "voice-translation",
            "multilingual-reels",
            "whisper-transcription",
            "tts-synthesis"
        ]
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
