# OpenCut Integration Strategy

## Objective
Enable users to edit auto-generated videos using OpenCut.

## Strategy: "Edit Link" with Project Injection

Since OpenCut is a full Next.js application and our app is a React + Flask app, fully embedding the code is impractical within the sprint timeframe. We will adopt a "Bridge" approach.

### 1. Architecture
- **ReelCreator (Python):** Generates the video and assets (audio, images).
- **OpenCutBridge (Python):** Converts the ReelCreator output into a format OpenCut can ingest (likely a JSON project file or a directory structure).
- **Frontend (React):** Displays an "Edit" button. When clicked, it:
    1.  Calls API to prepare the OpenCut project.
    2.  Redirects user to the OpenCut instance (e.g., `localhost:3000/editor/{project_id}`).

### 2. Data Flow
1.  `ReelCreator` finishes video generation.
2.  User clicks "Edit Video".
3.  Backend `OpenCutBridge` creates a new Project in OpenCut's database (or compatible format).
    - It maps the scenes, audio, and video clips to OpenCut's timeline format.
4.  Frontend redirects to OpenCut URL with the new Project ID.
5.  User edits in OpenCut.
6.  User exports from OpenCut.

### 3. Technical Details
- **Bridge Class:** `src/video_editor/opencut_bridge.py`
    - `create_project(video_path, assets)`: Creates project structure.
    - `get_editor_url(project_id)`: Returns the URL.

### 4. Constraints & Assumptions
- We assume OpenCut is running (user responsible for starting it, or we provide a script).
- For this sprint, we simulate the interaction by generating the "Project State" JSON. We won't spin up the full Next.js app in the test environment, but we will write the code that *would* interact with it.

## Implementation Steps
1.  Define `OpenCutProject` data class mirroring OpenCut's state.
2.  Implement `export_for_editing` to save this state.
3.  Update UI to call this endpoint.
