from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.services import MetadataService
from app.domain.models import MetadataCreate, MetadataResponse
from app.infrastructure.database import get_metadata_service

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/metadata", response_model=MetadataResponse, status_code=status.HTTP_201_CREATED, tags=["metadata"])
async def create_metadata(
    data: MetadataCreate, service: MetadataService = Depends(get_metadata_service)
) -> dict:
    return await service.create(data)