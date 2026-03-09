# Inverter

This page covers inverter health checks, energy flow data, and raw debug commands.

All examples assume a configured client and an inverter serial number:

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
inverter = client.inverter("CE2345G123")
```

---

## Health checks

Returns a list of health metrics for the inverter.

=== "Sync"

    ```python
    >>> checks = client.inverter("CE2345G123").get_health()
    >>> checks[0].name
    'battery_voltage'
    >>> checks[0].status
    'ok'
    >>> checks[0].value
    52.4

    ```

=== "Async"

    ```python
    >>> checks = asyncio.run(client.inverter("CE2345G123").aget_health())
    >>> checks[0].name
    'battery_voltage'

    ```

---

## Energy flows

!!! warning "Timezone-aware datetimes required"
    Both `start_time` and `end_time` **must** be timezone-aware `datetime` objects.
    Passing a naive `datetime` (one without `tzinfo`) raises a `ValueError` immediately,
    before any network call is made.

    ```python
    # CORRECT — timezone-aware
    import datetime as dt
    start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)

    # WRONG — naive datetime raises ValueError
    start = dt.datetime(2025, 1, 1, 0, 0)  # no tzinfo!
    ```

Returns time-series energy flow data between two timezone-aware datetimes.

=== "Sync"

    ```python
    >>> import datetime as dt
    >>> start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
    >>> end = dt.datetime(2025, 1, 2, 0, 0, tzinfo=dt.timezone.utc)
    >>> flows = client.inverter("CE2345G123").get_energy_flows(start_time=start, end_time=end)
    >>> flows[0].type.name
    'PV_TO_HOME'
    >>> flows[0].data[0].value
    2500.0

    ```

=== "Async"

    ```python
    >>> import datetime as dt
    >>> start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
    >>> end = dt.datetime(2025, 1, 2, 0, 0, tzinfo=dt.timezone.utc)
    >>> flows = asyncio.run(client.inverter("CE2345G123").aget_energy_flows(start_time=start, end_time=end))
    >>> flows[0].type.name
    'PV_TO_HOME'

    ```

The `grouping` parameter controls the time resolution. Available options:

| Grouping | Value | Description |
|----------|-------|-------------|
| `EnergyDataFlowGrouping.HALF_HOURLY` | default | One data point per 30 minutes |
| `EnergyDataFlowGrouping.DAILY` | — | One data point per day |
| `EnergyDataFlowGrouping.MONTHLY` | — | One data point per month |
| `EnergyDataFlowGrouping.YEARLY` | — | One data point per year |

---

## Debug commands

!!! danger "Use with caution"
    `send_debug_command()` sends raw hex commands directly to the inverter firmware.
    Incorrect commands can cause unexpected inverter behaviour or trip safety protections.
    Only use this method if you know exactly what command you are sending.

Sends a raw hex command to the inverter and returns the result.

=== "Sync"

    ```python
    >>> result = client.inverter("CE2345G123").send_debug_command(hex_command="0601")
    >>> result.success
    True
    >>> result.code
    0

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(client.inverter("CE2345G123").asend_debug_command(hex_command="0601"))
    >>> result.success
    True

    ```
