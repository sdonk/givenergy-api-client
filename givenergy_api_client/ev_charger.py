from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, model_validator

from givenergy_api_client.exceptions import raise_for_status
from givenergy_api_client.pagination import PaginatedResult

if TYPE_CHECKING:
    from givenergy_api_client.client import GivenergyAPIClient


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class EVChargerData(BaseModel):
    """EV charger record returned by the list/get endpoints."""

    model_config = ConfigDict(frozen=True)

    uuid: str
    serial_number: str
    type: str
    alias: str | None = None
    online: bool
    status: str


class EVChargerMeasurement(BaseModel):
    """A single measurand reading from a charger meter."""

    model_config = ConfigDict(frozen=True)

    measurand: str
    value: float
    unit: str


class EVChargerMeterReading(BaseModel):
    """A timestamped collection of measurements from a charger meter."""

    model_config = ConfigDict(frozen=True)

    meter_id: str
    timestamp: dt.datetime
    measurements: list[EVChargerMeasurement]


class ChargingSession(BaseModel):
    """A single EV charging session record."""

    model_config = ConfigDict(frozen=True)

    started_by: str | None = None
    meter_start: float
    started_at: dt.datetime
    stopped_by: str | None = None
    meter_stop: float | None = None
    stopped_at: dt.datetime | None = None


class EVChargerCommandResult(BaseModel):
    """Result of executing a command on an EV charger."""

    model_config = ConfigDict(frozen=True)

    code: int
    success: bool
    message: str


class EVChargerCommandState(BaseModel):
    """Current state of a specific command on an EV charger.

    Because the schema is command-specific, known fields are minimal;
    all remaining keys are captured in ``extra_fields``.
    """

    model_config = ConfigDict(frozen=True)

    extra_fields: dict[str, str | int | float | bool | None] = {}

    @model_validator(mode="before")
    @classmethod
    def _capture_extra(cls, data: Any) -> Any:
        if isinstance(data, dict):
            known = {"extra_fields"}
            extras: dict[str, str | int | float | bool | None] = {k: v for k, v in data.items() if k not in known}
            return {"extra_fields": extras}
        return data  # pragma: no cover


# ---------------------------------------------------------------------------
# Domain class
# ---------------------------------------------------------------------------


class EVCharger:
    """Domain object for a specific GivEnergy EV charger.

    Obtain via ``client.ev_charger(charger_uuid)`` rather than direct instantiation.
    """

    def __init__(self, client: GivenergyAPIClient, charger_uuid: str) -> None:
        self._client = client
        self._base = client._base_url
        self._uuid = charger_uuid

    # ------------------------------------------------------------------
    # Sync methods
    # ------------------------------------------------------------------

    def get(self) -> EVChargerData:
        """Return details of this EV charger."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/ev-charger/{self._uuid}")
            raise_for_status(response)
            return EVChargerData.model_validate(response.json()["data"])

    def get_meter_data(
        self,
        *,
        start_time: dt.datetime,
        end_time: dt.datetime,
        measurands: list[str],
        meter_ids: list[str],
        page: int = 1,
        page_size: int = 15,
    ) -> PaginatedResult[EVChargerMeterReading]:
        """Return paginated meter readings for this charger."""
        params: dict[str, Any] = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "measurands[]": measurands,
            "meter_ids[]": meter_ids,
            "page": page,
            "pageSize": page_size,
        }
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/ev-charger/{self._uuid}/meter-data", params=params)
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[EVChargerMeterReading].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    def list_commands(self) -> list[str]:
        """Return the list of command IDs supported by this charger."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/ev-charger/{self._uuid}/commands")
            raise_for_status(response)
            return list(response.json()["data"])

    def get_command(self, *, command_id: str) -> EVChargerCommandState:
        """Return the current state of a specific command on this charger."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/ev-charger/{self._uuid}/commands/{command_id}")
            raise_for_status(response)
            return EVChargerCommandState.model_validate(response.json()["data"])

    def execute_command(
        self,
        *,
        command_id: str,
        payload: dict[str, str | int | float | bool | None],
    ) -> EVChargerCommandResult:
        """Execute a command on this charger."""
        with self._client.get_client() as _client:
            response = _client.post(
                f"{self._base}/ev-charger/{self._uuid}/commands/{command_id}",
                json=payload,
            )
            raise_for_status(response)
            return EVChargerCommandResult.model_validate(response.json())

    def list_sessions(
        self,
        *,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        page: int = 1,
        page_size: int = 15,
    ) -> PaginatedResult[ChargingSession]:
        """Return paginated charging sessions for this charger."""
        params: dict[str, Any] = {"page": page, "pageSize": page_size}
        if start_time is not None:
            params["start_time"] = start_time.isoformat()
        if end_time is not None:
            params["end_time"] = end_time.isoformat()
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/ev-charger/{self._uuid}/charging-sessions", params=params)
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[ChargingSession].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    # ------------------------------------------------------------------
    # Async methods
    # ------------------------------------------------------------------

    async def aget(self) -> EVChargerData:
        """Async variant of :meth:`get`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/ev-charger/{self._uuid}")
            raise_for_status(response)
            return EVChargerData.model_validate(response.json()["data"])

    async def aget_meter_data(
        self,
        *,
        start_time: dt.datetime,
        end_time: dt.datetime,
        measurands: list[str],
        meter_ids: list[str],
        page: int = 1,
        page_size: int = 15,
    ) -> PaginatedResult[EVChargerMeterReading]:
        """Async variant of :meth:`get_meter_data`."""
        params: dict[str, Any] = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "measurands[]": measurands,
            "meter_ids[]": meter_ids,
            "page": page,
            "pageSize": page_size,
        }
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/ev-charger/{self._uuid}/meter-data", params=params)
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[EVChargerMeterReading].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    async def alist_commands(self) -> list[str]:
        """Async variant of :meth:`list_commands`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/ev-charger/{self._uuid}/commands")
            raise_for_status(response)
            return list(response.json()["data"])

    async def aget_command(self, *, command_id: str) -> EVChargerCommandState:
        """Async variant of :meth:`get_command`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/ev-charger/{self._uuid}/commands/{command_id}")
            raise_for_status(response)
            return EVChargerCommandState.model_validate(response.json()["data"])

    async def aexecute_command(
        self,
        *,
        command_id: str,
        payload: dict[str, str | int | float | bool | None],
    ) -> EVChargerCommandResult:
        """Async variant of :meth:`execute_command`."""
        async with self._client.aget_client() as _client:
            response = await _client.post(
                f"{self._base}/ev-charger/{self._uuid}/commands/{command_id}",
                json=payload,
            )
            raise_for_status(response)
            return EVChargerCommandResult.model_validate(response.json())

    async def alist_sessions(
        self,
        *,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        page: int = 1,
        page_size: int = 15,
    ) -> PaginatedResult[ChargingSession]:
        """Async variant of :meth:`list_sessions`."""
        params: dict[str, Any] = {"page": page, "pageSize": page_size}
        if start_time is not None:
            params["start_time"] = start_time.isoformat()
        if end_time is not None:
            params["end_time"] = end_time.isoformat()
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/ev-charger/{self._uuid}/charging-sessions", params=params)
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[ChargingSession].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _empty_meta(page: int, page_size: int) -> dict[str, int]:
    return {"current_page": page, "last_page": page, "per_page": page_size, "total": 0}
