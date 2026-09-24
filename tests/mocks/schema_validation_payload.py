BASE_SCHEMA = [
    {"field": "id", "type": "INT", "nullable": False, "description": None, "is_primary_key": True, "pii_type": None},
]
ADDITIONAL_SCHEMA = [
    {"field": "source", "type": "STRING", "nullable": True, "description": None, "is_primary_key": False, "pii_type": None},
]
OLD_SCHEMA = [{"field": "name", "type": "STRING", "nullable": True, "description": None, "is_primary_key": False, "pii_type": None}]
NEW_SCHEMA = [{"field": "name", "type": "STRING", "nullable": False, "description": None, "is_primary_key": False, "pii_type": None}]