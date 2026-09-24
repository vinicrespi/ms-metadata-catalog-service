from bson import ObjectId

from app.adapters.outbound.schemas.metadata_document import MetadataDocumentMapper
from tests.mocks.metadata_create_payload import METADATA_PAYLOAD


def test_metadata_document_mapper_round_trips_current_metadata_contract() -> None:
    metadata_id = ObjectId()
    mongo_document = {**METADATA_PAYLOAD, "_id": metadata_id}

    domain_model = MetadataDocumentMapper.to_domain(mongo_document)
    mapped_document = MetadataDocumentMapper.to_mongo(domain_model)

    assert domain_model.id == str(metadata_id)
    assert domain_model.dataset_id == METADATA_PAYLOAD["dataset_id"]
    assert domain_model.governance.data_classification == "confidencial_pii"
    assert domain_model.lineage.pipeline_job_id == "airflow_dag_pix_facts_daily_v2"
    assert mapped_document["_id"] == metadata_id
    assert mapped_document["storage"] == METADATA_PAYLOAD["storage"]
    assert mapped_document["governance"] == METADATA_PAYLOAD["governance"]
    assert mapped_document["current_schema"] == METADATA_PAYLOAD["current_schema"]
