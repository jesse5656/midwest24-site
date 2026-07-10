from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


PACKAGE_MARKERS = {
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "package.json": "node",
    "tsconfig.json": "typescript",
    "composer.json": "php",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "pom.xml": "java",
    "build.gradle": "java",
    "Gemfile": "ruby",
}


@dataclass(frozen=True)
class RepositoryPackageMarker:
    path: str
    marker_name: str
    ecosystem: str
    depth: int


@dataclass(frozen=True)
class RepositoryPackageMap:
    repository_path: str
    markers: list[RepositoryPackageMarker] = field(default_factory=list)

    @property
    def marker_count(self) -> int:
        return len(self.markers)

    @property
    def ecosystem_count(self) -> int:
        return len(self.ecosystems)

    @property
    def ecosystems(self) -> list[str]:
        return sorted({marker.ecosystem for marker in self.markers})

    @property
    def root_markers(self) -> list[RepositoryPackageMarker]:
        return [marker for marker in self.markers if marker.depth == 1]

    @property
    def has_package_markers(self) -> bool:
        return self.marker_count > 0

    def markers_for_ecosystem(self, ecosystem: str) -> list[RepositoryPackageMarker]:
        return [marker for marker in self.markers if marker.ecosystem == ecosystem]


class RepositoryPackageMapBuilder:
    ignored_names = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

    def build(self, repository_path: str | Path, max_depth: int = 5) -> RepositoryPackageMap:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        markers: list[RepositoryPackageMarker] = []

        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            parts = relative.parts

            if any(part in self.ignored_names for part in parts):
                continue

            if len(parts) > max_depth:
                continue

            if not path.is_file():
                continue

            ecosystem = PACKAGE_MARKERS.get(path.name)

            if ecosystem is None:
                continue

            markers.append(
                RepositoryPackageMarker(
                    path=relative.as_posix(),
                    marker_name=path.name,
                    ecosystem=ecosystem,
                    depth=len(parts),
                )
            )

        return RepositoryPackageMap(repository_path=str(root), markers=markers)
