from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_import_graph import (
    RepositoryImportEdge,
    RepositoryImportGraph,
    RepositoryImportGraphBuilder,
)
from app.connectors.repository.repository_import_graph_summary import RepositoryImportGraphSummaryBuilder
from app.schemas.repository_import_graph import (
    RepositoryImportEdgeResponse,
    RepositoryImportGraphRequest,
    RepositoryImportGraphResponse,
    RepositoryImportGraphSummaryResponse,
)

router = APIRouter()


def serialize_repository_import_edge(edge: RepositoryImportEdge) -> RepositoryImportEdgeResponse:
    return RepositoryImportEdgeResponse(
        source_file=edge.source_file,
        imported_name=edge.imported_name,
        import_type=edge.import_type,
        line_number=edge.line_number,
    )


def serialize_repository_import_graph(graph: RepositoryImportGraph) -> RepositoryImportGraphResponse:
    summary = RepositoryImportGraphSummaryBuilder().build(graph)

    return RepositoryImportGraphResponse(
        repository_path=graph.repository_path,
        edges=[serialize_repository_import_edge(edge) for edge in graph.edges],
        edge_count=graph.edge_count,
        source_file_count=graph.source_file_count,
        imported_name_count=graph.imported_name_count,
        source_files=graph.source_files,
        imported_names=graph.imported_names,
        summary=RepositoryImportGraphSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-import-graph",
    response_model=RepositoryImportGraphResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_import_graph(data: RepositoryImportGraphRequest):
    try:
        graph = RepositoryImportGraphBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_import_graph(graph)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
