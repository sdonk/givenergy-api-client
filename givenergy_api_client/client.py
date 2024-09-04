from contextlib import asynccontextmanager, contextmanager
from enum import IntEnum
from typing import AsyncGenerator, Generator, List

from httpx import AsyncClient, Client

from givenergy_api_client.account import Account
from givenergy_api_client.communication_device import CommunicationDevice


class EnergyDataFlowGrouping(IntEnum):
    HALF_HOURLY = 0
    DAILY = 1
    MONTHLY = 2
    YEARLY = 3
    TOTAL = 4


class EnergyDataFlowType(IntEnum):
    PV_TO_HOME = 0
    PV_TO_BATTERY = 1
    PV_TO_GRID = 2
    GRID_TO_HOME = 3
    GRID_TO_BATTERY = 4
    BATTERY_TO_HOME = 5
    BATTERY_TO_GRID = 6


class GivenergyAPIClient:

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._base_url = "https://api.givenergy.cloud/v1"

    @property
    def client(self) -> Client:
        return Client(
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    @contextmanager
    def get_client(self) -> Generator[Client, None, None]:
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

    def get_account(self) -> Account:
        with self.get_client() as _client:
            return Account.model_validate(obj=_client.get(f"{self._base_url}/account").json()["data"])

    def get_communication_devices(self) -> List[CommunicationDevice]:
        with self.get_client() as _client:
            return [
                CommunicationDevice.model_validate(obj=cd)
                for cd in _client.get(f"{self._base_url}/communication-device").json()["data"]
            ]

    def get_communication_device(self, *, serial_number: str) -> CommunicationDevice:
        with self.get_client() as _client:
            return CommunicationDevice.model_validate(
                obj=_client.get(f"{self._base_url}/communication-device/{serial_number}").json()["data"]
            )
