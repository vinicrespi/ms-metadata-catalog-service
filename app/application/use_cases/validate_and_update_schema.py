from datetime import datetime, timezone
from typing import Any

from app.application.ports.metadata_port import MetadataPort
from app.domain.models.metadata import FieldSchema, MetadataUpdate


class ValidateAndUpdateSchema:
    def __init__(self, repository: MetadataPort) -> None:
        self._repository = repository

    async def execute(
        self,
        metadata_id: str,
        new_schema: list[dict[str, Any]],
        changed_by: str = "schema-service",
    ) -> dict[str, Any]:
        existing_metadata = await self._repository.get_by_id(metadata_id)
        if not existing_metadata:
            raise ValueError(f"Metadata with ID {metadata_id} not found.")

        validated_schema = self._validate_schema(new_schema)
        errors = self._detect_breaking_changes(
            existing_metadata.get("current_schema", []), validated_schema
        )
        if errors:
            raise ValueError("Breaking schema changes: " + "; ".join(errors))

        old_fields = {
            field["field"] for field in existing_metadata.get("current_schema", [])
        }
        new_fields = {field["field"] for field in validated_schema}
        details = {
            "columns_added": [
                field for field in validated_schema if field["field"] not in old_fields
            ],
            "columns_removed": [
                field
                for field in existing_metadata.get("current_schema", [])
                if field["field"] not in new_fields
            ],
            "columns_modified": [],
        }
        updated_metadata = await self._repository.update(
            metadata_id,
            MetadataUpdate(
                current_schema=[FieldSchema(**field) for field in validated_schema],
                current_version=existing_metadata.get("current_version", 0) + 1,
                updated_at=datetime.now(timezone.utc),
            ),
            changed_by=changed_by,
            change_type="SCHEMA_EVOLUTION",
            details=details,
        )
        if not updated_metadata:
            raise RuntimeError("Failed to update metadata.")

        return updated_metadata

    @staticmethod
    def _validate_schema(schema: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(schema, list):
            raise ValueError("Schema must be a list of fields.")

        validated = [FieldSchema.model_validate(field).model_dump() for field in schema]
        names = [field["field"] for field in validated]
        if len(names) != len(set(names)):
            raise ValueError("Schema cannot contain duplicate field names.")
        return validated

    @staticmethod
    def _detect_breaking_changes(
        old_schema: list[dict[str, Any]], new_schema: list[dict[str, Any]]
    ) -> list[str]:
        old_fields = {field["field"]: field for field in old_schema}
        new_fields = {field["field"]: field for field in new_schema}
        errors: list[str] = []

        for field in old_fields.keys() - new_fields.keys():
            errors.append(f"field removed: {field}")

        for field in old_fields.keys() & new_fields.keys():
            old = old_fields[field]
            new = new_fields[field]
            if old["type"] != new["type"]:
                errors.append(
                    f"field type changed: {field} ({old['type']} -> {new['type']})"
                )
            if old["nullable"] and not new["nullable"]:
                errors.append(f"field became non-nullable: {field}")

        return errors