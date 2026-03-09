# Contract: EMS

**Module**: `givenergy_api_client.ems`

## Pydantic Models

```python
class EMSInverterReading(BaseModel):
    serial: str
    power: float
    model_config = ConfigDict(frozen=True)

class EMSMeterReading(BaseModel):
    meter_id: str
    power: float
    model_config = ConfigDict(frozen=True)

class EMSSnapshot(BaseModel):
    battery_power: float
    battery_wh_remaining: float
    grid_power: float
    inverters: list[EMSInverterReading]
    meters: list[EMSMeterReading]
    model_config = ConfigDict(frozen=True)
```

## Domain Class

```python
class EMS:
    def __init__(
        self, client: GivenergyAPIClient, inverter_serial_number: str
    ) -> None: ...

    def get_latest(self) -> EMSSnapshot: ...
    async def aget_latest(self) -> EMSSnapshot: ...
```

## Errors

| Condition | Exception |
|-----------|-----------|
| Invalid API key | `AuthenticationError` |
| Serial not found / not EMS-enabled | `NotFoundError` |
| Server error | `ServerError` |

## Factory

```python
ems = client.ems("CE2345G123")
snapshot = ems.get_latest()   # -> EMSSnapshot
```
