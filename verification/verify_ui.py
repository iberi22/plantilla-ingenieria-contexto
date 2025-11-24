from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Navigate to frontend
            page.goto("http://localhost:5173")

            # Wait for title
            expect(page.get_by_text("Voice Studio Pro")).to_be_visible()

            # Check for main sections
            expect(page.get_by_text("Record Narration")).to_be_visible()

            # Take screenshot of initial state
            page.screenshot(path="verification/ui_initial.png")
            print("Initial UI screenshot captured.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
