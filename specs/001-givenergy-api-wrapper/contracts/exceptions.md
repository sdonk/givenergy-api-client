# Contract: Exception Hierarchy

**Module**: `givenergy_api_client.exceptions`

```python
class GivEnergyAPIError(Exception):
    """Base exception for all GivEnergy API errors."""

class AuthenticationError(GivEnergyAPIError):
    """Raised on HTTP 401 — invalid or expired API key."""

class NotFoundError(GivEnergyAPIError):
    """Raised on HTTP 404 — serial number, UUID, or user ID not found."""

class APIValidationError(GivEnergyAPIError):
    """Raised on HTTP 422 — request rejected by the API's validation layer."""

class ServerError(GivEnergyAPIError):
    """Raised on HTTP 5xx — server-side failure.

    Attributes:
        status_code: int  The HTTP status code returned.
    """
    def __init__(self, message: str, status_code: int) -> None: ...
    status_code: int
```

## Trigger Conditions

| HTTP Status | Exception raised |
|-------------|-----------------|
| 401 | `AuthenticationError` |
| 404 | `NotFoundError` |
| 422 | `APIValidationError` |
| 5xx | `ServerError(status_code=...)` |
| Other 4xx | `GivEnergyAPIError` |

All exceptions preserve the API-returned error message as the exception string.
