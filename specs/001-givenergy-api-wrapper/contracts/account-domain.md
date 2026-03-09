# Contract: Account

**Module**: `givenergy_api_client.account`

> **Naming note**: The existing `Account` Pydantic model is renamed to `AccountData`.
> The new `Account` class is the domain class that wraps a client reference.

## Pydantic Models

```python
class AccountData(BaseModel):
    """Renamed from Account — full user account record."""
    id: int
    name: str
    first_name: str
    surname: str
    role: str
    email: EmailStr
    address: str
    postcode: str
    country: str
    telephone_number: str
    timezone: str
    standard_timezone: str
    model_config = ConfigDict(frozen=True)

class AccountDevice(BaseModel):
    serial_number: str
    type: str
    site_id: int | None
    inverter_serial: str
    inverter_status: str
    model_config = ConfigDict(frozen=True)
```

## Domain Class

```python
class Account:
    def __init__(self, client: GivenergyAPIClient) -> None: ...

    def get(self) -> AccountData: ...
    async def aget(self) -> AccountData: ...

    def get_by_id(self, user_id: str) -> AccountData: ...
    async def aget_by_id(self, user_id: str) -> AccountData: ...

    def search(self, username: str) -> AccountData: ...
    async def asearch(self, username: str) -> AccountData: ...

    def get_devices(
        self, username: str, *, page: int = 1, page_size: int = 15
    ) -> dict: ...
    async def aget_devices(
        self, username: str, *, page: int = 1, page_size: int = 15
    ) -> dict: ...

    def list_children(self, *, page: int = 1, page_size: int = 15) -> dict: ...
    async def alist_children(self, *, page: int = 1, page_size: int = 15) -> dict: ...

    def list_children_for_user(
        self, user_id: str, *, page: int = 1, page_size: int = 15
    ) -> dict: ...
    async def alist_children_for_user(
        self, user_id: str, *, page: int = 1, page_size: int = 15
    ) -> dict: ...

    def get_sso_accounts(self) -> dict: ...
    async def aget_sso_accounts(self) -> dict: ...
```

## Errors

| Condition | Exception |
|-----------|-----------|
| Invalid API key | `AuthenticationError` |
| User ID / username not found | `NotFoundError` |
| Server error | `ServerError` |

## Factory

```python
client = GivenergyAPIClient(api_key="...")
account = client.account()   # -> Account
data = account.get()         # -> AccountData
```
