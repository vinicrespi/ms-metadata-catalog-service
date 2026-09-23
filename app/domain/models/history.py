from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class SchemaColumnChange(BaseModel):
    field: str
    type: str


class HistoryDetails(BaseModel):
    columns_added: list[SchemaColumnChange] = Field(default_factory=list)
    columns_removed: list[SchemaColumnChange] = Field(default_factory=list)
    columns_modified: list[dict[str, Any]] = Field(default_factory=list)


class History(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    id: Optional[str] = Field(default=None, alias="_id")
    table_id: str
    table_name: str
    version: int
    changed_at: datetime
    changed_by: str
    change_type: str
    details: HistoryDetails
    previous_schema_snapshot_id: str