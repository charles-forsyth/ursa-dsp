import typer
from typing import Optional, Dict, Any
import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt, Confirm
from ursa_dsp.core.processor import DSPProcessor
from ursa_dsp.core.schema import ProjectMetadata, DataClassification, InfrastructureType

# Configure Rich Logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

app = typer.Typer(help="Ursa DSP Generator - Automated Data Security Plans")
console = Console()


def run_wizard(
    summary_path: str, defaults: Optional[Dict[str, Any]] = None
) -> ProjectMetadata:
    """Interactively gathers project metadata, using AI-extracted defaults."""
    console.rule("[bold blue]Ursa DSP: Interactive Wizard[/]")
    console.print(f"Creating DSP for summary: [cyan]{summary_path}[/]")

    if defaults is None:
        defaults = {}
    else:
        console.print("[dim]Defaults pre-filled from AI analysis of summary.[/]\n")

    return ProjectMetadata(
        project_name=Prompt.ask(
            "Project Name", default=defaults.get("project_name", "My Research Project")
        ),
        pi_name=Prompt.ask(
            "Principal Investigator (PI)", default=defaults.get("pi_name", "Unknown PI")
        ),
        uisl_name=Prompt.ask(
            "Unit Information Security Lead (UISL)",
            default=defaults.get("uisl_name", "Unknown UISL"),
        ),
        department=Prompt.ask(
            "Department/Unit", default=defaults.get("department", "Research Computing")
        ),
        classification=Prompt.ask(
            "Data Classification",
            choices=[e.value for e in DataClassification],
            default=defaults.get("classification", DataClassification.P4.value),
        ),
        is_cui=Confirm.ask(
            "Does this project involve CUI?", default=defaults.get("is_cui", False)
        ),
        data_provider=Prompt.ask(
            "Data Provider (e.g., NIH, Army)",
            default=defaults.get("data_provider", "External Agency"),
        ),
        infrastructure=Prompt.ask(
            "Infrastructure Type",
            choices=[e.value for e in InfrastructureType],
            default=defaults.get(
                "infrastructure", InfrastructureType.WORKSTATION.value
            ),
        ),
        os_type=Prompt.ask(
            "Operating System", default=defaults.get("os_type", "Ubuntu Linux 22.04")
        ),
        transfer_method=Prompt.ask(
            "Transfer Method",
            default=defaults.get("transfer_method", "Encrypted USB / Globus"),
        ),
        retention_date=Prompt.ask(
            "Project End Date (YYYY-MM-DD)",
            default=defaults.get("retention_date", "2030-01-01"),
        ),
        destruction_method=Prompt.ask(
            "Destruction Method",
            default=defaults.get("destruction_method", "DoD 5220.22-M 3-pass wipe"),
        ),
    )


@app.command()
def generate(
    summary: str = typer.Option(..., "--summary", "-s", help="Path to Summary.md"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Run interactive wizard with AI pre-fill"
    ),
    # CLI Flags for Power Users
    project_name: str = typer.Option("My Research Project", help="Project Name"),
    pi: str = typer.Option("Unknown PI", help="Principal Investigator Name"),
    uisl: str = typer.Option("Unknown UISL", help="UISL Name"),
    department: str = typer.Option("Research Computing", help="Department"),
    classification: DataClassification = typer.Option(
        DataClassification.P4, help="Data Classification"
    ),
    cui: bool = typer.Option(False, help="Is CUI?"),
    provider: str = typer.Option("External Agency", help="Data Provider"),
    infrastructure: InfrastructureType = typer.Option(
        InfrastructureType.WORKSTATION, help="Infrastructure Type"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """
    Generate a Data Security Plan (DSP).
    Use --interactive for a guided experience (with AI pre-fill), or provide flags for automation.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    processor = DSPProcessor()
    metadata = None

    if interactive:
        # Step 1: Read Summary
        console.print("[cyan]Reading summary...[/]")
        try:
            summary_text = processor.get_project_summary(summary)

            # Step 2: Extract Metadata via AI
            console.print("[cyan]Analyzing project with Gemini 3 Pro...[/]")
            defaults = processor.generator.extract_metadata(summary_text)

            # Step 3: Run Wizard with Defaults
            metadata = run_wizard(summary, defaults)

        except Exception:
            console.print("[bold red]Error during extraction:[/]")
            raise typer.Exit(code=1)

    else:
        # Construct from flags
        metadata = ProjectMetadata(
            project_name=project_name,
            pi_name=pi,
            uisl_name=uisl,
            department=department,
            classification=classification,
            is_cui=cui,
            data_provider=provider,
            infrastructure=infrastructure,
            # Defaults for fields not yet exposed as flags
            os_type="Linux",
            transfer_method="Secure Transfer",
            retention_date="2030-01-01",
            destruction_method="DoD Wipe",
        )

    try:
        console.rule(f"[bold blue]Processing: {summary}[/]")
        pdf_path = processor.process_project(summary, metadata, output_dir)
        console.print(
            f"\n[bold green]Success![/] DSP generated at: [underline]{pdf_path}[/]"
        )
    except Exception:
        console.print("\n[bold red]Error:[/]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version info."""
    print("Ursa DSP v0.2.7")


if __name__ == "__main__":
    app()
