from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryDependency:
    name: str
    source_file: str
    ecosystem: str
    dependency_type: str = "runtime"


@dataclass(frozen=True)
class RepositoryDependencyMap:
    repository_path: str
    dependencies: list[RepositoryDependency] = field(default_factory=list)

    @property
    def dependency_count(self) -> int:
        return len(self.dependencies)

    @property
    def ecosystem_count(self) -> int:
        return len(self.ecosystems)

    @property
    def ecosystems(self) -> list[str]:
        return sorted({dependency.ecosystem for dependency in self.dependencies})

    @property
    def runtime_count(self) -> int:
        return sum(1 for dependency in self.dependencies if dependency.dependency_type == "runtime")

    @property
    def development_count(self) -> int:
        return sum(1 for dependency in self.dependencies if dependency.dependency_type == "development")

    def dependencies_for_ecosystem(self, ecosystem: str) -> list[RepositoryDependency]:
        return [dependency for dependency in self.dependencies if dependency.ecosystem == ecosystem]


class RepositoryDependencyMapBuilder:
    ignored_names = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

    def build(self, repository_path: str | Path, max_depth: int = 5) -> RepositoryDependencyMap:
        root = Path(repository_path)

        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root}")

        dependencies: list[RepositoryDependency] = []

        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            parts = relative.parts

            if any(part in self.ignored_names for part in parts):
                continue

            if len(parts) > max_depth:
                continue

            if not path.is_file():
                continue

            if path.name == "requirements.txt":
                dependencies.extend(self._parse_requirements(path, relative.as_posix()))

            if path.name == "package.json":
                dependencies.extend(self._parse_package_json(path, relative.as_posix()))

            if path.name == "pyproject.toml":
                dependencies.extend(self._parse_pyproject(path, relative.as_posix()))

        return RepositoryDependencyMap(
            repository_path=str(root),
            dependencies=dependencies,
        )

    def _parse_requirements(self, path: Path, relative_path: str) -> list[RepositoryDependency]:
        dependencies: list[RepositoryDependency] = []

        for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#") or line.startswith("-"):
                continue

            name = re_split_requirement_name(line)

            if name:
                dependencies.append(
                    RepositoryDependency(
                        name=name,
                        source_file=relative_path,
                        ecosystem="python",
                        dependency_type="runtime",
                    )
                )

        return dependencies

    def _parse_package_json(self, path: Path, relative_path: str) -> list[RepositoryDependency]:
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError:
            return []

        dependencies: list[RepositoryDependency] = []

        for name in sorted((data.get("dependencies") or {}).keys()):
            dependencies.append(
                RepositoryDependency(
                    name=name,
                    source_file=relative_path,
                    ecosystem="node",
                    dependency_type="runtime",
                )
            )

        for name in sorted((data.get("devDependencies") or {}).keys()):
            dependencies.append(
                RepositoryDependency(
                    name=name,
                    source_file=relative_path,
                    ecosystem="node",
                    dependency_type="development",
                )
            )

        return dependencies

    def _parse_pyproject(self, path: Path, relative_path: str) -> list[RepositoryDependency]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        dependencies: list[RepositoryDependency] = []

        in_dependencies = False

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if line.startswith("[") and line.endswith("]"):
                in_dependencies = False

            if line.startswith("dependencies") and "[" in line:
                in_dependencies = True
                inline = line.split("[", 1)[1]
                dependencies.extend(
                    self._parse_pyproject_dependency_fragment(inline, relative_path)
                )
                if "]" in inline:
                    in_dependencies = False
                continue

            if in_dependencies:
                dependencies.extend(
                    self._parse_pyproject_dependency_fragment(line, relative_path)
                )
                if "]" in line:
                    in_dependencies = False

        return dependencies

    def _parse_pyproject_dependency_fragment(
        self,
        fragment: str,
        relative_path: str,
    ) -> list[RepositoryDependency]:
        dependencies = []

        for part in fragment.replace("]", "").split(","):
            cleaned = part.strip().strip('"').strip("'")

            if not cleaned:
                continue

            name = re_split_requirement_name(cleaned)

            if name:
                dependencies.append(
                    RepositoryDependency(
                        name=name,
                        source_file=relative_path,
                        ecosystem="python",
                        dependency_type="runtime",
                    )
                )

        return dependencies


def re_split_requirement_name(value: str) -> str:
    separators = ["==", ">=", "<=", "~=", "!=", ">", "<", "["]

    for separator in separators:
        if separator in value:
            value = value.split(separator, 1)[0]

    return value.strip()
