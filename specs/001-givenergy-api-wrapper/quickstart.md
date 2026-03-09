# Quickstart: GivEnergy API Client — Full Coverage

## Installation

```bash
pip install givenergy-api-client
```

## Authentication

All operations require a GivEnergy API key (Bearer token).

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
```

---

## Account Operations

```python
from givenergy_api_client.account import Account

account = client.account()

# Get authenticated user's account
me = account.get()
print(me.email, me.timezone)

# Look up a specific account by ID
other = account.get_by_id("12345")

# Search by username
found = account.search("johndoe")

# List devices for a username
devices = account.get_devices("johndoe", page=1, page_size=20)

# List child accounts (installer/multi-account scenarios)
children = account.list_children(page=1)

# SSO-linked accounts
sso_accounts = account.get_sso_accounts()
```

---

## Inverter Monitoring

```python
from givenergy_api_client.inverter import Inverter
from givenergy_api_client.energy_flow import EnergyDataFlowGrouping
import datetime

inv = client.inverter("CE2345G123")

# Health checks
for check in inv.get_health():
    print(check.name, check.value, check.status)

# Energy flows (must use timezone-aware datetimes)
start = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
end   = datetime.datetime(2026, 3, 7, tzinfo=datetime.timezone.utc)
flows = inv.get_energy_flows(start, end, grouping=EnergyDataFlowGrouping.DAILY)
for flow in flows:
    print(flow.type, [p.value for p in flow.data])

# Advanced: send raw debug command (use with caution)
result = inv.send_debug_command("0102030405")
print(result.success)
```

---

## EMS Plant Data

```python
from givenergy_api_client.ems import EMS

ems = client.ems("CE2345G123")
snapshot = ems.get_latest()
print(snapshot.battery_power, snapshot.battery_wh_remaining, snapshot.grid_power)
```

---

## EV Charger

```python
from givenergy_api_client.ev_charger import EVCharger
import datetime

# List all chargers
all_chargers = client.list_ev_chargers()

# Work with a specific charger
charger = client.ev_charger("uuid-1234-abcd")
info = charger.get()
print(info.online, info.status)

# Meter data (all params required)
start = datetime.datetime(2026, 3, 6, tzinfo=datetime.timezone.utc)
end   = datetime.datetime(2026, 3, 7, tzinfo=datetime.timezone.utc)
meter_data = charger.get_meter_data(
    start_time=start,
    end_time=end,
    measurands=["Energy.Active.Import.Register"],
    meter_ids=["meter-1"],
)

# Charging sessions
sessions = charger.list_sessions(start_time=start, end_time=end)

# Available commands
commands = charger.list_commands()

# Execute a command
result = charger.execute_command("StartCharging", {"connector_id": 1})
print(result.success, result.message)
```

---

## Inverter Presets

```python
from givenergy_api_client.inverter_preset import InverterPreset

presets = client.inverter_preset("CE2345G123")

# List available presets
for p in presets.list_presets():
    print(p.id, p.name, p.description)

# Read current values of a preset
current = presets.get_preset(3)

# Apply a preset
result = presets.apply_preset(3, {"charge_target": 80, "start_time": "00:30"})
print(result.success, result.message)
```

---

## Async Usage

Every sync method has an `a`-prefixed async variant:

```python
import asyncio
from givenergy_api_client.client import GivenergyAPIClient

async def main():
    client = GivenergyAPIClient(api_key="your-api-key")

    account = client.account()
    me = await account.aget()

    inv = client.inverter("CE2345G123")
    health = await inv.aget_health()

    charger = client.ev_charger("uuid-1234-abcd")
    result = await charger.aexecute_command("StopCharging", {})

asyncio.run(main())
```

---

## Error Handling

```python
from givenergy_api_client.exceptions import (
    AuthenticationError,
    NotFoundError,
    APIValidationError,
    ServerError,
    GivEnergyAPIError,
)

try:
    data = client.account().get()
except AuthenticationError:
    print("Invalid or expired API key")
except NotFoundError:
    print("Resource not found")
except APIValidationError as e:
    print(f"Request invalid: {e}")
except ServerError as e:
    print(f"Server error {e.status_code}: {e}")
except GivEnergyAPIError as e:
    print(f"Unexpected API error: {e}")
```
