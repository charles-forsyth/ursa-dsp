import json
import logging
from typing import Tuple, Any, Dict
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

    def extract_metadata(self, summary_text: str) -> Dict[str, Any]:
        """Uses Gemini to extract structured metadata from the project summary."""
        prompt = f"""
You are an expert Research Compliance Officer. Your task is to analyze the following research project summary and extract specific metadata fields to populate a Data Security Plan.

**Project Summary:**
{summary_text}

**Instructions:**
1. Extract the following fields. If a field is not explicitly stated, infer a reasonable guess based on the context (e.g., if "genomic data" is mentioned, classification might be P4/CUI).
2. If you absolutely cannot infer a value, use a generic placeholder like "Unknown".
3. Return **ONLY** a valid JSON object. Do not include markdown code blocks.

**Schema to Fill:**
{{
    "project_name": "Official title or short name",
    "pi_name": "Name of Principal Investigator",
    "uisl_name": "Name of IT Security Lead",
    "department": "Department or Unit",
    "classification": "One of: P3 (Moderate), P4 (High), HIPAA, CUI, Export Controlled",
    "is_cui": true/false,
    "data_provider": "Who is providing the data? (e.g. NIH)",
    "infrastructure": "One of: Standalone Workstation, UCR Research Cluster, Cloud (AWS/GCP), Air-gapped Server",
    "os_type": "Operating System (e.g. Linux, Windows)",
    "transfer_method": "How data moves (e.g. Globus, USB)",
    "retention_date": "YYYY-MM-DD (Estimate 5 years out if unknown)",
    "destruction_method": "e.g. DoD 5220.22-M"
}}
"""
        try:
            logger.info("Extracting metadata from summary...")
            response = self.model.generate_content(prompt)
            clean_json = response.text.strip().replace("```json", "").replace("```", "")
            data: Dict[str, Any] = json.loads(clean_json)
            return data
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
