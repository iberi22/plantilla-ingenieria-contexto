# Run Full Rust Pipeline
# Orchestrates the entire flow from Rust scanning to Blog generation

$ErrorActionPreference = "Stop"

# Load .env if it exists (simple parsing)
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

if (-not $env:GITHUB_TOKEN) {
    Write-Error "GITHUB_TOKEN is missing. Please check .env file."
    exit 1
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutputDir = "output"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$RustOutput = "$OutputDir/rust_scan_$Timestamp.json"
$BridgeOutput = "$OutputDir/bridge_scan_$Timestamp.json"
$AiOutput = "$OutputDir/ai_scan_$Timestamp.json"

Write-Host "🚀 Starting Full Rust Pipeline..." -ForegroundColor Green

# 1. Run Rust Scanner
Write-Host "`n1️⃣  Running Rust Scanner..." -ForegroundColor Cyan
python scripts/run_rust_scanner_wrapper.py small $RustOutput
if ($LASTEXITCODE -ne 0) { exit 1 }

# 2. Bridge to AI Format
Write-Host "`n2️⃣  Bridging to AI Format..." -ForegroundColor Cyan
python scripts/bridge_rust_to_ai.py $RustOutput $BridgeOutput
if ($LASTEXITCODE -ne 0) { exit 1 }

# 3. AI Review
Write-Host "`n3️⃣  Running AI Review..." -ForegroundColor Cyan
python scripts/ai_review_from_rust.py $BridgeOutput $AiOutput
if ($LASTEXITCODE -ne 0) { exit 1 }

# 4. Generate Blogs
Write-Host "`n4️⃣  Generating Blogs..." -ForegroundColor Cyan
python scripts/generate_blogs_from_analysis.py $AiOutput
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n✅ Pipeline Complete!" -ForegroundColor Green
