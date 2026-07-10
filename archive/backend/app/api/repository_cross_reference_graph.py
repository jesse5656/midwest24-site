from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_cross_reference_graph import (
    RepositoryCrossReference,
    RepositoryCrossReferenceGraph,
    RepositoryCrossReferenceGraphBuilder,
)
from app.connectors.repository.repository_cross_reference_graph_summary import (
    RepositoryCrossReferenceGraphSummaryBuilder,
)
from app.schemas.repository_cross_reference_graph import (
    RepositoryCrossReferenceGraphRequest,
    RepositoryCrossReferenceGraphResponse,
    RepositoryCrossReferenceGraphSummaryResponse,
    RepositoryCrossReferenceResponse,
)

router = APIRouter()


def serialize_repository_cross_reference(
    reference: RepositoryCrossReference,
) -> RepositoryCrossReferenceResponse:
    return RepositoryCrossReferenceResponse(
        source_file=reference.source_file,
        source_symbol=reference.source_symbol,
        referenced_name=reference.referenced_name,
        reference_type=reference.reference_type,
        line_number=reference.line_number,
    )


def serialize_repository_cross_reference_graph(
    graph: RepositoryCrossReferenceGraph,
) -> RepositoryCrossReferenceGraphResponse:
    summary = RepositoryCrossReferenceGraphSummaryBuilder().build(graph)

    return RepositoryCrossReferenceGraphResponse(
        repository_path=graph.repository_path,
        references=[
            serialize_repository_cross_reference(reference)
            for reference in graph.references
        ],
        reference_count=graph.reference_count,
        source_file_count=graph.source_file_count,
        referenced_name_count=graph.referenced_name_count,
        source_files=graph.source_files,
        referenced_names=graph.referenced_names,
        call_count=graph.call_count,
        attribute_count=graph.attribute_count,
        name_count=graph.name_count,
        summary=RepositoryCrossReferenceGraphSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-cross-reference-graph",
    response_model=RepositoryCrossReferenceGraphResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_cross_reference_graph(data: RepositoryCrossReferenceGraphRequest):
    try:
        graph = RepositoryCrossReferenceGraphBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_cross_reference_graph(graph)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
