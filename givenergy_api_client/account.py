from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from givenergy_api_client.exceptions import raise_for_status
from givenergy_api_client.pagination import PaginatedResult

if TYPE_CHECKING:
    from givenergy_api_client.client import GivenergyAPIClient


class AccountData(BaseModel):
    """Full GivEnergy user account record. (Formerly named Account.)"""

    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    first_name: str
    surname: str
    role: str
    email: str
    address: str
    postcode: str
    country: str
    telephone_number: str
    timezone: str
    standard_timezone: str


class AccountDevice(BaseModel):
    """Lightweight device record returned by the account-devices endpoint."""

    model_config = ConfigDict(frozen=True)

    serial_number: str
    type: str
    site_id: int | None = None
    inverter_serial: str
    inverter_status: str


# ---------------------------------------------------------------------------
# Domain class
# ---------------------------------------------------------------------------


class Account:
    """Domain object for GivEnergy account operations.

    Obtain via ``client.account()`` rather than direct instantiation.
    """

    def __init__(self, client: GivenergyAPIClient) -> None:
        self._client = client
        self._base = client._base_url

    # ------------------------------------------------------------------
    # Sync methods
    # ------------------------------------------------------------------

    def get(self) -> AccountData:
        """Return the authenticated user's own account."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/account")
            raise_for_status(response)
            return AccountData.model_validate(response.json()["data"])

    def get_by_id(self, *, user_id: str) -> AccountData:
        """Return a specific account by user ID."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/account/{user_id}")
            raise_for_status(response)
            return AccountData.model_validate(response.json()["data"])

    def search(self, *, username: str) -> AccountData:
        """Find an account by username."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/account/search/{username}")
            raise_for_status(response)
            return AccountData.model_validate(response.json()["data"])

    def get_devices(self, *, username: str, page: int = 1, page_size: int = 15) -> PaginatedResult[AccountDevice]:
        """List all communication devices registered to an account."""
        with self._client.get_client() as _client:
            response = _client.get(
                f"{self._base}/account/{username}/devices",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[AccountDevice].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    def list_children(self, *, page: int = 1, page_size: int = 15) -> PaginatedResult[AccountData]:
        """List all child accounts accessible to the current credentials."""
        with self._client.get_client() as _client:
            response = _client.get(
                f"{self._base}/account-children",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[AccountData].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    def list_children_for_user(
        self, *, user_id: str, page: int = 1, page_size: int = 15
    ) -> PaginatedResult[AccountData]:
        """List child accounts for a specific parent user."""
        with self._client.get_client() as _client:
            response = _client.get(
                f"{self._base}/account-children/{user_id}",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[AccountData].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    def get_sso_accounts(self) -> list[AccountData]:
        """Return all accounts linked to the authenticated SSO identity."""
        with self._client.get_client() as _client:
            response = _client.get(f"{self._base}/sso/me/accounts")
            raise_for_status(response)
            return [AccountData.model_validate(item) for item in response.json()["data"]]

    # ------------------------------------------------------------------
    # Async methods
    # ------------------------------------------------------------------

    async def aget(self) -> AccountData:
        """Async variant of :meth:`get`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/account")
            raise_for_status(response)
            return AccountData.model_validate(response.json()["data"])

    async def aget_by_id(self, *, user_id: str) -> AccountData:
        """Async variant of :meth:`get_by_id`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/account/{user_id}")
            raise_for_status(response)
            return AccountData.model_validate(response.json()["data"])

    async def asearch(self, *, username: str) -> AccountData:
        """Async variant of :meth:`search`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/account/search/{username}")
            raise_for_status(response)
            return AccountData.model_validate(response.json()["data"])

    async def aget_devices(
        self, *, username: str, page: int = 1, page_size: int = 15
    ) -> PaginatedResult[AccountDevice]:
        """Async variant of :meth:`get_devices`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(
                f"{self._base}/account/{username}/devices",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[AccountDevice].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    async def alist_children(self, *, page: int = 1, page_size: int = 15) -> PaginatedResult[AccountData]:
        """Async variant of :meth:`list_children`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(
                f"{self._base}/account-children",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[AccountData].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    async def alist_children_for_user(
        self, *, user_id: str, page: int = 1, page_size: int = 15
    ) -> PaginatedResult[AccountData]:
        """Async variant of :meth:`list_children_for_user`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(
                f"{self._base}/account-children/{user_id}",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            return PaginatedResult[AccountData].model_validate(
                {"data": payload["data"], "meta": payload.get("meta", _empty_meta(page, page_size))}
            )

    async def aget_sso_accounts(self) -> list[AccountData]:
        """Async variant of :meth:`get_sso_accounts`."""
        async with self._client.aget_client() as _client:
            response = await _client.get(f"{self._base}/sso/me/accounts")
            raise_for_status(response)
            return [AccountData.model_validate(item) for item in response.json()["data"]]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _empty_meta(page: int, page_size: int) -> dict[str, int]:
    """Synthesise a minimal PaginationMeta dict when the API omits it."""
    return {"current_page": page, "last_page": page, "per_page": page_size, "total": 0}
