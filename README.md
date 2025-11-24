# Open Source Video Generator

Automated tool to scan GitHub for trending repositories, generate a video script using AI (Gemini or Foundry Local), record a visual tour, and narrate it.

## ✨ Features

- **GitHub Scanner**: Finds recent, high-quality repositories (CI passing, good description).
- **AI Scriptwriter**: Generates engaging scripts using Google Gemini or Microsoft Foundry Local (for local LLMs).
- **Visual Engine**: Records a browser tour of the repository using Playwright.
- **Content Renderer**: Generates professional narration using Edge TTS and combines it with the video.
- **Image Generator**: Creates explanatory diagrams (architecture, problem-solution flows, feature showcases) using Nano Banana 2.
- **Firebase Persistence**: Tracks processed repositories to avoid duplicates and monitor status.
- **YouTube Uploader**: Uploads the final video to YouTube (OAuth2 authenticated).

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


```
src/
├── scanner/          # GitHub API interaction
├── agents/           # LLM interaction (Gemini/Foundry)
├── engine/           # Visual recording (Playwright) and Rendering (MoviePy + EdgeTTS)
├── uploader/         # YouTube API interaction
├── persistence/      # Firebase Firestore integration
└── image_gen/        # Image generation with Nano Banana 2
```

### Pipeline Flow

1. **Scan** → Find quality repositories on GitHub
2. **Check** → Verify not already processed (Firebase)
3. **Analyze** → Generate script with AI (Gemini/Foundry)
4. **Visualize** → Generate explanatory images (Nano Banana 2)
5. **Record** → Capture repository tour (Playwright)
6. **Render** → Combine video + narration (MoviePy + EdgeTTS)
7. **Upload** → Publish to YouTube
8. **Track** → Update status in Firebase

## 📚 Documentation

- [PLANNING.md](PLANNING.md) - Project architecture and roadmap
- [TASK.md](TASK.md) - Detailed task tracking
- [RULES.md](RULES.md) - Development rules and standards
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Latest implementation details

## 🤝 Contributing

See [RULES.md](RULES.md) for development guidelines and coding standards.

## 📄 License

MIT License - See LICENSE file for details