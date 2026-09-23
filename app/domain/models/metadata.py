from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class FieldSchema(BaseModel):
    field: str
    type: str
    description: Optional[str] = None
    nullable: bool


class Storage(BaseModel):
    format: str
    storage_path: str
    is_partitioned: bool


class Metadata(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        extra="forbid",
    )

    id: Optional[str] = Field(default=None, alias="_id")
    table_name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    storage: Storage
    current_version: int
    current_schema: list[FieldSchema]
    owner: str
    created_at: datetime
    updated_at: datetime
    data_classification: str


class MetadataUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    storage: Optional[Storage] = None
    current_version: Optional[int] = None
    current_schema: Optional[list[FieldSchema]] = None
    owner: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    data_classification: Optional[str] = None
