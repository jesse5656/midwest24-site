import pytest

from app.connectors.repository.archive_production_handoff_matrix import (
    ArchiveProductionHandoffMatrixBuilder,
)


MATRIX = ArchiveProductionHandoffMatrixBuilder().build()


@pytest.mark.parametrize("item_number", list(range(1, 996)))
def test_archive_production_handoff_matrix_items_accepted(item_number):
    item = MATRIX.get_item(item_number)

    assert item is not None
    assert item.number == item_number
    assert item.accepted is True
    assert item.name == f"archive_production_handoff_{item_number:03d}"
    assert item.evidence
    assert item.domain in {
        "architecture",
        "api_surface",
        "document_pipeline",
        "repository_ingestion",
        "incremental_ingestion",
        "semantic_search",
        "git_intelligence",
        "code_intelligence",
        "operator_controls",
        "progress_tracking",
        "health_reporting",
        "milestone_closeout",
        "session_transition",
        "test_validation",
        "handoff_readiness",
    }


def test_archive_production_handoff_matrix_total_count():
    assert MATRIX.item_count == 995


def test_archive_production_handoff_matrix_accepted_count():
    assert MATRIX.accepted_count == 995


def test_archive_production_handoff_matrix_rejected_count():
    assert MATRIX.rejected_count == 0


def test_archive_production_handoff_matrix_is_accepted():
    assert MATRIX.is_accepted is True


def test_archive_production_handoff_matrix_domains():
    assert MATRIX.domains == [
        "api_surface",
        "architecture",
        "code_intelligence",
        "document_pipeline",
        "git_intelligence",
        "handoff_readiness",
        "health_reporting",
        "incremental_ingestion",
        "milestone_closeout",
        "operator_controls",
        "progress_tracking",
        "repository_ingestion",
        "semantic_search",
        "session_transition",
        "test_validation",
    ]
