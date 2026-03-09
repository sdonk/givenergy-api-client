# GivEnergy API Client

A Python client library for the [GivEnergy Cloud API v1](https://givenergy.cloud/docs/api/v1).

- **Sync and async** — every method has an `a`-prefixed async variant
- **Typed** — all responses are validated Pydantic v2 models
- **Simple** — one client instance, domain objects per resource

---

## Installation

```bash
pip install givenergy-api-client
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add givenergy-api-client
```

---

## Authentication

Create a `GivenergyAPIClient` with your API key. All subsequent calls use it automatically.

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
```

---

## Quick start

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")

# Your account
account = client.account().get()
print(account.email)       # 'you@example.com'
print(account.timezone)    # 'Europe/London'

# Inverter health
health = client.inverter("CE2345G123").get_health()
for check in health:
    print(check.name, check.value, check.unit)

# Live EMS snapshot
snapshot = client.ems("CE2345G123").get_latest()
print(f"Battery: {snapshot.battery_power} W")
print(f"Grid:    {snapshot.grid_power} W")
```

---

## Resources

### Account

```python
account_resource = client.account()

# Authenticated user
me = account_resource.get()

# Look up by ID or username
user  = account_resource.get_by_id(user_id="42")
found = account_resource.search(username="someone@example.com")

# Devices on an account
devices = account_resource.get_devices(username="someone@example.com")
for device in devices.data:
    print(device.serial_number, device.type, device.inverter_status)

# Child accounts (paginated)
children = account_resource.list_children(page=1, page_size=25)
print(f"Page {children.meta.current_page} of {children.meta.last_page}")
```

### Inverter

```python
inverter = client.inverter("CE2345G123")

# Health checks
for check in inverter.get_health():
    print(f"{check.name}: {check.value} {check.unit or ''} [{check.status}]")

# Energy flows for a time range
from datetime import datetime, timezone
from givenergy_api_client.energy_flow import EnergyDataFlowGrouping

flows = inverter.get_energy_flows(
    start_time=datetime(2024, 6, 1, tzinfo=timezone.utc),
    end_time=datetime(2024, 6, 2, tzinfo=timezone.utc),
    grouping=EnergyDataFlowGrouping.HALF_HOURLY,
)
for flow in flows:
    print(flow.type.name, [p.value for p in flow.data[:3]])

# Send a debug command
result = inverter.send_debug_command(hex_command="0x0003")
print(result.success)
```

### EMS (Energy Management System)

```python
snapshot = client.ems("CE2345G123").get_latest()

print(f"Battery remaining: {snapshot.battery_wh_remaining} Wh")
print(f"Battery power:     {snapshot.battery_power} W")
print(f"Grid power:        {snapshot.grid_power} W")

for inv in snapshot.inverters:
    print(f"  Inverter {inv.serial}: {inv.power} W")
for meter in snapshot.meters:
    print(f"  Meter {meter.meter_id}: {meter.power} W")
```

### EV Charger

```python
charger = client.ev_charger("uuid-1234-abcd")

# Current status
info = charger.get()
print(info.alias, info.online, info.status)

# Meter data
from datetime import datetime, timezone

readings = charger.get_meter_data(
    start_time=datetime(2024, 6, 1, tzinfo=timezone.utc),
    end_time=datetime(2024, 6, 2, tzinfo=timezone.utc),
    measurands=["Power.Active.Import"],
    meter_ids=["meter-1"],
)
for reading in readings.data:
    for m in reading.measurements:
        print(f"{reading.timestamp}: {m.value} {m.unit}")

# Charging sessions
sessions = charger.list_sessions(page=1, page_size=10)
for s in sessions.data:
    print(s.started_at, s.meter_start, s.meter_stop)

# Available commands and execution
commands = charger.list_commands()
result = charger.execute_command(
    command_id="RemoteStartTransaction",
    payload={"idTag": "RFID-001"},
)
print(result.success, result.message)
```

### Inverter Presets

```python
presets_resource = client.inverter_preset("CE2345G123")

# List available presets
for preset in presets_resource.list_presets():
    print(preset.id, preset.name)
    for param in preset.parameters:
        print(f"  {param.id}: {param.type}")

# Read current values for a preset
current = presets_resource.get_preset(preset_id=1)
print(current.extra_fields)

# Apply a preset
result = presets_resource.apply_preset(
    preset_id=1,
    payload={"start_time": "06:00", "end_time": "09:00"},
)
print(result.success, result.message)
```

---

## Pagination

List endpoints return a `PaginatedResult[T]` with `.data` and `.meta`.

```python
page = client.account().list_children(page=1, page_size=25)

print(page.meta.current_page)  # 1
print(page.meta.last_page)     # 4
print(page.meta.total)         # 87

for child in page.data:
    print(child.email)

# Iterate all pages
page_num = 1
while True:
    page = client.account().list_children(page=page_num, page_size=25)
    for child in page.data:
        print(child.email)
    if page.meta.current_page >= page.meta.last_page:
        break
    page_num += 1
```

---

## Error handling

```python
from givenergy_api_client.exceptions import (
    AuthenticationError,
    NotFoundError,
    APIValidationError,
    ServerError,
    GivEnergyAPIError,
)

try:
    account = client.account().get_by_id(user_id="999")
except AuthenticationError:
    print("Invalid or expired API key")
except NotFoundError:
    print("Account not found")
except APIValidationError as e:
    print(f"Bad request: {e}")
except ServerError as e:
    print(f"Server error {e.status_code}")
except GivEnergyAPIError as e:
    print(f"Unexpected API error: {e}")
```

---

## Async usage

Every method has an `a`-prefixed async variant. Use `async with` and `await`:

```python
import asyncio
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")

async def main() -> None:
    # Account
    me = await client.account().aget()

    # Inverter health
    health = await client.inverter("CE2345G123").aget_health()

    # EMS snapshot
    snapshot = await client.ems("CE2345G123").aget_latest()

    # Run multiple requests concurrently
    account, snapshot = await asyncio.gather(
        client.account().aget(),
        client.ems("CE2345G123").aget_latest(),
    )
    print(account.email, snapshot.battery_power)

asyncio.run(main())
```

---

## Full documentation

The full API reference, including all method signatures and response models, is hosted at:

**<https://sdonk.github.io/givenergy-api-client/>**

To build and browse the docs locally:

```bash
# Install dependencies
uv sync --all-groups

# Serve with live reload at http://127.0.0.1:8000
uv run mkdocs serve

# Or build static HTML to site/
uv run mkdocs build
```

The docs cover:

- [Getting Started](https://sdonk.github.io/givenergy-api-client/) — installation and first call
- [Account](https://sdonk.github.io/givenergy-api-client/account/) — all account methods
- [Inverter](https://sdonk.github.io/givenergy-api-client/inverter/) — health, energy flows, debug
- [EMS](https://sdonk.github.io/givenergy-api-client/ems/) — system snapshots
- [EV Charger](https://sdonk.github.io/givenergy-api-client/ev-charger/) — sessions, meter data, commands
- [Inverter Presets](https://sdonk.github.io/givenergy-api-client/inverter-presets/) — preset management
- [Error Handling](https://sdonk.github.io/givenergy-api-client/error-handling/) — exception reference
- [Async Usage](https://sdonk.github.io/givenergy-api-client/async/) — async patterns
- [Advanced Topics](https://sdonk.github.io/givenergy-api-client/advanced/) — custom transports, timeouts

---

## Development

```bash
# Install all dependencies including dev
uv sync --all-groups

# Run tests
uv run pytest

# Lint and format
uv run ruff check --fix .
uv run ruff format .

# Type check
uv run ty .
```

## License

MIT
