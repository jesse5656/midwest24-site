from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_knowledge_graph import (
    RepositoryKnowledgeGraph,
    RepositoryKnowledgeGraphBuilder,
    RepositoryKnowledgeGraphEdge,
    RepositoryKnowledgeGraphNode,
)
from app.connectors.repository.repository_knowledge_graph_summary import (
    RepositoryKnowledgeGraphSummaryBuilder,
)
from app.schemas.repository_knowledge_graph import (
    RepositoryKnowledgeGraphEdgeResponse,
    RepositoryKnowledgeGraphNodeResponse,
    RepositoryKnowledgeGraphRequest,
    RepositoryKnowledgeGraphResponse,
    RepositoryKnowledgeGraphSummaryResponse,
)

router = APIRouter()


def serialize_repository_knowledge_graph_node(
    node: RepositoryKnowledgeGraphNode,
) -> RepositoryKnowledgeGraphNodeResponse:
    return RepositoryKnowledgeGraphNodeResponse(
        node_id=node.node_id,
        node_type=node.node_type,
        label=node.label,
        source=node.source,
    )


def serialize_repository_knowledge_graph_edge(
    edge: RepositoryKnowledgeGraphEdge,
) -> RepositoryKnowledgeGraphEdgeResponse:
    return RepositoryKnowledgeGraphEdgeResponse(
        source_id=edge.source_id,
        target_id=edge.target_id,
        relationship=edge.relationship,
    )


def serialize_repository_knowledge_graph(
    graph: RepositoryKnowledgeGraph,
) -> RepositoryKnowledgeGraphResponse:
    summary = RepositoryKnowledgeGraphSummaryBuilder().build(graph)

    return RepositoryKnowledgeGraphResponse(
        repository_path=graph.repository_path,
        nodes=[serialize_repository_knowledge_graph_node(node) for node in graph.nodes],
        edges=[serialize_repository_knowledge_graph_edge(edge) for edge in graph.edges],
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        node_types=graph.node_types,
        relationship_types=graph.relationship_types,
        file_node_count=graph.file_node_count,
        package_node_count=graph.package_node_count,
        dependency_node_count=graph.dependency_node_count,
        symbol_node_count=graph.symbol_node_count,
        import_node_count=graph.import_node_count,
        summary=RepositoryKnowledgeGraphSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-knowledge-graph",
    response_model=RepositoryKnowledgeGraphResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_knowledge_graph(data: RepositoryKnowledgeGraphRequest):
    try:
        graph = RepositoryKnowledgeGraphBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_knowledge_graph(graph)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
