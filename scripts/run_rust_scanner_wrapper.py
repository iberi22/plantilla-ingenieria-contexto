#!/usr/bin/env python3
"""
Run Rust Scanner Wrapper
Executes the Rust binary and extracts the JSON output.
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("Usage: run_rust_scanner_wrapper.py <tier> <output.json>")
        sys.exit(1)

    tier = sys.argv[1]
    output_file = sys.argv[2]

    # Path to Rust binary
    rust_bin = Path(__file__).parent.parent / 'rust-scanner' / 'target' / 'release' / 'hidden-gems-scanner.exe'

    if not rust_bin.exists():
        # Try without .exe (linux/mac)
        rust_bin = rust_bin.with_suffix('')

    if not rust_bin.exists():
        print(f"❌ Rust binary not found at {rust_bin}")
        print("Please run 'cargo build --release' in rust-scanner directory first.")
        sys.exit(1)

    print(f"🚀 Running Rust Scanner ({tier})...")

    env = os.environ.copy()
    if 'GITHUB_TOKEN' not in env:
        print("❌ GITHUB_TOKEN not set in environment")
        sys.exit(1)

    try:
        result = subprocess.run(
            [str(rust_bin), tier],
            capture_output=True,
            text=True,
            env=env,
            encoding='utf-8'
        )

        if result.returncode != 0:
            print(f"❌ Rust scanner failed: {result.stderr}")
            sys.exit(1)

        # Extract JSON
        stdout = result.stdout
        start_marker = "__REPO_JSON__"
        end_marker = "__END_JSON__"

        if start_marker not in stdout or end_marker not in stdout:
            print("❌ Could not find JSON markers in output")
            print(stdout)
            sys.exit(1)

        json_str = stdout.split(start_marker)[1].split(end_marker)[0].strip()

        # Validate JSON
        data = json.loads(json_str)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Saved {len(data)} repos to {output_file}")

    except Exception as e:
        print(f"❌ Error running scanner: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
