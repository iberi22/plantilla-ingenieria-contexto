# 🧪 Manual Testing Guide

## Test the Pipeline Locally

### Prerequisites

```powershell
# 1. Ensure Rust is installed
rustc --version

# 2. Ensure Python 3.11+ is installed
python --version

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Set environment variables
$env:GITHUB_TOKEN = (Get-Content .env | Select-String "GITHUB_TOKEN").ToString().Split('=')[1].Trim()
$env:RUST_LOG = "info"
```

### Step-by-Step Test

#### Step 1: Build Rust Scanner

```powershell
cd rust-scanner
cargo build --release --bin complete-analyzer
cd ..
```

Expected output:
```
Compiling rayon v1.11.0
Compiling futures v0.3.31
Finished `release` profile [optimized] target(s) in ~50s
```

#### Step 2: Run Rust Analysis

```powershell
# Create output directory
New-Item -ItemType Directory -Force -Path output

# Run analyzer
.\rust-scanner\target\release\complete-analyzer.exe small 3 | Tee-Object output\rust_analysis.log
```

Expected output:
```
[INFO] 📍 PHASE 1: Scanning for repositories...
[INFO] 🔍 Found 15 candidate repositories
[INFO] 📍 PHASE 2: Analyzing repositories in parallel...
[INFO] 🚀 Starting parallel analysis of 15 repositories with Rayon
[INFO] ✅ Analyzed owner/repo: 85.50/100
...
[INFO] 🎉 Phase 2 complete: 15 analyzed, 3 approved, 8 review, 4 reject
```

#### Step 3: Extract JSON

```powershell
# Extract JSON between markers
$content = Get-Content output\rust_analysis.log -Raw
$pattern = '(?s)__RESULTS_JSON__\s*(.*?)\s*__END_JSON__'
if ($content -match $pattern) {
    $Matches[1] | Out-File output\rust_results.json -Encoding utf8
    Write-Host "✅ JSON extracted successfully"
} else {
    Write-Host "❌ Failed to extract JSON"
}
```

#### Step 4: Run AI Review (Python)

```powershell
python scripts\ai_review_from_rust.py output\rust_results.json output\with_ai_review.json
```

Expected output:
```
📥 Loading Rust analysis from output\rust_results.json...
📊 Found 15 repositories to review

[1/15] owner/repo - APPROVE
  🤖 Running AI review...
  ✅ AI Review: 82.5/100
     Architecture: 8/10
     Documentation: 9/10
     Testing: 7/10
...
✅ AI Review Complete:
   - Total analyzed: 15
   - Approved: 3
   - With AI review: 3
```

#### Step 5: Generate Blog Posts

```powershell
python scripts\generate_blogs_from_analysis.py output\with_ai_review.json
```

Expected output:
```
📥 Loading analysis from output\with_ai_review.json...
📊 Found 3 approved repositories

📝 Generating blog post for owner/repo...
  ✅ Blog post created: 20250127-owner-repo.md
...
✅ Blog Generation Complete:
   - Approved repositories: 3
   - Blog posts generated: 3

📁 Generated files:
   - 20250127-owner-repo.md
```

#### Step 6: Verify Blog Posts

```powershell
# List generated blog posts
Get-ChildItem website\src\content\blog\*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# View a blog post
Get-Content website\src\content\blog\20250127-owner-repo.md
```

Expected structure:
```markdown
---
title: "Repo Name - Description"
date: 2025-01-27
description: "Repository description"
repo: owner/repo
stars: 1234
language: Python
tags: ["python", "ai", "tools"]
categories: ["AI Tools"]
---

## 🎯 The Problem
...

## 💡 The Solution
...

## ✅ Advantages
- ...

## 🎬 Verdict
...
```

### Troubleshooting

#### Rust Build Fails

```powershell
# Clean and rebuild
cd rust-scanner
cargo clean
cargo build --release --bin complete-analyzer
```

#### JSON Extraction Fails

Check log file contains markers:
```powershell
Select-String "__RESULTS_JSON__" output\rust_analysis.log
Select-String "__END_JSON__" output\rust_analysis.log
```

#### AI Review Fails

Test GitHub Models API:
```powershell
$token = $env:GITHUB_TOKEN
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{
    model = "gpt-4o"
    messages = @(
        @{
            role = "user"
            content = "Test"
        }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://models.inference.ai.azure.com/chat/completions" -Method POST -Headers $headers -Body $body
```

#### Blog Generation Fails

Check JSON structure:
```powershell
$data = Get-Content output\with_ai_review.json | ConvertFrom-Json
$data | ForEach-Object { Write-Host "$($_.repo) - $($_.recommendation) - $($_.total_score)" }
```

### Performance Benchmarks

Expected times:
- Rust build: ~50 seconds (first time), ~5 seconds (incremental)
- Rust analysis (10 repos): ~4 seconds ⚡
- AI review (3 repos): ~30 seconds
- Blog generation (3 repos): ~10 seconds
- **Total**: ~44 seconds for 3 blog posts!

Compare to old Python pipeline: ~4 minutes = **5x faster!** 🚀

### Clean Up

```powershell
# Remove output files
Remove-Item output\*.log, output\*.json -Force

# Remove test blog posts
Remove-Item website\src\content\blog\20250127-*.md -Force
```

---

**Ready for GitHub Actions?** See [GITHUB_ACTIONS_PIPELINE.md](GITHUB_ACTIONS_PIPELINE.md)
