import typer
from typing import Optional
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


def run_wizard(summary_path: str) -> ProjectMetadata:
    """Interactively gathers project metadata."""
    console.rule("[bold blue]Ursa DSP: Interactive Wizard[/]")
    console.print(f"Creating DSP for summary: [cyan]{summary_path}[/]\n")

    return ProjectMetadata(
        project_name=Prompt.ask("Project Name"),
        pi_name=Prompt.ask("Principal Investigator (PI)"),
        uisl_name=Prompt.ask("Unit Information Security Lead (UISL)"),
        department=Prompt.ask("Department/Unit"),
        classification=Prompt.ask(
            "Data Classification",
            choices=[e.value for e in DataClassification],
            default=DataClassification.P4.value,
        ),
        is_cui=Confirm.ask("Does this project involve CUI?"),
        data_provider=Prompt.ask("Data Provider (e.g., NIH, Army)"),
        infrastructure=Prompt.ask(
            "Infrastructure Type",
            choices=[e.value for e in InfrastructureType],
            default=InfrastructureType.WORKSTATION.value,
        ),
        os_type=Prompt.ask("Operating System", default="Ubuntu Linux 22.04"),
        transfer_method=Prompt.ask("Transfer Method", default="Encrypted USB / Globus"),
        retention_date=Prompt.ask("Project End Date (YYYY-MM-DD)"),
        destruction_method=Prompt.ask(
            "Destruction Method", default="DoD 5220.22-M 3-pass wipe"
        ),
    )


@app.command()
def generate(
    summary: str = typer.Option(..., "--summary", "-s", help="Path to Summary.md"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Run interactive wizard"
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
    Use --interactive for a guided experience, or provide flags for automation.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    metadata = None

    if interactive:
        metadata = run_wizard(summary)
    else:
        # Construct from flags (using defaults if not provided)
        # Note: In a real automated scenario, user should provide these flags.
        # We rely on defaults to keep it runnable without a 20-arg command for quick tests.
        metadata = ProjectMetadata(
            project_name=project_name,
            pi_name=pi,
            uisl_name=uisl,
            department=department,
            classification=classification,
            is_cui=cui,
            data_provider=provider,
            infrastructure=infrastructure,
            # Defaults for fields not yet exposed as flags (to keep CLI clean for now)
            os_type="Linux",
            transfer_method="Secure Transfer",
            retention_date="2030-01-01",
            destruction_method="DoD Wipe",
        )

    processor = DSPProcessor()

    try:
        console.rule(f"[bold blue]Processing: {summary}[/]")
        pdf_path = processor.process_project(summary, metadata, output_dir)
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
    print("Ursa DSP v0.2.6")


if __name__ == "__main__":
    app()
