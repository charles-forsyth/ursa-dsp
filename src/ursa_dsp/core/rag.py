import os
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
            # Skip templates and hidden files
            if "Template" in filename or filename.startswith("."):
                continue

            content = read_file_content(path)
            if content:
                # Add a header to identify the example source
                labeled_content = f"--- START EXAMPLE DSP: {filename} ---\n{content}\n--- END EXAMPLE DSP ---\n"
                self.examples.append(labeled_content)

        logger.info(
            f"Loaded {len(self.examples)} full example DSPs from {self.examples_dir}"
        )

    def get_full_context(self) -> str:
        """Returns the entire knowledge base as a single string."""
        return "\n".join(self.examples)
