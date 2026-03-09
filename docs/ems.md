# EMS

This page covers the Energy Management System (EMS) resource, which provides aggregate
plant metrics for a GivEnergy inverter installation.

!!! note "Compatibility"
    EMS data is only available on inverters that support the EMS feature.
    Calling `get_latest()` on an incompatible inverter returns a `404 Not Found`
    response, which the SDK raises as a `NotFoundError`.

All examples assume a configured client and an inverter serial number:

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
ems = client.ems("CE2345G123")
```

---

## Latest snapshot

Returns the current aggregate EMS snapshot for the inverter installation.
The snapshot includes battery state, grid power, and per-inverter and per-meter readings.

=== "Sync"

    ```python
    >>> snapshot = client.ems("CE2345G123").get_latest()
    >>> snapshot.battery_power
    -1200.0
    >>> snapshot.battery_wh_remaining
    8500.0
    >>> snapshot.grid_power
    300.0
    >>> snapshot.inverters[0].serial
    'CE2345G123'
    >>> snapshot.inverters[0].power
    2500.0
    >>> snapshot.meters[0].meter_id
    'm1'

    ```

=== "Async"

    ```python
    >>> snapshot = asyncio.run(client.ems("CE2345G123").aget_latest())
    >>> snapshot.battery_power
    -1200.0
    >>> snapshot.grid_power
    300.0

    ```

!!! note "Sign convention"
    A negative `battery_power` means the battery is discharging (supplying power).
    A positive value means it is charging (consuming power).
