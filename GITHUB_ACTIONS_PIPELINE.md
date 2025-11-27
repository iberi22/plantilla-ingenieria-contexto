# 🚀 GitHub Actions Pipeline - Hidden Gems Discovery

## Architecture Overview

This project uses a **hybrid Rust + Python pipeline** optimized for performance and flexibility:

### Pipeline Phases

```
┌─────────────────────────────────────────────────────────────┐
│  🦀 RUST (Parallel, Fast)                                   │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: Scan repositories (GitHub API)                    │
│  Phase 2: Analyze in parallel with Rayon (10 concurrent)    │
│           - Commit activity (last 90 days)                  │
│           - Code quality (README, tests, CI/CD)             │
│           - Developer engagement (issues, PRs)              │
│           - Project maturity (age, stars, forks)            │
│  Output: JSON with scores (60x faster than Python!)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  🐍 PYTHON (AI Review, Blog Generation)                     │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: AI Review with GitHub Models API                  │
│           - Architecture (1-10)                             │
│           - Documentation (1-10)                            │
│           - Testing (1-10)                                  │
│           - Best Practices (1-10)                           │
│           - Innovation (1-10)                               │
│  Phase 4: Generate Astro blog posts                         │
│           - Frontmatter with metadata                       │
│           - Content sections (overview, features, etc)      │
│           - AI insights and recommendations                 │
└─────────────────────────────────────────────────────────────┘
```

## 🏃 Running Locally

### Quick Test (Manual)

```powershell
# 1. Build Rust scanner
cd rust-scanner
cargo build --release --bin complete-analyzer

# 2. Run Rust analysis
$env:GITHUB_TOKEN = (Get-Content .env | Select-String "GITHUB_TOKEN").ToString().Split('=')[1].Trim()
$env:RUST_LOG = "info"
.\target\release\complete-analyzer.exe small 3 | Tee-Object output\rust_analysis.log

# 3. Extract JSON
Get-Content output\rust_analysis.log | 
  Select-String -Pattern '__RESULTS_JSON__' -Context 0,1000 | 
  Out-File output\rust_results.json

# 4. Run AI review
python scripts\ai_review_from_rust.py output\rust_results.json output\with_ai_review.json

# 5. Generate blogs
python scripts\generate_blogs_from_analysis.py output\with_ai_review.json
```

## 🤖 GitHub Actions Workflow

### Automatic Trigger (Daily)

The workflow runs **daily at 6 AM UTC** automatically:

```yaml
schedule:
  - cron: '0 6 * * *'
```

### Manual Trigger

Go to **Actions** tab → **🔍 Hidden Gems Discovery Pipeline** → **Run workflow**

Parameters:
- **tier**: `micro` | `small` | `medium` (repository size)
- **max_repos**: Number of repositories to approve (default: 3)

### Workflow Steps

1. **📥 Checkout** - Clone repository
2. **🦀 Setup Rust** - Install Rust toolchain with cache
3. **🐍 Setup Python** - Install Python 3.11 with pip cache
4. **📦 Install Dependencies** - Install Python packages
5. **🔨 Build Rust Scanner** - Compile with `--release` optimizations
6. **🔍 Phase 1 & 2** - Rust parallel analysis (fast!)
7. **🤖 Phase 3** - Python AI review with GitHub Models
8. **📝 Phase 4** - Generate blog posts
9. **📊 Summary Report** - Display results in GitHub UI
10. **📤 Commit** - Push new blog posts to repository
11. **📁 Upload Artifacts** - Save JSON results (30 days retention)

## 📊 Performance

### Benchmarks (10 repositories)

| Phase | Component | Time | Speedup |
|-------|-----------|------|---------|
| 1-2 | Rust analysis | ~4 seconds | **60x faster** |
| 3 | Python AI review | ~30 seconds | - |
| 4 | Blog generation | ~10 seconds | - |
| **Total** | **End-to-end** | **~44 seconds** | **5x faster** |

Old Python pipeline: ~4 minutes

## 🔧 Configuration

### Environment Variables

Required in GitHub Actions Secrets:
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

Optional (for local testing):
- `RUST_LOG` - Set to `info` or `debug` for verbose output
- `ENABLE_AI_REVIEW` - Set to `1` to enable AI review in Rust (experimental)

### Repository Tiers

- **micro**: 1-100 stars
- **small**: 100-1000 stars
- **medium**: 1000-10000 stars

### Scoring Thresholds

- **APPROVE**: Score ≥ 70/100
- **REVIEW**: Score 50-69/100
- **REJECT**: Score < 50/100

## 📁 Output Files

All outputs saved to `output/` directory:

- `rust_analysis.log` - Full Rust execution log
- `rust_results.json` - Rust analysis results (no AI review)
- `with_ai_review.json` - Complete analysis with AI insights
- Blog posts → `website/src/content/blog/*.md`

## 🐛 Troubleshooting

### Rust build fails

```bash
# Clean build cache
cd rust-scanner
cargo clean
cargo build --release
```

### AI review fails

Check GitHub Models API quota:
```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://models.inference.ai.azure.com/chat/completions
```

### Blog generation fails

Check that `with_ai_review.json` has APPROVE recommendations:
```bash
jq '.[] | select(.recommendation == "APPROVE")' output/with_ai_review.json
```

## 🎯 Next Steps

1. ✅ Monitor GitHub Actions workflow runs
2. ✅ Review generated blog posts in `website/src/content/blog/`
3. ✅ Deploy website to see new posts live
4. 📈 Adjust thresholds based on results quality
5. 🚀 Scale up: increase `max_repos` parameter

## 📚 Related Documentation

- [Rust Analyzer](../rust-scanner/README.md) - Technical details
- [GitHub Models API](../docs/GITHUB_MODELS_MIGRATION.md) - API integration
- [Blog Generator](../src/blog_generator/README.md) - Blog post format

---

**Built with** 🦀 Rust + 🐍 Python + ⚡ GitHub Actions
