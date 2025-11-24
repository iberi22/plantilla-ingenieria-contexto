# Phase 4 & 8 Plan

## Phase 4: GitHub Pages & UI (Polishing)
The existing files show that `default.html`, `post.html`, and `style.css` are already implemented with modern dark mode and sticky header.
However, `FT-01` (Search), `JK-04` (Tags/Categories), and `FT-03` (Gallery) are likely missing.
Also, the `post.html` layout could be enhanced to better display the generated images (Architecture, Flow, Screenshot).

1.  **Enhance `post.html`:** Add specific sections for the 3 key images (Screenshot, Architecture, Flow) if defined in frontmatter.
2.  **Add Search (FT-01):** Implement a simple JS-based search.
3.  **Add Tags Page (JK-04):** Create a tags archive page.

## Phase 8: Automation End-to-End (Advanced)
The basic `scripts/run_pipeline.py` exists. The advanced tasks are:
-   **E2E-02 (Orchestrator):** Simple cron or loop script is likely sufficient for now instead of Celery.
-   **E2E-04 (Webhooks):** A Flask endpoint to trigger the pipeline from a GitHub Webhook.

## Plan Steps

1.  *Enhance Blog UI*
    - Update `blog/_layouts/post.html` to nicely display `architecture`, `flow`, and `screenshot` images if present in the frontmatter.
    - Create `blog/search.html` and `blog/assets/js/search.js` for client-side search.
    - Create `blog/tags.html` for browsing by tag.

2.  *Implement Webhook Trigger (Phase 8)*
    - Create `api/webhook_server.py`: A simple Flask app that listens for GitHub webhooks (e.g., "star" event) to trigger the pipeline for that repo.

3.  *Final Review and Submit*
