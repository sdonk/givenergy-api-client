# EV Charger

This page covers all EV charger operations — listing chargers, reading meter data,
managing commands, and querying charging sessions.

All examples assume a configured client:

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
```

---

## Listing all chargers

Returns a paginated list of all EV chargers registered to this account.

=== "Sync"

    ```python
    >>> result = client.list_ev_chargers()
    >>> result.data[0].uuid
    'uuid-1234-abcd'
    >>> result.data[0].status
    'available'

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(client.alist_ev_chargers())
    >>> result.data[0].uuid
    'uuid-1234-abcd'

    ```

---

## Getting charger details

Returns the full details for a specific charger by UUID.

=== "Sync"

    ```python
    >>> charger = client.ev_charger("uuid-1234-abcd").get()
    >>> charger.uuid
    'uuid-1234-abcd'
    >>> charger.online
    True
    >>> charger.alias
    'Home Charger'

    ```

=== "Async"

    ```python
    >>> charger = asyncio.run(client.ev_charger("uuid-1234-abcd").aget())
    >>> charger.online
    True

    ```

---

## Meter data

Returns paginated meter readings for a charger over a time window.
`start_time`, `end_time`, `measurands`, and `meter_ids` are all required.

=== "Sync"

    ```python
    >>> import datetime as dt
    >>> start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
    >>> end = dt.datetime(2025, 1, 2, 0, 0, tzinfo=dt.timezone.utc)
    >>> result = client.ev_charger("uuid-1234-abcd").get_meter_data(
    ...     start_time=start,
    ...     end_time=end,
    ...     measurands=["Power.Active.Import"],
    ...     meter_ids=["m1"],
    ... )
    >>> result.data[0].measurements[0].measurand
    'Power.Active.Import'
    >>> result.data[0].measurements[0].value
    7.2

    ```

=== "Async"

    ```python
    >>> import datetime as dt
    >>> start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
    >>> end = dt.datetime(2025, 1, 2, 0, 0, tzinfo=dt.timezone.utc)
    >>> result = asyncio.run(
    ...     client.ev_charger("uuid-1234-abcd").aget_meter_data(
    ...         start_time=start,
    ...         end_time=end,
    ...         measurands=["Power.Active.Import"],
    ...         meter_ids=["m1"],
    ...     )
    ... )
    >>> result.data[0].measurements[0].value
    7.2

    ```

---

## Available commands

Returns the list of command IDs supported by a charger.

=== "Sync"

    ```python
    >>> commands = client.ev_charger("uuid-1234-abcd").list_commands()
    >>> commands[0]
    'charge-limit'

    ```

=== "Async"

    ```python
    >>> commands = asyncio.run(client.ev_charger("uuid-1234-abcd").alist_commands())
    >>> commands[0]
    'charge-limit'

    ```

---

## Command state

Returns the current configured state of a specific command.
Dynamic fields that vary by command type are available through `extra_fields`.

See [Advanced Topics — Open-schema responses](advanced.md#open-schema-responses) for more detail.

=== "Sync"

    ```python
    >>> state = client.ev_charger("uuid-1234-abcd").get_command(command_id="charge-limit")
    >>> state.extra_fields["charge_limit"]
    32
    >>> state.extra_fields["unit"]
    'A'

    ```

=== "Async"

    ```python
    >>> state = asyncio.run(
    ...     client.ev_charger("uuid-1234-abcd").aget_command(command_id="charge-limit")
    ... )
    >>> state.extra_fields["charge_limit"]
    32

    ```

---

## Executing a command

Sends a command to the charger with a payload of key/value parameters.

=== "Sync"

    ```python
    >>> result = client.ev_charger("uuid-1234-abcd").execute_command(
    ...     command_id="charge-limit",
    ...     payload={"charge_limit": 16},
    ... )
    >>> result.success
    True
    >>> result.message
    'Command executed'

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(
    ...     client.ev_charger("uuid-1234-abcd").aexecute_command(
    ...         command_id="charge-limit",
    ...         payload={"charge_limit": 16},
    ...     )
    ... )
    >>> result.success
    True

    ```

---

## Charging sessions

Returns a paginated list of charging sessions. Both `start_time` and `end_time`
are optional — omit them to retrieve all sessions.

### Without time filters

=== "Sync"

    ```python
    >>> result = client.ev_charger("uuid-1234-abcd").list_sessions()
    >>> result.data[0].meter_stop
    15.0

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(client.ev_charger("uuid-1234-abcd").alist_sessions())
    >>> result.data[0].meter_stop
    15.0

    ```

### With time filters

=== "Sync"

    ```python
    >>> import datetime as dt
    >>> start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
    >>> end = dt.datetime(2025, 1, 2, 0, 0, tzinfo=dt.timezone.utc)
    >>> result = client.ev_charger("uuid-1234-abcd").list_sessions(
    ...     start_time=start,
    ...     end_time=end,
    ... )
    >>> result.data[0].meter_stop
    15.0

    ```

=== "Async"

    ```python
    >>> import datetime as dt
    >>> start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
    >>> end = dt.datetime(2025, 1, 2, 0, 0, tzinfo=dt.timezone.utc)
    >>> result = asyncio.run(
    ...     client.ev_charger("uuid-1234-abcd").alist_sessions(
    ...         start_time=start,
    ...         end_time=end,
    ...     )
    ... )
    >>> result.data[0].meter_stop
    15.0

    ```
