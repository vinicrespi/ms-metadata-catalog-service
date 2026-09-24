import pytest

from app.application.use_cases.validate_and_update_schema import ValidateAndUpdateSchema
from tests.mocks.schema_validation_payload import ADDITIONAL_SCHEMA, BASE_SCHEMA, NEW_SCHEMA, OLD_SCHEMA



def test_additive_schema_change_is_allowed() -> None:
    new_schema = BASE_SCHEMA + ADDITIONAL_SCHEMA
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
    errors = ValidateAndUpdateSchema._detect_breaking_changes(OLD_SCHEMA, NEW_SCHEMA)
    assert errors == ["field became non-nullable: name"]


def test_duplicate_fields_are_rejected() -> None:
    schema = BASE_SCHEMA + BASE_SCHEMA
    with pytest.raises(ValueError, match="duplicate field names"):
        ValidateAndUpdateSchema._validate_schema(schema)
