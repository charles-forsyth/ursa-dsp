import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML  # type: ignore
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportRenderer:
    def __init__(self, templates_dir: str = "templates"):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )
        # Register markdown filter
        self.env.filters["markdown"] = lambda text: markdown.markdown(
            text, extensions=["extra"]
        )

    def render_html(self, project_name: str, sections: list[dict]) -> str:
        """Renders the report to an HTML string."""
        template = self.env.get_template("report.html")
        return template.render(
            project_name=project_name,
            sections=sections,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

    def generate_pdf(self, html_content: str, output_path: str):
        """Converts HTML content to PDF."""
        try:
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"PDF saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
