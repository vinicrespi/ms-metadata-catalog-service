import pytest

from app.application.use_cases.validate_and_update_schema import ValidateAndUpdateSchema


BASE_SCHEMA = [
    {"field": "id", "type": "INT", "nullable": False, "description": None},
]


def test_additive_schema_change_is_allowed() -> None:
    new_schema = BASE_SCHEMA + [
        {"field": "source", "type": "STRING", "nullable": True, "description": None}
    ]
    assert ValidateAndUpdateSchema._detect_breaking_changes(BASE_SCHEMA, new_schema) == []


@pytest.mark.parametrize(
    "new_schema, expected_message",
    [
        ([], "field removed: id"),
        (
            [{"field": "id", "type": "STRING", "nullable": False, "description": None}],
            "field type changed",
        ),
        (
            [{"field": "id", "type": "INT", "nullable": True, "description": None}],
            "",
        ),
    ],
)
def test_breaking_schema_changes(new_schema, expected_message: str) -> None:
    errors = ValidateAndUpdateSchema._detect_breaking_changes(BASE_SCHEMA, new_schema)
    if expected_message:
        assert any(expected_message in error for error in errors)
    else:
        assert errors == []


def test_non_nullable_transition_is_breaking() -> None:
    old_schema = [{"field": "name", "type": "STRING", "nullable": True}]
    new_schema = [{"field": "name", "type": "STRING", "nullable": False}]
    errors = ValidateAndUpdateSchema._detect_breaking_changes(old_schema, new_schema)
    assert errors == ["field became non-nullable: name"]


def test_duplicate_fields_are_rejected() -> None:
    schema = BASE_SCHEMA + BASE_SCHEMA
    with pytest.raises(ValueError, match="duplicate field names"):
        ValidateAndUpdateSchema._validate_schema(schema)
