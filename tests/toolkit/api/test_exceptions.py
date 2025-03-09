"""Module defining unit tests for the exceptions."""

from toolkit.api.exceptions import InternalServerError


def test_to_jsonable_dict_success() -> None:
    """Verify `to_jsonable_dict` method of `APIException` using its subclass."""
    internal_server_error = InternalServerError(
        "test error", field="test field", reason="test reason"
    )

    actual_error_data = internal_server_error.to_jsonable_dict()
    expected_error_data = {
        "status": internal_server_error.status.value,
        "message": internal_server_error.message,
        "documentationLink": internal_server_error.documentation_link.value,
        "details": {
            "field": internal_server_error.field,
            "reason": internal_server_error.reason,
        },
    }
    assert actual_error_data == expected_error_data
