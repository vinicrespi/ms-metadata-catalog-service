METADATA_PAYLOAD = {

    "dataset_id": "fintech_core.fact_transacoes_pix_v1",
    "table_name": "fact_transacoes_pix",
    "description": "Tabela fato incremental contendo todas as transações PIX liquidadas e com falha.",
    "domain": "Payment Processing",
    "owner": "squad-payments-data",
    "storage": {
        "provider": "aws_s3",
        "format": "iceberg",
        "storage_path": "s3://prod-fintech-data-lakehouse/payments/fact_transacoes_pix/",
        "is_partitioned": True,
        "partition_keys": ["data_transacao", "status_transacao"],
        "clustering_keys": ["id_conta_origem"],
    },
    "governance": {
        "data_classification": "confidencial_pii",
        "pci_dss_scope": False,
        "lgpd_sensitive_data": True,
        "data_retention_days": 1825,
        "encryption": "KMS_CUSTOMER_MANAGED_KEY",
    },
    "current_version": 4,
    "current_schema": [
        {
            "field": "id_transacao_end_to_end",
            "type": "STRING",
            "nullable": False,
            "description": "ID EndToEnd do BACEN (Identificador único da transação PIX).",
            "is_primary_key": True,
            "pii_type": None
        },
        {
            "field": "dt_hr_transacao",
            "type": "TIMESTAMP",
            "nullable": False,
            "description": "Carimbo de data/hora UTC do processamento da transação.",
            "is_primary_key": False,
            "pii_type": None
        },
        {
            "field": "id_conta_origem",
            "type": "STRING",
            "nullable": False,
            "description": "UUID da conta do pagador.",
            "is_primary_key": False,
            "pii_type": "ACCOUNT_ID"
        },
        {
            "field": "cpf_cnpj_destino",
            "type": "STRING",
            "nullable": False,
            "description": "Documento do recebedor (MASCARADO em ambientes não-produtivos).",
            "is_primary_key": False,
            "pii_type": "CPF_CNPJ"
        },
        {
            "field": "valor_transacao",
            "type": "DECIMAL(18,2)",
            "nullable": False,
            "description": "Valor nominal da transação em BRL com 2 casas decimais.",
            "is_primary_key": False,
            "pii_type": None
        },
        {
            "field": "status_transacao",
            "type": "STRING",
            "nullable": False,
            "description": "Estado final: LIQUIDADO, REJEITADO, CANCELADO, EM_ANALISE_FRAUDE.",
            "is_primary_key": False,
            "pii_type": None
        }
    ],
    "lineage": {
        "upstream_sources": [
            "kafka://prod-cluster/topics/pix-settlement-events",
            "s3://raw-landzone/bacen/pix_responses/"
        ],
        "pipeline_job_id": "airflow_dag_pix_facts_daily_v2"
    },
    "created_at": "2024-03-15T08:00:00Z",
    "updated_at": "2026-09-23T09:00:00Z"
}