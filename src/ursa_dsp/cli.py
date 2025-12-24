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
    summary_path: Optional[str] = None, defaults: Optional[Dict[str, Any]] = None
) -> ProjectMetadata:
    """Interactively gathers project metadata, using AI-extracted defaults if available."""
    console.rule("[bold blue]Ursa DSP: Interactive Wizard[/]")
    if summary_path:
        console.print(f"Creating DSP based on summary: [cyan]{summary_path}[/]")
    else:
        console.print("Creating a new DSP from scratch.")

    if defaults:
        console.print("[dim]Defaults pre-filled from AI analysis of summary.[/]\n")

    return ProjectMetadata(
        project_name=Prompt.ask(
            "Project Name",
            default=defaults.get("project_name", "My Research Project")
            if defaults
            else "My Research Project",
        ),
        pi_name=Prompt.ask(
            "Principal Investigator (PI)",
            default=defaults.get("pi_name", "Unknown PI") if defaults else "Unknown PI",
        ),
        uisl_name=Prompt.ask(
            "Unit Information Security Lead (UISL)",
            default=defaults.get("uisl_name", "Unknown UISL")
            if defaults
            else "Unknown UISL",
        ),
        department=Prompt.ask(
            "Department/Unit",
            default=defaults.get("department", "Research Computing")
            if defaults
            else "Research Computing",
        ),
        classification=Prompt.ask(
            "Data Classification",
            choices=[e.value for e in DataClassification],
            default=defaults.get("classification", DataClassification.P4.value)
            if defaults
            else DataClassification.P4.value,
        ),
        is_cui=Confirm.ask(
            "Does this project involve CUI?",
            default=defaults.get("is_cui", False) if defaults else False,
        ),
        data_provider=Prompt.ask(
            "Data Provider (e.g., NIH, Army)",
            default=defaults.get("data_provider", "External Agency")
            if defaults
            else "External Agency",
        ),
        infrastructure=Prompt.ask(
            "Infrastructure Type",
            choices=[e.value for e in InfrastructureType],
            default=defaults.get("infrastructure", InfrastructureType.WORKSTATION.value)
            if defaults
            else InfrastructureType.WORKSTATION.value,
        ),
        os_type=Prompt.ask(
            "Operating System",
            default=defaults.get("os_type", "Ubuntu Linux 22.04")
            if defaults
            else "Ubuntu Linux 22.04",
        ),
        transfer_method=Prompt.ask(
            "Transfer Method",
            default=defaults.get("transfer_method", "Encrypted USB / Globus")
            if defaults
            else "Encrypted USB / Globus",
        ),
        retention_date=Prompt.ask(
            "Project End Date (YYYY-MM-DD)",
            default=defaults.get("retention_date", "2030-01-01")
            if defaults
            else "2030-01-01",
        ),
        destruction_method=Prompt.ask(
            "Destruction Method",
            default=defaults.get("destruction_method", "DoD 5220.22-M 3-pass wipe")
            if defaults
            else "DoD 5220.22-M 3-pass wipe",
        ),
    )


@app.command()
def generate(
    summary: Optional[str] = typer.Option(
        None,
        "--summary",
        "-s",
        help="Path to Summary.md (Optional if using --interactive)",
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output", "-o", help="Directory to save the results"
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Run interactive wizard (with AI pre-fill if --summary is provided)",
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
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose debug logging"
    ),
) -> None:
    """
    Generate a Data Security Plan (DSP).
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    processor = DSPProcessor()
    metadata = None

    if interactive:
        defaults = None
        if summary:
            console.print("[cyan]Reading summary for AI pre-fill...[/]")
            try:
                summary_text = processor.get_project_summary(project_identifier=summary)
                console.print("[cyan]Analyzing project with Gemini 3 Pro...[/]")
                defaults = processor.generator.extract_metadata(
                    summary_text=summary_text
                )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: AI analysis failed ({e}). Continuing with manual wizard.[/]"
                )

        metadata = run_wizard(summary_path=summary, defaults=defaults)

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
            os_type="Linux",
            transfer_method="Secure Transfer",
            retention_date="2030-01-01",
            destruction_method="DoD Wipe",
        )

    try:
        # If summary is None, we pass None and the processor handles it (using metadata only)
        display_name = summary if summary else metadata.project_name
        console.rule(f"[bold blue]Processing: {display_name}[/]")

        pdf_path = processor.process_project(
            project_identifier=summary if summary else metadata.project_name,
            metadata=metadata,
            output_dir=output_dir,
        )
        console.print(
            f"\n[bold green]Success![/] DSP generated at: [underline]{pdf_path}[/]"
        )
    except Exception as e:
        console.print(f"\n[bold red]Error:[/] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version info."""
    print("Ursa DSP v0.2.8")


if __name__ == "__main__":
    app()
