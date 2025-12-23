# 🐻 Ursa DSP

**Automated Data Security Plan Generator for Research Compliance**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ursa DSP** is an enterprise-grade CLI tool designed to streamline the creation of Data Security Plans (DSPs) for university research. By leveraging the **Gemini 2.5 Pro** model and a modern Python reporting stack, it transforms unstructured project summaries into compliant, professional PDF documents.

---

## ✨ Features

*   **🤖 AI-Powered Content Generation:** Utilizes Google's Gemini 2.5 Pro to write context-aware, compliant security sections.
*   **📚 RAG Architecture:** Retrieval-Augmented Generation ensures generated content aligns with approved example DSPs.
*   **📄 Professional Output:** Generates beautiful, standardized PDFs using **WeasyPrint** and **Jinja2** templating.
*   **🖥️ Modern CLI:** Features a rich terminal user interface with progress bars and colored logging.
*   **🔒 Secure:** Strict environment variable management for API keys using `pydantic-settings`.
*   **📦 Easy Distribution:** Installable globally via `uv` or `pip`.

---

## 🏗️ The "Modern Python Reporting Stack"

Ursa DSP is built on a robust foundation of modern Python libraries:

| Component | Library | Purpose |
| :--- | :--- | :--- |
| **CLI & UI** | `Typer` + `Rich` | Beautiful, intuitive command-line interface. |
| **Intelligence** | `google-genai` | Access to Gemini 2.5 Pro for content generation. |
| **Data Integrity** | `Pydantic V2` | Strict data validation and settings management. |
| **Templating** | `Jinja2` | Separation of logic and presentation. |
| **Rendering** | `WeasyPrint` | HTML-to-PDF conversion with CSS paged media support. |

---

## 🚀 Installation

### Prerequisites
*   Python 3.9+
*   `uv` (recommended) or `pip`
*   Google Gemini API Key

### Install via `uv` (Recommended)
This installs Ursa DSP as a global tool, available anywhere on your system.

```bash
uv tool install git+https://github.com/charles-forsyth/ursa-dsp.git
```

### Install via `pip`
```bash
pip install git+https://github.com/charles-forsyth/ursa-dsp.git
```

---

## ⚙️ Configuration

Ursa DSP uses `pydantic-settings` to manage configuration. You can provide your API key via a `.env` file or environment variables.

**1. Create a `.env` file** (or export variables in your shell):
```bash
GEMINI_API_KEY=your_api_key_here
```

**Search Paths:**
The tool looks for `.env` in the following locations (in order):
1.  `/Research_CRM/.env` (Legacy)
2.  `./.env` (Current directory)
3.  `~/.config/ursa_dsp/.env` (User config)

---

## 🛠️ Usage

### Generate a DSP
To generate a new plan, simply provide the path to your project's summary markdown file or the project folder name (if following the standard structure).

```bash
ursa-dsp generate ./projects/MyNewStudy/Summary.md
```

**Options:**
*   `-o, --output <path>`: Specify a custom directory for the output files.
*   `-v, --verbose`: Enable detailed debug logging.

### Check Version
```bash
ursa-dsp version
```

---

## 👨‍💻 Development

To contribute or modify Ursa DSP, clone the repository and set up the environment:

```bash
# Clone
git clone git@github.com:charles-forsyth/ursa-dsp.git
cd ursa-dsp

# Install dependencies
uv sync

# Run Tests
uv run pytest
```

---

## 📄 License

This project is licensed under the MIT License.