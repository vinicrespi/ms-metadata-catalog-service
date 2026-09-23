from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.application.use_cases.auth_service import AuthService
from app.application.use_cases.history_service import HistoryService
from app.application.use_cases.services import MetadataService
from app.application.use_cases.validate_and_update_schema import ValidateAndUpdateSchema
from app.domain.models.metadata import Metadata, MetadataUpdate
from app.domain.models.security import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.infrastructure.dependencies import (
    get_auth_service,
    get_history_service,
    get_metadata_service,
    get_validate_and_update_schema,
    require_authenticated_user,
)


router = APIRouter()


@router.post("/auth/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
async def create_user(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return await service.create_user(data)


@router.post("/auth/token", response_model=TokenResponse, tags=["auth"])
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return await service.authenticate(data)


@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/metadata",
    response_model=Metadata,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    tags=["metadata"],
)
async def create_metadata(
    data: Metadata,
    service: MetadataService = Depends(get_metadata_service),
    change_type: str = Query(default="INITIAL_CREATION"),
    changed_by: str = Header(default="api"),
    details: str = Query(default=""),
    _: dict[str, Any] = Depends(require_authenticated_user),
) -> dict[str, Any]:
    return await service.create(data, change_type, changed_by, details)


@router.get(
    "/metadata",
    response_model=list[Metadata],
    response_model_by_alias=False,
    tags=["metadata"],
)
async def get_all_metadata(
    service: MetadataService = Depends(get_metadata_service),
    _: dict[str, Any] = Depends(require_authenticated_user),
) -> list[dict[str, Any]]:
    return await service.get_all()


@router.get(
    "/metadata/{metadata_id}/histories",
    response_model=list[dict[str, Any]],
    tags=["metadata"],
)
async def get_metadata_histories(
    metadata_id: str,
    service: HistoryService = Depends(get_history_service),
    _: dict[str, Any] = Depends(require_authenticated_user),
) -> list[dict[str, Any]]:
    return await service.get_by_metadata_id(metadata_id)


@router.get(
    "/metadata/{metadata_id}",
    response_model=Metadata,
    response_model_by_alias=False,
    tags=["metadata"],
)
async def get_metadata(
    metadata_id: str,
    service: MetadataService = Depends(get_metadata_service),
    _: dict[str, Any] = Depends(require_authenticated_user),
) -> dict[str, Any]:
    metadata = await service.get_by_id(metadata_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata


@router.put(
    "/metadata/{metadata_id}",
    response_model=Metadata,
    response_model_by_alias=False,
    tags=["metadata"],
)
async def update_metadata(
    metadata_id: str,
    data: MetadataUpdate,
    service: MetadataService = Depends(get_metadata_service),
    schema_updater: ValidateAndUpdateSchema = Depends(get_validate_and_update_schema),
    changed_by: str = Header(default="api"),
    change_type: str = Query(default="METADATA_UPDATE"),
    details: str = Query(default=""),
    _: dict[str, Any] = Depends(require_authenticated_user),
) -> dict[str, Any]:
    if data.current_schema is not None:
        try:
            metadata = await schema_updater.execute(
                metadata_id,
                [field.model_dump() for field in data.current_schema],
                changed_by,
            )
        except ValueError as exc:
            if "not found" in str(exc).lower():
                raise HTTPException(status_code=404, detail="Metadata not found") from exc
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        metadata = await service.update(
            metadata_id, data, changed_by, change_type, details
        )
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata


@router.delete(
    "/metadata/{metadata_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["metadata"],
)
async def delete_metadata(
    metadata_id: str,
    service: MetadataService = Depends(get_metadata_service),
    _: dict[str, Any] = Depends(require_authenticated_user),
) -> None:
    if not await service.delete(metadata_id):
        raise HTTPException(status_code=404, detail="Metadata not found")
