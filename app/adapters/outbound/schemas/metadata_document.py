from typing import Any

from bson import ObjectId

from app.domain.models.metadata import Metadata


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
        document = dict(mongo_doc)
        document["_id"] = str(document["_id"])
        return Metadata.model_validate(document)
