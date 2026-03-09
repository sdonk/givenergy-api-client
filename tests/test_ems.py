"""Tests for the EMS domain class (US5)."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from givenergy_api_client.client import GivenergyAPIClient
from givenergy_api_client.ems import EMSSnapshot
from givenergy_api_client.exceptions import NotFoundError

BASE = "https://api.givenergy.cloud/v1"
SN = "CE2345G123"

EMS_PAYLOAD = {
    "battery_power": -1200.0,
    "battery_wh_remaining": 5400.0,
    "grid_power": 300.0,
    "inverters": [{"serial": SN, "power": 2500.0}],
    "meters": [{"meter_id": "grid", "power": 300.0}],
}


def _client() -> GivenergyAPIClient:
    return GivenergyAPIClient(api_key="test-key")


class TestEMS:
    def test_get_latest_returns_snapshot(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/ems/{SN}/system-data/latest", method="GET", json={"data": EMS_PAYLOAD})
        result = _client().ems(SN).get_latest()
        assert isinstance(result, EMSSnapshot)
        assert result.battery_power == -1200.0
        assert result.battery_wh_remaining == 5400.0
        assert len(result.inverters) == 1
        assert result.inverters[0].serial == SN
        assert len(result.meters) == 1

    def test_get_latest_raises_not_found_for_non_ems_inverter(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/ems/NOEMS/system-data/latest",
            method="GET",
            status_code=404,
            json={"message": "Not an EMS inverter"},
        )
        with pytest.raises(NotFoundError):
            _client().ems("NOEMS").get_latest()

    async def test_aget_latest_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/ems/{SN}/system-data/latest", method="GET", json={"data": EMS_PAYLOAD})
        result = await _client().ems(SN).aget_latest()
        assert isinstance(result, EMSSnapshot)
        assert result.grid_power == 300.0
