#!/usr/bin/env python3
"""
Gemini Deep Research automation using the OpenClaw CLI.

Runs a workflow: snapshot -> find ref by label -> click/type via openclaw browser.
Snapshot output is kept in memory (no file I/O). Refs are in the form [ref=e<number>].
"""

import re
import subprocess
import sys
import time

# Delay in seconds between actions so the browser can update
ACTION_DELAY = 2
# When waiting for Deep Research to finish: snapshot every this many seconds (e.g. 5–10 min total)
WAIT_POLL_INTERVAL = 60
# Stop waiting after this many seconds (0 = no limit)
WAIT_TIMEOUT_SEC = 0

REF_RE = re.compile(r"\[ref=(e\d+)\]")


def run_snapshot() -> str:
    """
    Run openclaw browser snapshot --efficient and return output as a string.
    No file I/O; faster than writing to SnapShotResult.txt.
    """
    result = subprocess.run(
        ["openclaw", "browser", "snapshot", "--efficient"],
        capture_output=True,
        text=True,
        check=True,
    )
    time.sleep(ACTION_DELAY)
    return result.stdout


def find_ref_in_text(snapshot_text: str, label: str) -> str:
    """
    Search snapshot text for a line containing `label` and return its ref code (e.g. 'e37').
    Ref format: [ref=e<number>].
    """
    for line in snapshot_text.splitlines():
        if label in line:
            m = REF_RE.search(line)
            if m:
                return m.group(1)
    raise ValueError(f"Ref not found for label: {label!r}")


def ref_exists_in_text(snapshot_text: str, label: str) -> bool:
    """Return True if a line containing `label` with a ref exists in the snapshot text."""
    try:
        find_ref_in_text(snapshot_text, label)
        return True
    except ValueError:
        return False


def run_click(ref: str) -> None:
    """Execute: openclaw browser click <ref>"""
    subprocess.run(["openclaw", "browser", "click", ref], check=True)
    time.sleep(ACTION_DELAY)


def run_type(ref: str, text: str) -> None:
    """Execute: openclaw browser type <ref> <text>"""
    subprocess.run(["openclaw", "browser", "type", ref, text, "--submit"], check=True)
    time.sleep(ACTION_DELAY)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            'Usage: python gemini_deep_research.py "Your research prompt"',
            file=sys.stderr,
        )
        sys.exit(1)
    prompt = sys.argv[1].strip()
    if not prompt:
        print("Error: PROMPT cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Step 1: Snapshot
    print("Step 1: Snapshot...")
    snap = run_snapshot()

    # Step 2: Find "Tools" -> click
    print("Step 2: Click Tools...")
    ref_tools = find_ref_in_text(snap, "Tools")
    run_click(ref_tools)

    # Step 3: Snapshot -> Find "Deep Research" -> click
    print("Step 3: Snapshot, then click Deep research...")
    snap = run_snapshot()
    ref_deep = find_ref_in_text(snap, "Deep research")
    run_click(ref_deep)
    ref_modPicker = find_ref_in_text(snap, "Open mode picker")
    run_click(ref_modPicker)
    snap = run_snapshot()
    ref_thinking = find_ref_in_text(snap, "Thinking Solves complex problems")
    run_click(ref_thinking)

    # Step 4: Snapshot -> Find textbox "Enter a prompt for Gemini" -> type PROMPT
    print("Step 4: Snapshot, then type prompt into textbox...")
    snap = run_snapshot()
    ref_textbox = find_ref_in_text(snap, "Enter a prompt for Gemini")
    run_type(ref_textbox, prompt)
    start = time.monotonic()
    # wait till "start research" button appears
    while True:
        snap = run_snapshot()
        if ref_exists_in_text(snap, "Start research"):
            ref_startResearch = find_ref_in_text(snap, "Start research")
            run_click(ref_startResearch)
            break
        if WAIT_TIMEOUT_SEC and (time.monotonic() - start) >= WAIT_TIMEOUT_SEC:
            print(
                "Error: Start research did not appear within timeout.", file=sys.stderr
            )
            sys.exit(1)
        time.sleep(5)

    # Wait for Deep Research to finish: loop until snapshot finds "Share & Export"
    print("Waiting for Deep Research to complete (polling for Share & Export)...")
    start = time.monotonic()
    while True:
        snap = run_snapshot()
        if ref_exists_in_text(snap, "Share & Export"):
            break
        if WAIT_TIMEOUT_SEC and (time.monotonic() - start) >= WAIT_TIMEOUT_SEC:
            print(
                "Error: Share & Export did not appear within timeout.", file=sys.stderr
            )
            sys.exit(1)
        time.sleep(WAIT_POLL_INTERVAL)

    # Step 5: Find "Share & Export" -> click (we already have snapshot in snap)
    print("Step 5: Click Share & Export...")
    ref_share = find_ref_in_text(snap, "Share & Export")
    run_click(ref_share)

    # Step 6: Snapshot -> Find "Export to Docs" -> click
    print("Step 6: Snapshot, then click Export to Docs...")
    snap = run_snapshot()
    ref_export = find_ref_in_text(snap, "Export to Docs")
    run_click(ref_export)

    print("Done.")


if __name__ == "__main__":
    main()
