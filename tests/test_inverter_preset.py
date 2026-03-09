"""Tests for the InverterPreset domain class (US4)."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from givenergy_api_client.client import GivenergyAPIClient
from givenergy_api_client.exceptions import APIValidationError, NotFoundError
from givenergy_api_client.inverter_preset import (
    InverterPresetData,
    PresetApplyResult,
    PresetCurrentValues,
)

BASE = "https://api.givenergy.cloud/v1"
SN = "CE2345G123"

PRESET_PAYLOAD = {
    "id": 3,
    "identifier": "timed-charge",
    "name": "Timed Charge",
    "description": "Charge battery during off-peak hours",
    "parameters": [
        {"id": "charge_target", "name": "Charge Target (%)", "type": "integer", "validation": {"min": 0, "max": 100}},
        {"id": "start_time", "name": "Start Time", "type": "string", "validation": None},
    ],
}


def _client() -> GivenergyAPIClient:
    return GivenergyAPIClient(api_key="test-key")


class TestInverterPreset:
    def test_list_presets_returns_typed_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/inverter/{SN}/presets", method="GET", json={"data": [PRESET_PAYLOAD]})
        result = _client().inverter_preset(SN).list_presets()
        assert isinstance(result, list)
        assert isinstance(result[0], InverterPresetData)
        assert result[0].identifier == "timed-charge"
        assert len(result[0].parameters) == 2

    def test_get_preset_returns_current_values_with_extra_fields(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/{SN}/presets/3",
            method="GET",
            json={"data": {"charge_target": 80, "start_time": "00:30"}},
        )
        result = _client().inverter_preset(SN).get_preset(preset_id=3)
        assert isinstance(result, PresetCurrentValues)
        assert result.extra_fields["charge_target"] == 80
        assert result.extra_fields["start_time"] == "00:30"

    def test_apply_preset_returns_result(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/{SN}/presets/3",
            method="POST",
            json={"success": True, "message": "Preset applied"},
        )
        result = _client().inverter_preset(SN).apply_preset(preset_id=3, payload={"charge_target": 80})
        assert isinstance(result, PresetApplyResult)
        assert result.success is True

    def test_list_presets_raises_not_found_on_404(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/BAD/presets", method="GET", status_code=404, json={"message": "Not found"}
        )
        with pytest.raises(NotFoundError):
            _client().inverter_preset("BAD").list_presets()

    def test_apply_preset_raises_api_validation_error_on_422(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/{SN}/presets/3",
            method="POST",
            status_code=422,
            json={"message": "charge_target must be between 0 and 100"},
        )
        with pytest.raises(APIValidationError):
            _client().inverter_preset(SN).apply_preset(preset_id=3, payload={"charge_target": 200})

    async def test_alist_presets_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url=f"{BASE}/inverter/{SN}/presets", method="GET", json={"data": [PRESET_PAYLOAD]})
        result = await _client().inverter_preset(SN).alist_presets()
        assert isinstance(result, list)
        assert result[0].name == "Timed Charge"

    async def test_aget_preset_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/{SN}/presets/3",
            method="GET",
            json={"data": {"charge_target": 90, "start_time": "01:00"}},
        )
        result = await _client().inverter_preset(SN).aget_preset(preset_id=3)
        assert isinstance(result, PresetCurrentValues)
        assert result.extra_fields["charge_target"] == 90

    async def test_aapply_preset_async(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=f"{BASE}/inverter/{SN}/presets/3",
            method="POST",
            json={"success": True, "message": "Applied"},
        )
        result = await _client().inverter_preset(SN).aapply_preset(preset_id=3, payload={"charge_target": 90})
        assert isinstance(result, PresetApplyResult)
        assert result.success is True

    def test_preset_current_values_non_dict_passthrough(self) -> None:
        # Exercises the `return data` branch in _capture_extra when input is not a dict.
        existing = PresetCurrentValues.model_validate({"charge_target": 80})
        re_validated = PresetCurrentValues.model_validate(existing)
        assert re_validated.extra_fields == {"charge_target": 80}
