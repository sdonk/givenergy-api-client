# Contract: InverterPreset

**Module**: `givenergy_api_client.inverter_preset`

## Pydantic Models

```python
class PresetParameter(BaseModel):
    id: str
    name: str
    type: str
    validation: dict | None
    model_config = ConfigDict(frozen=True)

class InverterPresetData(BaseModel):
    """Renamed from InverterPreset to avoid clash with the domain class."""
    id: int
    identifier: str
    name: str
    description: str
    parameters: list[PresetParameter]
    model_config = ConfigDict(frozen=True)

class PresetApplyResult(BaseModel):
    success: bool
    message: str
    model_config = ConfigDict(frozen=True)
```

## Domain Class

```python
class InverterPreset:
    def __init__(
        self, client: GivenergyAPIClient, serial_number: str
    ) -> None: ...

    def list_presets(self) -> list[InverterPresetData]: ...
    async def alist_presets(self) -> list[InverterPresetData]: ...

    def get_preset(self, preset_id: int) -> dict: ...
    async def aget_preset(self, preset_id: int) -> dict: ...

    def apply_preset(self, preset_id: int, payload: dict) -> PresetApplyResult: ...
    async def aapply_preset(
        self, preset_id: int, payload: dict
    ) -> PresetApplyResult: ...
```

## Notes

- `get_preset` returns `dict` because preset value structure is preset-specific and
  not enumerable from the API spec.
- `apply_preset` forwards `payload` as the JSON request body unchanged.

## Errors

| Condition | Exception |
|-----------|-----------|
| Invalid API key | `AuthenticationError` |
| Serial or preset ID not found | `NotFoundError` |
| Invalid payload | `APIValidationError` |
| Server error | `ServerError` |

## Factory

```python
presets = client.inverter_preset("CE2345G123")
available = presets.list_presets()         # -> list[InverterPresetData]
result = presets.apply_preset(3, {"charge_target": 80})  # -> PresetApplyResult
```
