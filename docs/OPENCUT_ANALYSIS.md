# OpenCut Analysis

## Overview
OpenCut is a web-based video editor using Next.js, FFmpeg.wasm, and React. It provides a timeline-based editing experience, multi-track support, and real-time preview.

## Architecture
- **Frontend:** Next.js (React)
- **State Management:** Zustand
- **Video Processing:** FFmpeg (WASM) client-side
- **Backend/Database:** PostgreSQL with Drizzle ORM (Auth, Projects)

## Key Components
- `apps/web/src/components/` contains the UI components.
- `apps/web/src/stores/` manages the editor state.
- `apps/web/src/lib/` likely contains utility logic.

## Integration Points
Since OpenCut is a Next.js app, integrating it deeply into a Flask/Python backend + React frontend (our current stack) implies some challenges.

### Options:
1.  **Submodule/Fork:** Run OpenCut as a separate service on a different port. Our app links to it.
2.  **Component Extraction:** Extract specific React components (Timeline, Preview) and adapt them to our React app. This is complex due to dependencies (Next.js specific hooks, specific state management).
3.  **API/IPC:** Generate a project file compatible with OpenCut, and provide a "Edit in OpenCut" button that opens the OpenCut instance with that project loaded.

## Recommendation
Given the complexity of extracting components from a Next.js app into a generic React app (and the likely dependencies on Next.js specific features), the most robust path is **Option 3: API/IPC**.

We can treat OpenCut as a "service" or "tool" that we launch or link to.
However, the user wants "Integration" and "OpenCut Video Editor Integration".
The prompt says: "Integrar OpenCut para permitir edición manual opcional de videos auto-generados."

If we run OpenCut as a standalone web app, we need a way to pass the generated video assets to it.
OpenCut uses a database to store projects. We might need to inject a project into its DB or see if it supports importing from JSON.

Looking at `package.json`, it uses `@ffmpeg/ffmpeg`. It's client-side editing.
If we can reverse-engineer the project format, we can generate a project file and let OpenCut load it.

## Pros/Cons of Integration Strategies
*   **Fork/Submodule (Standalone):**
    *   Pros: Easiest to maintain, updates from upstream.
    *   Cons: Separate running process/port. User context switching.
*   **Component Extraction:**
    *   Pros: Seamless UI.
    *   Cons: Very high effort to decouple from Next.js. Breaking changes from upstream.
*   **API/IPC (Bridge):**
    *   Pros: Loose coupling.
    *   Cons: Need to reverse engineer project format.

## Chosen Strategy: Bridge/IPC
We will assume OpenCut runs as a separate service (or we provide a way to launch it). The "Integration" will primarily be generating a project file or structure that OpenCut understands, and redirecting the user there.

However, the prompt asks to *implement* the bridge.
I will assume we can define a JSON structure for the project.

## Dependencies
- FFmpeg WASM
- React
- Zustand
