from typing import Any, Optional

from bson import ObjectId
from pymongo import AsyncMongoClient

from app.application.ports.history_port import HistoryPort


class MongoHistoryAdapter(HistoryPort):
    def __init__(self, client: AsyncMongoClient, database_name: str) -> None:
        self._collection = client[database_name]["tab_schema_history"]

    @staticmethod
    def _object_id(value: str) -> Optional[ObjectId]:
        return ObjectId(value) if ObjectId.is_valid(value) else None

    @staticmethod
    def _to_response(document: dict[str, Any]) -> dict[str, Any]:
        response = document.copy()
        response["id"] = str(response.pop("_id"))
        return response

    async def create_version(
        self,
        metadata_id: str,
        table_name: str,
        version: int,
        changed_by: str,
        change_type: str,
        details: Any,
        changed_at: Any,
        schema_snapshot: list[dict[str, Any]],
        session: Any,
    ) -> None:
        await self._collection.insert_one(
            {
                "table_id": metadata_id,
                "table_name": table_name,
                "version": version,
                "changed_by": changed_by,
                "change_type": change_type,
                "details": details,
                "changed_at": changed_at,
                "schema_snapshot": schema_snapshot,
            },
            session=session,
        )

    async def get_by_metadata_id(self, metadata_id: str) -> list[dict[str, Any]]:
        documents = (
            await self._collection.find({"table_id": metadata_id})
            .sort("changed_at", -1)
            .to_list()
        )
        return [self._to_response(item) for item in documents]
