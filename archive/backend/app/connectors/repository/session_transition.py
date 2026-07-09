from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SessionTransitionCommandSet:
    repository_path: str

    @property
    def commands(self) -> list[str]:
        return [
            f"cd {self.repository_path}",
            "pwd",
            "git branch --show-current",
            "git status --short",
            "git log --oneline --decorate -5",
            "tree -L 3",
            "sed -n '1,220p' START-HERE.md",
            "sed -n '1,420p' OPERATING-PLAN.md",
            "cd archive",
            "make test",
        ]


@dataclass(frozen=True)
class SessionTransitionPrompt:
    repository_path: str
    source_of_truth: str
    current_objective: str
    completed: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    deferred: list[str] = field(default_factory=list)

    @property
    def command_set(self) -> SessionTransitionCommandSet:
        return SessionTransitionCommandSet(repository_path=self.repository_path)

    @property
    def completed_count(self) -> int:
        return len(self.completed)

    @property
    def next_step_count(self) -> int:
        return len(self.next_steps)

    @property
    def deferred_count(self) -> int:
        return len(self.deferred)

    def render(self) -> str:
        completed = "\n".join(f"- {item}" for item in self.completed)
        next_steps = "\n".join(f"- {item}" for item in self.next_steps)
        deferred = "\n".join(f"- {item}" for item in self.deferred)
        commands = "\n".join(self.command_set.commands)

        return (
            "# Session Transition Prompt\n\n"
            "We are continuing work on the Midwest24 Archive backend in:\n\n"
            f"{self.repository_path}\n\n"
            "The repository, not this conversation, is the authoritative source of truth.\n\n"
            "Do not redesign architecture unless explicitly requested through an Architecture Change Proposal.\n\n"
            "## Required Verification\n\n"
            f"{commands}\n\n"
            "## Current Objective\n\n"
            f"{self.current_objective}\n\n"
            "## Completed\n\n"
            f"{completed}\n\n"
            "## Next Steps\n\n"
            f"{next_steps}\n\n"
            "## Deferred\n\n"
            f"{deferred}\n\n"
            "## Operating Rule\n\n"
            "Execute one coherent objective, test, commit, update OPERATING-PLAN.md and the progress ledger, then stop.\n"
        )


class SessionTransitionPromptBuilder:
    def build(self, test_count: int) -> SessionTransitionPrompt:
        return SessionTransitionPrompt(
            repository_path="~/Documents/Projects/midwest24-site",
            source_of_truth="repository",
            current_objective="Archive Backend Health and Closeout",
            completed=[
                f"{test_count} passing tests",
                "Document ingestion pipeline",
                "Repository filesystem ingestion",
                "Incremental repository ingestion",
                "Semantic search enrichment",
                "Git Repository Intelligence",
                "Code Intelligence Preview",
                "Archive backend health reporting",
                "Archive backend milestone scorecard",
            ],
            next_steps=[
                "Prepare final transition prompt",
                "Promote the next Priority Queue item",
            ],
            deferred=[
                "Full AST parsing",
                "Symbol persistence",
                "Cross-reference graph",
                "Code intelligence embeddings",
            ],
        )
