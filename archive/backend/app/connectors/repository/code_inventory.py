from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.connectors.repository.filesystem_repository_connector import RepositoryFilesystemConnector


LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript React",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".md": "Markdown",
    ".txt": "Plain Text",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".rst": "reStructuredText",
}


@dataclass(frozen=True)
class CodeInventoryFile:
    path: str
    suffix: str
    language: str
    size_bytes: int


@dataclass(frozen=True)
class CodeInventoryLanguageSummary:
    language: str
    file_count: int
    size_bytes: int


@dataclass(frozen=True)
class CodeInventoryPreview:
    files: list[CodeInventoryFile] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_size_bytes(self) -> int:
        return sum(file.size_bytes for file in self.files)

    @property
    def language_count(self) -> int:
        return len(self.languages)

    @property
    def languages(self) -> list[str]:
        return sorted({file.language for file in self.files})

    @property
    def largest_file(self) -> CodeInventoryFile | None:
        if not self.files:
            return None
        return sorted(self.files, key=lambda file: (-file.size_bytes, file.path))[0]

    @property
    def language_summaries(self) -> list[CodeInventoryLanguageSummary]:
        totals: dict[str, dict[str, int]] = {}

        for file in self.files:
            totals.setdefault(file.language, {"file_count": 0, "size_bytes": 0})
            totals[file.language]["file_count"] += 1
            totals[file.language]["size_bytes"] += file.size_bytes

        return [
            CodeInventoryLanguageSummary(
                language=language,
                file_count=values["file_count"],
                size_bytes=values["size_bytes"],
            )
            for language, values in sorted(
                totals.items(),
                key=lambda item: (-item[1]["file_count"], item[0].lower()),
            )
        ]


class CodeInventoryPreviewBuilder:
    def build(self, repository_path: str | Path) -> CodeInventoryPreview:
        connector = RepositoryFilesystemConnector(repository_path)
        files = connector.discover()

        return CodeInventoryPreview(
            files=[
                CodeInventoryFile(
                    path=file.relative_path,
                    suffix=file.suffix,
                    language=LANGUAGE_BY_SUFFIX.get(file.suffix, "Unknown"),
                    size_bytes=file.size_bytes,
                )
                for file in files
            ]
        )
