import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

from rich.console import Console
from rich.table import Table


def classify_severity(issue: Dict) -> str:
    """
    Map pylint categories to severity levels.
    """
    t = (issue.get("type") or "").lower()

    if t in {"fatal", "error"}:
        return "critical"
    if t in {"warning", "refactor"}:
        return "major"
    # Some symbols are noisier and can stay minor
    return "minor"


QUICK_FIXES = {
    "unused-import": "Remove the unused import or use it. Example: delete the line if not needed.",
    "unused-variable": "Delete the variable or prefix with '_' if intentional.",
    "missing-docstring": "Add a short docstring describing purpose, params, returns.",
    "invalid-name": "Use snake_case for functions/variables and PascalCase for classes.",
    "bad-indentation": "Fix spaces/indentation to follow PEP8 (4 spaces).",
    "wrong-import-order": "Group: stdlib, third-party, local; and sort within groups.",
    "redefined-outer-name": "Rename local variable to avoid shadowing outer scope.",
}


def suggest_fix(issue: Dict) -> str:
    """
    Suggest a quick fix based on the pylint issue.
    """
    symbol = (issue.get("symbol") or "").lower()
    return QUICK_FIXES.get(symbol, "")


def simple_score(issues: List[Dict]) -> int:
    """
    Convert severities to a 0-100 score (100 = best).
    """
    if not issues:
        return 100
    penalty = 0
    for i in issues:
        sev = i.get("severity", "minor")
        if sev == "critical":
            penalty += 10
        elif sev == "major":
            penalty += 5
        else:
            penalty += 2
    # Compute a score where 100 is perfect and penalties reduce it.
    score = max(0, 100 - penalty)
    return score


def run_pylint(file_path: str, output_json: str = "reviews/lint_report.json") -> List[Dict]:
    """
    Run pylint on the given file and save results in JSON format.
    Returns issues (with severity & quick_fix) and an overall score.
    """
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"File {file_path} not found.")

    # Always use the current interpreter so this works on Streamlit Cloud (no .venv present)
    # and also works correctly in any local virtual environment.
    pylint_python = sys.executable

    # Run pylint and capture JSON output.
    result = subprocess.run(
        [pylint_python, "-m", "pylint", str(file), "-f", "json"],
        capture_output=True,
        text=True,
        check=False,
    )

    try:
        issues = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        issues = []

    # Enrich issues
    for it in issues:
        it["severity"] = classify_severity(it)
        it["quick_fix"] = suggest_fix(it)

    # Save report (issues only: UI will compute score too)
    output = Path(output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=4, ensure_ascii=False)

    return issues


def print_issues(issues: List[Dict]) -> None:
    """Print a formatted table of lint issues to the terminal."""
    console = Console()
    table = Table(title="Lint Issues")
    table.add_column("Severity")
    table.add_column("Type")
    table.add_column("Message")
    table.add_column("Line", justify="right")
    table.add_column("Quick Fix")

    for issue in issues:
        table.add_row(
            issue.get("severity", ""),
            issue.get("type", ""),
            issue.get("message", ""),
            str(issue.get("line", "")),
            issue.get("quick_fix", ""),
        )
    console.print(table)


if __name__ == "__main__":
    found = run_pylint("samples/example_code.py")
    print(f"Found {len(found)} issues. Saved to reviews/lint_report.json")
    print_issues(found)
