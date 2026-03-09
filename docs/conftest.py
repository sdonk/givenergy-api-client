"""Doctest fixtures for docs/ code snippet validation.

Injects ``client`` and supporting names into the doctest global namespace so
that all code snippets in the documentation run without a live API key or
network connection.
"""

from __future__ import annotations

import asyncio
import datetime as dt
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from givenergy_api_client.account import AccountData, AccountDevice
from givenergy_api_client.ems import EMSInverterReading, EMSMeterReading, EMSSnapshot
from givenergy_api_client.energy_flow import EnergyDataFlowGrouping, EnergyDataFlowType
from givenergy_api_client.ev_charger import (
    ChargingSession,
    EVChargerCommandResult,
    EVChargerCommandState,
    EVChargerData,
    EVChargerMeasurement,
    EVChargerMeterReading,
)
from givenergy_api_client.exceptions import (
    APIValidationError,
    AuthenticationError,
    GivEnergyAPIError,
    NotFoundError,
    ServerError,
)
from givenergy_api_client.inverter import DebugCommandResult, EnergyFlowData, EnergyFlowPoint, InverterHealthCheck
from givenergy_api_client.inverter_preset import (
    InverterPresetData,
    PresetApplyResult,
    PresetCurrentValues,
    PresetParameter,
)
from givenergy_api_client.pagination import PaginationMeta

# ---------------------------------------------------------------------------
# Canonical mock data — used consistently across all doc pages
# ---------------------------------------------------------------------------

_META_ONE_PAGE = PaginationMeta(current_page=1, last_page=1, per_page=15, total=1)
_META_TWO_PAGES_P1 = PaginationMeta(current_page=1, last_page=2, per_page=15, total=2)

_ACCOUNT = AccountData(
    id=1,
    name="Test User",
    first_name="Test",
    surname="User",
    role="admin",
    email="test@example.com",
    address="1 Test Street",
    postcode="TE1 1ST",
    country="GB",
    telephone_number="+441234567890",
    timezone="Europe/London",
    standard_timezone="UTC",
)

_ACCOUNT_DEVICE = AccountDevice(
    serial_number="CE2345G123",
    type="inverter",
    site_id=1,
    inverter_serial="CE2345G123",
    inverter_status="online",
)

_EV_CHARGER = EVChargerData(
    uuid="uuid-1234-abcd",
    serial_number="EVC123456",
    type="AC",
    alias="Home Charger",
    online=True,
    status="available",
)

_EMS = EMSSnapshot(
    battery_power=-1200.0,
    battery_wh_remaining=8500.0,
    grid_power=300.0,
    inverters=[EMSInverterReading(serial="CE2345G123", power=2500.0)],
    meters=[EMSMeterReading(meter_id="m1", power=300.0)],
)

_HEALTH_CHECKS = [
    InverterHealthCheck(name="battery_voltage", value=52.4, status="ok", unit="V"),
    InverterHealthCheck(name="inverter_temperature", value=38.0, status="ok", unit="°C"),
]

_ENERGY_FLOWS = [
    EnergyFlowData(
        type=EnergyDataFlowType.PV_TO_HOME,
        data=[
            EnergyFlowPoint(
                timestamp=dt.datetime(2025, 1, 1, 12, 0, tzinfo=dt.timezone.utc),
                value=2500.0,
            )
        ],
    )
]

_PRESET = InverterPresetData(
    id=1,
    identifier="timed-charge",
    name="Timed Charge",
    description="Charges battery during off-peak hours.",
    parameters=[
        PresetParameter(id="start_time", name="Start Time", type="time"),
        PresetParameter(id="end_time", name="End Time", type="time"),
    ],
)

_PRESET_VALUES = PresetCurrentValues.model_validate({"start_time": "00:30", "end_time": "05:00"})

_CMD_STATE = EVChargerCommandState.model_validate({"charge_limit": 32, "unit": "A"})

_CMD_RESULT = EVChargerCommandResult(code=0, success=True, message="Command executed")

_SESSION = ChargingSession(
    started_by="user",
    meter_start=0.0,
    started_at=dt.datetime(2025, 1, 1, 8, 0, tzinfo=dt.timezone.utc),
    meter_stop=15.0,
    stopped_at=dt.datetime(2025, 1, 1, 9, 30, tzinfo=dt.timezone.utc),
)

_METER_READING = EVChargerMeterReading(
    meter_id="m1",
    timestamp=dt.datetime(2025, 1, 1, 12, 0, tzinfo=dt.timezone.utc),
    measurements=[EVChargerMeasurement(measurand="Power.Active.Import", value=7.2, unit="kW")],
)


# ---------------------------------------------------------------------------
# Paginated-result helpers (SimpleNamespace mimics Pydantic field access)
# ---------------------------------------------------------------------------


class _Page:
    """Lightweight stand-in for PaginatedResult that supports attribute access."""

    def __init__(self, data: list[Any], meta: PaginationMeta) -> None:
        self.data = data
        self.meta = meta


_DEVICES_PAGE = _Page([_ACCOUNT_DEVICE], _META_ONE_PAGE)
_DEVICES_PAGE_P1 = _Page([_ACCOUNT_DEVICE], _META_TWO_PAGES_P1)
_CHILDREN_PAGE = _Page([_ACCOUNT], _META_ONE_PAGE)
_CHARGERS_PAGE = _Page([_EV_CHARGER], _META_ONE_PAGE)
_METER_PAGE = _Page([_METER_READING], _META_ONE_PAGE)
_SESSIONS_PAGE = _Page([_SESSION], _META_ONE_PAGE)


# ---------------------------------------------------------------------------
# Mock client factory
# ---------------------------------------------------------------------------


def _make_mock_client() -> MagicMock:
    """Return a fully-configured mock GivenergyAPIClient."""
    mock = MagicMock(name="GivenergyAPIClient")

    # --- account domain ---
    acc = mock.account.return_value
    acc.get.return_value = _ACCOUNT
    acc.aget = AsyncMock(return_value=_ACCOUNT)
    acc.get_by_id.return_value = _ACCOUNT
    acc.aget_by_id = AsyncMock(return_value=_ACCOUNT)
    acc.search.return_value = _ACCOUNT
    acc.asearch = AsyncMock(return_value=_ACCOUNT)
    acc.get_devices.return_value = _DEVICES_PAGE
    acc.aget_devices = AsyncMock(return_value=_DEVICES_PAGE)
    acc.list_children.return_value = _CHILDREN_PAGE
    acc.alist_children = AsyncMock(return_value=_CHILDREN_PAGE)
    acc.list_children_for_user.return_value = _CHILDREN_PAGE
    acc.alist_children_for_user = AsyncMock(return_value=_CHILDREN_PAGE)
    acc.get_sso_accounts.return_value = [_ACCOUNT]
    acc.aget_sso_accounts = AsyncMock(return_value=[_ACCOUNT])

    # --- inverter domain ---
    inv = mock.inverter.return_value
    inv.get_health.return_value = _HEALTH_CHECKS
    inv.aget_health = AsyncMock(return_value=_HEALTH_CHECKS)
    inv.get_energy_flows.return_value = _ENERGY_FLOWS
    inv.aget_energy_flows = AsyncMock(return_value=_ENERGY_FLOWS)
    _debug = DebugCommandResult(success=True, code=0)
    inv.send_debug_command.return_value = _debug
    inv.asend_debug_command = AsyncMock(return_value=_debug)

    # --- ems domain ---
    ems = mock.ems.return_value
    ems.get_latest.return_value = _EMS
    ems.aget_latest = AsyncMock(return_value=_EMS)

    # --- ev_charger domain (list at client level) ---
    mock.list_ev_chargers.return_value = _CHARGERS_PAGE
    mock.alist_ev_chargers = AsyncMock(return_value=_CHARGERS_PAGE)

    # --- ev_charger domain (per-charger) ---
    evc = mock.ev_charger.return_value
    evc.get.return_value = _EV_CHARGER
    evc.aget = AsyncMock(return_value=_EV_CHARGER)
    evc.get_meter_data.return_value = _METER_PAGE
    evc.aget_meter_data = AsyncMock(return_value=_METER_PAGE)
    evc.list_commands.return_value = ["charge-limit", "smart-charging"]
    evc.alist_commands = AsyncMock(return_value=["charge-limit", "smart-charging"])
    evc.get_command.return_value = _CMD_STATE
    evc.aget_command = AsyncMock(return_value=_CMD_STATE)
    evc.execute_command.return_value = _CMD_RESULT
    evc.aexecute_command = AsyncMock(return_value=_CMD_RESULT)
    evc.list_sessions.return_value = _SESSIONS_PAGE
    evc.alist_sessions = AsyncMock(return_value=_SESSIONS_PAGE)

    # --- inverter_preset domain ---
    ip = mock.inverter_preset.return_value
    ip.list_presets.return_value = [_PRESET]
    ip.alist_presets = AsyncMock(return_value=[_PRESET])
    ip.get_preset.return_value = _PRESET_VALUES
    ip.aget_preset = AsyncMock(return_value=_PRESET_VALUES)
    _apply = PresetApplyResult(success=True, message="Preset applied")
    ip.apply_preset.return_value = _apply
    ip.aapply_preset = AsyncMock(return_value=_apply)

    return mock


# ---------------------------------------------------------------------------
# Doctest namespace fixture
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def doctest_namespace(doctest_namespace: dict[str, Any]) -> dict[str, Any]:  # type: ignore[override]
    """Inject mock objects into every doctest's global namespace."""
    doctest_namespace.update(
        {
            "client": _make_mock_client(),
            "asyncio": asyncio,
            "dt": dt,
            "EnergyDataFlowGrouping": EnergyDataFlowGrouping,
            "EnergyDataFlowType": EnergyDataFlowType,
            "AuthenticationError": AuthenticationError,
            "NotFoundError": NotFoundError,
            "APIValidationError": APIValidationError,
            "ServerError": ServerError,
            "GivEnergyAPIError": GivEnergyAPIError,
        }
    )
    return doctest_namespace
