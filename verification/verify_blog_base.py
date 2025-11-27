from playwright.sync_api import sync_playwright, expect

def verify_blog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Correct base path
            url = "http://localhost:4321/bestof-opensorce/"
            print(f"Navigating to {url}")
            page.goto(url)

            # Wait for content
            try:
                page.wait_for_selector("h3:has-text('opencut')", timeout=5000)
                print("Found OpenCut card!")
            except:
                print("Timeout waiting for OpenCut card")

            # Screenshot of directory with real content
            page.screenshot(path="verification/directory_fixed.png", full_page=False)

            try:
                # Click the List View toggle
                page.click("button[title='List View']")
                print("Switched to List View")
                page.wait_for_timeout(1000)

                # Find the BlogCard that contains "opencut"
                # The structure is: div.group containing h2 text=opencut
                # We want to click the "Read Post" link inside that container

                # Locate the container
                card_locator = page.locator(".group", has_text="opencut").first

                # Find the 'Read Post' link inside it
                read_link = card_locator.locator("a", has_text="Read Post")

                read_link.click()
                print("Clicked Read Post for OpenCut")

                # Wait for blog post content
                page.wait_for_selector("h1", timeout=5000)
                expect(page.get_by_role("heading", level=1)).to_contain_text("OpenCut")

                # Screenshot of blog post
                page.screenshot(path="verification/blog_post_fixed.png", full_page=True)
                print("Blog post verified")
            except Exception as e:
                print(f"Failed to navigate to blog post: {e}")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error_fixed.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_blog()
