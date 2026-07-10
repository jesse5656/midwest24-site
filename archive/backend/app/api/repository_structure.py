from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_structure import (
    RepositoryStructureBuilder,
    RepositoryStructureNode,
    RepositoryStructureReport,
)
from app.connectors.repository.repository_structure_summary import RepositoryStructureSummaryBuilder
from app.schemas.repository_structure import (
    RepositoryStructureNodeResponse,
    RepositoryStructureRequest,
    RepositoryStructureResponse,
    RepositoryStructureSummaryResponse,
)

router = APIRouter()


def serialize_repository_structure_node(node: RepositoryStructureNode) -> RepositoryStructureNodeResponse:
    return RepositoryStructureNodeResponse(
        path=node.path,
        node_type=node.node_type,
        depth=node.depth,
        child_count=node.child_count,
    )


def serialize_repository_structure_report(report: RepositoryStructureReport) -> RepositoryStructureResponse:
    summary = RepositoryStructureSummaryBuilder().build(report)

    return RepositoryStructureResponse(
        repository_path=report.repository_path,
        nodes=[serialize_repository_structure_node(node) for node in report.nodes],
        node_count=report.node_count,
        file_count=report.file_count,
        directory_count=report.directory_count,
        max_depth=report.max_depth,
        top_level_nodes=[
            serialize_repository_structure_node(node)
            for node in report.top_level_nodes
        ],
        summary=RepositoryStructureSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-structure",
    response_model=RepositoryStructureResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_structure(data: RepositoryStructureRequest):
    try:
        report = RepositoryStructureBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_structure_report(report)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
