# 🌍 Multilingual Voice Translation System

A professional, local-first system for translating your voice into multiple languages to generate multilingual video reels.

## ✨ Features

### 🎙️ Voice Translation Pipeline
- **Transcription:** State-of-the-art `Whisper` for highly accurate transcription of your original narration.
- **Text Translation:** `MarianMT` (Helsinki-NLP) models for professional-grade text translation.
- **Speech Synthesis:** `Coqui TTS XTTS-v2` for synthesizing the translated text while retaining the characteristics of your original voice.
- **Local:** 100% on your machine. No external APIs, no fees, no privacy concerns.

### 🎬 Multilingual Reel Generation
- **Automated:** Generates videos for each translated language.
- **Format:** Vertical 9:16 (1080x1920) videos, perfect for social media.
- **Audio:** Your translated voice, synchronized with video content.

## 🎯 The Workflow: From One Voice to Many

The system follows a sophisticated voice-to-voice translation pipeline:

1.  **Record Your Narration**
    *   You record your voice reading a script in your natural language (e.g., English).

2.  **Transcription (Speech-to-Text)**
    *   The `Whisper` model listens to your recording and transcribes it into text with high accuracy.

3.  **Text Translation**
    *   The transcribed text is fed into `MarianMT` models, which translate it into the target languages you selected (e.g., Spanish, French, German).

4.  **Speech Synthesis (Text-to-Speech)**
    *   The powerful `XTTS-v2` model takes the *translated text* and synthesizes it into speech.
    *   Crucially, it uses your **original recording** as a reference to ensure the synthesized speech has the same tone, pace, and characteristics as your own voice.

5.  **Video Generation**
    *   `MoviePy` creates a 20-second video reel for each language, combining the translated audio with project images and text overlays.

6.  **Result**
    *   You get multiple video reels, ready to publish, each with your voice speaking a different language.

## 📋 Supported Languages

The system supports translation from English to 9 other languages. The voice synthesis (XTTS) supports 16 languages, making the system highly extensible.

| Language | Code | Text Translation (EN→) | Voice Synthesis |
|---|---|---|---|
| English | `en` | (Source) | ✅ |
| Spanish | `es` | ✅ | ✅ |
| French | `fr` | ✅ | ✅ |
| German | `de` | ✅ | ✅ |
| Italian | `it` | ✅ | ✅ |
| Portuguese | `pt` | ✅ | ✅ |
| Russian | `ru` | ✅ | ✅ |
| Chinese | `zh-cn`| ✅ | ✅ |
| Japanese | `ja` | ✅ | ✅ |
| Arabic | `ar` | ✅ | ✅ |
| *Other XTTS languages*| | ❌ | ✅ |


## 🚀 Installation

All dependencies are listed in `requirements.txt`.

```bash
# Install all required Python packages
pip install -r requirements.txt
```
**Note:** The models (Whisper, MarianMT, XTTS) will be downloaded automatically on first use. This may take some time and requires a stable internet connection.

## 💻 Usage

### Option 1: Web UI (Recommended)

The Voice Translation Studio provides a user-friendly interface to manage the entire process.

```bash
# 1. In one terminal, start the backend API
python api/multilingual_api.py

# 2. In another terminal, start the frontend
cd web
npm install
npm run dev

# 3. Open your browser to http://localhost:5173
```

#### Steps in the UI:
1.  **Record Your Voice:** Click the microphone and read your script (15-20 seconds).
2.  **Select Languages:** Choose the target languages for translation.
3.  **Generate Reels:** Click the "Translate Voice & Generate Reels" button.
4.  **Download:** Once processing is complete, download your generated video files.

### Option 2: Python Script (Advanced)

You can directly use the `VoiceTranslationPipeline` in your own scripts.

```python
from src.video_generator.voice_translation import VoiceTranslationPipeline

# 1. Initialize the pipeline
pipeline = VoiceTranslationPipeline(whisper_model="base")

# 2. Define source audio and output directory
original_narration = "path/to/your/voice.wav"
output_folder = "output/translated_audio"
target_languages = ["es", "fr", "de"]

# 3. Run the batch translation process
results = pipeline.batch_translate_voice(
    original_audio=original_narration,
    target_languages=target_languages,
    output_dir=output_folder,
    base_filename="my-project"
)

# 4. Print results
for lang, result in results.items():
    print(f"--- {lang.upper()} ---")
    print(f"  Original: {result['original_text']}")
    print(f"  Translated: {result['translated_text']}")
    print(f"  Audio Path: {result['audio_path']}")
```

## 📊 System Requirements

- **RAM:** 12 GB minimum, 16 GB+ recommended.
- **Storage:** 15 GB+ free space for models.
- **GPU:** An NVIDIA GPU with 8GB+ VRAM is **highly recommended** for acceptable performance. CPU-only execution will be very slow.

## 🔧 Troubleshooting

### Error: "CUDA out of memory"
Your GPU does not have enough VRAM. Close other applications using the GPU. If the error persists, you may need to run on CPU, which will be much slower.

### Slow Performance on CPU
This is expected. Voice synthesis and transcription are computationally expensive tasks. A CUDA-enabled GPU is recommended for a better experience.

### Poor Audio Quality
- Ensure your recording environment is quiet.
- Use a high-quality microphone.
- Speak clearly and naturally for 15-30 seconds. The model needs enough data to learn your voice characteristics.

---

**Built with ❤️ using incredible open-source models.**
