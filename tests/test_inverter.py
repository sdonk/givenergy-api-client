"""Tests for the Inverter domain class (US2)."""

from __future__ import annotations

import datetime as dt

import pytest
from pytest_httpx import HTTPXMock

from givenergy_api_client.client import GivenergyAPIClient
from givenergy_api_client.energy_flow import EnergyDataFlowType
from givenergy_api_client.exceptions import NotFoundError
from givenergy_api_client.inverter import DebugCommandResult, EnergyFlowData, InverterHealthCheck

BASE = "https://api.givenergy.cloud/v1"
SN = "CE2345G123"
UTC = dt.UTC

HEALTH_PAYLOAD = [
    {"name": "battery_voltage", "value": 51.2, "status": "OK", "unit": "V"},
    {"name": "grid_frequency", "value": "50.0", "status": "OK", "unit": "Hz"},
]

FLOW_PAYLOAD = [
    {
        "type": 0,
        "data": [
            {"timestamp": "2026-03-01T00:00:00+00:00", "value": 1.5},
            {"timestamp": "2026-03-01T00:30:00+00:00", "value": 2.0},
        ],
    }
]


def _client() -> GivenergyAPIClient:
    return GivenergyAPIClient(api_key="test-key")


class TestInverter:
    def test_get_health_returns_list_of_checks(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/inverter/{SN}/health", method="GET", json={"data": HEALTH_PAYLOAD})
        result = _client().inverter(SN).get_health()
        assert isinstance(result, list)
        assert all(isinstance(h, InverterHealthCheck) for h in result)
        assert result[0].name == "battery_voltage"
        assert result[0].status == "OK"

    def test_get_energy_flows_returns_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/inverter/{SN}/energy-flows", method="POST", json={"data": FLOW_PAYLOAD})
        start = dt.datetime(2026, 3, 1, tzinfo=UTC)
        end = dt.datetime(2026, 3, 7, tzinfo=UTC)
        result = _client().inverter(SN).get_energy_flows(start_time=start, end_time=end)
        assert isinstance(result, list)
        assert all(isinstance(f, EnergyFlowData) for f in result)
        assert result[0].type == EnergyDataFlowType.PV_TO_HOME
        assert len(result[0].data) == 2

    def test_get_energy_flows_raises_on_naive_start(self) -> None:
        naive = dt.datetime(2026, 3, 1)
        aware = dt.datetime(2026, 3, 7, tzinfo=UTC)
        with pytest.raises(ValueError, match="timezone-aware"):
            _client().inverter(SN).get_energy_flows(start_time=naive, end_time=aware)

    def test_get_energy_flows_raises_on_naive_end(self) -> None:
        aware = dt.datetime(2026, 3, 1, tzinfo=UTC)
        naive = dt.datetime(2026, 3, 7)
        with pytest.raises(ValueError, match="timezone-aware"):
            _client().inverter(SN).get_energy_flows(start_time=aware, end_time=naive)

    def test_get_energy_flows_raises_when_end_before_start(self) -> None:
        start = dt.datetime(2026, 3, 7, tzinfo=UTC)
        end = dt.datetime(2026, 3, 1, tzinfo=UTC)
        with pytest.raises(ValueError, match="after"):
            _client().inverter(SN).get_energy_flows(start_time=start, end_time=end)

    def test_get_health_raises_not_found_on_404(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/UNKNOWN/health", method="GET", status_code=404, json={"message": "Not found"}
        )
        with pytest.raises(NotFoundError):
            _client().inverter("UNKNOWN").get_health()

    async def test_aget_health_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/inverter/{SN}/health", method="GET", json={"data": HEALTH_PAYLOAD})
        result = await _client().inverter(SN).aget_health()
        assert isinstance(result, list)
        assert result[1].unit == "Hz"

    def test_get_energy_flows_default_grouping(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/inverter/{SN}/energy-flows", method="POST", json={"data": FLOW_PAYLOAD})
        start = dt.datetime(2026, 3, 1, tzinfo=UTC)
        end = dt.datetime(2026, 3, 2, tzinfo=UTC)
        # Should not raise — default grouping is HALF_HOURLY
        result = _client().inverter(SN).get_energy_flows(start_time=start, end_time=end)
        assert result[0].type == EnergyDataFlowType.PV_TO_HOME

    def test_send_debug_command(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/{SN}/debug/transparent/send",
            method="POST",
            json={"success": True, "code": 0},
        )
        result = _client().inverter(SN).send_debug_command(hex_command="0102")
        assert isinstance(result, DebugCommandResult)
        assert result.success is True

    async def test_aget_energy_flows_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/inverter/{SN}/energy-flows", method="POST", json={"data": FLOW_PAYLOAD})
        start = dt.datetime(2026, 3, 1, tzinfo=UTC)
        end = dt.datetime(2026, 3, 7, tzinfo=UTC)
        result = await _client().inverter(SN).aget_energy_flows(start_time=start, end_time=end)
        assert isinstance(result, list)
        assert all(isinstance(f, EnergyFlowData) for f in result)

    async def test_asend_debug_command_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/{SN}/debug/transparent/send",
            method="POST",
            json={"success": True, "code": 0},
        )
        result = await _client().inverter(SN).asend_debug_command(hex_command="AABB")
        assert isinstance(result, DebugCommandResult)
        assert result.code == 0
