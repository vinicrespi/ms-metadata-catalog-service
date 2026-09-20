from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.use_cases.services import MetadataService
from app.domain.models import MetadataCreate, MetadataResponse
from app.infrastructure.database import get_metadata_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@router.post("/metadata", response_model=MetadataResponse, status_code=status.HTTP_201_CREATED, tags=["metadata"])
async def create_metadata(
    data: MetadataCreate, service: MetadataService = Depends(get_metadata_service)
) -> dict:
    return await service.create(data)

@router.get("/metadata", response_model=list[MetadataResponse], tags=["metadata"])
async def list_metadata(service: MetadataService = Depends(get_metadata_service)) -> list[dict[str, Any]]:
    return await service.get_all()

@router.get("/metadata/{metadata_id}", response_model=MetadataResponse, tags=["metadata"])
async def get_metadata(
    metadata_id: str, service: MetadataService = Depends(get_metadata_service)
) -> dict:
    metadata = await service.get_by_id(metadata_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata