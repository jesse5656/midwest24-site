#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


APPROVED_STATUSES = {"approved", "accepted"}


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


def load_policy(root: Path) -> dict[str, Any]:
    path = root / ".governance/policy.yaml"

    if not path.exists():
        raise SystemExit(f"Governance policy not found: {path}")

    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid governance policy {path}: {exc}") from exc


def staged_files(root: Path) -> list[str]:
    output = run_git(
        root,
        "diff",
        "--cached",
        "--name-only",
        "--diff-filter=ACMR",
    )

    return [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]


def changed_files(root: Path, base: str) -> list[str]:
    output = run_git(
        root,
        "diff",
        "--name-only",
        f"{base}...HEAD",
    )

    if not output:
        return staged_files(root)

    return [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]


def path_matches(path: str, pattern: str) -> bool:
    normalized_path = path.strip("/")
    normalized_pattern = pattern.strip()

    if normalized_pattern.endswith("/"):
        return normalized_path.startswith(
            normalized_pattern.strip("/") + "/"
        )

    if any(character in normalized_pattern for character in "*?["):
        return fnmatch.fnmatch(normalized_path, normalized_pattern)

    return (
        normalized_path == normalized_pattern.strip("/")
        or normalized_path.startswith(
            normalized_pattern.strip("/") + "/"
        )
    )


def protected_files(
    files: list[str],
    patterns: list[str],
) -> list[str]:
    return sorted(
        {
            path
            for path in files
            if any(path_matches(path, pattern) for pattern in patterns)
        }
    )


def extract_status(text: str) -> str | None:
    lines = text.splitlines()

    for index, line in enumerate(lines):
        stripped = line.strip()

        if not stripped.lower().startswith("status:"):
            continue

        inline = stripped.split(":", 1)[1].strip()

        if inline:
            return inline

        for following in lines[index + 1:]:
            value = following.strip()

            if value:
                return value

        return None

    return None


def extract_scope(text: str) -> list[str]:
    lines = text.splitlines()
    scope: list[str] = []
    collecting = False

    for line in lines:
        stripped = line.strip()

        if re.fullmatch(r"(?:#+\s*)?Scope:?", stripped, flags=re.I):
            collecting = True
            continue

        if collecting and stripped.startswith("#"):
            break

        if collecting and re.fullmatch(r"-{10,}", stripped):
            if scope:
                break
            continue

        if collecting:
            match = re.match(r"^-\s+`?([^`]+?)`?\s*$", stripped)

            if match:
                scope.append(match.group(1).strip())
                continue

            if scope and stripped:
                break

    return scope


def load_proposal(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative

    if not path.exists():
        return {
            "path": relative,
            "exists": False,
            "approved": False,
            "status": None,
            "scope": [],
        }

    text = path.read_text(errors="replace")
    status = extract_status(text)

    return {
        "path": relative,
        "exists": True,
        "approved": (
            status is not None
            and status.lower() in APPROVED_STATUSES
        ),
        "status": status,
        "scope": extract_scope(text),
    }


def proposal_references_from_environment() -> list[str]:
    value = os.environ.get("GOVERNANCE_PROPOSAL", "").strip()

    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def proposal_references_from_files(files: list[str]) -> list[str]:
    references = []

    for path in files:
        upper = Path(path).name.upper()

        if "ACP-" in upper or "OCP-" in upper:
            references.append(path)

    return references


def proposal_references_from_commits(
    root: Path,
    base: str,
) -> list[str]:
    messages = run_git(
        root,
        "log",
        "--format=%B",
        f"{base}..HEAD",
    )

    return [
        match.strip()
        for match in re.findall(
            r"(?im)^Governance-Proposal:\s*(\S+)\s*$",
            messages,
        )
    ]


def discover_proposals(
    root: Path,
    files: list[str],
    base: str,
) -> list[dict[str, Any]]:
    references = []

    references.extend(proposal_references_from_environment())
    references.extend(proposal_references_from_files(files))
    references.extend(proposal_references_from_commits(root, base))

    unique = sorted(set(references))

    return [
        load_proposal(root, relative)
        for relative in unique
    ]


def proposal_covers_path(
    proposal: dict[str, Any],
    path: str,
) -> bool:
    if not proposal.get("approved"):
        return False

    return any(
        path_matches(path, pattern)
        for pattern in proposal.get("scope", [])
    )


def uncovered_paths(
    protected: list[str],
    proposals: list[dict[str, Any]],
) -> list[str]:
    return [
        path
        for path in protected
        if not any(
            proposal_covers_path(proposal, path)
            for proposal in proposals
        )
    ]


def validate_required_metadata(
    root: Path,
    files: list[str],
    policy: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    metadata = policy.get("metadata", {})
    paths = metadata.get("paths", [])
    fields = metadata.get("required_fields", [])

    for relative in files:
        if not relative.endswith(".md"):
            continue

        if not any(
            path_matches(relative, prefix)
            for prefix in paths
        ):
            continue

        path = root / relative

        if not path.exists():
            continue

        text = path.read_text(errors="replace")

        for field in fields:
            if not re.search(
                rf"(?im)^{re.escape(field)}:\s*(?:\n\s*)?\S+",
                text,
            ):
                errors.append(
                    f"{relative}: required metadata field "
                    f"missing or empty: {field}"
                )

    return errors


def validate_policy_shape(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    required = [
        "schema_version",
        "policy_version",
        "repository",
        "protected_assets",
        "approvals",
    ]

    for key in required:
        if key not in policy:
            errors.append(f"Policy is missing required key: {key}")

    if not isinstance(policy.get("protected_assets", []), list):
        errors.append("protected_assets must be a list")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Enforce deterministic, machine-verifiable "
            "repository governance."
        )
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
    )

    parser.add_argument(
        "--staged",
        action="store_true",
    )

    parser.add_argument(
        "--base",
        default=os.environ.get(
            "GOVERNANCE_BASE",
            "origin/main",
        ),
    )

    parser.add_argument(
        "--report-only",
        action="store_true",
    )

    args = parser.parse_args()

    root = find_repository_root(args.root.resolve())
    policy = load_policy(root)

    errors = validate_policy_shape(policy)

    files = (
        staged_files(root)
        if args.staged
        else changed_files(root, args.base)
    )

    protected = protected_files(
        files,
        policy.get("protected_assets", []),
    )

    errors.extend(
        validate_required_metadata(root, files, policy)
    )

    proposals = discover_proposals(
        root,
        files,
        args.base,
    )

    if protected:
        approved = [
            proposal
            for proposal in proposals
            if proposal["approved"]
        ]

        if not approved:
            errors.append(
                "Protected assets changed without an approved "
                "ACP/OCP reference."
            )
        else:
            uncovered = uncovered_paths(
                protected,
                approved,
            )

            if uncovered:
                errors.append(
                    "Approved proposals do not cover these "
                    "protected paths: "
                    + ", ".join(uncovered)
                )

    print("Governance Enforcement")
    print("=" * 80)

    if files:
        print("Files under review:")

        for file in files:
            print(f"- {file}")
    else:
        print("No changed files detected.")

    if protected:
        print("\nProtected assets affected:")

        for file in protected:
            print(f"- {file}")

    if proposals:
        print("\nProposal references:")

        for proposal in proposals:
            print(
                f"- {proposal['path']} "
                f"(status={proposal['status'] or 'missing'}, "
                f"scope={len(proposal['scope'])})"
            )

    if errors:
        print("\nViolations:")

        for error in errors:
            print(f"- {error}")

        if args.report_only:
            print(
                "\nREPORT ONLY: violations did not block execution."
            )
            return 0

        return 1

    print("\nGovernance checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
