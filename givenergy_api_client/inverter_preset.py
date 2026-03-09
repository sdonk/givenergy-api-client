from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, model_validator

from givenergy_api_client.exceptions import raise_for_status

if TYPE_CHECKING:
    from givenergy_api_client.client import GivenergyAPIClient


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class PresetParameter(BaseModel):
    """A configurable parameter within an inverter preset."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    type: str
    validation: dict[str, str | int | float | bool | None] | None = None


class InverterPresetData(BaseModel):
    """Descriptor for an available inverter configuration preset."""

    model_config = ConfigDict(frozen=True)

    id: int
    identifier: str
    name: str
    description: str
    parameters: list[PresetParameter]


class PresetCurrentValues(BaseModel):
    """Current configured values for a specific preset.

    Because the schema is preset-specific, all known scalar values are captured
    in ``extra_fields``; no dynamic ``dict`` is exposed.
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


class PresetApplyResult(BaseModel):
    """Result of applying an inverter preset."""

    model_config = ConfigDict(frozen=True)

    success: bool
    message: str


# ---------------------------------------------------------------------------
# Domain class
# ---------------------------------------------------------------------------


class InverterPreset:
    """Domain object for inverter preset control.

    Obtain via ``client.inverter_preset(serial_number)`` rather than direct instantiation.
    """

    def __init__(self, client: GivenergyAPIClient, serial_number: str) -> None:
        self._client = client
        self._base = client._base_url
        self._serial = serial_number

    # ------------------------------------------------------------------
    # Sync methods
    # ------------------------------------------------------------------

    def list_presets(self) -> list[InverterPresetData]:
        """Return all available configuration presets for this inverter."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/inverter/{self._serial}/presets")
            raise_for_status(response)
            return [InverterPresetData.model_validate(item) for item in response.json()["data"]]

    def get_preset(self, *, preset_id: int) -> PresetCurrentValues:
        """Return the current configured values for a specific preset."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/inverter/{self._serial}/presets/{preset_id}")
            raise_for_status(response)
            return PresetCurrentValues.model_validate(response.json()["data"])

    def apply_preset(
        self,
        *,
        preset_id: int,
        payload: dict[str, str | int | float | bool | None],
    ) -> PresetApplyResult:
        """Apply a preset configuration to the inverter."""
        with self._client.get_client() as _client:
            response = _client.post(
                f"{self._base}/inverter/{self._serial}/presets/{preset_id}",
                json=payload,
            )
            raise_for_status(response)
            return PresetApplyResult.model_validate(response.json())

    # ------------------------------------------------------------------
    # Async methods
    # ------------------------------------------------------------------

    async def alist_presets(self) -> list[InverterPresetData]:
        """Async variant of :meth:`list_presets`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/inverter/{self._serial}/presets")
            raise_for_status(response)
            return [InverterPresetData.model_validate(item) for item in response.json()["data"]]

    async def aget_preset(self, *, preset_id: int) -> PresetCurrentValues:
        """Async variant of :meth:`get_preset`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/inverter/{self._serial}/presets/{preset_id}")
            raise_for_status(response)
            return PresetCurrentValues.model_validate(response.json()["data"])

    async def aapply_preset(
        self,
        *,
        preset_id: int,
        payload: dict[str, str | int | float | bool | None],
    ) -> PresetApplyResult:
        """Async variant of :meth:`apply_preset`."""
        async with self._client.aget_client() as _client:
            response = await _client.post(
                f"{self._base}/inverter/{self._serial}/presets/{preset_id}",
                json=payload,
            )
            raise_for_status(response)
            return PresetApplyResult.model_validate(response.json())
