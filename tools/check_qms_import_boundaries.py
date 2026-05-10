"""Check canonical QMS import boundaries.

The checker is intentionally small and local: it scans Python imports under
`qos/` and rejects obvious layer inversions.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QOS = ROOT / "qos"

LAYER_ORDER = {
    "contracts": 0,
    "foundation": 1,
    "measurement": 2,
    "acquisition": 3,
    "diagnostics": 4,
    "control": 5,
}

DISALLOWED = {
    "foundation": {"measurement", "acquisition", "diagnostics", "control"},
    "measurement": {"acquisition", "diagnostics", "control"},
    "acquisition": {"foundation", "measurement", "diagnostics", "control"},
    "diagnostics": {"foundation", "measurement", "acquisition", "control"},
    "control": {"foundation", "measurement", "acquisition", "diagnostics"},
}


def qos_layer(module_name: str) -> str | None:
    parts = module_name.split(".")
    if len(parts) < 2 or parts[0] != "qos":
        return None
    return parts[1]


def file_layer(path: Path) -> str | None:
    rel = path.relative_to(QOS)
    if not rel.parts:
        return None
    return rel.parts[0]


def imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def main() -> int:
    failures: list[str] = []

    for path in QOS.rglob("*.py"):
        current_layer = file_layer(path)
        if current_layer not in DISALLOWED:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for module in imported_modules(tree):
            imported_layer = qos_layer(module)
            if imported_layer in DISALLOWED[current_layer]:
                failures.append(
                    f"{path.relative_to(ROOT)} imports {module}; "
                    f"{current_layer} cannot import {imported_layer}"
                )

    if failures:
        print("QMS import boundary violations:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("QMS import boundaries OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

