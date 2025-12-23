# Ursa DSP

**Automated Data Security Plan Generator for UCR Research**

Ursa DSP is a professional-grade CLI tool that transforms project summaries into formal Data Security Plans (DSP) using the "Modern Python Reporting Stack" (Rich, Jinja2, WeasyPrint, Pydantic) and the Gemini 2.5 Pro API.

## 🚀 Installation

You can install Ursa DSP directly from the Git repository using `uv`. This makes the tool available globally on your system.

### Install via HTTPS
```bash
uv tool install git+https://github.com/charles-forsyth/ursa-dsp.git
```

### Install via SSH (Recommended for developers)
```bash
uv tool install git+git@github.com:charles-forsyth/ursa-dsp.git
```

## 🔄 Management

### Update to the Latest Version
`uv` makes it easy to pull the latest changes from the repository and update your installation:
```bash
uv tool upgrade ursa-dsp
```

### Uninstall
```bash
uv tool uninstall ursa-dsp
```

## 🛠 Usage

Generate a DSP by providing a project summary or a project folder name:

```bash
ursa-dsp generate <ProjectName_or_Path_to_Summary>
```

**Options:**
* `-o, --output`: Specify a custom output directory.
* `-v, --verbose`: Enable detailed debug logging.

## 🏗 Stack
* **Intelligence:** Google Gemini 2.5 Pro
* **CLI UI:** Typer & Rich
* **Data Integrity:** Pydantic V2
* **Templating:** Jinja2
* **PDF Rendering:** WeasyPrint
