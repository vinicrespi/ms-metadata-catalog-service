from typing import Any, Protocol


class HistoryPort(Protocol):
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
        ...

    async def get_by_metadata_id(self, metadata_id: str) -> list[dict[str, Any]]:
        ...
