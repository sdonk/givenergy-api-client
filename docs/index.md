# Getting Started

This page shows you how to install the GivEnergy API Client, authenticate with your API key,
and make your first API call — all in under five minutes.

---

## Installation

```bash
pip install givenergy-api-client
```

---

## Authentication

Create a `GivenergyAPIClient` instance with your GivEnergy API key:

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
```

!!! tip "Placeholder values"
    Replace `"your-api-key"` with your real API key before running.
    All code examples use placeholder values such as `"your-api-key"`, `"CE2345G123"`, and
    `"uuid-1234-abcd"` to make it clear which values you need to substitute.

---

## Your First API Call

Retrieve your account details:

```python
>>> account = client.account().get()
>>> account.email
'test@example.com'
>>> account.name
'Test User'

```

---

## Next Steps

Explore the resource-specific pages for complete method references:

- [Account](account.md) — account lookup, device listing, child accounts, SSO
- [Inverter](inverter.md) — health checks, energy flows, debug commands
- [EMS](ems.md) — latest system snapshot
- [EV Charger](ev-charger.md) — charger status, meter data, charging sessions
- [Inverter Presets](inverter-presets.md) — list, read, and apply presets

For error handling, async usage, and advanced patterns see:

- [Error Handling](error-handling.md)
- [Async Usage](async.md)
- [Advanced Topics](advanced.md)
