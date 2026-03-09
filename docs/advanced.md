# Advanced Topics

This page covers three patterns that are less obvious on first use:
pagination, open-schema responses, and timezone-aware datetimes.

---

## Pagination

Methods that return large collections return a `PaginatedResult` object with two attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `data` | `list[T]` | Items on the current page |
| `meta.current_page` | `int` | Current page number (1-based) |
| `meta.last_page` | `int` | Total number of pages |
| `meta.per_page` | `int` | Items per page |
| `meta.total` | `int` | Total items across all pages |

### Fetching all pages

Use `meta.last_page` to detect when all pages have been fetched:

```python
>>> page = 1
>>> all_devices = []
>>> while True:
...     result = client.account().get_devices(username="jdoe", page=page)
...     all_devices.extend(result.data)
...     if result.meta.last_page == page:
...         break
...     page += 1
>>> len(all_devices)
1

```

### Checking pagination metadata

```python
>>> result = client.account().get_devices(username="jdoe")
>>> result.meta.current_page
1
>>> result.meta.last_page
1
>>> result.meta.per_page
15
>>> result.meta.total
1

```

---

## Open-schema responses

Some endpoints return responses whose exact fields vary by context — for example,
the current state of an EV charger command, or the current values of an inverter preset.
Because these fields are not known at compile time, the SDK captures them all in a
single `extra_fields` dictionary.

### EV charger command state

```python
>>> state = client.ev_charger("uuid-1234-abcd").get_command(command_id="charge-limit")
>>> state.extra_fields
{'charge_limit': 32, 'unit': 'A'}
>>> state.extra_fields["charge_limit"]
32

```

### Inverter preset current values

```python
>>> values = client.inverter_preset("CE2345G123").get_preset(preset_id=1)
>>> values.extra_fields
{'start_time': '00:30', 'end_time': '05:00'}
>>> values.extra_fields["start_time"]
'00:30'

```

All values in `extra_fields` are typed as `str | int | float | bool | None`.
Cast them as needed for arithmetic or comparison operations.

---

## Timezone-aware datetimes

Any method that accepts a time range requires **timezone-aware** `datetime` objects.
A naive `datetime` (one without `tzinfo`) raises a `ValueError` immediately, before
any network call is made.

### Correct — timezone-aware

```python
>>> import datetime as dt
>>> start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
>>> end = dt.datetime(2025, 1, 2, 0, 0, tzinfo=dt.timezone.utc)
>>> start.tzinfo is not None
True

```

Using `datetime.now()` with a timezone:

```python
>>> import datetime as dt
>>> now = dt.datetime.now(tz=dt.timezone.utc)
>>> now.tzinfo is not None
True

```

### Incorrect — naive datetime raises ValueError

```python
>>> import datetime as dt
>>> naive = dt.datetime(2025, 1, 1, 0, 0)   # no tzinfo!
>>> naive.tzinfo is None
True

```

Passing a naive datetime to `get_energy_flows()` raises:

```
ValueError: start_time must be timezone-aware
```

### Recommended pattern

Always construct datetimes with an explicit timezone:

```python
import datetime as dt

# UTC
start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=dt.timezone.utc)

# Local timezone (Python 3.12+)
local_tz = dt.timezone(dt.timedelta(hours=1))  # UTC+1
start = dt.datetime(2025, 1, 1, 0, 0, tzinfo=local_tz)
```
