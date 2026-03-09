# Async Usage

Every synchronous SDK method has an async counterpart with an `a`-prefix and identical
parameters and return type. Use the async variants inside `async def` functions and
`await` their results.

---

## Pattern

| Sync method | Async counterpart |
|-------------|-------------------|
| `client.account().get()` | `await client.account().aget()` |
| `client.inverter(sn).get_health()` | `await client.inverter(sn).aget_health()` |
| `client.ems(sn).get_latest()` | `await client.ems(sn).aget_latest()` |
| `client.ev_charger(uuid).get()` | `await client.ev_charger(uuid).aget()` |
| `client.inverter_preset(sn).apply_preset(...)` | `await client.inverter_preset(sn).aapply_preset(...)` |

---

## Single-resource async example

Retrieve account details asynchronously:

```python
>>> account = asyncio.run(client.account().aget())
>>> account.email
'test@example.com'

```

In a real `async def` function you would use `await` directly:

```python
import asyncio
from givenergy_api_client.client import GivenergyAPIClient

async def main() -> None:
    client = GivenergyAPIClient(api_key="your-api-key")
    account = await client.account().aget()
    print(account.email)

asyncio.run(main())
```

---

## Concurrent multi-resource example

Use `asyncio.gather()` to call multiple resources simultaneously:

```python
>>> async def fetch_all():
...     account, health = await asyncio.gather(
...         client.account().aget(),
...         client.inverter("CE2345G123").aget_health(),
...     )
...     return account, health
>>> account, health = asyncio.run(fetch_all())
>>> account.email
'test@example.com'
>>> health[0].name
'battery_voltage'

```

---

## When to use async vs sync

| Use **sync** when… | Use **async** when… |
|--------------------|----------------------|
| Writing scripts or CLI tools | Running inside an `async` web framework (FastAPI, aiohttp, …) |
| Making one call at a time | Fetching multiple resources concurrently |
| Simplicity is the priority | Low latency matters and calls can overlap |

The async API makes no difference to the data returned — only to how the call
is scheduled on the event loop.
