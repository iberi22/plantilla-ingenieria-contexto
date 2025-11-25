"""
Blog Watcher Script.

Watches the `blog/_posts` directory for new Markdown files and triggers the video generation pipeline.
Useful for local development where you write a post and want the video to auto-generate.
"""

import time
import logging
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BlogWatcher")

class NewPostHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filename = Path(event.src_path).name
        if filename.endswith(".md"):
            logger.info(f"📝 New post detected: {filename}")
            self.trigger_pipeline(event.src_path)

    def trigger_pipeline(self, post_path):
        """Triggers the run_pipeline.py script for the new post."""
        try:
            # Extract repo name from frontmatter or filename if possible
            # For simplicity, we'll just pass the post path and let pipeline handle it
            # But run_pipeline requires --repo.
            # We might need to parse the post to find the repo url.

            repo_url = self._extract_repo_url(post_path)
            if not repo_url:
                logger.warning(f"Could not find 'repo:' in frontmatter of {post_path}. Skipping video generation.")
                return

            logger.info(f"🎬 Triggering video generation for {repo_url}...")

            subprocess.Popen([
                sys.executable,
                "scripts/run_pipeline.py",
                "--repo", repo_url,
                "--blog-post", post_path
                # Add --upload if you want auto-upload locally
            ])

        except Exception as e:
            logger.error(f"Failed to trigger pipeline: {e}")

    def _extract_repo_url(self, post_path):
        """Reads the 'repo:' field from Jekyll frontmatter."""
        try:
            with open(post_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple parsing
                import re
                match = re.search(r'^repo:\s*(.+)$', content, re.MULTILINE)
                if match:
                    repo_slug = match.group(1).strip()
                    # Ensure full URL
                    if "github.com" not in repo_slug:
                        return f"https://github.com/{repo_slug}"
                    return repo_slug
        except Exception:
            pass
        return None

def main():
    path = "blog/_posts"
    if not os.path.exists(path):
        logger.error(f"Directory {path} does not exist. Create it first.")
        return

    event_handler = NewPostHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    logger.info(f"👀 Watching {path} for new posts...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
