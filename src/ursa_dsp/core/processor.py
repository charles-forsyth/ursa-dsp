import os
import json
import logging
from typing import List, Dict, Any
from rich.progress import Progress, SpinnerColumn, TextColumn

from ursa_dsp.core.rag import KnowledgeBase
from ursa_dsp.core.generator import DSPGenerator
from ursa_dsp.output.renderer import ReportRenderer
from ursa_dsp.utils.io import read_file_content

logger = logging.getLogger(__name__)


class DSPProcessor:
    def __init__(self):
        self.rag = KnowledgeBase()
        self.generator = DSPGenerator()
        self.renderer = ReportRenderer()

    def get_project_summary(self, project_identifier: str) -> str:
        """
        Resolves project summary.
        Accepts either a project name (looking in projects/NAME/Summary.md)
        or a direct path to a file.
        """
        # Check if it's a direct file path
        if os.path.exists(project_identifier) and os.path.isfile(project_identifier):
            return read_file_content(project_identifier)

        # Check standard convention
        summary_path = os.path.join("projects", project_identifier, "Summary.md")
        if os.path.exists(summary_path):
            return read_file_content(summary_path)

        raise FileNotFoundError(f"Could not find summary for '{project_identifier}'")

    def load_template_structure(self) -> List[Dict[str, Any]]:
        template_path = os.path.join("templates", "dsp_template_structure.json")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template structure not found at {template_path}")

        with open(template_path, "r") as f:
            return json.load(f)

    def process_project(self, project_identifier: str, output_dir: str = None):
        """Main execution flow."""

        # 1. Gather Info
        summary = self.get_project_summary(project_identifier)
        template = self.load_template_structure()

        project_name = (
            os.path.basename(project_identifier).replace(".md", "")
            if os.path.isfile(project_identifier)
            else project_identifier
        )

        if not output_dir:
            output_dir = os.path.join("projects", project_name)

        os.makedirs(output_dir, exist_ok=True)

        generated_sections = []

        # 2. Generate Content
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                description="Generating DSP...", total=len(template)
            )

            for section in template:
                title = section["title"]
                body = section["body"]

                progress.update(task, description=f"Generating: {title}")

                # RAG: Get examples
                examples = self.rag.get_relevant_examples(title)

                # AI: Generate
                _, content = self.generator.generate_section(
                    title, body, summary, examples
                )

                generated_sections.append({"title": title, "content": content})

                progress.advance(task)

        # 3. Save Output
        # Save JSON Log
        log_path = os.path.join(output_dir, f"{project_name}_dsp_log.json")
        with open(log_path, "w") as f:
            json.dump(generated_sections, f, indent=2)

        # Render HTML
        html_content = self.renderer.render_html(project_name, generated_sections)
        html_path = os.path.join(output_dir, f"{project_name}_dsp.html")
        with open(html_path, "w") as f:
            f.write(html_content)

        # Generate PDF
        pdf_path = os.path.join(output_dir, f"{project_name}_dsp.pdf")
        self.renderer.generate_pdf(html_content, pdf_path)

        return pdf_path
