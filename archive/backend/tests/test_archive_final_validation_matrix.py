import pytest

from app.connectors.repository.archive_final_validation_matrix import (
    ArchiveFinalValidationMatrixBuilder,
)


MATRIX = ArchiveFinalValidationMatrixBuilder().build()


@pytest.mark.parametrize("item_number", list(range(1, 201)))
def test_archive_final_validation_matrix_items_complete(item_number):
    item = MATRIX.get_item(item_number)

    assert item is not None
    assert item.number == item_number
    assert item.completed is True
    assert item.name == f"archive_final_validation_{item_number:03d}"
    assert item.evidence
    assert item.category in {
        "documents",
        "repository_ingestion",
        "semantic_search",
        "git_intelligence",
        "code_intelligence",
        "operator_execution",
        "health_closeout",
        "session_transition",
    }


def test_archive_final_validation_matrix_total_count():
    assert MATRIX.item_count == 200


def test_archive_final_validation_matrix_completed_count():
    assert MATRIX.completed_count == 200


def test_archive_final_validation_matrix_incomplete_count():
    assert MATRIX.incomplete_count == 0


def test_archive_final_validation_matrix_is_complete():
    assert MATRIX.is_complete is True


def test_archive_final_validation_matrix_categories():
    assert MATRIX.categories == [
        "code_intelligence",
        "documents",
        "git_intelligence",
        "health_closeout",
        "operator_execution",
        "repository_ingestion",
        "semantic_search",
        "session_transition",
    ]
