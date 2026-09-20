from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.services import MetadataService
from app.domain.models import MetadataCreate, MetadataResponse, MetadataUpdate
from app.infrastructure.dependencies import get_metadata_service

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@router.post("/metadata", response_model=MetadataResponse, status_code=status.HTTP_201_CREATED, tags=["metadata"])
async def create_metadata(
    data: MetadataCreate, service: MetadataService = Depends(get_metadata_service)
) -> dict:
    return await service.create(data)

@router.get("/metadata", response_model=list[MetadataResponse], tags=["metadata"])
async def get_all_metadata(service: MetadataService = Depends(get_metadata_service)) -> list[dict[str, Any]]:
    return await service.get_all()

@router.get("/metadata/{metadata_id}", response_model=MetadataResponse, tags=["metadata"])
async def get_by_id_metadata(
    metadata_id: str, service: MetadataService = Depends(get_metadata_service)
) -> dict:
    metadata = await service.get_by_id(metadata_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata

@router.put("/metadata/{metadata_id}", response_model=MetadataResponse, tags=["metadata"])
async def update_metadata(
    metadata_id: str,
    data: MetadataUpdate,
    service: MetadataService = Depends(get_metadata_service),
) -> dict:
    metadata = await service.update(metadata_id, data)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata

@router.delete("/metadata/{metadata_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["metadata"])
async def delete_metadata(
    metadata_id: str, service: MetadataService = Depends(get_metadata_service)
) -> None:
    if not await service.delete(metadata_id):
        raise HTTPException(status_code=404, detail="Metadata not found")