# Contract: Inverter

**Module**: `givenergy_api_client.inverter`

## Pydantic Models

```python
class InverterHealthCheck(BaseModel):
    name: str
    value: str | int | float
    status: str
    unit: str | None
    model_config = ConfigDict(frozen=True)

class EnergyFlowPoint(BaseModel):
    timestamp: datetime
    value: float
    model_config = ConfigDict(frozen=True)

class EnergyFlowData(BaseModel):
    type: EnergyDataFlowType   # from energy_flow.py
    data: list[EnergyFlowPoint]
    model_config = ConfigDict(frozen=True)

class DebugCommandResult(BaseModel):
    success: bool
    code: int
    model_config = ConfigDict(frozen=True)
```

## Domain Class

```python
class Inverter:
    def __init__(
        self, client: GivenergyAPIClient, serial_number: str
    ) -> None: ...

    def get_health(self) -> list[InverterHealthCheck]: ...
    async def aget_health(self) -> list[InverterHealthCheck]: ...

    def get_energy_flows(
        self,
        start_time: datetime,
        end_time: datetime,
        *,
        grouping: EnergyDataFlowGrouping = EnergyDataFlowGrouping.HALF_HOURLY,
    ) -> list[EnergyFlowData]: ...
    async def aget_energy_flows(
        self,
        start_time: datetime,
        end_time: datetime,
        *,
        grouping: EnergyDataFlowGrouping = EnergyDataFlowGrouping.HALF_HOURLY,
    ) -> list[EnergyFlowData]: ...

    def send_debug_command(self, hex_command: str) -> DebugCommandResult: ...
    async def asend_debug_command(self, hex_command: str) -> DebugCommandResult: ...
```

## Validation

- `start_time` and `end_time` MUST be timezone-aware `datetime` objects.
  Raises `ValueError` if naive.
- `end_time` MUST be after `start_time`. Raises `ValueError` if not.

## Errors

| Condition | Exception |
|-----------|-----------|
| Invalid API key | `AuthenticationError` |
| Serial number not found | `NotFoundError` |
| Server error | `ServerError` |

## Factory

```python
inv = client.inverter("CE2345G123")
health = inv.get_health()          # -> list[InverterHealthCheck]
flows = inv.get_energy_flows(start, end)   # -> list[EnergyFlowData]
```
