"""Tests for the exceptions module and raise_for_status helper."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from givenergy_api_client.client import GivenergyAPIClient
from givenergy_api_client.exceptions import (
    APIValidationError,
    AuthenticationError,
    GivEnergyAPIError,
    NotFoundError,
    ServerError,
)

BASE = "https://api.givenergy.cloud/v1"


def _client() -> GivenergyAPIClient:
    return GivenergyAPIClient(api_key="test-key")


class TestRaiseForStatus:
    def test_server_error_raised_on_500(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/account", method="GET", status_code=500, json={"message": "Internal server error"}
        )
        with pytest.raises(ServerError) as exc_info:
            _client().account().get()
        assert exc_info.value.status_code == 500

    def test_server_error_raised_on_503(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/account", method="GET", status_code=503, json={"message": "Service unavailable"}
        )
        with pytest.raises(ServerError) as exc_info:
            _client().account().get()
        assert exc_info.value.status_code == 503

    def test_generic_error_raised_on_unexpected_status(self, httpx_mock: HTTPXMock) -> None:
        # 400 is not mapped to a specific typed exception
        httpx_mock.add_response(url=f"{BASE}/account", method="GET", status_code=400, json={"message": "Bad request"})
        with pytest.raises(GivEnergyAPIError, match="HTTP 400"):
            _client().account().get()

    def test_fallback_to_text_when_json_parse_fails(self, httpx_mock: HTTPXMock) -> None:
        # Response body is not valid JSON — raise_for_status must fall back to response.text
        httpx_mock.add_response(url=f"{BASE}/account", method="GET", status_code=401, content=b"Unauthenticated")
        with pytest.raises(AuthenticationError, match="Unauthenticated"):
            _client().account().get()

    def test_server_error_stores_status_code(self) -> None:
        err = ServerError("boom", status_code=502)
        assert err.status_code == 502
        assert str(err) == "boom"

    def test_all_typed_exceptions_are_subclasses_of_base(self) -> None:
        assert issubclass(AuthenticationError, GivEnergyAPIError)
        assert issubclass(NotFoundError, GivEnergyAPIError)
        assert issubclass(APIValidationError, GivEnergyAPIError)
        assert issubclass(ServerError, GivEnergyAPIError)
