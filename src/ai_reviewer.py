import os
from pathlib import Path
from typing import List, Dict

# Load .env for local development (no-op if file is absent, e.g. on Streamlit Cloud)
try:
    from dotenv import load_dotenv
    _project_root = Path(__file__).resolve().parents[1]
    load_dotenv(_project_root / ".env")
    load_dotenv(_project_root / "ui" / ".env")
except ImportError:
    pass

from openai import OpenAI


def _get_secret(key: str) -> str | None:
    """
    Read a secret from st.secrets (Streamlit Cloud / local secrets.toml) first,
    then fall back to environment variables (local .env / system env).
    """
    try:
        import streamlit as st
        return st.secrets.get(key)
    except Exception:
        pass
    return os.getenv(key)


def _build_client():
    """
    Build the OpenAI-compatible client from whichever API key is available.
    Priority: GROQ_API_KEY → GEMINI_API_KEY → OPENAI_API_KEY
    Returns (client, model_name) or (None, None).
    """
    groq_key = _get_secret("GROQ_API_KEY")
    gemini_key = _get_secret("GEMINI_API_KEY")
    openai_key = _get_secret("OPENAI_API_KEY")

    if groq_key:
        client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
        )
        return client, "llama3-8b-8192"

    if gemini_key:
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        return client, "gemini-1.5-flash"

    if openai_key and openai_key != "REPLACE_WITH_A_NEW_OPENAI_API_KEY":
        client = OpenAI(api_key=openai_key)
        return client, "gpt-4o-mini"

    return None, None


# Module-level client — initialised once per process
client, MODEL = _build_client()


def review_code_with_ai(code: str) -> str:
    """
    Send code to the configured LLM and return a structured review as Markdown.
    """
    if client is None:
        raise RuntimeError(
            "No API key configured. "
            "Set GROQ_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY "
            "in your .env file or Streamlit secrets."
        )

    prompt = f"""You are an AI code reviewer. Review the following Python code:

```python
{code}
```

Provide structured feedback with:
- Good practices
- Issues / Bugs
- Suggestions for improvement
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an expert Python code reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=900,
    )
    return response.choices[0].message.content


def ai_fix_suggestions(code: str, issues: List[Dict]) -> str:
    """
    Ask the LLM to propose concrete fix snippets for the issues found by pylint.
    Returns Markdown with patch-like blocks or code snippets.
    """
    if client is None:
        raise RuntimeError(
            "No API key configured. "
            "Set GROQ_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY "
            "in your .env file or Streamlit secrets."
        )

    issues_summary = "\n".join(
        f"- [{it.get('symbol', '')} @ line {it.get('line', '?')}] {it.get('message', '')}"
        for it in issues
    ) or "(no issues)"

    prompt = f"""You are an AI pair programmer. Given the following Python code and a list of
static-analysis findings, propose concrete fixes. Where feasible show a minimal corrected
snippet or a unified diff.

Code:
```python
{code}
```

Issues:
{issues_summary}

Output format (Markdown):
- Short note for each issue
- A corrected code snippet or a small unified diff
- Keep suggestions safe and minimal
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a precise and safe Python fixer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    )
    return response.choices[0].message.content
