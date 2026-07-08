from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_REPOSITORY_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".cache",
}

DEFAULT_REPOSITORY_INCLUDED_SUFFIXES = {
    ".md",
    ".txt",
    ".rst",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
}


@dataclass(frozen=True)
class RepositorySkippedPath:
    path: str
    reason: str


@dataclass(frozen=True)
class RepositoryUnsupportedFile:
    path: str
    suffix: str
    reason: str = "unsupported_extension"


@dataclass(frozen=True)
class RepositoryDiscoveryReport:
    supported_files: list[object] = field(default_factory=list)
    skipped_paths: list[RepositorySkippedPath] = field(default_factory=list)
    unsupported_files: list[RepositoryUnsupportedFile] = field(default_factory=list)

    @property
    def supported_count(self) -> int:
        return len(self.supported_files)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_paths)

    @property
    def unsupported_count(self) -> int:
        return len(self.unsupported_files)
