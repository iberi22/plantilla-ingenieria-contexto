# YouTube Integration Decision

## Decision: Option B (Direct API Integration)

### Justification
1.  **Functionality Gap:** The analyzed `youtube-mcp-server` only supports read operations (Data API) and lacks video upload capabilities.
2.  **Complexity:** Implementing a full MCP server just for a background upload task adds unnecessary architectural overhead (running a separate Node.js/Python server process just to call an API).
3.  **OAuth Handling:** Uploading to YouTube requires sensitive OAuth handling (refresh tokens, write scopes). Managing this directly in our backend application is more secure and straightforward than delegating it to a generic MCP server.
4.  **Performance:** Direct library calls (`google-api-python-client`) are faster and easier to debug than IPC calls to an MCP server.

### Implementation Plan
We will enhance the existing `src/uploader/youtube.py` (renaming or refactoring it to `YouTubeAPIClient` pattern) to include:
- Robust OAuth flow with token refresh.
- Resumable uploads for large files.
- Metadata management (Title, Description, Tags).
- Retry logic with exponential backoff.

### Future MCP Compatibility
We will design the `YouTubeAPIClient` class with clean methods (`upload`, `get_stats`) that can be easily wrapped by an MCP server in the future if we decide to expose these capabilities to an AI agent.

## Architecture
- **Module:** `src/uploader/youtube_api_client.py`
- **Key Class:** `YouTubeAPIClient`
- **Integration:** Called by `src/video_generator/reel_creator.py` after video generation.
