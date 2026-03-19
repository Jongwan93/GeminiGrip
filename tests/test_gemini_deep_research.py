import sys

import gemini_deep_research as g


def test_find_ref_in_text_extracts_ref():
    snapshot = "Intro\nTools button [ref=e37]\nFooter"
    assert g.find_ref_in_text(snapshot, "Tools") == "e37"


def test_find_ref_in_text_raises_when_label_missing():
    snapshot = "No matching lines here"
    try:
        g.find_ref_in_text(snapshot, "Tools")
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError when label is missing"


def test_ref_exists_in_text_true_false():
    snapshot = "Tools [ref=e1]\nOther [ref=e2]"
    assert g.ref_exists_in_text(snapshot, "Tools") is True
    assert g.ref_exists_in_text(snapshot, "Missing label") is False


def test_run_click_invokes_openclaw_correctly(monkeypatch):
    calls = []

    def fake_run(args, check):
        calls.append((args, check))

    monkeypatch.setattr(g.subprocess, "run", fake_run)
    monkeypatch.setattr(g.time, "sleep", lambda _s: None)

    g.run_click("e12")

    assert calls == [(["openclaw", "browser", "click", "e12"], True)]


def test_run_type_invokes_openclaw_correctly(monkeypatch):
    calls = []

    def fake_run(args, check):
        calls.append((args, check))

    monkeypatch.setattr(g.subprocess, "run", fake_run)
    monkeypatch.setattr(g.time, "sleep", lambda _s: None)

    g.run_type("e2", "hello")

    assert calls == [(["openclaw", "browser", "type", "e2", "hello", "--submit"], True)]


def test_main_happy_path_sequence(monkeypatch, capsys):
    # Arrange: mock snapshots so loops terminate immediately/soon.
    snapshots = iter(
        [
            "Tools [ref=e1]",
            "Deep research [ref=e2]\nOpen mode picker [ref=e3]",
            "Thinking Solves complex problems [ref=e4]",
            "Enter a prompt for Gemini [ref=e5]",
            "No start yet",
            "Start research [ref=e6]",
            "Working...",
            "Share & Export [ref=e7]",
            "Export to Docs [ref=e8]",
        ]
    )

    monkeypatch.setattr(g, "run_snapshot", lambda: next(snapshots))

    calls = []

    def fake_run_click(ref):
        calls.append(("click", ref))

    def fake_run_type(ref, text):
        calls.append(("type", ref, text))

    monkeypatch.setattr(g, "run_click", fake_run_click)
    monkeypatch.setattr(g, "run_type", fake_run_type)
    monkeypatch.setattr(g.time, "sleep", lambda _s: None)

    monkeypatch.setattr(sys, "argv", ["gemini_deep_research.py", "my prompt"])

    # Act
    g.main()

    # Assert
    assert calls == [
        ("click", "e1"),
        ("click", "e2"),
        ("click", "e3"),
        ("click", "e4"),
        ("type", "e5", "my prompt"),
        ("click", "e6"),
        ("click", "e7"),
        ("click", "e8"),
    ]

    # Ensure the command printed something (sanity check that flow ran).
    out = capsys.readouterr().out
    assert "Done." in out


def test_main_rejects_empty_prompt(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["gemini_deep_research.py", "   "])
    try:
        g.main()
    except SystemExit as exc:
        assert exc.code == 1
    else:
        assert False, "Expected SystemExit(1) for empty prompt"

