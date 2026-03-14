"""
Browser automation manager for GeminiGrip.

Handles launching or connecting to a browser (Playwright persistent context or
OpenClaw CDP), then performs the Gemini Deep Research workflow: navigate to
Gemini, switch to Deep Research, enter the prompt, and submit.
"""

from __future__ import annotations

import time
from typing import Callable

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

from .config import (
    DEEP_RESEARCH_OPTION_TEXT,
    ELEMENT_WAIT_TIMEOUT,
    GEMINI_BASE_URL,
    NAVIGATION_TIMEOUT,
    OPENCLAW_CDP_URL,
    PROMPT_TEXTAREA,
    START_RESEARCH_TEXT,
    SUBMIT_BUTTON,
    SUBMIT_WAIT_TIMEOUT,
    TOOL_SELECTOR_BUTTON,
    USER_DATA_DIR,
)


class BrowserManagerError(Exception):
    """Raised when a browser automation step fails."""

    pass


class BrowserManager:
    """
    Manages browser lifecycle and Gemini Deep Research automation.

    Supports two modes:
    - Persistent context: launch Chromium with a user data directory (default).
    - OpenClaw CDP: connect to an existing browser via OPENCLAW_CDP_URL.
    """

    def __init__(self, headless: bool = False, on_status: Callable[[str], None] | None = None):
        """
        Args:
            headless: If True, run the browser without a visible window.
            on_status: Optional callback for status messages (e.g. for rich console).
        """
        self._headless = headless
        self._on_status = on_status or (lambda _: None)
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._owns_browser = False

    def _status(self, message: str) -> None:
        self._on_status(message)

    def _select_first_selector(self, page: Page, selectors: str) -> str | None:
        """
        Try each comma-separated selector until one matches.
        Returns the selector that matched, or None if none match.
        """
        for selector in (s.strip() for s in selectors.split(",")):
            selector = selector.strip()
            if not selector:
                continue
            try:
                loc = page.locator(selector)
                if loc.count() > 0:
                    return selector
            except Exception:
                continue
        return None

    def start(self) -> None:
        """Start the browser (persistent context or connect to OpenClaw CDP)."""
        self._playwright = sync_playwright().start()

        if OPENCLAW_CDP_URL:
            self._status("Connecting to OpenClaw browser via CDP...")
            self._browser = self._playwright.chromium.connect_over_cdp(OPENCLAW_CDP_URL)
            self._owns_browser = False
            # Use default context and first page, or new page if none
            if self._browser.contexts:
                self._context = self._browser.contexts[0]
                self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
            else:
                self._context = self._browser.new_context()
                self._page = self._context.new_page()
        else:
            self._status("Launching browser with persistent profile...")
            USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
            self._context = self._playwright.chromium.launch_persistent_context(
                str(USER_DATA_DIR),
                headless=self._headless,
                viewport={"width": 1280, "height": 720},
                accept_downloads=False,
            )
            self._browser = None  # persistent context does not expose browser handle the same way
            self._owns_browser = True
            self._page = self._context.pages[0] if self._context.pages else self._context.new_page()

        self._page.set_default_timeout(NAVIGATION_TIMEOUT * 1000)
        self._page.set_default_navigation_timeout(NAVIGATION_TIMEOUT * 1000)

    def stop(self) -> None:
        """Close the browser and cleanup. Safe to call even if start() was not used."""
        try:
            if self._context and self._owns_browser:
                self._context.close()
            elif self._browser and not self._owns_browser:
                self._browser.close()
        except Exception:
            pass
        if self._playwright:
            self._playwright.stop()
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    def run_deep_research(self, prompt: str) -> None:
        """
        Execute the full Deep Research workflow on the current page.

        1. Navigate to Gemini.
        2. Click tool selector and choose Deep Research.
        3. Enter the prompt into the textarea.
        4. Click submit.
        5. If "Start Research" appears, click it.

        Raises:
            BrowserManagerError: If any step fails (selector not found, timeout).
        """
        if not self._page:
            raise BrowserManagerError("Browser not started. Call start() first.")

        page = self._page

        # Step 1: Navigate to Gemini
        self._status("Navigating to Gemini...")
        try:
            page.goto(GEMINI_BASE_URL, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT * 1000)
        except PlaywrightTimeoutError as e:
            raise BrowserManagerError(f"Navigation to {GEMINI_BASE_URL} timed out: {e}") from e
        except Exception as e:
            raise BrowserManagerError(f"Navigation failed: {e}") from e

        # Allow the page to settle (SPA may render tools after load)
        time.sleep(2)

        # Step 2: Open tool selector and switch to Deep Research
        self._status("Switching to Deep Research...")
        tool_selector = self._select_first_selector(page, TOOL_SELECTOR_BUTTON)
        if tool_selector:
            try:
                page.locator(tool_selector).first.click(timeout=ELEMENT_WAIT_TIMEOUT * 1000)
                time.sleep(1)
                # Click the option that contains "Deep Research" text
                deep_opt = page.get_by_text(DEEP_RESEARCH_OPTION_TEXT, exact=False).first
                if deep_opt.count() > 0:
                    deep_opt.click(timeout=ELEMENT_WAIT_TIMEOUT * 1000)
                    time.sleep(1)
                else:
                    self._status("Deep Research option not found by text; continuing with prompt.")
            except PlaywrightTimeoutError:
                self._status("Tool selector or Deep Research option not found; continuing with prompt.")
            except Exception as e:
                self._status(f"Tool selection warning: {e}; continuing with prompt.")
        else:
            self._status("Tool selector not found; continuing with prompt.")

        # Step 3: Focus and fill the prompt textarea
        self._status("Entering prompt...")
        textarea_selector = self._select_first_selector(page, PROMPT_TEXTAREA)
        if not textarea_selector:
            raise BrowserManagerError(
                "Could not find the prompt textarea. The Gemini UI may have changed. "
                "Try setting GEMINIGRIP_PROMPT_SELECTOR in .env."
            )
        try:
            textarea = page.locator(textarea_selector).first
            textarea.click(timeout=ELEMENT_WAIT_TIMEOUT * 1000)
            textarea.fill(prompt, timeout=ELEMENT_WAIT_TIMEOUT * 1000)
        except PlaywrightTimeoutError as e:
            raise BrowserManagerError(f"Prompt textarea not found or not editable: {e}") from e
        except Exception as e:
            raise BrowserManagerError(f"Failed to enter prompt: {e}") from e

        time.sleep(0.5)

        # Step 4: Click submit
        self._status("Submitting...")
        submit_selector = self._select_first_selector(page, SUBMIT_BUTTON)
        if not submit_selector:
            raise BrowserManagerError(
                "Could not find the submit button. Try setting GEMINIGRIP_SUBMIT_SELECTOR in .env."
            )
        try:
            page.locator(submit_selector).first.click(timeout=ELEMENT_WAIT_TIMEOUT * 1000)
        except PlaywrightTimeoutError as e:
            raise BrowserManagerError(f"Submit button not found or not clickable: {e}") from e
        except Exception as e:
            raise BrowserManagerError(f"Failed to click submit: {e}") from e

        # Step 5: Wait for and click "Start Research" if it appears
        self._status("Checking for Start Research button...")
        try:
            start_btn = page.get_by_role("button", name=START_RESEARCH_TEXT)
            start_btn.wait_for(state="visible", timeout=SUBMIT_WAIT_TIMEOUT * 1000)
            start_btn.click(timeout=ELEMENT_WAIT_TIMEOUT * 1000)
            self._status("Start Research clicked.")
        except PlaywrightTimeoutError:
            # Optional step; many flows may not show this button
            self._status("Start Research button did not appear; workflow may still be in progress.")
        except Exception:
            self._status("Start Research button not clicked; continuing.")

        self._status("Deep Research workflow completed. You can monitor progress in the browser.")
