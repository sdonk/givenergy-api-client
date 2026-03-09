"""Tests for the Account domain class (US1 and US6)."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from givenergy_api_client.account import AccountData, AccountDevice
from givenergy_api_client.client import GivenergyAPIClient
from givenergy_api_client.exceptions import AuthenticationError, NotFoundError
from givenergy_api_client.pagination import PaginatedResult

BASE = "https://api.givenergy.cloud/v1"

ACCOUNT_PAYLOAD = {
    "id": 1,
    "name": "johndoe",
    "first_name": "John",
    "surname": "Doe",
    "role": "OWNER",
    "email": "john@example.com",
    "address": "1 Solar Street",
    "postcode": "AB1 2CD",
    "country": "UNITED_KINGDOM",
    "telephone_number": "01234 567890",
    "timezone": "GMT",
    "standard_timezone": "Europe/London",
}

META_PAYLOAD = {"current_page": 1, "last_page": 1, "per_page": 15, "total": 1}


def _client() -> GivenergyAPIClient:
    return GivenergyAPIClient(api_key="test-key")


# ---------------------------------------------------------------------------
# US1 — Account basic operations
# ---------------------------------------------------------------------------


class TestAccountBasic:
    def test_get_returns_account_data(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/account", method="GET", json={"data": ACCOUNT_PAYLOAD})
        result = _client().account().get()
        assert isinstance(result, AccountData)
        assert result.email == "john@example.com"

    def test_get_by_id(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/account/42", method="GET", json={"data": ACCOUNT_PAYLOAD})
        result = _client().account().get_by_id(user_id="42")
        assert isinstance(result, AccountData)

    def test_search(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/account/search/johndoe", method="GET", json={"data": ACCOUNT_PAYLOAD})
        result = _client().account().search(username="johndoe")
        assert isinstance(result, AccountData)
        assert result.name == "johndoe"

    def test_get_devices_returns_paginated_result(self, httpx_mock: HTTPXMock) -> None:
        device = {
            "serial_number": "WF123",
            "type": "WIFI",
            "site_id": None,
            "inverter_serial": "CE123",
            "inverter_status": "NORMAL",
        }
        httpx_mock.add_response(
            method="GET",
            json={"data": [device], "meta": META_PAYLOAD},
        )
        result = _client().account().get_devices(username="johndoe")
        assert isinstance(result, PaginatedResult)
        assert len(result.data) == 1
        assert isinstance(result.data[0], AccountDevice)
        assert result.meta.total == 1

    def test_get_raises_authentication_error_on_401(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/account", method="GET", status_code=401, json={"message": "Unauthenticated"}
        )
        with pytest.raises(AuthenticationError):
            _client().account().get()

    def test_get_by_id_raises_not_found_on_404(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/account/999", method="GET", status_code=404, json={"message": "Not found"})
        with pytest.raises(NotFoundError):
            _client().account().get_by_id(user_id="999")

    async def test_aget_returns_account_data(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/account", method="GET", json={"data": ACCOUNT_PAYLOAD})
        result = await _client().account().aget()
        assert isinstance(result, AccountData)
        assert result.first_name == "John"


# ---------------------------------------------------------------------------
# US6 — Multi-account & SSO hierarchy
# ---------------------------------------------------------------------------


class TestAccountHierarchy:
    def test_list_children_returns_paginated_result(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            method="GET",
            json={"data": [ACCOUNT_PAYLOAD], "meta": META_PAYLOAD},
        )
        result = _client().account().list_children()
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.data[0], AccountData)

    def test_list_children_for_user(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            method="GET",
            json={"data": [ACCOUNT_PAYLOAD], "meta": META_PAYLOAD},
        )
        result = _client().account().list_children_for_user(user_id="5")
        assert isinstance(result, PaginatedResult)

    def test_get_sso_accounts(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/sso/me/accounts", method="GET", json={"data": [ACCOUNT_PAYLOAD]})
        result = _client().account().get_sso_accounts()
        assert isinstance(result, list)
        assert isinstance(result[0], AccountData)

    def test_list_children_raises_authentication_error_on_401(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(method="GET", status_code=401, json={"message": "Unauthenticated"})
        with pytest.raises(AuthenticationError):
            _client().account().list_children()

    async def test_alist_children(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            method="GET",
            json={"data": [ACCOUNT_PAYLOAD], "meta": META_PAYLOAD},
        )
        result = await _client().account().alist_children()
        assert isinstance(result, PaginatedResult)

    async def test_aget_by_id_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/account/42", method="GET", json={"data": ACCOUNT_PAYLOAD})
        result = await _client().account().aget_by_id(user_id="42")
        assert isinstance(result, AccountData)
        assert result.email == "john@example.com"

    async def test_asearch_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/account/search/johndoe", method="GET", json={"data": ACCOUNT_PAYLOAD})
        result = await _client().account().asearch(username="johndoe")
        assert isinstance(result, AccountData)
        assert result.name == "johndoe"

    async def test_aget_devices_async(self, httpx_mock: HTTPXMock) -> None:
        device = {
            "serial_number": "WF123",
            "type": "WIFI",
            "site_id": None,
            "inverter_serial": "CE123",
            "inverter_status": "NORMAL",
        }
        httpx_mock.add_response(method="GET", json={"data": [device], "meta": META_PAYLOAD})
        result = await _client().account().aget_devices(username="johndoe")
        assert isinstance(result, PaginatedResult)
        assert result.meta.total == 1

    async def test_alist_children_for_user_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(method="GET", json={"data": [ACCOUNT_PAYLOAD], "meta": META_PAYLOAD})
        result = await _client().account().alist_children_for_user(user_id="5")
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.data[0], AccountData)

    async def test_aget_sso_accounts_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/sso/me/accounts", method="GET", json={"data": [ACCOUNT_PAYLOAD]})
        result = await _client().account().aget_sso_accounts()
        assert isinstance(result, list)
        assert result[0].surname == "Doe"
