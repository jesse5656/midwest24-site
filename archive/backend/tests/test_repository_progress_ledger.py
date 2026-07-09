from app.connectors.repository import (
    RepositoryProgressCheckpoint,
    RepositoryProgressLedger,
    RepositoryProgressLedgerStore,
)


def test_progress_ledger_latest_none_when_empty():
    ledger = RepositoryProgressLedger(repository="midwest24-site")

    assert ledger.latest is None
    assert ledger.latest_test_count == 0


def test_progress_ledger_latest_returns_last_checkpoint():
    ledger = RepositoryProgressLedger(
        repository="midwest24-site",
        checkpoints=[
            RepositoryProgressCheckpoint(name="A", test_count=100, status="completed"),
            RepositoryProgressCheckpoint(name="B", test_count=200, status="completed"),
        ],
    )

    assert ledger.latest.name == "B"
    assert ledger.latest_test_count == 200


def test_progress_ledger_counts_checkpoints():
    ledger = RepositoryProgressLedger(
        repository="midwest24-site",
        checkpoints=[
            RepositoryProgressCheckpoint(name="A", test_count=100, status="completed"),
            RepositoryProgressCheckpoint(name="B", test_count=200, status="in_progress"),
        ],
    )

    assert ledger.checkpoint_count == 2
    assert ledger.completed_count == 1


def test_progress_ledger_add_checkpoint_returns_new_ledger():
    ledger = RepositoryProgressLedger(repository="midwest24-site")
    updated = ledger.add_checkpoint(
        RepositoryProgressCheckpoint(name="A", test_count=100, status="completed")
    )

    assert ledger.checkpoint_count == 0
    assert updated.checkpoint_count == 1
    assert updated.latest_test_count == 100


def test_progress_ledger_store_loads_empty_when_missing(tmp_path):
    store = RepositoryProgressLedgerStore(tmp_path / "missing.json")

    ledger = store.load()

    assert ledger.repository == ""
    assert ledger.checkpoints == []


def test_progress_ledger_store_saves_and_loads_ledger(tmp_path):
    path = tmp_path / "progress.json"
    store = RepositoryProgressLedgerStore(path)

    ledger = RepositoryProgressLedger(
        repository="midwest24-site",
        checkpoints=[
            RepositoryProgressCheckpoint(
                name="Git Repository Intelligence",
                test_count=443,
                status="completed",
                notes="Git primitives complete.",
            )
        ],
    )

    store.save(ledger)
    loaded = store.load()

    assert loaded.repository == "midwest24-site"
    assert loaded.latest.name == "Git Repository Intelligence"
    assert loaded.latest_test_count == 443


def test_progress_ledger_store_creates_parent_directory(tmp_path):
    path = tmp_path / "nested" / "progress.json"
    store = RepositoryProgressLedgerStore(path)

    store.save(RepositoryProgressLedger(repository="midwest24-site"))

    assert path.exists()


def test_progress_checkpoint_preserves_notes_default():
    checkpoint = RepositoryProgressCheckpoint(
        name="Checkpoint",
        test_count=1,
        status="completed",
    )

    assert checkpoint.notes == ""
