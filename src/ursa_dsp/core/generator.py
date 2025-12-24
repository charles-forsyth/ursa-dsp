import json
import logging
import re
from typing import Tuple, Any, Dict
from google import genai
from google.genai import types
from ursa_dsp.config import settings
from ursa_dsp.core.schema import ProjectMetadata, DSPSectionResponse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class DSPGenerator:
    def __init__(self, model_name: str = "gemini-3-pro-preview") -> None:
        """
        Initializes the Gemini 3 Generator.
        Strictly uses the specified model version.
        """
        self.model_name = model_name
        self.client = genai.Client(api_key=settings.gemini_api_key)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(
            f"Rate limited or API error. Retrying... (Attempt {retry_state.attempt_number})"
        ),
    )
    def _call_gemini(self, prompt: str, schema: Any) -> Any:
        """Internal helper to call Gemini with retry logic and strict schema enforcement."""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", response_schema=schema
            ),
        )
        if not response.text:
            raise ValueError("Empty response from Gemini API")

        # With response_schema, the text is guaranteed to be valid JSON matching the schema
        return json.loads(response.text)

    def _sanitize_content(self, text: str) -> str:
        """Removes AI artifacts like markdown code blocks and raw HTML tags."""
        # 1. Remove markdown code block wrappers (e.g., ```markdown ... ```)
        text = re.sub(r"```(markdown)?", "", text)
        text = text.replace("```", "")

        # 2. Remove raw HTML tags that might have been included
        text = re.sub(r"<[^>]+>", "", text)

        return text.strip()

    def generate_section(
        self,
        section_title: str,
        section_body: str,
        project_summary: str,
        full_context: str,
    ) -> Tuple[str, str]:
        """Generates content for a single section using full-context RAG and strict schema."""

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
You must output a JSON object adhering to the schema.
**CRITICAL INSTRUCTIONS FOR CONTENT:**
- The `section_content` must be **comprehensive and detailed**. Do not summarize.
- Use **multi-paragraph prose** and bullet points where appropriate, just like the examples.
- Use **STRICT MARKDOWN**. Do not use HTML tags.
- Do not include the section title in the content.
"""
        try:
            logger.info(
                f"Generating content for: {section_title} using {self.model_name}"
            )

            # Enforce DSPSectionResponse schema
            data = self._call_gemini(prompt=prompt, schema=DSPSectionResponse)

            raw_content = data.get("section_content", "")
            clean_content = self._sanitize_content(text=raw_content)

            return prompt, clean_content

        except Exception as e:
            logger.error(f"Generation failed for {section_title}: {e}")
            return prompt, f"[[ERROR: Generation failed after retries: {e}]]"

    def extract_metadata(self, summary_text: str) -> Dict[str, Any]:
        """Uses Gemini to extract structured metadata from the project summary using strict schema."""
        prompt = f"""
You are an expert Research Compliance Officer. Your task is to analyze the following research project summary and extract specific metadata fields to populate a Data Security Plan.

**Project Summary:**
{summary_text}

**Instructions:**
1. Extract the following fields. If a field is not explicitly stated, infer a reasonable guess based on the context.
2. If you absolutely cannot infer a value, use a generic placeholder like "Unknown".
"""
        try:
            logger.info(f"Extracting metadata using {self.model_name}...")

            # Enforce ProjectMetadata schema
            # Note: We pass the Pydantic model directly to helper which passes it to SDK
            data = self._call_gemini(prompt=prompt, schema=ProjectMetadata)
            return data  # type: ignore

        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
