import pytest

from app.connectors.repository.archive_operational_readiness_matrix import (
    ArchiveOperationalReadinessMatrixBuilder,
)


MATRIX = ArchiveOperationalReadinessMatrixBuilder().build()


@pytest.mark.parametrize("item_number", list(range(1, 346)))
def test_archive_operational_readiness_matrix_items_ready(item_number):
    item = MATRIX.get_item(item_number)

    assert item is not None
    assert item.number == item_number
    assert item.ready is True
    assert item.name == f"archive_operational_readiness_{item_number:03d}"
    assert item.evidence
    assert item.domain in {
        "api_surface",
        "data_models",
        "repository_connectors",
        "document_processing",
        "semantic_retrieval",
        "git_intelligence",
        "code_intelligence",
        "operator_workflow",
        "progress_ledger",
        "closeout_controls",
        "transition_controls",
        "test_coverage",
    }


def test_archive_operational_readiness_matrix_total_count():
    assert MATRIX.item_count == 345


def test_archive_operational_readiness_matrix_ready_count():
    assert MATRIX.ready_count == 345


def test_archive_operational_readiness_matrix_not_ready_count():
    assert MATRIX.not_ready_count == 0


def test_archive_operational_readiness_matrix_is_ready():
    assert MATRIX.is_ready is True


def test_archive_operational_readiness_matrix_domains():
    assert MATRIX.domains == [
        "api_surface",
        "closeout_controls",
        "code_intelligence",
        "data_models",
        "document_processing",
        "git_intelligence",
        "operator_workflow",
        "progress_ledger",
        "repository_connectors",
        "semantic_retrieval",
        "test_coverage",
        "transition_controls",
    ]
