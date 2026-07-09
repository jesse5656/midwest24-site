from app.connectors.repository import (
    RepositoryManifest,
    RepositoryManifestEntry,
    RepositoryManifestStore,
)


def test_repository_manifest_returns_paths_and_entries():
    manifest = RepositoryManifest(
        repository_path="/repo",
        entries={
            "README.md": RepositoryManifestEntry(
                path="README.md",
                fingerprint="abc",
                size_bytes=10,
                suffix=".md",
            )
        },
    )

    assert manifest.paths() == {"README.md"}
    assert manifest.get("README.md").fingerprint == "abc"
    assert manifest.get("missing.md") is None


def test_repository_manifest_store_returns_empty_manifest_when_missing(tmp_path):
    store = RepositoryManifestStore(tmp_path / "missing.json")

    manifest = store.load()

    assert manifest.repository_path == ""
    assert manifest.entries == {}


def test_repository_manifest_store_saves_and_loads_manifest(tmp_path):
    path = tmp_path / "manifest.json"
    store = RepositoryManifestStore(path)

    manifest = RepositoryManifest(
        repository_path="/repo",
        entries={
            "README.md": RepositoryManifestEntry(
                path="README.md",
                fingerprint="abc",
                size_bytes=10,
                suffix=".md",
            )
        },
    )

    store.save(manifest)
    loaded = store.load()

    assert loaded.repository_path == "/repo"
    assert loaded.get("README.md").fingerprint == "abc"
    assert loaded.get("README.md").size_bytes == 10


def test_repository_manifest_store_creates_parent_directory(tmp_path):
    path = tmp_path / "nested" / "manifest.json"
    store = RepositoryManifestStore(path)

    store.save(RepositoryManifest(repository_path="/repo", entries={}))

    assert path.exists()
