import os
import re
from pathlib import Path

def cleanup_files():
    blog_dir = Path("website/src/content/blog")
    files = list(blog_dir.rglob("*.md"))

    print(f"Found {len(files)} markdown files.")

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Pattern to match "Full Narration" section and everything after it
            # Adjust regex if the section is not always at the end
            # Using a simpler split approach might be safer if it's always at the end

            if "### 📝 Full Narration" in content:
                print(f"Cleaning {file_path.name}...")
                # Split and keep the first part
                new_content = content.split("### 📝 Full Narration")[0]

                # Clean up trailing newlines/separators
                new_content = new_content.rstrip()
                if new_content.endswith("---"):
                    new_content = new_content[:-3].rstrip()

                # Add one newline at end of file
                new_content += "\n"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("Done.")
            else:
                print(f"Skipping {file_path.name} (no Full Narration found)")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    cleanup_files()
