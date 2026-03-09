# Inverter Presets

This page covers inverter configuration presets — listing the available presets,
reading current values, and applying a preset.

All examples assume a configured client and an inverter serial number:

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
presets = client.inverter_preset("CE2345G123")
```

---

## Listing presets

Returns all configuration presets available for the inverter.
Each preset has an `id`, a human-readable `name`, a description, and a list of
configurable `parameters`.

=== "Sync"

    ```python
    >>> presets = client.inverter_preset("CE2345G123").list_presets()
    >>> presets[0].id
    1
    >>> presets[0].name
    'Timed Charge'
    >>> presets[0].identifier
    'timed-charge'
    >>> presets[0].parameters[0].id
    'start_time'

    ```

=== "Async"

    ```python
    >>> presets = asyncio.run(client.inverter_preset("CE2345G123").alist_presets())
    >>> presets[0].name
    'Timed Charge'

    ```

---

## Reading current values

Returns the current configured values for a specific preset.
Because the exact fields vary by preset type, all values are exposed through
`extra_fields`.

See [Advanced Topics — Open-schema responses](advanced.md#open-schema-responses) for more detail.

=== "Sync"

    ```python
    >>> values = client.inverter_preset("CE2345G123").get_preset(preset_id=1)
    >>> values.extra_fields["start_time"]
    '00:30'
    >>> values.extra_fields["end_time"]
    '05:00'

    ```

=== "Async"

    ```python
    >>> values = asyncio.run(client.inverter_preset("CE2345G123").aget_preset(preset_id=1))
    >>> values.extra_fields["start_time"]
    '00:30'

    ```

---

## Applying a preset

Applies a preset configuration to the inverter. The `payload` must contain all
parameters required by that preset (use `list_presets()` to see the parameter list).

=== "Sync"

    ```python
    >>> result = client.inverter_preset("CE2345G123").apply_preset(
    ...     preset_id=1,
    ...     payload={"start_time": "00:30", "end_time": "05:00"},
    ... )
    >>> result.success
    True
    >>> result.message
    'Preset applied'

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(
    ...     client.inverter_preset("CE2345G123").aapply_preset(
    ...         preset_id=1,
    ...         payload={"start_time": "00:30", "end_time": "05:00"},
    ...     )
    ... )
    >>> result.success
    True

    ```
