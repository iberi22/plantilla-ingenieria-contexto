# YouTube MCP Analysis

## Overview
The `youtube-mcp-server` (by ZubeidHendricks) is an implementation of the **Model Context Protocol (MCP)** for YouTube.
MCP is a standard that enables AI models to interact with external tools and data.

## Features
- **Video Info:** Get details, stats, search.
- **Transcripts:** Fetch transcripts.
- **Channel/Playlist:** Manage channels and playlists.

## MCP Architecture
MCP works on a Client-Server model.
- **Server:** Exposes tools (like `get_video_details`, `search_videos`).
- **Client:** (Usually an LLM interface like Claude Desktop or an IDE) connects to the server and calls these tools.

## Relevance to Our Goal
Our goal is **Automated Video Upload**.
Reviewing the `README.md` and features of `zubeid-youtube-mcp-server`:
- It supports **Reading** data (Video details, Transcripts, Search).
- It **does NOT** seem to support **Uploading** videos.

The provided examples show `getVideo`, `getTranscript`, `searchVideos`. There is no `uploadVideo` or `insertVideo`.

## Conclusion
The existing `youtube-mcp-server` is read-focused (Data API). Uploading requires `videos.insert` with media upload support, which is often more complex due to large file handling and OAuth write scopes.

Using this specific MCP server would require forking it and adding Upload capabilities.

## Alternative: Direct Integration
Direct integration using `google-api-python-client` (as we partially have in `src/uploader/youtube.py`) is more direct for a backend service. MCP is great for exposing tools to an *Agent* (like me, or Claude), but for a scheduled background job (`ReelCreator` -> Upload), a direct library call is more efficient than running an MCP server + client.

However, the prompt asks to "Evaluate Strategies".
1.  **Option A: MCP Protocol**
    *   Pros: Standardized interface. If we want to let an AI agent manage the channel later (e.g. "Check comments and reply"), MCP is great.
    *   Cons: The current server lacks Upload. We'd need to build a custom MCP server or extend this one. Adds overhead of running an MCP server process.
2.  **Option B: Direct API (Extraction)**
    *   Pros: Simple, already partially implemented, full control over OAuth flow (which is tricky for uploads).
    *   Cons: Not "AI-ready" in the standardized sense (but we are building the automation logic, not exposing it to an LLM user).

## Recommendation
Given that we need **Upload** automation (Phase 7 objective) and the analyzed MCP server lacks it, **Option B (Direct API)** is the pragmatic choice for this sprint. We can structure it cleanly so it *could* be wrapped in an MCP server later if desired.

For the purpose of this task, we will implement a robust `YouTubeAPIClient`.
