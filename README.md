# gemini-token-calculator

A standalone CLI tool to calculate, analyze, and beautifully display token usage from the Gemini CLI's local history.

## Features
- **Auto-Detection**: Finds your Gemini CLI data directory automatically.
- **Time Filtering**: Filter by date range (e.g., `--since 2026-04-01` or `--until 2026-04-30`).
- **Project Breakdown**: Maps internal workspace IDs to your actual project folders and sanitizes your home path.
- **Top Projects**: Shows your 5 most token-heavy projects cleanly.
- **Model Usage**: Breaks down the number of tokens used per model.
- **Exports**: Export raw token data to JSON or CSV for further analysis.

## Installation

### Using the Standalone Binary (Recommended)
You can download the pre-compiled, zero-dependency executable from the [Releases page](https://github.com/Eevee8340/Gemini-Token-Calculator/releases).

**Windows:**
1. Download `gemini-token-calculator.exe`.
2. Add the folder containing it to your system's `PATH` environment variable, or run it directly from your terminal.

### From Source (Python)
If you prefer running the script from source:
1. Ensure you have Python 3.8+ installed.
2. Clone the repository: `git clone https://github.com/Eevee8340/Gemini-Token-Calculator.git`
3. Install the dependencies: `pip install -r requirements.txt`
4. Run the script: `python -m src.main`

## Usage

Simply run the tool in your terminal to see a beautiful breakdown of your usage:
```bash
gemini-token-calculator
```

**Filtering by Date:**
```bash
gemini-token-calculator --since 2026-04-01
gemini-token-calculator --since 2026-01-01 --until 2026-03-31
```

**Exporting Data:**
```bash
gemini-token-calculator --export json > stats.json
gemini-token-calculator --export csv > stats.csv
```

## Building Locally
To build the `.exe` yourself:
```bash
pip install -r requirements.txt
python build.py
```
The executable will be located in the `dist/` directory.
