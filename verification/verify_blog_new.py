from playwright.sync_api import sync_playwright, expect

def verify_blog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Check logs showed http://localhost:4321/bestof-opensorce
        # Need to be careful with base path if configured
        page = browser.new_page()
        try:
            # Try root first, then base path if redirected
            page.goto("http://localhost:4321")

            # Print title to debug
            print(f"Page title: {page.title()}")

            # Screenshot of whatever loaded
            page.screenshot(path="verification/debug_home.png")

            # Look for any text on the page
            content = page.content()
            # print(content[:500]) # Print first 500 chars

            if "OpenCut" in content:
                print("Found OpenCut in content")
            else:
                print("OpenCut NOT found in content")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_blog()
