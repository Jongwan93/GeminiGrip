"""
Configuration management for GeminiGrip.

Loads environment variables and defines constants such as URLs and CSS selectors
for the Gemini Deep Research automation workflow. Selectors may need to be
updated if Google changes the Gemini UI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of scripts/) if present
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

# -----------------------------------------------------------------------------
# Environment variables
# -----------------------------------------------------------------------------

# Optional: CDP URL for connecting to an existing OpenClaw-managed browser.
# If set, GeminiGrip will connect to this browser instead of launching its own.
# Example: http://127.0.0.1:18800 (OpenClaw default profile port)
OPENCLAW_CDP_URL: str | None = os.getenv("OPENCLAW_CDP_URL") or None

# Persistent user data directory for the browser (cookies, login state).
# Used only when not connecting to OpenClaw. Default: .gemini_grip_profile in project root.
_USER_DATA_DIR = os.getenv("GEMINIGRIP_USER_DATA_DIR")
if _USER_DATA_DIR:
    USER_DATA_DIR = Path(_USER_DATA_DIR).resolve()
else:
    USER_DATA_DIR = _project_root / ".gemini_grip_profile"

# Timeouts (seconds)
NAVIGATION_TIMEOUT = int(os.getenv("GEMINIGRIP_NAVIGATION_TIMEOUT", "30"))
ELEMENT_WAIT_TIMEOUT = int(os.getenv("GEMINIGRIP_ELEMENT_WAIT_TIMEOUT", "15"))
SUBMIT_WAIT_TIMEOUT = int(os.getenv("GEMINIGRIP_SUBMIT_WAIT_TIMEOUT", "10"))

# -----------------------------------------------------------------------------
# URLs
# -----------------------------------------------------------------------------

GEMINI_BASE_URL = "https://gemini.google.com"

# -----------------------------------------------------------------------------
# Selectors (Gemini Deep Research UI)
# -----------------------------------------------------------------------------
# These selectors target the Gemini web UI. Google may change the DOM;
# update these or override via env if automation fails.

# Tool/mode selector (e.g. "Deep Research" option in the UI)
TOOL_SELECTOR_BUTTON = os.getenv(
    "GEMINIGRIP_TOOL_SELECTOR",
    "button[aria-label*='Tools'], [data-tool-selector], [aria-haspopup='true']",
)
# Option text to click for Deep Research
DEEP_RESEARCH_OPTION_TEXT = os.getenv("GEMINIGRIP_DEEP_RESEARCH_LABEL", "Deep Research")

# Main input textarea for the prompt
PROMPT_TEXTAREA = os.getenv(
    "GEMINIGRIP_PROMPT_SELECTOR",
    "textarea[placeholder*='Message'], textarea[aria-label*='message'], textarea[data-placeholder]",
)

# Submit / send button
SUBMIT_BUTTON = os.getenv(
    "GEMINIGRIP_SUBMIT_SELECTOR",
    "button[aria-label*='Send'], button[type='submit'], button[data-submit]",
)

# "Start Research" button that may appear after entering the prompt
START_RESEARCH_BUTTON = os.getenv(
    "GEMINIGRIP_START_RESEARCH_SELECTOR",
    "button:has-text('Start Research'), [aria-label*='Start Research'], button:has-text('Start research')",
)

# Fallback: try by visible text for buttons (Playwright supports :has-text())
START_RESEARCH_TEXT = "Start Research"
