# 🏭 PrintOps

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![CAD Engine](https://img.shields.io/badge/CAD-build123d-orange)](https://github.com/gumyr/build123d)
[![CLI Framework](https://img.shields.io/badge/CLI-Typer-purple)](https://typer.tiangolo.com)
[![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)](https://github.com)

**PrintOps Sovereign** is a headless, modular CAD/CAM agent designed to automate 3D printing pipelines. It transforms the traditional high-friction workflow—_Manual CAD editing -> STL Export -> Slicing GUI -> G-code generation_—into an automated **CI/CD pipeline for physical hardware.**

Designed for engineers and robotics hobbyists who need to iterate on mechanical parts and personalized hardware at scale.

## ✨ System Architecture

<div align="center">
  <img src="printops_demo.gif" alt="PrintOps Sovereign Demo">
</div>

- **🧩 Modular Forging:** CAD logic is decoupled from the UI. Add new designs by dropping Python files into `templates/`.
- **👁️ Visual Calibration Engine:** Uses `vedo` to render live 3D previews with interactive sliders, allowing you to align text/labels on slanted surfaces without guessing coordinates.
- **🔪 Headless Slicing Pipeline:** Integrates directly with `prusa-slicer-console` to compute G-code, mass, and time automatically.
- **🏭 Batch Processing:** Process hundreds of unique jobs from a single `.txt` recipe file with zero manual oversight.

---

## 🚀 Quick Start

### 1. Installation

Ensure you have Python 3.11+ and your preferred slicing engine (e.g., PrusaSlicer) installed.

```bash
# Clone the repository
git clone [https://github.com/yourusername/printops.git](https://github.com/yourusername/printops.git)
cd printops

# Install system dependencies
pip install typer rich build123d vedo

```

### 2. Usage Modes

**Interactive Mode** (Human-in-the-loop):
Launches the Sovereign visual calibration and setup wizard.

```bash
python main.py
```

**Headless Automation** (Power-User):
Directly forge a specific part via the terminal.

```bash
python main.py keychain "VANNY" --width 100
```

### 3. All Commands & Customization

Use the --help flag infront of any command to get information on it.

```bash
python main.py --help
```

To change themes, you may use the --set-theme flag infront of the config command.

```bash
python main.py config --set-theme theme_name
```

A list of available themes: `printops,cyberpunk,hacker,ocean,dracula,nord,retro,forest,sunset,monochrome`

## 🛠️ Calibration & Custom Models

PrintOps includes a "Custom Model Modifier" that can ingest any .stl or .step file.

1. Run python main.py and choose Mode 2.

2. Select your base model file.

3. Select Visual Calibration.

4. Use the on-screen sliders to position your text. When aligned, simply Close the viewer and the Agent will persist your coordinates for future builds.

## ⚠️ Common Issues

### Slicer Path Error:

PrintOps requires the "Console" version of PrusaSlicer.

- Windows: `C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe`

- macOS: `/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer`
  If the agent crashes, ensure you have linked the console executable, not the standard GUI application.

### Dependency Errors:

If you see TypeError: `... missing required positional argument`, ensure you have the `__init__`.py files present in all subdirectories of `templates/`. This is required for PrintOps to discover your CAD templates.
