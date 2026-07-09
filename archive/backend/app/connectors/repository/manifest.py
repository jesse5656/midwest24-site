from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryManifestEntry:
    path: str
    fingerprint: str
    size_bytes: int
    suffix: str


@dataclass(frozen=True)
class RepositoryManifest:
    repository_path: str
    entries: dict[str, RepositoryManifestEntry] = field(default_factory=dict)

    def get(self, path: str) -> RepositoryManifestEntry | None:
        return self.entries.get(path)

    def paths(self) -> set[str]:
        return set(self.entries.keys())


class RepositoryManifestStore:
    def __init__(self, manifest_path: str | Path):
        self.manifest_path = Path(manifest_path)

    def exists(self) -> bool:
        return self.manifest_path.exists()

    def load(self) -> RepositoryManifest:
        if not self.manifest_path.exists():
            return RepositoryManifest(repository_path="", entries={})

        raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))

        return RepositoryManifest(
            repository_path=raw.get("repository_path", ""),
            entries={
                path: RepositoryManifestEntry(**entry)
                for path, entry in raw.get("entries", {}).items()
            },
        )

    def save(self, manifest: RepositoryManifest) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "repository_path": manifest.repository_path,
            "entries": {
                path: asdict(entry)
                for path, entry in sorted(manifest.entries.items())
            },
        }

        self.manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
