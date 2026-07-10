from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_dependency_map import (
    RepositoryDependency,
    RepositoryDependencyMap,
    RepositoryDependencyMapBuilder,
)
from app.connectors.repository.repository_dependency_map_summary import RepositoryDependencyMapSummaryBuilder
from app.schemas.repository_dependency_map import (
    RepositoryDependencyMapRequest,
    RepositoryDependencyMapResponse,
    RepositoryDependencyMapSummaryResponse,
    RepositoryDependencyResponse,
)

router = APIRouter()


def serialize_repository_dependency(dependency: RepositoryDependency) -> RepositoryDependencyResponse:
    return RepositoryDependencyResponse(
        name=dependency.name,
        source_file=dependency.source_file,
        ecosystem=dependency.ecosystem,
        dependency_type=dependency.dependency_type,
    )


def serialize_repository_dependency_map(dependency_map: RepositoryDependencyMap) -> RepositoryDependencyMapResponse:
    summary = RepositoryDependencyMapSummaryBuilder().build(dependency_map)

    return RepositoryDependencyMapResponse(
        repository_path=dependency_map.repository_path,
        dependencies=[
            serialize_repository_dependency(dependency)
            for dependency in dependency_map.dependencies
        ],
        dependency_count=dependency_map.dependency_count,
        ecosystem_count=dependency_map.ecosystem_count,
        ecosystems=dependency_map.ecosystems,
        runtime_count=dependency_map.runtime_count,
        development_count=dependency_map.development_count,
        summary=RepositoryDependencyMapSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-dependency-map",
    response_model=RepositoryDependencyMapResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_dependency_map(data: RepositoryDependencyMapRequest):
    try:
        dependency_map = RepositoryDependencyMapBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_dependency_map(dependency_map)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
