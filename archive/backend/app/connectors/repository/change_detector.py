from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.repository.manifest import RepositoryManifest


@dataclass(frozen=True)
class RepositoryChangeSet:
    new_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    unchanged_files: list[str] = field(default_factory=list)

    @property
    def changed_files(self) -> list[str]:
        return [*self.new_files, *self.modified_files]

    @property
    def changed_count(self) -> int:
        return len(self.new_files) + len(self.modified_files) + len(self.deleted_files)


class RepositoryChangeDetector:
    def compare(
        self,
        previous: RepositoryManifest,
        current: RepositoryManifest,
    ) -> RepositoryChangeSet:
        previous_paths = previous.paths()
        current_paths = current.paths()

        new_files = sorted(current_paths - previous_paths)
        deleted_files = sorted(previous_paths - current_paths)

        modified_files = []
        unchanged_files = []

        for path in sorted(previous_paths & current_paths):
            previous_entry = previous.get(path)
            current_entry = current.get(path)

            if previous_entry and current_entry and previous_entry.fingerprint != current_entry.fingerprint:
                modified_files.append(path)
            else:
                unchanged_files.append(path)

        return RepositoryChangeSet(
            new_files=new_files,
            modified_files=modified_files,
            deleted_files=deleted_files,
            unchanged_files=unchanged_files,
        )
