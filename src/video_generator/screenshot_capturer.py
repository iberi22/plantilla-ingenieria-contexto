"""
Screenshot Capturer module.

Captures high-quality screenshots of repository webpages using Playwright.
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict
from playwright.async_api import async_playwright

class ScreenshotCapturer:
    """
    Captures screenshots of web pages.
    """

    def __init__(self, output_dir: str = "blog/assets/images"):
        """
        Initialize ScreenshotCapturer.

        Args:
            output_dir: Directory to save screenshots.
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def capture_repo_page(self, url: str, repo_name: str) -> Optional[str]:
        """
        Capture a screenshot of the repository page.

        Args:
            url: URL of the repository.
            repo_name: Name of the repository (for filename).

        Returns:
            Path to the saved screenshot, or None if failed.
        """
        try:
            self.logger.info(f"Capturing screenshot for {url}")

            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    device_scale_factor=2
                )
                page = await context.new_page()

                # Navigate
                await page.goto(url, wait_until="networkidle")

                # Try to remove cookie banners (basic heuristic)
                await self._remove_banners(page)

                # Create output path
                safe_name = repo_name.lower().replace(" ", "-").replace("/", "-")
                repo_dir = self.output_dir / safe_name
                repo_dir.mkdir(parents=True, exist_ok=True)

                output_path = repo_dir / "screenshot.png"

                # Take screenshot
                await page.screenshot(path=str(output_path), full_page=False)

                await browser.close()

                self.logger.info(f"Screenshot saved to {output_path}")
                return str(output_path)

        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return None

    async def capture_highlights(self, url: str, repo_name: str, highlights: Dict[str, str]) -> Dict[str, str]:
        """
        Capture screenshots of specific elements on the page.

        Args:
            url: URL of the repository.
            repo_name: Name of the repository.
            highlights: Dictionary mapping name to CSS selector (e.g., {'readme': 'article.markdown-body'}).

        Returns:
            Dictionary mapping highlight name to file path.
        """
        results = {}
        try:
            self.logger.info(f"Capturing highlights for {url}")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    device_scale_factor=2
                )
                page = await context.new_page()
                if url.startswith("file://"):
                    # For local files, we might need to wait for load event
                    await page.goto(url)
                else:
                    await page.goto(url, wait_until="networkidle")

                await self._remove_banners(page)

                safe_name = repo_name.lower().replace(" ", "-").replace("/", "-")
                repo_dir = self.output_dir / safe_name
                repo_dir.mkdir(parents=True, exist_ok=True)

                for name, selector in highlights.items():
                    try:
                        # Wait for selector to appear (useful for client-side rendered content)
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                        except:
                            pass # proceed to query_selector

                        element = await page.query_selector(selector)
                        if element:
                            output_path = repo_dir / f"{name}.png"
                            await element.screenshot(path=str(output_path))
                            results[name] = str(output_path)
                            self.logger.info(f"Captured highlight '{name}' to {output_path}")
                        else:
                            self.logger.warning(f"Element not found for highlight '{name}' (selector: {selector})")
                    except Exception as e:
                        self.logger.error(f"Failed to capture highlight '{name}': {e}")

                await browser.close()

        except Exception as e:
            self.logger.error(f"Failed to capture highlights: {e}")

        return results

    async def _remove_banners(self, page):
        """Attempt to remove common cookie banners and popups."""
        try:
            # Common selectors for cookie banners
            selectors = [
                "#cookie-banner",
                ".cookie-banner",
                "[aria-label='cookie consent']",
                ".js-consent-banner" # GitHub specific
            ]

            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await page.evaluate("(element) => element.remove()", element)
                except:
                    pass
        except Exception:
            pass

