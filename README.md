# 🐻 Ursa DSP

**The AI Compliance Agent for High-Assurance Research Data**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Standard](https://img.shields.io/badge/Compliance-NIST%20800--171-green.svg)](https://csrc.nist.gov/publications/detail/sp/800-171/rev-2/final)
[![Standard](https://img.shields.io/badge/Compliance-CMMC%20L2%2F3-green.svg)](https://www.acq.osd.mil/cmmc/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ursa DSP** is an enterprise-grade AI Agent designed to automate the creation of rigorous Data Security Plans (DSPs) for highly sensitive research environments. 

It replaces manual, error-prone compliance writing with a **Retrieval-Augmented Generation (RAG)** workflow, ensuring every plan meets strict federal standards such as **NIST 800-171**, **CUI**, **CMMC Level 2/3**, **FedRAMP High**, and **HIPAA**.

---

## 🛡️ Mission Critical Compliance

Research involving Controlled Unclassified Information (CUI) or Export Controlled data (ITAR/EAR) requires more than a template. Ursa DSP leverages **Gemini 2.5 Pro** to intelligently synthesize:

*   **Project Specifics:** Deep analysis of the research summary, data types, and infrastructure.
*   **Institutional Knowledge:** Retrieval of approved language from a local vector store of successful, signed DSPs.
*   **Regulatory Controls:** Automatic mapping of technical controls to compliance frameworks (NIST/ISO/GDPR).

---

## 🏗️ The Modern AI Agent Stack

Ursa DSP is engineered as a reference architecture for modern Python CLI tools. It combines high-performance tooling with Generative AI to deliver production-ready documents.

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Cognitive Core** | `Google Gemini 2.5 Pro` | Advanced reasoning and technical writing compliance. |
| **Context Engine** | `RAG` (Vector-less) | In-context learning from a curated corpus of "Gold Standard" DSPs. |
| **Interface** | `Typer` + `Rich` | Beautiful, interactive terminal UI with real-time progress. |
| **Data Safety** | `Pydantic V2` | Strict schema validation and secure secret management (`pydantic-settings`). |
| **Rendering** | `Jinja2` + `WeasyPrint` | Dynamic HTML templating converted to print-ready, paged PDF. |

---

## 🚀 Installation

### Global Installation (Recommended)
Install Ursa DSP as a standalone tool available system-wide using `uv`.

```bash
uv tool install git+https://github.com/charles-forsyth/ursa-dsp.git
```

### Developer Setup
If you are contributing or customizing the agent:

```bash
git clone git@github.com:charles-forsyth/ursa-dsp.git
cd ursa-dsp
uv sync
```

---

## ⚡ Usage

### 1. Configure Credentials
Ursa DSP requires a Google Gemini API key. It securely loads this from your environment or a `.env` file.

```bash
# ~/.config/ursa_dsp/.env
GEMINI_API_KEY=AIzaSy...
```

### 2. Generate a Plan
Feed the agent your project's summary. The summary should describe the data flow, research goals, and personnel.

```bash
ursa-dsp generate --summary ./projects/Project_Nebula/Summary.md --output ./artifacts/
```

**The Agent Workflow:**
1.  **Analyze:** Reads and understands the `Summary.md`.
2.  **Retrieve:** Searches the `example_dsps/` knowledge base for relevant compliance patterns.
3.  **Synthesize:** Generates each section of the DSP (Executive Summary, Data Transfer, Storage, Destruction) iteratively.
4.  **Render:** Compiles the sections into a branded, professional PDF.

### 3. Management
Keep your agent up to date with the latest compliance logic:

```bash
uv tool upgrade ursa-dsp
```

---

## 🔒 Security & Privacy

*   **Zero Retention:** Ursa DSP processes data statelessly. No project data is stored by the tool after generation.
*   **Secret Safety:** API keys are managed via strict `pydantic` types and never hardcoded.
*   **Local First:** All PDF generation and file processing happens locally on your machine.

---

## 👨‍💻 Contributing

We follow a strict **High-Velocity Development Workflow**:
1.  **Branch:** `feat/feature-name`
2.  **Quality Gate:** Pass `ruff`, `mypy`, and `pytest` before pushing.
3.  **PR:** All changes via Pull Request.

To run the full test suite:
```bash
uv run pytest
```

---

## 📄 License

MIT License. Designed for use by University Research Computing and Compliance teams.
