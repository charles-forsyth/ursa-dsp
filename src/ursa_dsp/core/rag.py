import os
import re
import logging
from typing import List
from ursa_dsp.utils.io import read_file_content

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self, examples_dir: str = "example_dsps") -> None:
        self.examples_dir = examples_dir
        self.examples: List[str] = []
        self.load_examples()

    def load_examples(self) -> None:
        """Loads all valid examples from the directory."""
        if not os.path.exists(self.examples_dir):
            logger.warning(f"Examples directory not found: {self.examples_dir}")
            return

        for filename in os.listdir(self.examples_dir):
            path = os.path.join(self.examples_dir, filename)
            if "Template" in filename:
                continue

            content = read_file_content(path)
            if content:
                self.examples.append(content)

        logger.info(f"Loaded {len(self.examples)} examples from {self.examples_dir}")

    def get_relevant_examples(self, section_title: str) -> str:
        """Finds text segments relevant to the specific section title."""
        relevant_segments = []

        for example in self.examples:
            # Simple text finding logic (legacy behavior preserved but encapsulated)
            if section_title in example:
                start_index = example.find(section_title)
                # Try to find the start of the next section (often Capitalized words preceded by newlines)
                # This regex is a heuristic from the original script
                next_section_match = re.search(
                    r"\n\n[A-Z][a-z]+", example[start_index + len(section_title) :]
                )

                if next_section_match:
                    end_index = (
                        start_index + len(section_title) + next_section_match.start()
                    )
                    relevant_segments.append(example[start_index:end_index])
                else:
                    # If no next section found, take a chunk or the rest
                    relevant_segments.append(
                        example[
                            start_index : start_index + 2000
                        ]  # Cap at 2k chars if no end found
                    )

        return "\n--- EXAMPLE ---\n".join(relevant_segments)
