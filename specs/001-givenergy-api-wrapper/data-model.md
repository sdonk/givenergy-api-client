# Data Model: GivEnergy API Full Coverage

**Branch**: `001-givenergy-api-wrapper` | **Date**: 2026-03-07

All models use `ConfigDict(frozen=True)`. Fields are annotated with their Python types.
Optional fields default to `None`.

---

## Module: `exceptions.py` (NEW)

```
GivEnergyAPIError(Exception)
  └── AuthenticationError       # HTTP 401 — invalid or expired API key
  └── NotFoundError             # HTTP 404 — resource not found
  └── APIValidationError        # HTTP 422 — request rejected by API validation
  └── ServerError               # HTTP 5xx — server-side failure
        field: status_code: int
```

All exceptions carry the original API error message as the exception message.

---

## Module: `account.py` (EXTEND)

### Existing models (unchanged)
- `Account` — full user account record

### New models

**`AccountDevice`**
| Field | Type | Notes |
|-------|------|-------|
| `serial_number` | `str` | Dongle serial number |
| `type` | `str` | e.g. `"WIFI"` |
| `site_id` | `int \| None` | Optional site association |
| `inverter_serial` | `str` | Linked inverter serial |
| `inverter_status` | `str` | e.g. `"NORMAL"`, `"WAITING"` |

### Domain class

**`Account`** (domain class)

Constructor: `Account(client: GivenergyAPIClient)`

| Method | Async variant | Returns | Endpoint |
|--------|--------------|---------|----------|
| `get()` | `aget()` | `Account` | `GET /account` |
| `get_by_id(user_id)` | `aget_by_id(user_id)` | `Account` | `GET /account/{user_id}` |
| `search(username)` | `asearch(username)` | `Account` | `GET /account/search/{username}` |
| `get_devices(username, *, page, page_size)` | `aget_devices(...)` | `dict` | `GET /account/{username}/devices` |
| `list_children(*, page, page_size)` | `alist_children(...)` | `dict` | `GET /account-children` |
| `list_children_for_user(user_id, *, page, page_size)` | `alist_children_for_user(...)` | `dict` | `GET /account-children/{user_id}` |
| `get_sso_accounts()` | `aget_sso_accounts()` | `dict` | `GET /sso/me/accounts` |

*`dict` return type for paginated endpoints includes raw `data` list + `meta` pagination
object as returned by the API.*

---

## Module: `inverter.py` (EXTEND from stub)

### New models

**`InverterHealthCheck`**
| Field | Type | Notes |
|-------|------|-------|
| `name` | `str` | Metric name |
| `value` | `str \| int \| float` | Current reading |
| `status` | `str` | e.g. `"OK"`, `"WARNING"`, `"ERROR"` |
| `unit` | `str \| None` | Unit of measure |

**`EnergyFlowPoint`**
| Field | Type | Notes |
|-------|------|-------|
| `timestamp` | `datetime` | Data point time |
| `value` | `float` | Energy value (Wh or kWh per API) |

**`EnergyFlowData`**
| Field | Type | Notes |
|-------|------|-------|
| `type` | `EnergyDataFlowType` | Flow type (enum from `energy_flow.py`) |
| `data` | `list[EnergyFlowPoint]` | Ordered time series |

**`DebugCommandResult`**
| Field | Type | Notes |
|-------|------|-------|
| `success` | `bool` | Whether command was accepted |
| `code` | `int` | Response code |

### Domain class

**`Inverter`** (domain class)

Constructor: `Inverter(client: GivenergyAPIClient, serial_number: str)`

| Method | Async variant | Returns | Endpoint |
|--------|--------------|---------|----------|
| `get_health()` | `aget_health()` | `list[InverterHealthCheck]` | `GET /inverter/{sn}/health` |
| `get_energy_flows(start_time, end_time, *, grouping)` | `aget_energy_flows(...)` | `list[EnergyFlowData]` | `POST /inverter/{sn}/energy-flows` |
| `send_debug_command(hex_command)` | `asend_debug_command(hex_command)` | `DebugCommandResult` | `POST /inverter/{sn}/debug/transparent/send` |

Parameters:
- `start_time: datetime` — timezone-aware; raises `ValueError` if naive
- `end_time: datetime` — timezone-aware; must be after `start_time`
- `grouping: EnergyDataFlowGrouping` — defaults to `HALF_HOURLY`

---

## Module: `energy_flow.py` (EXTEND from stub)

Enums moved here from `client.py` (re-exported from `client.py` for compat):

**`EnergyDataFlowGrouping`** (IntEnum)
| Name | Value |
|------|-------|
| `HALF_HOURLY` | 0 |
| `DAILY` | 1 |
| `MONTHLY` | 2 |
| `YEARLY` | 3 |
| `TOTAL` | 4 |

**`EnergyDataFlowType`** (IntEnum)
| Name | Value |
|------|-------|
| `PV_TO_HOME` | 0 |
| `PV_TO_BATTERY` | 1 |
| `PV_TO_GRID` | 2 |
| `GRID_TO_HOME` | 3 |
| `GRID_TO_BATTERY` | 4 |
| `BATTERY_TO_HOME` | 5 |
| `BATTERY_TO_GRID` | 6 |

---

## Module: `ems.py` (EXTEND from stub)

### New models

**`EMSInverterReading`**
| Field | Type | Notes |
|-------|------|-------|
| `serial` | `str` | Inverter serial |
| `power` | `float` | Current power (W) |

**`EMSMeterReading`**
| Field | Type | Notes |
|-------|------|-------|
| `meter_id` | `str` | Meter identifier |
| `power` | `float` | Current power (W) |

**`EMSSnapshot`**
| Field | Type | Notes |
|-------|------|-------|
| `battery_power` | `float` | Current battery power (W) |
| `battery_wh_remaining` | `float` | Remaining charge (Wh) |
| `grid_power` | `float` | Current grid power (W) |
| `inverters` | `list[EMSInverterReading]` | Per-inverter readings |
| `meters` | `list[EMSMeterReading]` | Per-meter readings |

### Domain class

**`EMS`** (domain class)

Constructor: `EMS(client: GivenergyAPIClient, inverter_serial_number: str)`

| Method | Async variant | Returns | Endpoint |
|--------|--------------|---------|----------|
| `get_latest()` | `aget_latest()` | `EMSSnapshot` | `GET /ems/{sn}/system-data/latest` |

---

## Module: `ev_charger.py` (NEW)

### New models

**`EVCharger`**
| Field | Type | Notes |
|-------|------|-------|
| `uuid` | `str` | Charger UUID |
| `serial_number` | `str` | Hardware serial |
| `type` | `str` | Charger type |
| `alias` | `str \| None` | Human-readable name |
| `online` | `bool` | Connectivity status |
| `status` | `str` | Operational status |

**`EVChargerMeasurement`**
| Field | Type | Notes |
|-------|------|-------|
| `measurand` | `str` | What is being measured |
| `value` | `float` | Reading value |
| `unit` | `str` | Unit of measure |

**`EVChargerMeterReading`**
| Field | Type | Notes |
|-------|------|-------|
| `meter_id` | `str` | Meter identifier |
| `timestamp` | `datetime` | Reading time |
| `measurements` | `list[EVChargerMeasurement]` | One or more measurands |

**`ChargingSession`**
| Field | Type | Notes |
|-------|------|-------|
| `started_by` | `str \| None` | Actor who started session |
| `meter_start` | `float` | Odometer at session start (Wh) |
| `started_at` | `datetime` | Session start time |
| `stopped_by` | `str \| None` | Actor who stopped session |
| `meter_stop` | `float \| None` | Odometer at session end (Wh) |
| `stopped_at` | `datetime \| None` | Session end time |

**`EVChargerCommandResult`**
| Field | Type | Notes |
|-------|------|-------|
| `code` | `int` | Numeric response code |
| `success` | `bool` | Whether command succeeded |
| `message` | `str` | Human-readable result message |

### Domain class

**`EVCharger`** (domain class)

Constructor: `EVCharger(client: GivenergyAPIClient, charger_uuid: str)`

| Method | Async variant | Returns | Endpoint |
|--------|--------------|---------|----------|
| `get()` | `aget()` | `EVCharger` | `GET /ev-charger/{uuid}` |
| `get_meter_data(start_time, end_time, measurands, meter_ids, *, page, page_size)` | `aget_meter_data(...)` | `dict` | `GET /ev-charger/{uuid}/meter-data` |
| `list_commands()` | `alist_commands()` | `list[str]` | `GET /ev-charger/{uuid}/commands` |
| `get_command(command_id)` | `aget_command(command_id)` | `dict` | `GET /ev-charger/{uuid}/commands/{id}` |
| `execute_command(command_id, payload)` | `aexecute_command(command_id, payload)` | `EVChargerCommandResult` | `POST /ev-charger/{uuid}/commands/{id}` |
| `list_sessions(*, start_time, end_time, page, page_size)` | `alist_sessions(...)` | `dict` | `GET /ev-charger/{uuid}/charging-sessions` |

**Top-level factory method** on `GivenergyAPIClient`:
- `list_ev_chargers(*, page, page_size)` / `alist_ev_chargers(...)` → `dict`
  (`GET /ev-charger`) — list all chargers without a specific UUID context.

---

## Module: `inverter_preset.py` (NEW)

### New models

**`PresetParameter`**
| Field | Type | Notes |
|-------|------|-------|
| `id` | `str` | Parameter identifier |
| `name` | `str` | Human-readable label |
| `type` | `str` | Data type hint |
| `validation` | `dict \| None` | Validation constraints from API |

**`InverterPreset`**
| Field | Type | Notes |
|-------|------|-------|
| `id` | `int` | Preset numeric ID |
| `identifier` | `str` | Slug identifier |
| `name` | `str` | Display name |
| `description` | `str` | What the preset does |
| `parameters` | `list[PresetParameter]` | Configurable parameters |

**`PresetApplyResult`**
| Field | Type | Notes |
|-------|------|-------|
| `success` | `bool` | Whether preset was applied |
| `message` | `str` | Human-readable result message |

### Domain class

**`InverterPreset`** (domain class)

Constructor: `InverterPreset(client: GivenergyAPIClient, serial_number: str)`

| Method | Async variant | Returns | Endpoint |
|--------|--------------|---------|----------|
| `list_presets()` | `alist_presets()` | `list[InverterPreset]` | `GET /inverter/{sn}/presets` |
| `get_preset(preset_id)` | `aget_preset(preset_id)` | `dict` | `GET /inverter/{sn}/presets/{id}` |
| `apply_preset(preset_id, payload)` | `aapply_preset(preset_id, payload)` | `PresetApplyResult` | `POST /inverter/{sn}/presets/{preset}` |

*`get_preset` returns `dict` because the structure of preset values is
preset-specific and not enumerable from the spec.*

---

## Client Factory Methods Summary

Added to `GivenergyAPIClient`:

| Factory method | Returns | Notes |
|---------------|---------|-------|
| `account()` | `Account` | No additional args |
| `inverter(serial_number: str)` | `Inverter` | Binds to one inverter |
| `ems(inverter_serial_number: str)` | `EMS` | Binds to one EMS inverter |
| `ev_charger(charger_uuid: str)` | `EVCharger` | Binds to one charger |
| `inverter_preset(serial_number: str)` | `InverterPreset` | Binds to one inverter |
| `list_ev_chargers(*, page, page_size)` | `dict` | Collection endpoint — no UUID context |
| `alist_ev_chargers(*, page, page_size)` | `dict` | Async variant |

Existing methods (`get_account`, `get_communication_devices`, `get_communication_device`)
remain unchanged.
