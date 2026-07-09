from app.connectors.repository import (
    RepositoryChangeDetector,
    RepositoryManifest,
    RepositoryManifestEntry,
)


def entry(path: str, fingerprint: str):
    return RepositoryManifestEntry(
        path=path,
        fingerprint=fingerprint,
        size_bytes=1,
        suffix=".md",
    )


def test_repository_change_detector_reports_new_files():
    previous = RepositoryManifest(repository_path="/repo", entries={})
    current = RepositoryManifest(
        repository_path="/repo",
        entries={"README.md": entry("README.md", "a")},
    )

    changes = RepositoryChangeDetector().compare(previous, current)

    assert changes.new_files == ["README.md"]
    assert changes.modified_files == []
    assert changes.deleted_files == []
    assert changes.unchanged_files == []
    assert changes.changed_count == 1


def test_repository_change_detector_reports_modified_files():
    previous = RepositoryManifest(
        repository_path="/repo",
        entries={"README.md": entry("README.md", "a")},
    )
    current = RepositoryManifest(
        repository_path="/repo",
        entries={"README.md": entry("README.md", "b")},
    )

    changes = RepositoryChangeDetector().compare(previous, current)

    assert changes.modified_files == ["README.md"]
    assert changes.changed_files == ["README.md"]
    assert changes.changed_count == 1


def test_repository_change_detector_reports_deleted_files():
    previous = RepositoryManifest(
        repository_path="/repo",
        entries={"README.md": entry("README.md", "a")},
    )
    current = RepositoryManifest(repository_path="/repo", entries={})

    changes = RepositoryChangeDetector().compare(previous, current)

    assert changes.deleted_files == ["README.md"]
    assert changes.changed_count == 1


def test_repository_change_detector_reports_unchanged_files():
    previous = RepositoryManifest(
        repository_path="/repo",
        entries={"README.md": entry("README.md", "a")},
    )
    current = RepositoryManifest(
        repository_path="/repo",
        entries={"README.md": entry("README.md", "a")},
    )

    changes = RepositoryChangeDetector().compare(previous, current)

    assert changes.unchanged_files == ["README.md"]
    assert changes.changed_count == 0


def test_repository_change_detector_sorts_file_paths():
    previous = RepositoryManifest(repository_path="/repo", entries={})
    current = RepositoryManifest(
        repository_path="/repo",
        entries={
            "z.md": entry("z.md", "z"),
            "a.md": entry("a.md", "a"),
        },
    )

    changes = RepositoryChangeDetector().compare(previous, current)

    assert changes.new_files == ["a.md", "z.md"]
