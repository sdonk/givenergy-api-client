from __future__ import annotations

import httpx


class GivEnergyAPIError(Exception):
    """Base exception for all GivEnergy API errors."""


class AuthenticationError(GivEnergyAPIError):
    """Raised on HTTP 401 — invalid or expired API key."""


class NotFoundError(GivEnergyAPIError):
    """Raised on HTTP 404 — serial number, UUID, or user ID not found."""


class APIValidationError(GivEnergyAPIError):
    """Raised on HTTP 422 — request rejected by the API's validation layer."""


class ServerError(GivEnergyAPIError):
    """Raised on HTTP 5xx — server-side failure."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


def raise_for_status(response: httpx.Response) -> None:
    """Inspect an httpx response and raise a typed GivEnergy exception if the status indicates an error."""
    if response.is_success:
        return
    try:
        message = response.json().get("message", response.text)
    except Exception:
        message = response.text

    status = response.status_code
    if status == 401:
        raise AuthenticationError(message)
    if status == 404:
        raise NotFoundError(message)
    if status == 422:
        raise APIValidationError(message)
    if status >= 500:
        raise ServerError(message, status_code=status)
    raise GivEnergyAPIError(f"HTTP {status}: {message}")
