# Gemini Deep Research (OpenClaw CLI)

Automates the Gemini Deep Research flow using the **OpenClaw CLI**: snapshot → parse refs → click/type.

## Requirements

- Python 3.6+
- [OpenClaw](https://github.com/OpenClaw) with browser running and `openclaw` on your PATH

## Usage

```bash
python gemini_deep_research.py "Your research prompt here"
```

The script will:

1. Snapshot → click **Tools**
2. Snapshot → click **Deep Research**
3. Snapshot → type your prompt into **Enter a prompt for Gemini**
4. Snapshot → click **Share & Export**
5. Snapshot → click **Export to Docs**

Refs are read from `SnapShotResult.txt` (created in the current directory). Ensure the OpenClaw browser is on the Gemini page before running.
