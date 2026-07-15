#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.platform.parsers.operating_plan import parse_operating_plan


def parse(text: str) -> dict[str, object]:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "OPERATING-PLAN.md"
        path.write_text(text, encoding="utf-8")
        return parse_operating_plan(path)


def test_structured_current_objective() -> None:
    result = parse(
        """# Current Objective

Type:
Research Program
Name:
Institutional Memory Evidence Development
Status:
In Progress
Objective:
Advance Research Program 001.
Scope:
Rogers Commission evidence extraction
NASA Challenger case study development
Success Criteria:
Evidence extracted from at least one primary source
Case study updated with evidence
Active Sprint:
Evidence Extraction Sprint
Next Concrete Step:
Extract Rogers Commission evidence.
"""
    )

    assert result["type"] == "Research Program"
    assert result["name"] == "Institutional Memory Evidence Development"
    assert result["status"] == "In Progress"
    assert result["objective"] == "Advance Research Program 001."
    assert result["scope"] == (
        "Rogers Commission evidence extraction\n"
        "NASA Challenger case study development"
    )
    assert result["success_criteria"] == (
        "Evidence extracted from at least one primary source\n"
        "Case study updated with evidence"
    )
    assert result["active_sprint"] == "Evidence Extraction Sprint"
    assert result["next_concrete_step"] == "Extract Rogers Commission evidence."


def test_session_updates_do_not_override_current_state() -> None:
    result = parse(
        """# Current Objective

Type:
Engineering Sprint
Name:
Repository Ingestion Observability
Status:
In Progress
Objective:
Improve observability.

## Session Update

Status:

- Historical status.

Current Objective:

- Git Repository Intelligence.

Next Concrete Step:

- Historical next step.
"""
    )

    assert result["type"] == "Engineering Sprint"
    assert result["name"] == "Repository Ingestion Observability"
    assert result["status"] == "In Progress"
    assert result["objective"] == "Improve observability."
    assert result["active_sprint"] is None
    assert result["next_concrete_step"] is None


def test_missing_optional_fields_remain_unresolved() -> None:
    result = parse(
        """# Current Objective

Type:
Operational Improvement
Name:
Mission-Critical SOP Standardization
Status:
In Progress
Objective:
Document and validate systems.
"""
    )

    assert result["active_sprint"] is None
    assert result["next_concrete_step"] is None


def main() -> int:
    test_structured_current_objective()
    test_session_updates_do_not_override_current_state()
    test_missing_optional_fields_remain_unresolved()
    print("Operating Plan parser tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
