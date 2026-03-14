# GeminiGrip
<<<<<<< HEAD

A Python CLI that automates **Google Gemini’s Deep Research** flow: it opens Gemini in a browser (with a persistent profile so you stay logged in), switches to Deep Research, enters your prompt, and submits. It works with a local Playwright browser or by connecting to an **OpenClaw**-managed browser.

## Requirements

- Python 3.11+
- Chromium (installed via Playwright; see setup below)

## Setup

### 1. Virtual environment

```bash
cd GeminiGrip
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (cmd):**

```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

To get the `geminigrip` command on your PATH (optional):

```bash
pip install -e .
```

### 3. Install Playwright browsers

```bash
playwright install chromium
```

### 4. Optional: environment and OpenClaw

- Copy `.env.example` to `.env` and edit if you need custom profile path, timeouts, or selectors.
- To use an **OpenClaw**-managed browser: start OpenClaw and its browser (e.g. `openclaw browser --browser-profile openclaw start`), then set `OPENCLAW_CDP_URL` in `.env` (e.g. `http://127.0.0.1:18800`). GeminiGrip will connect to that browser instead of launching its own.

## Usage

Run a Deep Research task:

```bash
geminigrip research "Your research question or topic here"
```

Or run the script directly (from the project root):

```bash
python main.py research "Your research question or topic here"
```

**Options:**

- `--headless` / `-H`: Run the browser in headless mode (no visible window).

**First run:** The first time you run without OpenClaw, a Chromium window will open. Log in to your Google account on [gemini.google.com](https://gemini.google.com) if needed. The profile is stored in `.gemini_grip_profile` (or the path in `GEMINIGRIP_USER_DATA_DIR`), so later runs stay logged in.

## Project layout

| File / folder              | Purpose |
|----------------------------|--------|
| `main.py`                  | CLI entry point (Typer); `geminigrip research "PROMPT"` |
| `scripts/browser_manager.py` | Browser launch (Playwright persistent context or OpenClaw CDP) and Deep Research steps |
| `scripts/config.py`        | Env vars, URLs, timeouts, and selectors |
| `.env`                     | Local overrides at project root (optional; copy from `.env.example`) |
| `requirements.txt`         | Python dependencies |

## Configuration

See `.env.example` and `scripts/config.py`. You can override:

- **OPENCLAW_CDP_URL** – Use an existing OpenClaw browser instead of launching one.
- **GEMINIGRIP_USER_DATA_DIR** – Custom browser profile directory.
- **GEMINIGRIP_NAVIGATION_TIMEOUT**, **GEMINIGRIP_ELEMENT_WAIT_TIMEOUT**, **GEMINIGRIP_SUBMIT_WAIT_TIMEOUT** – Timeouts in seconds.
- **GEMINIGRIP_***_SELECTOR** – CSS selectors if the Gemini UI changes.

## Notes

- **Selectors:** Google can change the Gemini UI. If automation fails (e.g. “Could not find the prompt textarea”), update the selectors in `.env` or `scripts/config.py`.
- **OpenClaw:** For the “OpenClaw framework” workflow, run the OpenClaw gateway and browser, set `OPENCLAW_CDP_URL`, and run `geminigrip research "PROMPT"`. The tool will attach to that browser and run the same Deep Research steps.

## License

MIT.
=======
Tool for Openclaw to automate Gemini deep research feature.
>>>>>>> 15be0f51e30c62de8e94dca6386fb394ba8c81b8
