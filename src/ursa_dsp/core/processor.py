import os
import json
import logging
import concurrent.futures
from typing import List, Dict, Any, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID

from ursa_dsp.core.rag import KnowledgeBase
from ursa_dsp.core.generator import DSPGenerator
from ursa_dsp.output.renderer import ReportRenderer
from ursa_dsp.utils.io import read_file_content

logger = logging.getLogger(__name__)


class DSPProcessor:
    def __init__(self) -> None:
        self.rag = KnowledgeBase()
        self.generator = DSPGenerator()
        self.renderer = ReportRenderer()

    def get_project_summary(self, project_identifier: str) -> str:
        """Resolves project summary."""
        if os.path.exists(project_identifier) and os.path.isfile(project_identifier):
            return read_file_content(project_identifier)

        summary_path = os.path.join("projects", project_identifier, "Summary.md")
        if os.path.exists(summary_path):
            return read_file_content(summary_path)

        raise FileNotFoundError(f"Could not find summary for '{project_identifier}'")

    def load_template_structure(self) -> List[Dict[str, Any]]:
        template_path = os.path.join("templates", "dsp_template_structure.json")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template structure not found at {template_path}")

        with open(template_path, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            raise ValueError("Template structure must be a list of sections.")

    def process_section(
        self,
        section: Dict[str, Any],
        summary: str,
        full_context: str,
        progress: Progress,
        task_id: TaskID,
    ) -> Dict[str, Any]:
        """Worker function for parallel processing."""
        title = section["title"]
        body = section["body"]

        # Determine the order index from the section if available, otherwise 0 (handled later)
        # Actually, we will just return the result and sort by original index later.

        _, content = self.generator.generate_section(title, body, summary, full_context)

        progress.advance(task_id)
        return {"title": title, "content": content}

    def process_project(
        self, project_identifier: str, output_dir: Optional[str] = None
    ) -> str:
        """Main execution flow with parallel generation."""

        # 1. Gather Info
        summary = self.get_project_summary(project_identifier)
        template = self.load_template_structure()
        full_context = self.rag.get_full_context()

        project_name = (
            os.path.basename(project_identifier).replace(".md", "")
            if os.path.isfile(project_identifier)
            else project_identifier
        )

        if not output_dir:
            output_dir = os.path.join("projects", project_name)

        os.makedirs(output_dir, exist_ok=True)

        generated_sections: List[Dict[str, Any]] = [
            {} for _ in template
        ]  # Pre-allocate to maintain order?
        # Better strategy: Generate (index, result) tuples and sort.

        # 2. Parallel Generation
        logger.info(f"Starting parallel generation for {len(template)} sections...")

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            main_task = progress.add_task(
                f"[cyan]Generating {len(template)} sections...", total=len(template)
            )

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Map futures to their index to preserve order
                future_to_index = {
                    executor.submit(
                        self.process_section,
                        section,
                        summary,
                        full_context,
                        progress,
                        main_task,
                    ): i
                    for i, section in enumerate(template)
                }

                results = []
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        data = future.result()
                        results.append((index, data))
                    except Exception as exc:
                        logger.error(
                            f"Section generation generated an exception: {exc}"
                        )
                        results.append(
                            (
                                index,
                                {
                                    "title": template[index]["title"],
                                    "content": "[[GENERATION ERROR]]",
                                },
                            )
                        )

        # Sort results by original index to ensure document flow matches template
        results.sort(key=lambda x: x[0])
        generated_sections = [data for _, data in results]

        # 3. Save Output
        log_path = os.path.join(output_dir, f"{project_name}_dsp_log.json")
        with open(log_path, "w") as f:
            json.dump(generated_sections, f, indent=2)

        html_content = self.renderer.render_html(project_name, generated_sections)
        html_path = os.path.join(output_dir, f"{project_name}_dsp.html")
        with open(html_path, "w") as f:
            f.write(html_content)

        pdf_path = os.path.join(output_dir, f"{project_name}_dsp.pdf")
        self.renderer.generate_pdf(html_content, pdf_path)

        return pdf_path
