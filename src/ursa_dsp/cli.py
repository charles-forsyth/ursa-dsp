import argparse
import sys
import logging
from typing import Optional, Dict, Any
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

console = Console()


class CustomFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom formatter to show detailed examples."""

    pass


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

    # Helper for defaults
    def get_def(key: str, fallback: Any) -> Any:
        return defaults.get(key, fallback) if defaults else fallback

    return ProjectMetadata(
        project_name=Prompt.ask(
            "Project Name", default=get_def("project_name", "My Research Project")
        ),
        pi_name=Prompt.ask(
            "Principal Investigator (PI)", default=get_def("pi_name", "Unknown PI")
        ),
        uisl_name=Prompt.ask(
            "Unit Information Security Lead (UISL)",
            default=get_def("uisl_name", "Unknown UISL"),
        ),
        department=Prompt.ask(
            "Department/Unit", default=get_def("department", "Research Computing")
        ),
        classification=Prompt.ask(
            "Data Classification",
            choices=[e.value for e in DataClassification],
            default=get_def("classification", DataClassification.P4.value),
        ),
        is_cui=Confirm.ask(
            "Does this project involve CUI?", default=get_def("is_cui", False)
        ),
        data_provider=Prompt.ask(
            "Data Provider (e.g., NIH, Army)",
            default=get_def("data_provider", "External Agency"),
        ),
        infrastructure=Prompt.ask(
            "Infrastructure Type",
            choices=[e.value for e in InfrastructureType],
            default=get_def("infrastructure", InfrastructureType.WORKSTATION.value),
        ),
        os_type=Prompt.ask(
            "Operating System", default=get_def("os_type", "Ubuntu Linux 22.04")
        ),
        transfer_method=Prompt.ask(
            "Transfer Method",
            default=get_def("transfer_method", "Encrypted USB / Globus"),
        ),
        retention_date=Prompt.ask(
            "Project End Date (YYYY-MM-DD)",
            default=get_def("retention_date", "2030-01-01"),
        ),
        destruction_method=Prompt.ask(
            "Destruction Method",
            default=get_def("destruction_method", "DoD 5220.22-M 3-pass wipe"),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="""
🐻 Ursa DSP Generator (v0.2.11)
==============================
An AI-powered agent for creating high-assurance Data Security Plans (DSP).

Examples:
  1. Generate from a summary file (AI Auto-Extraction):
     $ ursa-dsp --summary ./projects/Nebula/Summary.md

  2. Interactive Wizard (Guided):
     $ ursa-dsp --interactive

  3. Hybrid (AI Extraction + Manual Verification):
     $ ursa-dsp --summary ./Summary.md --interactive

  5. Piped Input (Unix Philosophy):
     $ echo "We are analyzing CUI data..." | ursa-dsp --summary - --interactive

  6. Raw String Summary:
     $ ursa-dsp --summary "This project analyzes sensitive genomic data." --interactive
""",
        formatter_class=CustomFormatter,
    )

    # Core Arguments
    core_group = parser.add_argument_group("Core Options")
    core_group.add_argument(
        "-s", "--summary", help="Path to file, raw text string, or '-' for stdin."
    )
    core_group.add_argument(
        "-o", "--output", help="Directory to save the generated artifacts."
    )
    core_group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Launch the interactive wizard (uses AI defaults if summary provided).",
    )
    core_group.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose debug logging."
    )
    core_group.add_argument(
        "--version", action="store_true", help="Show version info and exit."
    )

    # Metadata Overrides
    meta_group = parser.add_argument_group("Metadata Overrides (for automation)")
    meta_group.add_argument(
        "--project-name", default="My Research Project", help="Official project title"
    )
    meta_group.add_argument(
        "--pi", default="Unknown PI", help="Principal Investigator Name"
    )
    meta_group.add_argument(
        "--uisl", default="Unknown UISL", help="Unit Information Security Lead"
    )
    meta_group.add_argument(
        "--department", default="Research Computing", help="Research Unit/Dept"
    )
    meta_group.add_argument(
        "--classification",
        type=DataClassification,
        choices=list(DataClassification),
        default=DataClassification.P4,
        help="Data Sensitivity Level",
    )
    meta_group.add_argument(
        "--cui", action="store_true", help="Flag if project involves CUI"
    )
    meta_group.add_argument(
        "--provider", default="External Agency", help="Data Provider Name"
    )
    meta_group.add_argument(
        "--infrastructure",
        type=InfrastructureType,
        choices=list(InfrastructureType),
        default=InfrastructureType.WORKSTATION,
        help="Primary Storage Infrastructure",
    )

    args = parser.parse_args()

    if args.version:
        print("Ursa DSP v0.2.12")
        sys.exit(0)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validation: Must have either summary or interactive
    if not args.summary and not args.interactive:
        parser.error("You must provide --summary OR use --interactive mode.")

    processor = DSPProcessor()
    metadata = None

    if args.interactive:
        defaults = None
        if args.summary:
            console.print("[cyan]Reading summary for AI pre-fill...[/]")
            try:
                summary_text = processor.get_project_summary(
                    project_identifier=args.summary
                )
                console.print("[cyan]Analyzing project with Gemini 3 Pro...[/]")
                defaults = processor.generator.extract_metadata(
                    summary_text=summary_text
                )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: AI analysis failed ({e}). Continuing with manual wizard.[/]"
                )

        metadata = run_wizard(summary_path=args.summary, defaults=defaults)

    else:
        # Construct from flags
        metadata = ProjectMetadata(
            project_name=args.project_name,
            pi_name=args.pi,
            uisl_name=args.uisl,
            department=args.department,
            classification=args.classification,
            is_cui=args.cui,
            data_provider=args.provider,
            infrastructure=args.infrastructure,
            # Defaults for fields not yet exposed as flags
            os_type="Linux",
            transfer_method="Secure Transfer",
            retention_date="2030-01-01",
            destruction_method="DoD Wipe",
        )

    try:
        # If summary is missing, use metadata project name as identifier
        identifier = args.summary if args.summary else metadata.project_name
        console.rule(f"[bold blue]Processing: {identifier}[/]")

        pdf_path = processor.process_project(
            project_identifier=identifier, metadata=metadata, output_dir=args.output
        )
        console.print(
            f"\n[bold green]Success![/] DSP generated at: [underline]{pdf_path}[/]"
        )
    except Exception as e:
        console.print(f"\n[bold red]Error:[/] {e}")
        if args.verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
