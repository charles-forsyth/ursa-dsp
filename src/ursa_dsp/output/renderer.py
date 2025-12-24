import markdown
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
from weasyprint import HTML  # type: ignore
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportRenderer:
    def __init__(self, templates_dir: str = "templates") -> None:
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )
        # Register markdown filter and mark output as SAFE for Jinja2
        self.env.filters["markdown"] = lambda text: Markup(
            markdown.markdown(text, extensions=["extra", "tables", "fenced_code"])
        )

    def render_html(self, project_name: str, sections: List[Dict[str, Any]]) -> str:
        """Renders the report to an HTML string."""
        template = self.env.get_template("report.html")
        return template.render(
            project_name=project_name,
            sections=sections,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

    def generate_pdf(self, html_content: str, output_path: str) -> None:
        """Converts HTML content to PDF."""
        try:
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"PDF saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
