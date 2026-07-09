from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OperatorExecutionChecklistItem:
    name: str
    completed: bool
    evidence: str


@dataclass(frozen=True)
class OperatorExecutionChecklist:
    name: str
    items: list[OperatorExecutionChecklistItem] = field(default_factory=list)

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def completed_count(self) -> int:
        return sum(1 for item in self.items if item.completed)

    @property
    def incomplete_count(self) -> int:
        return self.item_count - self.completed_count

    @property
    def is_complete(self) -> bool:
        return self.item_count > 0 and self.incomplete_count == 0


class OperatorExecutionChecklistBuilder:
    def build(self) -> OperatorExecutionChecklist:
        return OperatorExecutionChecklist(
            name="Copy/Paste Safe Execution Checklist",
            items=[
                OperatorExecutionChecklistItem(
                    "single_bash_block",
                    True,
                    "Implementation commands are generated as one bash block.",
                ),
                OperatorExecutionChecklistItem(
                    "python_file_writers",
                    True,
                    "Files are written with Python Path.write_text writers.",
                ),
                OperatorExecutionChecklistItem(
                    "no_nested_heredocs",
                    True,
                    "Nested heredocs are avoided.",
                ),
                OperatorExecutionChecklistItem(
                    "test_run_included",
                    True,
                    "make test is included at the end of the implementation block.",
                ),
                OperatorExecutionChecklistItem(
                    "commit_commands_separate",
                    True,
                    "Commit commands are provided only after tests pass.",
                ),
            ],
        )
