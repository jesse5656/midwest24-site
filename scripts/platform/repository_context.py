#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


from scripts.platform.parsers.operating_plan import parse_operating_plan


SCHEMA_VERSION = "1.0.0"


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def find_repository_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        raise SystemExit(f"Not inside a Git repository: {start}")

    return Path(result.stdout.strip()).resolve()


def load_policy(root: Path) -> dict[str, Any]:
    path = root / ".governance/policy.yaml"

    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid policy file {path}: {exc}") from exc


def find_operating_plan(
    root: Path,
    policy: dict[str, Any],
) -> Path | None:
    configured = policy.get("operating_plan", {}).get("candidates", [])

    candidates = configured or [
        "OPERATING-PLAN.md",
        "docs/discipline/OPERATING-PLAN.md",
    ]

    for candidate in candidates:
        path = root / candidate

        if path.exists():
            return path

    return None


def existing_paths(root: Path, values: list[str]) -> list[str]:
    return [
        value
        for value in values
        if (root / value).exists()
    ]


def discover_proposals(root: Path) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue

        upper = path.name.upper()

        if "ACP" not in upper and "OCP" not in upper:
            continue

        text = path.read_text(errors="replace")

        status_match = re.search(
            r"(?im)^Status:\s*(?:\n\s*)?(.+?)\s*$",
            text,
        )

        results.append(
            {
                "path": str(path.relative_to(root)),
                "status": (
                    status_match.group(1).strip()
                    if status_match
                    else "Unknown"
                ),
            }
        )

    return sorted(results, key=lambda item: item["path"])


def build_context(root: Path) -> dict[str, Any]:
    policy = load_policy(root)
    operating_plan_path = find_operating_plan(root, policy)

    operating_plan: dict[str, Any] = {
        "path": None,
        "current_objective": None,
        "objective_type": None,
        "status": None,
        "objective": None,
        "scope": None,
        "success_criteria": None,
        "active_sprint": None,
        "next_concrete_step": None,
    }

    if operating_plan_path:
        parsed = parse_operating_plan(operating_plan_path)

        operating_plan = {
            "path": str(operating_plan_path.relative_to(root)),
            "current_objective": parsed["name"],
            "objective_type": parsed["type"],
            "status": parsed["status"],
            "objective": parsed["objective"],
            "scope": parsed["scope"],
            "success_criteria": parsed["success_criteria"],
            "active_sprint": parsed["active_sprint"],
            "next_concrete_step": parsed["next_concrete_step"],
        }

    governance = policy.get("governance", {})
    classification = policy.get("classification", {})

    context = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "root": str(root),
            "name": policy.get("repository", {}).get("name", root.name),
            "branch": run_git(root, "branch", "--show-current"),
            "head_commit": run_git(root, "rev-parse", "HEAD"),
            "working_tree_status": run_git(root, "status", "--short"),
        },
        "operating_plan": operating_plan,
        "governance": {
            "normative_sources": existing_paths(
                root,
                governance.get("normative_sources", []),
            ),
            "policy_path": (
                ".governance/policy.yaml"
                if (root / ".governance/policy.yaml").exists()
                else None
            ),
            "policy_version": policy.get("policy_version"),
        },
        "engineering_standards": existing_paths(
            root,
            classification.get("engineering_standards", []),
        ),
        "operational_procedures": existing_paths(
            root,
            classification.get("operational_procedures", []),
        ),
        "implementation_guides": existing_paths(
            root,
            classification.get("implementation_guides", []),
        ),
        "ai_collaboration": existing_paths(
            root,
            classification.get("ai_collaboration", []),
        ),
        "protected_assets": policy.get(
            "protected_assets",
            [],
        ),
        "approvals": {
            "proposal_patterns": policy.get(
                "approvals",
                {},
            ).get("proposal_patterns", []),
            "active_proposals": discover_proposals(root),
        },
        "warnings": [],
    }

    if not operating_plan_path:
        context["warnings"].append(
            "No Operating Plan was found using configured candidates."
        )

    if context["repository"]["working_tree_status"]:
        context["warnings"].append(
            "The repository contains uncommitted changes."
        )

    missing_normative = [
        path
        for path in governance.get("normative_sources", [])
        if not (root / path).exists()
    ]

    if missing_normative:
        context["warnings"].append(
            "Configured normative sources are missing: "
            + ", ".join(missing_normative)
        )

    return context


def render_text(context: dict[str, Any]) -> str:
    repository = context["repository"]
    operating = context["operating_plan"]

    lines = [
        "Repository Context Resolution",
        "=" * 80,
        f"Repository: {repository['name']}",
        f"Root: {repository['root']}",
        f"Branch: {repository['branch'] or '(unknown)'}",
        f"HEAD: {repository['head_commit'] or '(unknown)'}",
        "",
        "Operating Plan",
        "-" * 80,
        f"Path: {operating['path'] or '(not found)'}",
        f"Current Objective: {operating['current_objective'] or '(not resolved)'}",
        f"Objective Type: {operating['objective_type'] or '(not resolved)'}",
        f"Status: {operating['status'] or '(not resolved)'}",
        f"Active Sprint: {operating['active_sprint'] or '(not resolved)'}",
        f"Next Concrete Step: {operating['next_concrete_step'] or '(not resolved)'}",
        "",
        "Applicable Governance",
        "-" * 80,
    ]

    for path in context["governance"]["normative_sources"]:
        lines.append(f"- {path}")

    lines.extend(
        [
            "",
            "Engineering Standards",
            "-" * 80,
        ]
    )

    for path in context["engineering_standards"]:
        lines.append(f"- {path}")

    lines.extend(
        [
            "",
            "Operational Procedures",
            "-" * 80,
        ]
    )

    for path in context["operational_procedures"]:
        lines.append(f"- {path}")

    lines.extend(
        [
            "",
            "AI Collaboration Standards",
            "-" * 80,
        ]
    )

    for path in context["ai_collaboration"]:
        lines.append(f"- {path}")

    lines.extend(
        [
            "",
            "Protected Assets",
            "-" * 80,
        ]
    )

    for pattern in context["protected_assets"]:
        lines.append(f"- {pattern}")

    lines.extend(
        [
            "",
            "Working Tree",
            "-" * 80,
            repository["working_tree_status"] or "(clean)",
        ]
    )

    if context["warnings"]:
        lines.extend(
            [
                "",
                "Warnings",
                "-" * 80,
            ]
        )

        for warning in context["warnings"]:
            lines.append(f"- {warning}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve applicable repository context before repository changes."
        )
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository path. Defaults to the current directory.",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
    )

    parser.add_argument(
        "--output",
        type=Path,
    )

    args = parser.parse_args()

    root = find_repository_root(args.root.resolve())
    context = build_context(root)

    if args.format == "text":
        rendered = render_text(context)
    else:
        # policy.yaml and YAML output use JSON-compatible YAML.
        rendered = json.dumps(context, indent=2, sort_keys=True)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered.rstrip() + "\n")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
