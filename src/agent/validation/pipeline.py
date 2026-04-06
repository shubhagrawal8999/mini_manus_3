from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ValidationReport:
    schema_ok: bool
    code_ok: bool
    issues: list[str]

    @property
    def passed(self) -> bool:
        return self.schema_ok and self.code_ok and not self.issues


def validate_json_payload(payload: dict[str, Any], required_keys: set[str]) -> tuple[bool, list[str]]:
    missing = [k for k in sorted(required_keys) if k not in payload]
    if missing:
        return False, [f"Missing required keys: {', '.join(missing)}"]
    return True, []


def validate_python_code(code: str) -> tuple[bool, list[str]]:
    issues: list[str] = []
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return False, [f"Syntax error: {exc.msg} (line {exc.lineno})"]

    banned_fragments = ["os.system(", "subprocess.Popen("]
    for frag in banned_fragments:
        if frag in code:
            issues.append(f"Potentially unsafe call detected: {frag}")

    return len(issues) == 0, issues


def cross_verify(primary_text: str, reviewer_text: str) -> bool:
    """Simple deterministic cross-check placeholder.

    In production this should call a second model and run task-specific consistency checks.
    """
    return bool(primary_text.strip()) and bool(reviewer_text.strip())


def build_report(payload: dict[str, Any], required_keys: set[str], code: str) -> ValidationReport:
    schema_ok, schema_issues = validate_json_payload(payload, required_keys)
    code_ok, code_issues = validate_python_code(code)
    issues = [*schema_issues, *code_issues]

    # Ensure payload can be serialized for audit storage.
    try:
        json.dumps(payload)
    except TypeError:
        issues.append("Payload is not JSON serializable")

    return ValidationReport(schema_ok=schema_ok, code_ok=code_ok, issues=issues)
