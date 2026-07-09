from app.connectors.repository import (
    RepositoryProgressCheckpoint,
    RepositoryProgressLedger,
    RepositoryProgressLedgerStore,
)


def write_fixture_ledger(tmp_path):
    path = tmp_path / "archive-progress-ledger.json"
    store = RepositoryProgressLedgerStore(path)

    store.save(
        RepositoryProgressLedger(
            repository="midwest24-site",
            checkpoints=[
                RepositoryProgressCheckpoint(
                    name="Repository Ingestion Observability",
                    test_count=177,
                    status="completed",
                    notes="Repository ingestion observability completed.",
                ),
                RepositoryProgressCheckpoint(
                    name="Git Repository Intelligence",
                    test_count=443,
                    status="in_progress",
                    notes="Git intelligence in progress.",
                ),
            ],
        )
    )

    return path


def test_archive_progress_ledger_fixture_loads(tmp_path):
    ledger = RepositoryProgressLedgerStore(write_fixture_ledger(tmp_path)).load()

    assert ledger.repository == "midwest24-site"
    assert ledger.latest.name == "Git Repository Intelligence"
    assert ledger.latest_test_count == 443


def test_archive_progress_ledger_fixture_has_completed_repository_observability(tmp_path):
    ledger = RepositoryProgressLedgerStore(write_fixture_ledger(tmp_path)).load()

    completed_names = [
        checkpoint.name
        for checkpoint in ledger.checkpoints
        if checkpoint.status == "completed"
    ]

    assert "Repository Ingestion Observability" in completed_names


def test_archive_progress_ledger_fixture_tracks_checkpoint_count(tmp_path):
    ledger = RepositoryProgressLedgerStore(write_fixture_ledger(tmp_path)).load()

    assert ledger.checkpoint_count == 2
