# Contract: EVCharger

**Module**: `givenergy_api_client.ev_charger`

## Pydantic Models

```python
class EVChargerData(BaseModel):
    """Renamed from EVCharger to avoid clash with the domain class."""
    uuid: str
    serial_number: str
    type: str
    alias: str | None
    online: bool
    status: str
    model_config = ConfigDict(frozen=True)

class EVChargerMeasurement(BaseModel):
    measurand: str
    value: float
    unit: str
    model_config = ConfigDict(frozen=True)

class EVChargerMeterReading(BaseModel):
    meter_id: str
    timestamp: datetime
    measurements: list[EVChargerMeasurement]
    model_config = ConfigDict(frozen=True)

class ChargingSession(BaseModel):
    started_by: str | None
    meter_start: float
    started_at: datetime
    stopped_by: str | None
    meter_stop: float | None
    stopped_at: datetime | None
    model_config = ConfigDict(frozen=True)

class EVChargerCommandResult(BaseModel):
    code: int
    success: bool
    message: str
    model_config = ConfigDict(frozen=True)
```

## Domain Class

```python
class EVCharger:
    def __init__(
        self, client: GivenergyAPIClient, charger_uuid: str
    ) -> None: ...

    def get(self) -> EVChargerData: ...
    async def aget(self) -> EVChargerData: ...

    def get_meter_data(
        self,
        start_time: datetime,
        end_time: datetime,
        measurands: list[str],
        meter_ids: list[str],
        *,
        page: int = 1,
        page_size: int = 15,
    ) -> dict: ...
    async def aget_meter_data(
        self,
        start_time: datetime,
        end_time: datetime,
        measurands: list[str],
        meter_ids: list[str],
        *,
        page: int = 1,
        page_size: int = 15,
    ) -> dict: ...

    def list_commands(self) -> list[str]: ...
    async def alist_commands(self) -> list[str]: ...

    def get_command(self, command_id: str) -> dict: ...
    async def aget_command(self, command_id: str) -> dict: ...

    def execute_command(
        self, command_id: str, payload: dict
    ) -> EVChargerCommandResult: ...
    async def aexecute_command(
        self, command_id: str, payload: dict
    ) -> EVChargerCommandResult: ...

    def list_sessions(
        self,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        page: int = 1,
        page_size: int = 15,
    ) -> dict: ...
    async def alist_sessions(
        self,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        page: int = 1,
        page_size: int = 15,
    ) -> dict: ...
```

## Collection Endpoint (on GivenergyAPIClient)

```python
# List all EV chargers — no charger_uuid required
client.list_ev_chargers(*, page: int = 1, page_size: int = 15) -> dict
await client.alist_ev_chargers(*, page: int = 1, page_size: int = 15) -> dict
```

## Errors

| Condition | Exception |
|-----------|-----------|
| Invalid API key | `AuthenticationError` |
| Charger UUID not found | `NotFoundError` |
| Unsupported command ID | `APIValidationError` (API message preserved) |
| Server error | `ServerError` |

## Factory

```python
charger = client.ev_charger("uuid-1234")
info = charger.get()                   # -> EVChargerData
result = charger.execute_command("StartCharging", {"mode": "smart"})
# -> EVChargerCommandResult
```
