from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from pymongo import AsyncMongoClient, ReturnDocument

from app.application.ports.history_port import HistoryPort
from app.application.ports.metadata_port import MetadataPort
from app.domain.models.metadata import Metadata, MetadataUpdate
from app.adapters.outbound.schemas.metadata_document import MetadataDocumentMapper


class MongoMetadataAdapter(MetadataPort):

    def __init__(
        self,
        client: AsyncMongoClient,
        database_name: str,
        history_repository: HistoryPort,
    ) -> None:
        self._client = client
        self._database = client[database_name]
        self._versioned_metadata_collection = self._database["tab_metadata"]
        self._history_repository = history_repository

    @staticmethod
    def _object_id(value: str) -> Optional[ObjectId]:
        return ObjectId(value) if ObjectId.is_valid(value) else None

    async def create(
        self,
        metadata: Metadata,
        change_type: str,
        changed_by: str,
        details: Any,
    ) -> dict[str, Any]:
        """Upsert the metadata and append its schema change atomically."""
        mongo_document = MetadataDocumentMapper.to_mongo(metadata)
        mongo_document.pop("_id", None)

        async with self._client.start_session() as session:
            async with await session.start_transaction():
                await self._versioned_metadata_collection.update_one(
                    {"table_name": metadata.table_name},
                    {"$set": mongo_document},
                    upsert=True,
                    session=session,
                )
                metadata_document = await self._versioned_metadata_collection.find_one(
                    {"table_name": metadata.table_name}, session=session
                )
                if metadata_document is None:
                    raise RuntimeError("Metadata was not saved")
                await self._history_repository.create_version(
                    metadata_id=str(metadata_document["_id"]),
                    table_name=metadata.table_name,
                    version=metadata.current_version,
                    changed_by=changed_by,
                    change_type=change_type,
                    details=details,
                    changed_at=metadata.updated_at,
                    schema_snapshot=mongo_document["current_schema"],
                    session=session,
                )

                document = metadata_document

        if document is None:
            raise RuntimeError("Metadata was not saved")
        return MetadataDocumentMapper.to_domain(document).model_dump()

    async def get_all(self) -> list[dict[str, Any]]:
        documents = await self._versioned_metadata_collection.find().sort(
            "table_name", 1
        ).to_list()
        return [MetadataDocumentMapper.to_domain(item).model_dump() for item in documents]

    async def get_by_id(self, metadata_id: str) -> Optional[dict[str, Any]]:
        object_id = self._object_id(metadata_id)
        if object_id is None:
            return None
        document = await self._versioned_metadata_collection.find_one(
            {"_id": object_id}
        )
        return MetadataDocumentMapper.to_domain(document).model_dump() if document else None

    async def update(
        self,
        metadata_id: str,
        data: MetadataUpdate,
        changed_by: str = "api",
        change_type: str = "METADATA_UPDATE",
        details: Any = None,
    ) -> Optional[dict[str, Any]]:
        object_id = self._object_id(metadata_id)
        if object_id is None:
            return None
        values = data.model_dump(exclude_unset=True, exclude_none=True)
        if not values:
            return await self.get_by_id(metadata_id)

        async with self._client.start_session() as session:
            async with await session.start_transaction():
                current = await self._versioned_metadata_collection.find_one(
                    {"_id": object_id}, session=session
                )
                if current is None:
                    return None

                values["updated_at"] = datetime.now(timezone.utc)
                document = await self._versioned_metadata_collection.find_one_and_update(
                    {"_id": object_id},
                    {"$set": values},
                    return_document=ReturnDocument.AFTER,
                    session=session,
                )
                if document is None:
                    return None

                await self._history_repository.create_version(
                    metadata_id=metadata_id,
                    table_name=document["table_name"],
                    version=document["current_version"],
                    changed_by=changed_by,
                    change_type=change_type,
                    details=details or {"updated_fields": list(values)},
                    changed_at=document["updated_at"],
                    schema_snapshot=document["current_schema"],
                    session=session,
                )
        return MetadataDocumentMapper.to_domain(document).model_dump() if document else None

    async def delete(self, metadata_id: str) -> bool:
        object_id = self._object_id(metadata_id)
        if object_id is None:
            return False
        result = await self._versioned_metadata_collection.delete_one(
            {"_id": object_id}
        )
        return result.deleted_count == 1
    
