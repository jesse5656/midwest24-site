import pytest

from app.connectors.repository.archive_release_acceptance_matrix import (
    ArchiveReleaseAcceptanceMatrixBuilder,
)


MATRIX = ArchiveReleaseAcceptanceMatrixBuilder().build()


@pytest.mark.parametrize("item_number", list(range(1, 346)))
def test_archive_release_acceptance_matrix_items_accepted(item_number):
    item = MATRIX.get_item(item_number)

    assert item is not None
    assert item.number == item_number
    assert item.accepted is True
    assert item.name == f"archive_release_acceptance_{item_number:03d}"
    assert item.evidence
    assert item.area in {
        "api_contracts",
        "document_pipeline",
        "repository_ingestion",
        "incremental_ingestion",
        "semantic_search",
        "git_reports",
        "code_reports",
        "operator_controls",
        "progress_tracking",
        "milestone_closeout",
    }


def test_archive_release_acceptance_matrix_total_count():
    assert MATRIX.item_count == 345


def test_archive_release_acceptance_matrix_accepted_count():
    assert MATRIX.accepted_count == 345


def test_archive_release_acceptance_matrix_rejected_count():
    assert MATRIX.rejected_count == 0


def test_archive_release_acceptance_matrix_is_accepted():
    assert MATRIX.is_accepted is True


def test_archive_release_acceptance_matrix_areas():
    assert MATRIX.areas == [
        "api_contracts",
        "code_reports",
        "document_pipeline",
        "git_reports",
        "incremental_ingestion",
        "milestone_closeout",
        "operator_controls",
        "progress_tracking",
        "repository_ingestion",
        "semantic_search",
    ]
