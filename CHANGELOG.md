# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-01-28 - GitHub Models API Migration

### 🤖 AI Review System Overhaul

#### Changed
- **Migrated to GitHub Models API** (`src/scanner/grok_reviewer.py`)
  - ❌ **Deprecated**: gh-copilot CLI extension (announced Sept 2025)
  - ✅ **New**: Direct REST API calls to `https://models.inference.ai.azure.com`
  - Uses GitHub token authentication (via `gh auth token` or `GITHUB_TOKEN`)
  - Supports multiple models: gpt-4o, gpt-4o-mini, claude-3.5-sonnet, phi-4
  - No external API keys required (leverages Copilot subscription)

#### Fixed
- **Blog Content Generation** (`scripts/discover_hidden_gems.py`)
  - Blog posts now generate complete content sections:
    - 🎯 Problem statement with context
    - 💡 Solution description with gem score
    - ✅ Strengths list (3+ items from analysis)
    - ⚠️ Considerations (areas to improve)
    - 🎬 Verdict with recommendation
    - 📝 Full narration with technical details
  - Previously only generated frontmatter (causing empty posts)

#### Removed
- `XAI_API_KEY` dependency (xAI/Grok direct API approach abandoned)
- `GOOGLE_API_KEY` dependency (Gemini rate limits too restrictive)
- All external API key requirements from `discover_hidden_gems.py`

#### Documentation
- ✅ Created `docs/COPILOT_INTEGRATION.md` - Complete guide for GitHub Models API
- ✅ Added `scripts/test_grok.py` - Test reviewer initialization
- ✅ Added `scripts/test_api_call.py` - Test real API calls with sample data
- ⚠️ `docs/GROK_INTEGRATION.md` now obsolete (xAI approach abandoned)

#### Testing Results
```
✅ Token detection: Working (gh CLI + environment variable)
✅ API authentication: Successful (Bearer token)
✅ Model call (gpt-4o): Response received in ~2s
✅ JSON parsing: Extracted all 5 scores + strengths + assessment
✅ Retry logic: Exponential backoff implemented
```

---

## [PR #2] - 2025-01-XX - Voice Translation Studio & Video Enhancements

### 🎙️ Voice Translation Studio (Area 1)

#### Added
- **Interactive React UI** (`web/src/components/VoiceRecorder.jsx`)
  - Browser-based voice recording with MediaRecorder API
  - Real-time audio playback and preview
  - Step-by-step workflow with visual feedback
  - Modern dark-themed gradient UI with Lucide icons
  - Responsive design for desktop and mobile

- **Backend API Endpoints** (`api/multilingual_api.py`)
  - `POST /api/transcribe` - Transcribe audio using Whisper
  - `POST /api/translate` - Translate text to multiple languages
  - `POST /api/synthesize` - Synthesize speech with voice cloning (XTTS v2)
  - `POST /api/upload-image` - Upload custom scene images
  - `POST /api/generate-video` - Generate single language video
  - `POST /api/generate-multilingual-reels` - Batch generate videos (legacy)
  - `GET /api/languages` - Get supported languages list
  - `GET /api/download/<filename>` - Download generated files
  - `GET /api/serve-audio/<filename>` - Serve audio for preview

- **Workflow Features**
  - Multi-step process: Record → Transcribe → Translate → Synthesize → Generate
  - Support for 10+ languages with flags: 🇺🇸 🇪🇸 🇫🇷 🇩🇪 🇮🇹 🇵🇹 🇷🇺 🇨🇳 🇯🇵 🇸🇦
  - Editable transcription and translation text
  - Custom image upload for architecture, flow, and screenshot sections
  - Individual video generation per language
  - Audio preview for synthesized voices

### 🎬 Video Editing Logic (Area 2)

#### Enhanced
- **ReelCreator** (`src/video_generator/reel_creator.py`)
  - **Dynamic Scene Durations**: Accept custom duration dict for each section
    ```python
    durations = {
        'intro': 3,
        'problem': 5,
        'solution': 5,
        'architecture': 4,
        'outro': 3
    }
    ```
  - **Keyword Highlighting**: Highlight specific words by changing text color to accent
    ```python
    script_data = {
        'hook': 'Text content',
        'hook_highlights': ['keyword1', 'keyword2']
    }
    ```
  - **Background Music Mixing**: Support for background music with volume ducking
    - Automatic looping if music is shorter than video
    - Volume reduction (15%) when narration is present
    - Composite audio mixing with narration

#### Technical Improvements
- Improved audio handling with `CompositeAudioClip`
- Added `MultiplyVolume` effect for music ducking
- Better error handling and logging
- Support for both narration-driven and fixed-duration videos

### 🎨 Blog Design (Area 3)

#### Redesigned
- **Modern Dark Theme** (`blog/assets/css/style.css`)
  - Dark color scheme with blue accents
  - Gradient backgrounds and smooth transitions
  - Responsive card-based layout
  - Glassmorphism effects on header
  - Professional typography with better readability

- **Layout Templates**
  - `blog/_layouts/default.html` - Sticky header with backdrop blur
  - `blog/_layouts/post.html` - Video embedding support with poster
  - Improved meta information display
  - Schema.org markup for SEO

- **Blog Features**
  - Video embedding in posts with controls
  - Featured reel container with styling
  - Responsive design for mobile devices
  - Syntax highlighting support for code blocks

### 🔧 Infrastructure

#### Added
- **Testing**
  - `tests/test_reel_creator_features.py` - Unit tests for dynamic durations and music
  - `verification/verify_ui.py` - Playwright UI verification script
  - Screenshot capture for UI state verification

- **Dependencies**
  - Added to `web/package-lock.json` for React frontend
  - Lucide React icons for UI
  - Flask-CORS for API

#### Fixed
- TTS installation issues on Python 3.12
- MoviePy audio effects imports
- Image file validation and upload handling
- CORS configuration for local development

### 📝 Documentation

#### Updated
- **README.md** - Added Voice Translation Studio section with usage guide
- **Architecture** - Updated to reflect new components and API structure
- Added workflow diagrams for both pipelines
- Comprehensive feature list with emojis

#### API Documentation
- Detailed endpoint documentation in `api/multilingual_api.py` docstrings
- Request/response formats for each endpoint
- Error handling specifications

### 🚀 Usage

#### Start Voice Translation Studio
```bash
# Terminal 1: Backend API
python api/multilingual_api.py

# Terminal 2: Frontend
cd web
npm install
npm run dev
```

#### Access at
- Frontend: `http://localhost:5173`
- API: `http://localhost:5000`

### 🎯 Supported Languages

English (🇺🇸), Español (🇪🇸), Français (🇫🇷), Deutsch (🇩🇪), Italiano (🇮🇹), Português (🇵🇹), Русский (🇷🇺), 中文 (🇨🇳), 日本語 (🇯🇵), العربية (🇸🇦)

### 📊 Statistics

- **16 files changed**
- **+7,018 additions**
- **-884 deletions**

### 🔍 Files Modified

1. `api/multilingual_api.py` - Refactored with granular endpoints
2. `src/video_generator/reel_creator.py` - Dynamic durations, highlights, music
3. `web/src/components/VoiceRecorder.jsx` - Complete voice studio UI
4. `blog/_layouts/default.html` - Modern dark theme layout
5. `blog/_layouts/post.html` - Video embedding support
6. `blog/assets/css/style.css` - Professional styling
7. `blog/index.md` - Updated blog index
8. `tests/test_reel_creator_features.py` - New test suite
9. `verification/verify_ui.py` - UI verification
10. `.gitignore` - Updated exclusions
11. `TASK.md` - Task tracking updates
12. Plus new submodules: TTS, Trainer

---

## Previous Releases

See git history for earlier changes.
