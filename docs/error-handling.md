# Error Handling

This page describes every exception the SDK can raise, when each is raised,
and how to catch and handle them correctly.

---

## Exception hierarchy

All SDK exceptions inherit from `GivEnergyAPIError`, so you can always catch
everything with a single base class:

```
GivEnergyAPIError          ← base class; catch-all for all SDK errors
├── AuthenticationError    ← HTTP 401 — invalid or expired API key
├── NotFoundError          ← HTTP 404 — serial number, UUID, or ID not found
├── APIValidationError     ← HTTP 422 — request rejected by API validation
└── ServerError            ← HTTP 5xx — server-side failure (has .status_code)
```

---

## AuthenticationError

Raised when the API returns HTTP 401. This indicates the API key is missing,
invalid, or has been revoked.

```python
>>> try:
...     raise AuthenticationError("Invalid API key")
... except AuthenticationError as exc:
...     print(str(exc))
Invalid API key

```

**What to do**: Check that your API key is correct and has not expired.

---

## NotFoundError

Raised when the API returns HTTP 404. This indicates the requested resource
(serial number, UUID, or user ID) does not exist or is not accessible
to your account.

```python
>>> try:
...     raise NotFoundError("Inverter CE2345G123 not found")
... except NotFoundError as exc:
...     print(str(exc))
Inverter CE2345G123 not found

```

**What to do**: Verify the serial number, UUID, or ID. For EMS resources,
also confirm the inverter supports the EMS feature (see [EMS](ems.md)).

---

## APIValidationError

Raised when the API returns HTTP 422. This indicates the request was
structurally valid but was rejected by the API's business-rule validation.
The exception message contains a human-readable description from the API.

```python
>>> try:
...     raise APIValidationError("end_time must be after start_time")
... except APIValidationError as exc:
...     print(exc.args[0])
end_time must be after start_time

```

**What to do**: Inspect `exc.args[0]` for the API's description of the
validation failure and correct the offending parameter.

---

## ServerError

Raised when the API returns HTTP 5xx. The `.status_code` attribute contains
the exact HTTP status code returned by the server.

```python
>>> try:
...     raise ServerError("Service unavailable", 503)
... except ServerError as exc:
...     print(exc.status_code)
503

```

**What to do**: These errors indicate a problem on GivEnergy's side. Retry
the request with exponential back-off. If the error persists, contact
GivEnergy support.

---

## GivEnergyAPIError (base class)

Use `GivEnergyAPIError` as a catch-all when you do not need to distinguish
between specific error types.

```python
>>> try:
...     raise NotFoundError("resource not found")
... except GivEnergyAPIError as exc:
...     print(f"SDK error: {exc}")
SDK error: resource not found

```

---

## Complete example

This pattern covers all exception types in a single `try/except` block:

```python
>>> from givenergy_api_client.exceptions import (
...     AuthenticationError,
...     NotFoundError,
...     APIValidationError,
...     ServerError,
...     GivEnergyAPIError,
... )
>>> def handle_api_call(result_fn):
...     try:
...         return result_fn()
...     except AuthenticationError:
...         print("Check your API key")
...     except NotFoundError:
...         print("Resource not found")
...     except APIValidationError as exc:
...         print(f"Validation error: {exc.args[0]}")
...     except ServerError as exc:
...         print(f"Server error {exc.status_code} — retry later")
...     except GivEnergyAPIError as exc:
...         print(f"Unexpected SDK error: {exc}")
>>> handle_api_call(lambda: (_ for _ in ()).throw(NotFoundError("not found")))
Resource not found

```
