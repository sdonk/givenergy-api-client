from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from givenergy_api_client.exceptions import raise_for_status

if TYPE_CHECKING:
    from givenergy_api_client.client import GivenergyAPIClient


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class EMSInverterReading(BaseModel):
    """Per-inverter reading within an EMS snapshot."""

    model_config = ConfigDict(frozen=True)

    serial: str
    power: float


class EMSMeterReading(BaseModel):
    """Per-meter reading within an EMS snapshot."""

    model_config = ConfigDict(frozen=True)

    meter_id: str
    power: float


class EMSSnapshot(BaseModel):
    """Latest aggregate EMS plant metrics."""

    model_config = ConfigDict(frozen=True)

    battery_power: float
    battery_wh_remaining: float
    grid_power: float
    inverters: list[EMSInverterReading]
    meters: list[EMSMeterReading]


# ---------------------------------------------------------------------------
# Domain class
# ---------------------------------------------------------------------------


class EMS:
    """Domain object for GivEnergy EMS plant data.

    Obtain via ``client.ems(inverter_serial_number)`` rather than direct instantiation.
    """

    def __init__(self, client: GivenergyAPIClient, inverter_serial_number: str) -> None:
        self._client = client
        self._base = client._base_url
        self._serial = inverter_serial_number

    def get_latest(self) -> EMSSnapshot:
        """Return the latest EMS system snapshot for this inverter."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/ems/{self._serial}/system-data/latest")
            raise_for_status(response)
            return EMSSnapshot.model_validate(response.json()["data"])

    async def aget_latest(self) -> EMSSnapshot:
        """Async variant of :meth:`get_latest`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/ems/{self._serial}/system-data/latest")
            raise_for_status(response)
            return EMSSnapshot.model_validate(response.json()["data"])
