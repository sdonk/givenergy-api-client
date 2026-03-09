# Account

This page covers all operations available on the `Account` resource — looking up accounts,
listing devices, managing child accounts, and accessing SSO-linked accounts.

All examples assume a configured client:

```python
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
```

---

## Getting your account

Returns the authenticated user's own account record.

=== "Sync"

    ```python
    >>> account = client.account().get()
    >>> account.email
    'test@example.com'
    >>> account.id
    1

    ```

=== "Async"

    ```python
    >>> account = asyncio.run(client.account().aget())
    >>> account.email
    'test@example.com'

    ```

---

## Looking up by ID

Returns a specific account by its user ID.

=== "Sync"

    ```python
    >>> account = client.account().get_by_id(user_id="1")
    >>> account.name
    'Test User'

    ```

=== "Async"

    ```python
    >>> account = asyncio.run(client.account().aget_by_id(user_id="1"))
    >>> account.name
    'Test User'

    ```

---

## Searching by username

Finds an account by its username (email address).

=== "Sync"

    ```python
    >>> account = client.account().search(username="test@example.com")
    >>> account.email
    'test@example.com'

    ```

=== "Async"

    ```python
    >>> account = asyncio.run(client.account().asearch(username="test@example.com"))
    >>> account.email
    'test@example.com'

    ```

---

## Listing devices

Returns a paginated list of communication devices registered to an account.
The `meta` attribute contains pagination information.

=== "Sync"

    ```python
    >>> result = client.account().get_devices(username="jdoe")
    >>> result.data[0].serial_number
    'CE2345G123'
    >>> result.meta.last_page
    1

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(client.account().aget_devices(username="jdoe"))
    >>> result.data[0].serial_number
    'CE2345G123'

    ```

See [Advanced Topics — Pagination](advanced.md#pagination) for a complete multi-page loop example.

---

## Child accounts

### List all child accounts

Returns a paginated list of all child accounts accessible to the current credentials.

=== "Sync"

    ```python
    >>> result = client.account().list_children()
    >>> result.data[0].email
    'test@example.com'

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(client.account().alist_children())
    >>> result.data[0].email
    'test@example.com'

    ```

### List child accounts for a specific user

=== "Sync"

    ```python
    >>> result = client.account().list_children_for_user(user_id="1")
    >>> result.data[0].email
    'test@example.com'

    ```

=== "Async"

    ```python
    >>> result = asyncio.run(client.account().alist_children_for_user(user_id="1"))
    >>> result.data[0].email
    'test@example.com'

    ```

---

## SSO accounts

Returns all accounts linked to the authenticated SSO identity.

=== "Sync"

    ```python
    >>> accounts = client.account().get_sso_accounts()
    >>> accounts[0].email
    'test@example.com'

    ```

=== "Async"

    ```python
    >>> accounts = asyncio.run(client.account().aget_sso_accounts())
    >>> accounts[0].email
    'test@example.com'

    ```
