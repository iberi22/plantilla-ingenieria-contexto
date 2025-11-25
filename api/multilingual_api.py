"""
Flask API for professional multilingual reel generation.

Uses voice translation pipeline:
1. User records narration in their voice
2. System transcribes and translates to target languages
3. System synthesizes speech in target languages with user's voice characteristics
4. System generates video reels for each language

Endpoints:
- POST /api/transcribe - Transcribe audio
- POST /api/translate - Translate text
- POST /api/synthesize - Synthesize speech
- POST /api/upload-image - Upload image for video
- POST /api/generate-video - Generate single video
- POST /api/generate-multilingual-reels - Generate reels in multiple languages (Legacy/Batch)
- GET /api/languages - Get supported languages
- GET /api/download/<filename> - Download generated file
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import sys
from pathlib import Path
import json
from werkzeug.utils import secure_filename
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_generator.voice_translation import VoiceTranslationPipeline
from video_generator.reel_creator import ReelCreator
from persistence.firebase_store import FirebaseStore
try:
    from video_editor.opencut_bridge import OpenCutBridge
except ImportError:
    OpenCutBridge = None

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
IMAGE_FOLDER = Path('blog/assets/images/custom')

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
AUDIO_FOLDER.mkdir(parents=True, exist_ok=True)
IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'webm', 'm4a'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# Global pipeline instance
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        logger.info("Initializing VoiceTranslationPipeline...")
        _pipeline = VoiceTranslationPipeline(
            whisper_model="base",
            tts_model="tts_models/multilingual/multi-dataset/xtts_v2"
        )
    return _pipeline

# Initialize Persistence
firebase_store = None
try:
    firebase_store = FirebaseStore()
except Exception:
    pass

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get processing status from Firebase."""
    try:
        limit = int(request.args.get('limit', 10))
        if firebase_store:
            # Mocking retrieval for now as FirebaseStore methods might need update to list all
            # Assuming firebase_store has a method or we mock it.
            # Real implementation would query 'processed_repos' collection
            return jsonify({"status": "connected", "jobs": []})
        return jsonify({"status": "disconnected", "jobs": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe uploaded audio file."""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400

        filename = secure_filename(audio_file.filename)
        file_path = UPLOAD_FOLDER / f"transcribe_{filename}"
        audio_file.save(str(file_path))

        pipeline = get_pipeline()
        text, language = pipeline.transcribe_audio(str(file_path))

        return jsonify({
            "text": text,
            "language": language,
            "audio_path": str(file_path)
        })

    except Exception as e:
        logger.error(f"Error transcribing: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Translate text to multiple languages."""
    try:
        data = request.json
        text = data.get('text')
        source_lang = data.get('source_lang', 'en')
        target_langs = data.get('target_langs', [])

        if not text or not target_langs:
            return jsonify({"error": "Missing text or target languages"}), 400

        pipeline = get_pipeline()
        translations = {}

        for lang in target_langs:
            if lang == source_lang:
                translations[lang] = text
            else:
                translated = pipeline.translate_text(text, source_lang, lang)
                translations[lang] = translated if translated else "Translation failed"

        return jsonify({"translations": translations})

    except Exception as e:
        logger.error(f"Error translating: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/synthesize', methods=['POST'])
def synthesize_speech():
    """Synthesize speech for a specific language."""
    try:
        data = request.json
        text = data.get('text')
        language = data.get('language')
        reference_audio = data.get('reference_audio')

        if not text or not language or not reference_audio:
            return jsonify({"error": "Missing parameters"}), 400

        # Ensure reference audio exists
        if not Path(reference_audio).exists():
             return jsonify({"error": "Reference audio not found"}), 404

        pipeline = get_pipeline()

        filename = f"synth_{language}_{Path(reference_audio).name}"
        output_path = AUDIO_FOLDER / filename

        audio_path = pipeline.synthesize_speech(
            text=text,
            reference_audio=reference_audio,
            output_path=str(output_path),
            language=language
        )

        if not audio_path:
            return jsonify({"error": "Synthesis failed"}), 500

        return jsonify({
            "audio_path": str(output_path),
            "filename": filename
        })

    except Exception as e:
        logger.error(f"Error synthesizing: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Upload an image for video generation."""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No image selected"}), 400

        if not allowed_image(image_file.filename):
            return jsonify({"error": "Invalid image format"}), 400

        filename = secure_filename(image_file.filename)
        file_path = IMAGE_FOLDER / filename
        image_file.save(str(file_path))

        return jsonify({
            "path": str(file_path),
            "filename": filename
        })

    except Exception as e:
        logger.error(f"Error uploading image: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """Generate a single video from audio and images."""
    try:
        data = request.json
        audio_path = data.get('audio_path')
        images = data.get('images', {}) # dict of key -> path
        text_content = data.get('text_content', '')
        repo_name = data.get('repo_name', 'custom-video')
        language = data.get('language', 'en')
        auto_upload = data.get('auto_upload', False) # Check for auto upload flag

        if not audio_path or not Path(audio_path).exists():
            return jsonify({"error": "Invalid audio path"}), 400

        reel_creator = ReelCreator(output_dir=str(OUTPUT_FOLDER), enable_upload=auto_upload)

        # Use provided images or fallbacks
        placeholder_images = {
            'architecture': 'blog/assets/images/placeholder/architecture.png',
            'flow': 'blog/assets/images/placeholder/flow.png',
            'screenshot': 'blog/assets/images/placeholder/screenshot.png'
        }

        # Merge provided images with placeholders
        final_images = placeholder_images.copy()
        final_images.update(images)

        # Parse new optional parameters
        durations = data.get('durations', None) # dict { 'intro': 3, ... }
        background_music = data.get('background_music', None)

        # Prepare script data
        # We can also accept highlights now if passed
        highlights = data.get('highlights', {}) # { 'hook_highlights': ['word'] }

        script_data = {
            'hook': text_content[:100],
            'solution': text_content,
            'verdict': 'Check it out!'
        }
        script_data.update(highlights)

        video_path = reel_creator.create_reel(
            repo_name=f"{repo_name}-{language}",
            script_data=script_data,
            images=final_images,
            audio_path=audio_path,
            durations=durations,
            background_music=background_music
        )

        if not video_path:
            return jsonify({"error": "Video generation failed"}), 500

        # Prepare OpenCut Project if Bridge is available
        opencut_data = None
        if OpenCutBridge:
            try:
                bridge = OpenCutBridge()
                assets = [
                    {"type": "video", "path": video_path},
                    {"type": "audio", "path": audio_path}
                ]
                metadata = {
                    "title": f"{repo_name}-{language}",
                    "duration": 20 # approx
                }
                opencut_data = bridge.export_for_editing(video_path, metadata, assets)
            except Exception as e:
                logger.error(f"OpenCut bridge error: {e}")

        return jsonify({
            "video_path": video_path,
            "filename": Path(video_path).name,
            "opencut": opencut_data
        })

    except Exception as e:
        logger.error(f"Error generating video: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-multilingual-reels', methods=['POST'])
def generate_multilingual_reels():
    """
    Generate video reels in multiple languages from original narration.
    (Legacy Batch Mode)
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
        pipeline = get_pipeline()

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
    """Download generated video or audio file."""
    try:
        # Check in video folder
        video_path = OUTPUT_FOLDER / filename
        if video_path.exists():
            return send_file(
                str(video_path),
                as_attachment=True,
                download_name=filename
            )

        # Check in audio folder
        audio_path = AUDIO_FOLDER / filename
        if audio_path.exists():
             return send_file(
                str(audio_path),
                as_attachment=True,
                download_name=filename
            )

        return jsonify({"error": "File not found"}), 404

    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({"error": str(e)}), 500

# Add a specific endpoint to serve audio files if needed for preview
@app.route('/api/serve-audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve audio file for playback."""
    try:
        audio_path = AUDIO_FOLDER / filename
        if audio_path.exists():
            return send_file(str(audio_path))
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
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
