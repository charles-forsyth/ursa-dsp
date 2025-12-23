import typer
from typing import Optional
import logging
from rich.console import Console
from rich.logging import RichHandler
from ursa_dsp.core.processor import DSPProcessor

# Configure Rich Logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

app = typer.Typer(help="Ursa DSP Generator - Automated Data Security Plans")
console = Console()


@app.command()
def generate(
    project_identifier: str = typer.Argument(
        ..., help="Project name (folder in projects/) or path to Summary.md"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output", "-o", help="Custom output directory"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose debug logging"
    ),
) -> None:
    """
    Generate a Data Security Plan (DSP) for a given project.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    processor = DSPProcessor()

    try:
        console.rule(f"[bold blue]Processing: {project_identifier}[/]")
        pdf_path = processor.process_project(project_identifier, output_dir)
        console.print(
            f"\n[bold green]Success![/] DSP generated at: [underline]{pdf_path}[/]"
        )
    except Exception as e:
        console.print(f"\n[bold red]Error:[/]; {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version info."""
    print("Ursa DSP v0.2.3")


if __name__ == "__main__":
    app()
