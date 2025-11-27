from playwright.sync_api import sync_playwright, expect

def verify_blog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Assuming Astro dev server runs on 4321
        page = browser.new_page()
        try:
            page.goto("http://localhost:4321")

            # Wait for content
            page.wait_for_selector("text=OpenCut - Video Editor Made Simple", timeout=10000)

            # Screenshot of directory with real content
            page.screenshot(path="verification/directory.png", full_page=False)
            print("Directory screenshot taken")

            # Click on the blog post
            page.click("text=OpenCut - Video Editor Made Simple")

            # Wait for blog post content
            page.wait_for_selector("h1", timeout=5000)
            expect(page.get_by_role("heading", level=1)).to_contain_text("OpenCut")

            # Screenshot of blog post
            page.screenshot(path="verification/blog_post.png", full_page=True)
            print("Blog post screenshot taken")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_blog()
