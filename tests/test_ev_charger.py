"""Tests for the EVCharger domain class (US3)."""

from __future__ import annotations

import datetime as dt

import pytest
from pytest_httpx import HTTPXMock

from givenergy_api_client.client import GivenergyAPIClient
from givenergy_api_client.ev_charger import (
    ChargingSession,
    EVChargerCommandResult,
    EVChargerCommandState,
    EVChargerData,
    EVChargerMeterReading,
)
from givenergy_api_client.exceptions import APIValidationError, NotFoundError
from givenergy_api_client.pagination import PaginatedResult

BASE = "https://api.givenergy.cloud/v1"
UUID = "uuid-1234-abcd"
UTC = dt.UTC

CHARGER_PAYLOAD = {
    "uuid": UUID,
    "serial_number": "EV123",
    "type": "AC",
    "alias": "Garage Charger",
    "online": True,
    "status": "Available",
}

META = {"current_page": 1, "last_page": 1, "per_page": 15, "total": 1}


def _client() -> GivenergyAPIClient:
    return GivenergyAPIClient(api_key="test-key")


class TestEVCharger:
    def test_list_ev_chargers_returns_paginated_result(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(method="GET", json={"data": [CHARGER_PAYLOAD], "meta": META})
        result = _client().list_ev_chargers()
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.data[0], EVChargerData)
        assert result.data[0].online is True

    def test_get_returns_charger_data(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/ev-charger/{UUID}", method="GET", json={"data": CHARGER_PAYLOAD})
        result = _client().ev_charger(UUID).get()
        assert isinstance(result, EVChargerData)
        assert result.alias == "Garage Charger"

    def test_get_meter_data_returns_paginated_readings(self, httpx_mock: HTTPXMock) -> None:
        reading = {
            "meter_id": "m1",
            "timestamp": "2026-03-06T12:00:00+00:00",
            "measurements": [{"measurand": "Energy.Active.Import.Register", "value": 100.5, "unit": "Wh"}],
        }
        httpx_mock.add_response(method="GET", json={"data": [reading], "meta": META})
        start = dt.datetime(2026, 3, 6, tzinfo=UTC)
        end = dt.datetime(2026, 3, 7, tzinfo=UTC)
        result = (
            _client()
            .ev_charger(UUID)
            .get_meter_data(
                start_time=start, end_time=end, measurands=["Energy.Active.Import.Register"], meter_ids=["m1"]
            )
        )
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.data[0], EVChargerMeterReading)

    def test_execute_command_returns_result(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/{UUID}/commands/StartCharging",
            method="POST",
            json={"code": 200, "success": True, "message": "Command accepted"},
        )
        result = _client().ev_charger(UUID).execute_command(command_id="StartCharging", payload={"connector_id": 1})
        assert isinstance(result, EVChargerCommandResult)
        assert result.success is True

    def test_list_sessions_returns_paginated(self, httpx_mock: HTTPXMock) -> None:
        session = {
            "started_by": "user",
            "meter_start": 1000.0,
            "started_at": "2026-03-06T10:00:00+00:00",
            "stopped_by": "user",
            "meter_stop": 1020.0,
            "stopped_at": "2026-03-06T11:00:00+00:00",
        }
        httpx_mock.add_response(method="GET", json={"data": [session], "meta": META})
        result = _client().ev_charger(UUID).list_sessions()
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.data[0], ChargingSession)
        assert result.data[0].meter_stop == 1020.0

    def test_get_raises_not_found_on_404(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/bad-uuid", method="GET", status_code=404, json={"message": "Not found"}
        )
        with pytest.raises(NotFoundError):
            _client().ev_charger("bad-uuid").get()

    def test_execute_command_raises_api_validation_error_on_422(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/{UUID}/commands/BadCommand",
            method="POST",
            status_code=422,
            json={"message": "Unsupported command"},
        )
        with pytest.raises(APIValidationError, match="Unsupported command"):
            _client().ev_charger(UUID).execute_command(command_id="BadCommand", payload={})

    def test_list_commands_returns_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/{UUID}/commands",
            method="GET",
            json={"data": ["StartCharging", "StopCharging", "SetMaxCurrent"]},
        )
        result = _client().ev_charger(UUID).list_commands()
        assert result == ["StartCharging", "StopCharging", "SetMaxCurrent"]

    def test_get_command_returns_state(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/{UUID}/commands/SetMaxCurrent",
            method="GET",
            json={"data": {"current_limit": 16, "enabled": True}},
        )
        result = _client().ev_charger(UUID).get_command(command_id="SetMaxCurrent")
        assert isinstance(result, EVChargerCommandState)
        assert result.extra_fields["current_limit"] == 16
        assert result.extra_fields["enabled"] is True

    def test_list_sessions_with_time_filters(self, httpx_mock: HTTPXMock) -> None:
        session = {
            "started_by": "user",
            "meter_start": 500.0,
            "started_at": "2026-03-01T08:00:00+00:00",
            "stopped_by": "user",
            "meter_stop": 520.0,
            "stopped_at": "2026-03-01T09:00:00+00:00",
        }
        httpx_mock.add_response(method="GET", json={"data": [session], "meta": META})
        start = dt.datetime(2026, 3, 1, tzinfo=UTC)
        end = dt.datetime(2026, 3, 2, tzinfo=UTC)
        result = _client().ev_charger(UUID).list_sessions(start_time=start, end_time=end)
        assert isinstance(result, PaginatedResult)
        assert result.data[0].meter_start == 500.0

    async def test_aexecute_command_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/{UUID}/commands/StopCharging",
            method="POST",
            json={"code": 200, "success": True, "message": "Stopped"},
        )
        result = await _client().ev_charger(UUID).aexecute_command(command_id="StopCharging", payload={})
        assert isinstance(result, EVChargerCommandResult)
        assert result.success is True

    async def test_aget_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/ev-charger/{UUID}", method="GET", json={"data": CHARGER_PAYLOAD})
        result = await _client().ev_charger(UUID).aget()
        assert isinstance(result, EVChargerData)
        assert result.status == "Available"

    async def test_aget_meter_data_async(self, httpx_mock: HTTPXMock) -> None:
        reading = {
            "meter_id": "m1",
            "timestamp": "2026-03-06T12:00:00+00:00",
            "measurements": [{"measurand": "Energy.Active.Import.Register", "value": 50.0, "unit": "Wh"}],
        }
        httpx_mock.add_response(method="GET", json={"data": [reading], "meta": META})
        start = dt.datetime(2026, 3, 6, tzinfo=UTC)
        end = dt.datetime(2026, 3, 7, tzinfo=UTC)
        result = await (
            _client()
            .ev_charger(UUID)
            .aget_meter_data(
                start_time=start, end_time=end, measurands=["Energy.Active.Import.Register"], meter_ids=["m1"]
            )
        )
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.data[0], EVChargerMeterReading)

    async def test_alist_commands_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/{UUID}/commands",
            method="GET",
            json={"data": ["StartCharging"]},
        )
        result = await _client().ev_charger(UUID).alist_commands()
        assert result == ["StartCharging"]

    async def test_aget_command_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ev-charger/{UUID}/commands/SetMaxCurrent",
            method="GET",
            json={"data": {"max_current": 32}},
        )
        result = await _client().ev_charger(UUID).aget_command(command_id="SetMaxCurrent")
        assert isinstance(result, EVChargerCommandState)
        assert result.extra_fields["max_current"] == 32

    async def test_alist_sessions_async(self, httpx_mock: HTTPXMock) -> None:
        session = {
            "started_by": "auto",
            "meter_start": 200.0,
            "started_at": "2026-03-05T07:00:00+00:00",
            "stopped_by": "auto",
            "meter_stop": 215.0,
            "stopped_at": "2026-03-05T08:00:00+00:00",
        }
        httpx_mock.add_response(method="GET", json={"data": [session], "meta": META})
        result = await _client().ev_charger(UUID).alist_sessions()
        assert isinstance(result, PaginatedResult)
        assert result.data[0].meter_stop == 215.0

    async def test_alist_sessions_async_with_time_filters(self, httpx_mock: HTTPXMock) -> None:
        session = {
            "started_by": "auto",
            "meter_start": 300.0,
            "started_at": "2026-03-06T07:00:00+00:00",
            "stopped_by": "auto",
            "meter_stop": 310.0,
            "stopped_at": "2026-03-06T08:00:00+00:00",
        }
        httpx_mock.add_response(method="GET", json={"data": [session], "meta": META})
        start = dt.datetime(2026, 3, 6, tzinfo=UTC)
        end = dt.datetime(2026, 3, 7, tzinfo=UTC)
        result = await _client().ev_charger(UUID).alist_sessions(start_time=start, end_time=end)
        assert isinstance(result, PaginatedResult)
        assert result.data[0].meter_start == 300.0

    def test_ev_charger_command_state_non_dict_passthrough(self) -> None:
        # When the model validator receives a non-dict, it returns data as-is.
        # This exercises the `return data` branch (line 94).
        existing = EVChargerCommandState.model_validate({"speed": 10})
        re_validated = EVChargerCommandState.model_validate(existing)
        assert re_validated.extra_fields == {"speed": 10}
