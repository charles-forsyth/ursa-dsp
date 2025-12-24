import json
import logging
from typing import Tuple, Any
import google.generativeai as genai
from ursa_dsp.config import settings

logger = logging.getLogger(__name__)


class DSPGenerator:
    def __init__(self, model_name: str = "gemini-3-pro") -> None:
        # We ignore these calls because the library is untyped
        genai.configure(api_key=settings.gemini_api_key)  # type: ignore[attr-defined]
        self.model: Any = genai.GenerativeModel(model_name)  # type: ignore[attr-defined]

    def generate_section(
        self,
        section_title: str,
        section_body: str,
        project_summary: str,
        full_context: str,
    ) -> Tuple[str, str]:
        """Generates content for a single section using full-context RAG."""

        prompt = f"""
You are an expert Research Compliance Officer at a top-tier university. Your goal is to write a specific section of a Data Security Plan (DSP) for a new research project.

### 1. The Task
Write the content for the DSP section titled: **"{section_title}"**.
Context/Instructions for this section: "{section_body}"

### 2. The New Project (Summary)
{project_summary}

### 3. The Knowledge Base (Reference Examples)
Below are full text examples of previously approved DSPs. 
**INSTRUCTIONS:** 
1. SEARCH these examples for how they handle the "{section_title}" section.
2. ADAPT the best language and security controls to fit the specific needs of the "New Project" above.
3. IGNORE irrelevant details from the examples (e.g., specific names, old dates).
4. ENSURE the tone is formal, professional, and compliant (NIST 800-171/CMMC standards).

--- START KNOWLEDGE BASE ---
{full_context}
--- END KNOWLEDGE BASE ---

### 4. Output Format
Return **ONLY** a JSON object with a single key "section_content". The value must be the Markdown-formatted text of the section. Do not include the title in the markdown, just the body content.

Example JSON:
{{
  "section_content": "The research team will utilize..."
}}
"""
        try:
            logger.info(f"Generating content for: {section_title}")
            response = self.model.generate_content(prompt)

            # Clean and parse JSON
            clean_json = response.text.strip().replace("```json", "").replace("```", "")
            parsed_json = json.loads(clean_json)
            content = parsed_json.get(
                "section_content", "[[ERROR: 'section_content' key not found]]"
            )

            return prompt, content
        except Exception as e:
            logger.error(f"Generation failed for {section_title}: {e}")
            return prompt, f"[[ERROR: Generation failed: {e}]]"
