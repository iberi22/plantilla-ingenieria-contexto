# Automation Pipeline Guide

## Overview
The `scripts/run_pipeline.py` script acts as the orchestrator for the Video Generator ecosystem. It connects the Blog Generation, Video Creation, and YouTube Upload phases into a single workflow.

## Usage

```bash
python3 scripts/run_pipeline.py --repo https://github.com/owner/repo --upload
```

### Arguments
- `--repo`: The URL of the GitHub repository to process.
- `--blog-post` (Optional): Path to an existing Markdown blog post to generate video from.
- `--upload` (Optional): Flag to enable automatic upload to YouTube.

## Workflow Steps

1.  **Input Analysis:** Takes a repo URL.
2.  **Blog Generation:** (Simulated in current version) Generates script content and highlights.
3.  **Video Generation:** Calls `ReelCreator` to compile images, text, and audio into a 20s vertical reel.
4.  **Upload:** If enabled, uses `YouTubeAPIClient` (via `ReelCreator`) to upload the video with metadata.

## Environment Variables
For uploads to work, ensure `.env` contains:
- `YOUTUBE_CLIENT_SECRET_FILE`: Path to `client_secret.json`
- `YOUTUBE_TOKEN_FILE`: Path to `token.pickle`

## Integration Details
The pipeline uses `src/video_generator/reel_creator.py` which now internally supports `YouTubeAPIClient`. This encapsulates the "Create & Publish" logic within the generator itself.
