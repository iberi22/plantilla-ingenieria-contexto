# Open Source Video Generator

[![CI Status](https://github.com/iberi22/plantilla-ingenieria-contexto/actions/workflows/ci.yml/badge.svg)](https://github.com/iberi22/plantilla-ingenieria-contexto/actions)
[![Tests](https://img.shields.io/badge/tests-32%2F45%20passing-yellow)](https://github.com/iberi22/plantilla-ingenieria-contexto)
[![Coverage](https://img.shields.io/badge/coverage-71%25-yellow)]()
[![Status](https://img.shields.io/badge/status-87%25%20complete-blue)]()

Automated tool to scan GitHub for trending repositories, generate a video script using AI (Gemini or Foundry Local), record a visual tour, and narrate it. Now with **Voice Translation Studio** for creating multilingual video reels with voice cloning!

## 📊 Current Status (Nov 2025)

- ✅ **Core pipeline:** Scanner → Blog → Video → Upload (operational)
- ✅ **CI/CD:** GitHub Actions for testing and blog generation
- ⚠️ **Voice translation:** Requires `sentencepiece` installation
- ⚠️ **Webhook server:** Prototype (needs production queue - see [ROADMAP.md](ROADMAP.md))
- 📊 **Test Coverage:** 71% (32/45 tests passing - fixes in progress)
- 📝 **Documentation:** [Full Status Report](PROJECT_STATUS_REPORT.md)

## ✨ Features

### Core Features
- **GitHub Scanner**: Finds recent, high-quality repositories (CI passing, good description).
- **AI Scriptwriter**: Generates engaging scripts using Google Gemini or Microsoft Foundry Local (for local LLMs).
- **Visual Engine**: Records a browser tour of the repository using Playwright.
- **Content Renderer**: Generates professional narration using Edge TTS and combines it with the video.
- **Image Generator**: Creates explanatory diagrams (architecture, problem-solution flows, feature showcases) using Nano Banana 2.
- **Firebase Persistence**: Tracks processed repositories to avoid duplicates and monitor status.
- **YouTube Uploader**: Uploads the final video to YouTube (OAuth2 authenticated).

### New Features (Voice Translation Studio)
- **🎙️ Voice Recording**: Record narration directly from your browser
- **📝 Transcription**: Automatic speech-to-text with language detection using Whisper
- **🌍 Translation**: Translate content to 10+ languages (English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Arabic)
- **🗣️ Voice Cloning**: Synthesize translated audio with your voice characteristics using XTTS v2
- **🎬 Video Generation**: Create professional 9:16 vertical reels with:
  - Dynamic scene durations
  - Keyword highlighting in text overlays
  - Background music mixing with volume ducking
  - Custom image support
- **🎨 Modern Blog Design**: Dark-themed Jekyll blog with video embedding support

## 📋 Prerequisites

- Python 3.11+
- FFmpeg (for MoviePy)
- Google API Key (if using Gemini)
- Foundry Local (if using local LLMs)
- Firebase Project (optional, for persistence)

## 🚀 Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
4. Configure your environment variables:
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `GOOGLE_API_KEY`: Your Google Gemini API key (if using Gemini)
   - `FIREBASE_CREDENTIALS`: Path to Firebase service account JSON or base64-encoded credentials
   - `YOUTUBE_CLIENT_SECRET`: YouTube OAuth2 client secret
   - `YOUTUBE_REFRESH_TOKEN`: YouTube OAuth2 refresh token

## 💻 Usage

### Voice Translation Studio (New!)

Start the backend API and frontend:

```bash
# Terminal 1: Start Flask API
python api/multilingual_api.py

# Terminal 2: Start React frontend
cd web
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser to access the Voice Studio interface.

**Workflow:**
1. **Record**: Click the microphone to record your narration
2. **Transcribe**: Review and edit the transcribed text
3. **Translate**: Select target languages and translate
4. **Synthesize**: Generate voice cloned audio in each language
5. **Upload Images**: Add custom architecture, flow, or screenshot images
6. **Generate**: Create professional 9:16 vertical video reels

### Original Pipeline (GitHub Scanner)

### Basic Usage (Run Once)

```bash
python src/main.py --mode once
```

### Run as Daemon (Hourly Scan)

```bash
python src/main.py --mode daemon
```

### Use Local LLM (Foundry Local)

Ensure Foundry Local is running or installed.

```bash
python src/main.py --provider foundry --model phi-3.5-mini
```

### Enable Firebase Persistence

Avoid processing duplicate repositories:

```bash
python src/main.py --use-firebase
```

### Enable Image Generation

Generate explanatory diagrams with Nano Banana 2:

```bash
python src/main.py --generate-images
```

### Full-Featured Example

```bash
python src/main.py \
  --provider foundry \
  --model phi-3.5-mini \
  --use-firebase \
  --generate-images \
  --headless
```

### Headless Mode (for Server/CI)

```bash
python src/main.py --headless
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_scanner.py -v
cd web
npm install
npm run dev
```

## 🏗️ Architecture

```text
src/
├── scanner/             # GitHub API interaction
├── agents/              # LLM interaction (Gemini/Foundry)
├── engine/              # Visual recording (Playwright) and Rendering (MoviePy + EdgeTTS)
├── uploader/            # YouTube API interaction
├── persistence/         # Firebase Firestore integration
├── image_gen/           # Image generation with Nano Banana 2
├── video_generator/     # NEW: Reel creation with voice translation
│   ├── reel_creator.py          # Video generation with dynamic durations & music
│   ├── voice_translation.py     # Voice cloning and translation pipeline
│   └── narration_generator.py   # Audio synthesis
├── blog_generator/      # Blog post generation and management
api/
└── multilingual_api.py  # NEW: Flask API for voice studio
web/
└── src/components/
    └── VoiceRecorder.jsx  # NEW: React voice studio interface
```

### Pipeline Flow

**Original Video Generator:**
1. **Scan** → Find quality repositories on GitHub
2. **Check** → Verify not already processed (Firebase)
3. **Analyze** → Generate script with AI (Gemini/Foundry)
4. **Visualize** → Generate explanatory images (Nano Banana 2)
5. **Record** → Capture repository tour (Playwright)
6. **Render** → Combine video + narration (MoviePy + EdgeTTS)
7. **Upload** → Publish to YouTube
8. **Track** → Update status in Firebase

**Voice Translation Studio (New):**
1. **Record** → Capture narration in browser
2. **Transcribe** → Convert speech to text (Whisper)
3. **Translate** → Translate to target languages (Google Translate API)
4. **Synthesize** → Clone voice in each language (XTTS v2)
5. **Generate** → Create professional vertical reels with custom visuals
6. **Export** → Download videos for social media

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_scanner.py -v
pytest tests/test_reel_creator_features.py -v

# Test voice translation
pytest tests/test_voice_translation.py -v

# Run frontend tests
cd web
npm test
```
## 📚 Documentation

- [PLANNING.md](PLANNING.md) - Project architecture and roadmap
- [TASK.md](TASK.md) - Detailed task tracking with Phases 6-8 (NEW)
- [RULES.md](RULES.md) - Development rules and standards
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Latest implementation details
- [docs/MULTILINGUAL_README.md](docs/MULTILINGUAL_README.md) - Multilingual features documentation
- [docs/AUTOMATION_GUIDE.md](docs/AUTOMATION_GUIDE.md) - Guide for the new Automation Pipeline
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment instructions for API and Webhooks
- [CHANGELOG.md](CHANGELOG.md) - Detailed changelog of PR #2
- [PR_REVIEW.md](PR_REVIEW.md) - Comprehensive code review and recommendations

## 🚀 Automation Features

### End-to-End Pipeline
The `scripts/run_pipeline.py` script orchestrates the entire flow:
1.  Scans/Analyses a Repo.
2.  Generates a Blog Post (simulated).
3.  Creates a Video Reel with audio and images.
4.  Auto-uploads to YouTube (if enabled).

### Webhook Integration
The `api/webhook_server.py` listens for GitHub events (e.g., Star) and automatically triggers the pipeline for the starred repository.

### OpenCut Editor Bridge
Videos generated can be opened in [OpenCut](https://github.com/OpenCut-app/OpenCut) for manual editing via the "Edit Video" button in the Voice Studio UI.

See [TASK.md](TASK.md) for detailed task status.

## 🤝 Contributing

See [RULES.md](RULES.md) for development guidelines and coding standards.

## 📄 License

MIT License - See LICENSE file for details
