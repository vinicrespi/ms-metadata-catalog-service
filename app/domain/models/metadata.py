from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class FieldSchema(BaseModel):
    field: str
    type: str
    nullable: bool
    description: Optional[str] = None
    is_primary_key: bool = False
    pii_type: Optional[str] = None


class Storage(BaseModel):
    provider: str
    format: str
    storage_path: str
    is_partitioned: bool
    partition_keys: Optional[list[str]] = None
    clustering_keys: Optional[list[str]] = None


class Governance(BaseModel):
    data_classification: str
    pci_dss_scope: bool
    lgpd_sensitive_data: bool
    data_retention_days: int
    encryption: str


class Lineage(BaseModel):
    upstream_sources: Optional[list[str]] = None
    pipeline_job_id: Optional[str] = None


class Metadata(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        extra="forbid",
    )

    id: Optional[str] = Field(default=None, alias="_id")
    dataset_id: str
    table_name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    owner: str
    storage: Storage
    governance: Governance
    current_version: int
    current_schema: list[FieldSchema]
    lineage: Optional[Lineage] = None
    created_at: datetime
    updated_at: datetime


class MetadataUpdate(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        extra="forbid",
    )

    dataset_id: Optional[str] = None
    table_name: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    owner: Optional[str] = None
    storage: Optional[Storage] = None
    governance: Optional[Governance] = None
    current_version: Optional[int] = None
    current_schema: Optional[list[FieldSchema]] = None
    lineage: Optional[Lineage] = None
    updated_at: Optional[datetime] = None