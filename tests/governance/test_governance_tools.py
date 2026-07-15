from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[2]

CONTEXT = load_module(
    "repository_context",
    ROOT / "scripts/platform/repository_context.py",
)

ENGINE = load_module(
    "governance_engine",
    ROOT / "scripts/governance/governance_engine.py",
)


class RepositoryContextTests(unittest.TestCase):
    def test_parse_authoritative_current_objective(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "OPERATING-PLAN.md"

            path.write_text(
                """# Current Objective

Type:
Engineering Sprint
Name:
Repository Ingestion Observability
Status:
In Progress
Objective:
Improve operational visibility.

## Session Update

Status:

- Historical status.

Current Objective:

- Git Repository Intelligence.

Next Concrete Step:

- Historical next step.
""",
                encoding="utf-8",
            )

            parsed = CONTEXT.parse_operating_plan(path)

        self.assertEqual(
            parsed["type"],
            "Engineering Sprint",
        )
        self.assertEqual(
            parsed["name"],
            "Repository Ingestion Observability",
        )
        self.assertEqual(
            parsed["status"],
            "In Progress",
        )
        self.assertEqual(
            parsed["objective"],
            "Improve operational visibility.",
        )
        self.assertIsNone(
            parsed["active_sprint"],
        )
        self.assertIsNone(
            parsed["next_concrete_step"],
        )

    def test_policy_is_json_compatible_yaml(self):
        policy = json.loads(
            (ROOT / ".governance/policy.yaml").read_text()
        )

        self.assertIn("protected_assets", policy)


class GovernanceEngineTests(unittest.TestCase):
    def test_prefix_path_matching(self):
        self.assertTrue(
            ENGINE.path_matches(
                "docs/institute/CONSTITUTION.md",
                "docs/institute/",
            )
        )

    def test_exact_path_matching(self):
        self.assertTrue(
            ENGINE.path_matches(
                "START-HERE.md",
                "START-HERE.md",
            )
        )

    def test_glob_path_matching(self):
        self.assertTrue(
            ENGINE.path_matches(
                "docs/architecture/acp/ACP-002.md",
                "docs/**/*ACP*.md",
            )
        )

    def test_extract_approved_status(self):
        text = "# Proposal\n\nStatus:\nApproved\n"

        self.assertEqual(
            ENGINE.extract_status(text),
            "Approved",
        )

    def test_extract_scope(self):
        text = """
# Proposal

Status:
Approved

Scope:

- docs/institute/
- `.governance/`

## Problem

Example
"""

        self.assertEqual(
            ENGINE.extract_scope(text),
            [
                "docs/institute/",
                ".governance/",
            ],
        )

    def test_proposal_scope_coverage(self):
        proposal = {
            "approved": True,
            "scope": [
                "docs/institute/",
                ".governance/",
            ],
        }

        self.assertTrue(
            ENGINE.proposal_covers_path(
                proposal,
                "docs/institute/CONSTITUTION.md",
            )
        )

        self.assertFalse(
            ENGINE.proposal_covers_path(
                proposal,
                "docs/operations/WORKFLOW.md",
            )
        )

    def test_uncovered_paths(self):
        proposals = [
            {
                "approved": True,
                "scope": ["docs/institute/"],
            }
        ]

        self.assertEqual(
            ENGINE.uncovered_paths(
                [
                    "docs/institute/CONSTITUTION.md",
                    "docs/operations/WORKFLOW.md",
                ],
                proposals,
            ),
            ["docs/operations/WORKFLOW.md"],
        )


class CommandTests(unittest.TestCase):
    def test_policy_validator(self):
        result = subprocess.run(
            [
                "python3",
                str(
                    ROOT
                    / "scripts/governance/"
                    "validate_governance_policy.py"
                ),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
