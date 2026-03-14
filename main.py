"""
GeminiGrip — CLI entry point.

Automates Google Gemini's Deep Research feature via the OpenClaw-compatible
browser flow: persistent profile or connect to OpenClaw CDP, then navigate,
select Deep Research, enter prompt, and submit.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.text import Text
from rich.theme import Theme

from scripts.browser_manager import BrowserManager, BrowserManagerError

# Rich theme for consistent styling
APP_THEME = Theme(
    {
        "app.name": "bold cyan",
        "app.success": "bold green",
        "app.error": "bold red",
        "app.warning": "bold yellow",
        "app.info": "dim",
    }
)

console = Console(theme=APP_THEME)
app = typer.Typer(
    name="geminigrip",
    help="Automate Google Gemini Deep Research from the CLI using a persistent browser profile or OpenClaw.",
    add_completion=False,
)


def _status_callback(message: str) -> None:
    """Forward status messages to Rich console."""
    console.print(Text(message, style="app.info"))


@app.command()
def research(
    prompt: str = typer.Argument(..., help="The research prompt to send to Gemini Deep Research."),
    headless: bool = typer.Option(False, "--headless", "-H", help="Run the browser in headless mode."),
) -> None:
    """
    Run a Deep Research task on Gemini.

    Launches (or connects to) a browser, opens Gemini, switches to Deep Research,
    enters your prompt, and submits. Use a persistent profile so you stay logged
    into Google.
    """
    console.print(Text("GeminiGrip", style="app.name"), " — Deep Research")
    console.print()
    if not prompt.strip():
        console.print(Text("Error: Prompt cannot be empty.", style="app.error"))
        raise typer.Exit(1)

    manager = BrowserManager(headless=headless, on_status=_status_callback)

    try:
        with console.status(
            "[bold cyan]Starting browser...",
            spinner="dots",
            spinner_style="cyan",
        ):
            manager.start()

        console.print(Text("Browser ready.", style="app.success"))
        console.print()

        with console.status(
            "[bold cyan]Running Deep Research workflow...",
            spinner="dots",
            spinner_style="cyan",
        ):
            manager.run_deep_research(prompt.strip())

        console.print()
        console.print(Text("Done. Check the browser window for research progress.", style="app.success"))
    except BrowserManagerError as e:
        console.print()
        console.print(Text("Error: ", style="app.error") + Text(str(e)))
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print(Text("\nInterrupted.", style="app.warning"))
        raise typer.Exit(130)
    except Exception as e:
        console.print(Text(f"Unexpected error: {e}", style="app.error"))
        raise typer.Exit(1)
    finally:
        console.print(Text("Closing browser...", style="app.info"))
        manager.stop()
        console.print(Text("Goodbye.", style="app.info"))


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
) -> None:
    """GeminiGrip — automate Gemini Deep Research from the CLI."""
    if ctx.invoked_subcommand is None:
        console.print(Text("GeminiGrip", style="app.name"))
        console.print("Use [bold cyan]geminigrip research \"Your prompt\"[/] to run Deep Research.")
        console.print("Use [bold cyan]geminigrip --help[/] for more options.")
        return


if __name__ == "__main__":
    app()
