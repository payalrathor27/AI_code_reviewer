from __future__ import annotations
from typing import List, Dict, Tuple

def apply_auto_fixes(code: str, issues: List[Dict]) -> Tuple[str, List[str]]:
    """
    Safe, deterministic auto-fixes based on pylint issues.
    Handles:
      - unused-import: remove the import line
      - missing-docstring: insert a docstring template after the def/class line
    Returns: (fixed_code, applied_fixes)
    """
    lines = code.splitlines()
    applied: List[str] = []

    #1) Remove unused imports first (work from bottom to top to avoid shifting)
    unused_import_lines = sorted(
        [i["line"] for i in issues if (i.get("symbol") or "").lower() == "unused-import" and i.get("line")],
        reverse=True,
    )
    for ln in unused_import_lines:
        idx = ln - 1
        if 0 <= idx < len(lines):
            # remove the entire line 
            removed = lines.pop(idx)
            applied.append(f"Removed unused import at line {ln}: {removed.strip()}")


    #2) Add docstrings (also bottom -> top to keep indexes valid)
    missing_doc_issues = sorted(
        [i for i in issues if (i.get("symbol") or "").lower() == "missing-docstring" and i.get("line")],
        key=lambda x:x["line"],
        reverse=True,
    )
    for it in missing_doc_issues:
        ln = it["line"]
        idx = ln - 1
        if 0 <= idx < len(lines):
            target = lines[idx]
            # Heuristic: only add if the line likely starts a def/class
            if target.lstrip().startswith(("def", "class")):
                indent = " " * (len(target) - len(target.lstrip()))
                #Insert basic docstring template on next line
                insert_at = idx + 1
                template = [
                    f'{indent}"""',
                    f'{indent}TODO: Add docstring.',
                    f'{indent}"""',
                ]
                lines[insert_at:insert_at] = template
                applied.append(f"Inserted docstring template after line {ln} ({target.strip().split()[0]}).")
    return "\n".join(lines) + ("\n" if not code.endswith("\n") else ""), applied