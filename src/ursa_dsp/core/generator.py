import json
import logging
import google.generativeai as genai # type: ignore
from ursa_dsp.config import settings

logger = logging.getLogger(__name__)

class DSPGenerator:
    def __init__(self, model_name: str = 'gemini-2.5-pro'):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_section(self, section_title: str, section_body: str, project_summary: str, examples_text: str) -> tuple[str, str]:
        """Generates content for a single section."""
        
        prompt = f"""
You are an expert in writing Data Security Plans for university research. Your task is to complete the following section of a DSP, replacing all placeholders like [PLACEHOLDER] with specific, relevant information.

**Template Section to Complete:**
Title: {section_title}
Body: {section_body}

**Project-Specific Information (from its Summary.md):**
{project_summary}

**Examples of similar, completed sections from other DSPs:**
{examples_text}

**Instructions:**
Based on all the information above, write a new, complete version of the section. It must be comprehensive, professional, and directly relevant to the project's details. **Do not use any placeholder text.** 
Return your response as a single JSON object with one key: "section_content". The value should be the fully completed text for the new section, formatted in Markdown.
"""
        try:
            logger.info(f"Generating content for: {section_title}")
            response = self.model.generate_content(prompt)
            
            # Clean and parse JSON
            clean_json = response.text.strip().replace("```json", "").replace("```", "")
            parsed_json = json.loads(clean_json)
            content = parsed_json.get("section_content", "[[ERROR: 'section_content' key not found]]")
            
            return prompt, content
        except Exception as e:
            logger.error(f"Generation failed for {section_title}: {e}")
            return prompt, f"[[ERROR: Generation failed: {e}]]"
