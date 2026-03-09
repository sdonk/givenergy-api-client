from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING

from httpx import AsyncClient, Client

from givenergy_api_client.account import AccountData
from givenergy_api_client.communication_device import CommunicationDevice

# Backward-compatible re-exports (moved to energy_flow.py)
from givenergy_api_client.energy_flow import EnergyDataFlowGrouping, EnergyDataFlowType
from givenergy_api_client.pagination import PaginatedResult

if TYPE_CHECKING:
    from givenergy_api_client.account import Account
    from givenergy_api_client.ems import EMS
    from givenergy_api_client.ev_charger import EVCharger, EVChargerData
    from givenergy_api_client.inverter import Inverter
    from givenergy_api_client.inverter_preset import InverterPreset

__all__ = [
    "GivenergyAPIClient",
    "EnergyDataFlowGrouping",
    "EnergyDataFlowType",
]


class GivenergyAPIClient:
    """Authenticated HTTP client for the GivEnergy Cloud API v1.

    Use factory methods (``account()``, ``inverter()``, etc.) to obtain typed
    domain objects for each resource group.
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._base_url = "https://api.givenergy.cloud/v1"

    # ------------------------------------------------------------------
    # Transport context managers
    # ------------------------------------------------------------------

    @contextmanager
    def get_client(self) -> Generator[Client, None, None]:
        """Yield an authenticated sync httpx client."""
        client = Client(
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        try:
            yield client
        finally:
            client.close()

    @asynccontextmanager
    async def aget_client(self) -> AsyncGenerator[AsyncClient, None]:
        """Yield an authenticated async httpx client."""
        client = AsyncClient(
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        try:
            yield client
        finally:
            await client.aclose()

    # ------------------------------------------------------------------
    # Domain-object factories
    # ------------------------------------------------------------------

    def account(self) -> Account:
        """Return an Account domain object bound to this client."""
        from givenergy_api_client.account import Account as _Account

        return _Account(self)

    def inverter(self, serial_number: str) -> Inverter:
        """Return an Inverter domain object for the given serial number."""
        from givenergy_api_client.inverter import Inverter as _Inverter

        return _Inverter(self, serial_number)

    def ems(self, inverter_serial_number: str) -> EMS:
        """Return an EMS domain object for the given inverter serial number."""
        from givenergy_api_client.ems import EMS as _EMS

        return _EMS(self, inverter_serial_number)

    def ev_charger(self, charger_uuid: str) -> EVCharger:
        """Return an EVCharger domain object for the given UUID."""
        from givenergy_api_client.ev_charger import EVCharger as _EVCharger

        return _EVCharger(self, charger_uuid)

    def inverter_preset(self, serial_number: str) -> InverterPreset:
        """Return an InverterPreset domain object for the given serial number."""
        from givenergy_api_client.inverter_preset import InverterPreset as _InverterPreset

        return _InverterPreset(self, serial_number)

    # ------------------------------------------------------------------
    # Collection endpoints (no resource identifier needed)
    # ------------------------------------------------------------------

    def list_ev_chargers(self, *, page: int = 1, page_size: int = 15) -> PaginatedResult[EVChargerData]:
        """Return a paginated list of all EV chargers registered to this account."""
        from givenergy_api_client.ev_charger import EVChargerData as _EVChargerData

        with self.get_client() as _client:
            from givenergy_api_client.exceptions import raise_for_status

            response = _client.get(
                f"{self._base_url}/ev-charger",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            meta = payload.get("meta", {"current_page": page, "last_page": page, "per_page": page_size, "total": 0})
            return PaginatedResult[_EVChargerData].model_validate({"data": payload["data"], "meta": meta})

    async def alist_ev_chargers(self, *, page: int = 1, page_size: int = 15) -> PaginatedResult[EVChargerData]:
        """Async variant of :meth:`list_ev_chargers`."""
        from givenergy_api_client.ev_charger import EVChargerData as _EVChargerData

        async with self.aget_client() as _client:
            from givenergy_api_client.exceptions import raise_for_status

            response = await _client.get(
                f"{self._base_url}/ev-charger",
                params={"page": page, "pageSize": page_size},
            )
            raise_for_status(response)
            payload = response.json()
            meta = payload.get("meta", {"current_page": page, "last_page": page, "per_page": page_size, "total": 0})
            return PaginatedResult[_EVChargerData].model_validate({"data": payload["data"], "meta": meta})

    # ------------------------------------------------------------------
    # Legacy top-level methods (preserved for backward compatibility)
    # ------------------------------------------------------------------

    def get_account(self) -> AccountData:
        """Return the authenticated user's account. Use ``client.account().get()`` for new code."""
        with self.get_client() as _client:
            from givenergy_api_client.exceptions import raise_for_status

            response = _client.get(f"{self._base_url}/account")
            raise_for_status(response)
            return AccountData.model_validate(response.json()["data"])

    def get_communication_devices(self) -> list[CommunicationDevice]:
        """Return all communication devices registered to this account."""
        with self.get_client() as _client:
            from givenergy_api_client.exceptions import raise_for_status

            response = _client.get(f"{self._base_url}/communication-device")
            raise_for_status(response)
            return [CommunicationDevice.model_validate(obj=cd) for cd in response.json()["data"]]

    def get_communication_device(self, *, serial_number: str) -> CommunicationDevice:
        """Return a single communication device by serial number."""
        with self.get_client() as _client:
            from givenergy_api_client.exceptions import raise_for_status

            response = _client.get(f"{self._base_url}/communication-device/{serial_number}")
            raise_for_status(response)
            return CommunicationDevice.model_validate(response.json()["data"])
