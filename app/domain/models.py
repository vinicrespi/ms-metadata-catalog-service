from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class MetadataCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    owner: str = Field(min_length=1, max_length=120)
    source_system: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)
    version: Optional[str] = Field(default=None, min_length=1, max_length=20)

class MetadataUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    owner: Optional[str] = Field(default=None, min_length=1, max_length=120)
    source_system: Optional[str] = Field(default=None, min_length=1, max_length=120)
    payload: Optional[dict[str, Any]] = Field(default=None)
    version: Optional[str] = Field(default=None, min_length=1, max_length=20)

class MetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    owner: str
    source_system: str
    payload: dict[str, Any]
    version: Optional[str]
    created_at: datetime
    updated_at: datetime