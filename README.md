# AI Code Reviewer

An AI-powered Python code review tool combining **Pylint static analysis** with **LLM feedback** (Google Gemini or OpenAI). Upload or paste Python code and get a quality score, lint issues, AI suggestions, and optional auto-fixes — all in a Streamlit web UI.

---

## Features

- Static analysis via Pylint with severity classification and quick-fix hints
- AI code review via Google Gemini (free) or OpenAI GPT-4o-mini
- AI-powered fix suggestions for detected issues
- Safe deterministic auto-fixes (removes unused imports, inserts docstring templates)
- Downloadable Markdown report and raw lint JSON
- Streamlit web UI

---

## Project Structure

```
AI_code_reviewer/
├── src/
│   ├── ai_reviewer.py       # LLM review & fix suggestions
│   ├── static_analyzer.py   # Pylint runner & issue enrichment
│   └── auto_fixer.py        # Deterministic code auto-fixes
├── ui/
│   └── streamlit_app.py     # Streamlit web interface
├── samples/
│   └── example_code.py      # Sample Python file to test with
├── reviews/                 # Auto-generated review outputs
├── .env                     # API keys (see Setup)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python 3.9 or higher
- A Google Gemini API key (free) **or** an OpenAI API key

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Edit `.env` in the project root (or `ui/.env`) and set your key:

```env
# Free option — Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Paid option — OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

You only need one key. If both are present, Gemini is used.

Get a free Gemini key at: https://aistudio.google.com/app/apikey

---

## Running the App

From the project root, with the virtual environment active:

```bash
streamlit run ui/streamlit_app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Usage

1. **Upload** a `.py` file or **paste** Python code into the text area.
2. Click **Review Code** to run Pylint + AI review.
3. View the **Quality Score**, **Lint Issues** table, and **AI Feedback**.
4. Download the **Markdown report** or **raw lint JSON**.
5. In the **Fixes** section:
   - Click **Generate AI Fix Suggestion** to get LLM-proposed patches.
   - Click **Show Auto-Fixed Code (safe)** to apply deterministic fixes (unused import removal, docstring insertion).
   - Download the fixed file.

---

## Running Static Analysis from the Terminal

```bash
# Analyze a specific file and print a table to the terminal
python src/static_analyzer.py
```

By default this analyzes `samples/example_code.py` and saves `reviews/lint_report.json`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `RuntimeError: No API key configured` | Add `GEMINI_API_KEY` or `OPENAI_API_KEY` to `.env` |
| `ModuleNotFoundError` | Activate the venv and run `pip install -r requirements.txt` |
| `streamlit: command not found` | Activate the venv first, or use `python -m streamlit run ui/streamlit_app.py` |
| Pylint produces no output | Ensure the file path passed to `run_pylint()` exists |

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| streamlit | 1.59.1 | Web UI |
| pylint | 4.0.8 | Static analysis |
| openai | 3.8.0 | LLM API client (Gemini + OpenAI) |
| python-dotenv | 1.2.3 | `.env` loading |
| rich | 15.0.0 | Terminal output formatting |
| pydantic | 2.13.5 | Data validation |
| isort | 9.0.1 | Import sorting |
