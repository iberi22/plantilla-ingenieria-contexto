# 🌟 Best of Open Source

**Automated discovery and analysis** of high-quality open source projects using **Rust + Python + AI**.

> 🚀 **Performance:** 60x faster analysis with Rust parallelism + GitHub Models API for AI insights

## 🎯 What's This

Discover hidden gems in the open source world through:

- 🦀 **Rust Scanner** - Parallel repository analysis (60x faster!)
- 🤖 **AI Review** - GitHub Models API for quality assessment
- 📝 **Blog Generator** - Automated Astro blog posts
- 🔄 **GitHub Actions** - Fully automated daily pipeline

## 🌐 Live Site

Visit our blog at: **[https://iberi22.github.io/bestof-opensorce](https://iberi22.github.io/bestof-opensorce)**

## ⚡ Quick Start

### Option 1: GitHub Actions (Recommended)

1. Go to **Actions** tab
2. Select **🔍 Hidden Gems Discovery Pipeline**
3. Click **Run workflow**
4. Choose tier (micro/small/medium) and max repos
5. Watch it discover, analyze, and publish! 🎉

### Option 2: Local Testing

See [MANUAL_TESTING_GUIDE.md](MANUAL_TESTING_GUIDE.md) for detailed steps.

```powershell
# Quick test
cargo build --release --bin complete-analyzer
.\rust-scanner\target\release\complete-analyzer.exe small 3
```

## 🏗️ Architecture

### Hybrid Rust + Python Pipeline

```text
┌─────────────────────────────────────────────────────────────┐
│  Phase 1-2: RUST (Parallel Analysis) ⚡                     │
│  - GitHub API scanning                                      │
│  - Rayon parallel processing (10 repos simultaneously)      │
│  - 4-factor scoring (commit, quality, engagement, maturity) │
│  - Output: JSON with analysis results                       │
│  - Performance: ~4 seconds for 10 repos (60x faster!)       │
└─────────────────────────────────────────────────────────────┘
                            ↓ JSON
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: PYTHON (AI Review) 🤖                             │
│  - GitHub Models API (gpt-4o)                               │
│  - Architecture, docs, testing, practices, innovation       │
│  - Strengths & weaknesses analysis                          │
│  - Output: Enhanced JSON with AI insights                   │
└─────────────────────────────────────────────────────────────┘
                            ↓ JSON
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: PYTHON (Blog Generation) 📝                       │
│  - Astro markdown blog posts                                │
│  - Complete with frontmatter & content                      │
│  - Output: website/src/content/blog/*.md                    │
└─────────────────────────────────────────────────────────────┘
                            ↓ Git Commit
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions: Auto-deploy to GitHub Pages 🚀            │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **`rust-scanner/`** - High-performance parallel analyzer
  - `analyzer.rs` - 4-factor scoring with Rayon
  - `complete_analyzer.rs` - Main pipeline orchestrator

- **`scripts/`** - Python bridge scripts
  - `ai_review_from_rust.py` - Consumes Rust JSON, adds AI review
  - `generate_blogs_from_analysis.py` - Creates Astro blog posts

- **`src/blog_generator/`** - Blog post generation
  - `blog_post_generator.py` - High-level generator
  - `markdown_writer.py` - Astro-compatible markdown writer

- **`scripts/`** - Image generation
  - `generate_blog_images.py` - Gemini AI image generator (ready)
  - `generate_placeholder_headers.py` - SVG fallbacks (active)
  - See [IMAGE_GENERATION_STATUS.md](./IMAGE_GENERATION_STATUS.md) for details

- **`.github/workflows/`** - Automation
  - `discover-hidden-gems.yml` - Daily pipeline (6 AM UTC)

### Documentation

- [GITHUB_ACTIONS_PIPELINE.md](./GITHUB_ACTIONS_PIPELINE.md) - Pipeline details
- [MANUAL_TESTING_GUIDE.md](./MANUAL_TESTING_GUIDE.md) - Local testing

## 📂 Project Structure

```
investigations/      # ⭐ Markdown database (main content)
website/             # Astro blog frontend
src/
├── scanner/         # GitHub repository scanner
└── persistence/     # Data storage layer
scripts/
├── run_scanner.py   # Public scanner script
└── watch_blog.py    # Blog watcher
docs/
├── INDEX.md         # Documentation index
├── archive/         # Historical documentation
├── planning/        # Roadmaps and planning
└── sprints/         # Sprint reports
tests/               # Unit tests
```

## 🚀 Contributing

We welcome contributions! To add a new investigation:

1. Fork this repository
2. Create a new markdown file in \investigations/\
3. Follow the frontmatter format:

\\\yaml
---
url: https://github.com/owner/repo
name: Project Name
category: web-framework
language: JavaScript
stars: 10000
status: active
reviewed: false
---
\\\

4. Submit a pull request

## 🔧 Local Development

### Blog Website (Astro)

```bash
cd website
npm install
npm run dev
```

### Scanner Script (10x Faster with Rust!)

```bash
# Option 1: Quick setup with Rust (recommended)
.\rust-scanner\setup.ps1

# Option 2: Python only
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python scripts/run_scanner.py
```

**Performance:**
- 🦀 Rust scanner: ~3 seconds
- 🐍 Python fallback: ~30 seconds

See [rust-scanner/QUICKSTART.md](rust-scanner/QUICKSTART.md) for details.

## 📊 Stats

- **Investigations:** Microsoft.PowerShell.Commands.GenericMeasureInfo.Count+ projects analyzed
- **Categories:** AI, Web Frameworks, Developer Tools, DevOps, etc.
- **Languages:** Python, JavaScript, TypeScript, Go, Rust, and more

## 🤝 Community

- **Discussions:** [GitHub Discussions](https://github.com/iberi22/bestof-opensorce/discussions)
- **Issues:** [Report bugs or request features](https://github.com/iberi22/bestof-opensorce/issues)

## 📝 License

**MIT License** - This repository is open source and free to use.

---

**Note:** Video generation, TTS, and advanced content processing are handled in a private repository to protect API keys and proprietary assets.
