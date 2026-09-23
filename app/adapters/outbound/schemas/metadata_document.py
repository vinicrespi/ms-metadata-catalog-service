from typing import Any

from bson import ObjectId

from app.domain.models.metadata import FieldSchema, Metadata


class MetadataDocumentMapper:
    """Translate the Metadata domain model to and from MongoDB documents."""

    @staticmethod
    def to_mongo(domain_model: Metadata) -> dict[str, Any]:
        document = domain_model.model_dump(exclude={"id"}, by_alias=False)

        if domain_model.id:
            document["_id"] = ObjectId(domain_model.id)

        return document

    @staticmethod
    def to_domain(mongo_doc: dict[str, Any]) -> Metadata:
        return Metadata(
            id=str(mongo_doc["_id"]),
            table_name=mongo_doc["table_name"],
            description=mongo_doc.get("description"),
            domain=mongo_doc.get("domain"),
            storage=mongo_doc["storage"],
            current_version=mongo_doc["current_version"],
            current_schema=[
                FieldSchema(**field) for field in mongo_doc["current_schema"]
            ],
            owner=mongo_doc["owner"],
            created_at=mongo_doc["created_at"],
            updated_at=mongo_doc["updated_at"],
            data_classification=mongo_doc["data_classification"],
        )
