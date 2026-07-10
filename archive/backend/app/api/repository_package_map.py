from fastapi import APIRouter, HTTPException, status

from app.connectors.repository.repository_package_map import (
    RepositoryPackageMap,
    RepositoryPackageMapBuilder,
    RepositoryPackageMarker,
)
from app.connectors.repository.repository_package_map_summary import RepositoryPackageMapSummaryBuilder
from app.schemas.repository_package_map import (
    RepositoryPackageMapRequest,
    RepositoryPackageMapResponse,
    RepositoryPackageMapSummaryResponse,
    RepositoryPackageMarkerResponse,
)

router = APIRouter()


def serialize_repository_package_marker(marker: RepositoryPackageMarker) -> RepositoryPackageMarkerResponse:
    return RepositoryPackageMarkerResponse(
        path=marker.path,
        marker_name=marker.marker_name,
        ecosystem=marker.ecosystem,
        depth=marker.depth,
    )


def serialize_repository_package_map(package_map: RepositoryPackageMap) -> RepositoryPackageMapResponse:
    summary = RepositoryPackageMapSummaryBuilder().build(package_map)

    return RepositoryPackageMapResponse(
        repository_path=package_map.repository_path,
        markers=[serialize_repository_package_marker(marker) for marker in package_map.markers],
        marker_count=package_map.marker_count,
        ecosystem_count=package_map.ecosystem_count,
        ecosystems=package_map.ecosystems,
        root_markers=[serialize_repository_package_marker(marker) for marker in package_map.root_markers],
        summary=RepositoryPackageMapSummaryResponse(
            outcome=summary.outcome,
            message=summary.message,
            action_required=summary.action_required,
        ),
    )


@router.post(
    "/api/v1/repository-package-map",
    response_model=RepositoryPackageMapResponse,
    status_code=status.HTTP_200_OK,
)
def get_repository_package_map(data: RepositoryPackageMapRequest):
    try:
        package_map = RepositoryPackageMapBuilder().build(
            repository_path=data.repository_path,
            max_depth=data.max_depth,
        )
        return serialize_repository_package_map(package_map)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NotADirectoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
