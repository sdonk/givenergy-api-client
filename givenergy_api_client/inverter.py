from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from givenergy_api_client.energy_flow import EnergyDataFlowGrouping, EnergyDataFlowType
from givenergy_api_client.exceptions import raise_for_status

if TYPE_CHECKING:
    from givenergy_api_client.client import GivenergyAPIClient


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class InverterHealthCheck(BaseModel):
    """A single inverter health metric."""

    model_config = ConfigDict(frozen=True)

    name: str
    value: str | int | float
    status: str
    unit: str | None = None


class EnergyFlowPoint(BaseModel):
    """A single timestamped energy-flow data point."""

    model_config = ConfigDict(frozen=True)

    timestamp: dt.datetime
    value: float


class EnergyFlowData(BaseModel):
    """Time-series data for one energy flow type."""

    model_config = ConfigDict(frozen=True)

    type: EnergyDataFlowType
    data: list[EnergyFlowPoint]


class DebugCommandResult(BaseModel):
    """Result of sending a raw debug command to an inverter."""

    model_config = ConfigDict(frozen=True)

    success: bool
    code: int


# ---------------------------------------------------------------------------
# Domain class
# ---------------------------------------------------------------------------


class Inverter:
    """Domain object for GivEnergy inverter operations.

    Obtain via ``client.inverter(serial_number)`` rather than direct instantiation.
    """

    def __init__(self, client: GivenergyAPIClient, serial_number: str) -> None:
        self._client = client
        self._base = client._base_url
        self._serial = serial_number

    # ------------------------------------------------------------------
    # Sync methods
    # ------------------------------------------------------------------

    def get_health(self) -> list[InverterHealthCheck]:
        """Return the list of health checks for this inverter."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/inverter/{self._serial}/health")
            raise_for_status(response)
            return [InverterHealthCheck.model_validate(item) for item in response.json()["data"]]

    def get_energy_flows(
        self,
        *,
        start_time: dt.datetime,
        end_time: dt.datetime,
        grouping: EnergyDataFlowGrouping = EnergyDataFlowGrouping.HALF_HOURLY,
    ) -> list[EnergyFlowData]:
        """Return energy-flow data between two timezone-aware datetimes.

        Raises:
            ValueError: If either datetime is timezone-naive or end_time <= start_time.
        """
        _validate_time_range(start_time, end_time)
        payload = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "grouping": int(grouping),
        }
        with self._client.get_client() as _client:
            response = _client.post(f"{self._base}/inverter/{self._serial}/energy-flows", json=payload)
            raise_for_status(response)
            return [EnergyFlowData.model_validate(item) for item in response.json()["data"]]

    def send_debug_command(self, *, hex_command: str) -> DebugCommandResult:
        """Send a raw hex command to the inverter. Use with caution."""
        with self._client.get_client() as _client:
            response = _client.post(
                f"{self._base}/inverter/{self._serial}/debug/transparent/send",
                json={"command": hex_command},
            )
            raise_for_status(response)
            return DebugCommandResult.model_validate(response.json())

    # ------------------------------------------------------------------
    # Async methods
    # ------------------------------------------------------------------

    async def aget_health(self) -> list[InverterHealthCheck]:
        """Async variant of :meth:`get_health`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/inverter/{self._serial}/health")
            raise_for_status(response)
            return [InverterHealthCheck.model_validate(item) for item in response.json()["data"]]

    async def aget_energy_flows(
        self,
        *,
        start_time: dt.datetime,
        end_time: dt.datetime,
        grouping: EnergyDataFlowGrouping = EnergyDataFlowGrouping.HALF_HOURLY,
    ) -> list[EnergyFlowData]:
        """Async variant of :meth:`get_energy_flows`."""
        _validate_time_range(start_time, end_time)
        payload = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "grouping": int(grouping),
        }
        async with self._client.aget_client() as _client:
            response = await _client.post(f"{self._base}/inverter/{self._serial}/energy-flows", json=payload)
            raise_for_status(response)
            return [EnergyFlowData.model_validate(item) for item in response.json()["data"]]

    async def asend_debug_command(self, *, hex_command: str) -> DebugCommandResult:
        """Async variant of :meth:`send_debug_command`."""
        async with self._client.aget_client() as _client:
            response = await _client.post(
                f"{self._base}/inverter/{self._serial}/debug/transparent/send",
                json={"command": hex_command},
            )
            raise_for_status(response)
            return DebugCommandResult.model_validate(response.json())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_time_range(start_time: dt.datetime, end_time: dt.datetime) -> None:
    if start_time.tzinfo is None:
        raise ValueError("start_time must be timezone-aware")
    if end_time.tzinfo is None:
        raise ValueError("end_time must be timezone-aware")
    if end_time <= start_time:
        raise ValueError("end_time must be after start_time")
