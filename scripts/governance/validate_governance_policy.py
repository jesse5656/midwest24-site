#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise SystemExit(f"Required file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON-compatible YAML in {path}: {exc}") from exc


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    policy_path = root / ".governance/policy.yaml"
    schema_path = root / ".governance/policy.schema.json"

    policy = load_json(policy_path)
    schema = load_json(schema_path)

    required = schema.get("required", [])
    errors: list[str] = []

    for key in required:
        if key not in policy:
            errors.append(f"Missing required policy key: {key}")

    expected_types = {
        "schema_version": str,
        "policy_version": str,
        "repository": dict,
        "operating_plan": dict,
        "governance": dict,
        "classification": dict,
        "protected_assets": list,
        "approvals": dict,
        "metadata": dict,
    }

    for key, expected in expected_types.items():
        if key in policy and not isinstance(policy[key], expected):
            errors.append(
                f"{key} must be {expected.__name__}, "
                f"found {type(policy[key]).__name__}"
            )

    if errors:
        print("Governance policy validation failed:")

        for error in errors:
            print(f"- {error}")

        return 1

    print(
        "Governance policy is valid: "
        f"schema={policy['schema_version']} "
        f"policy={policy['policy_version']}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
