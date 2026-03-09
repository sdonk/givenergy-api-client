# Research: GivEnergy API Full Coverage

**Branch**: `001-givenergy-api-wrapper` | **Date**: 2026-03-07

## Decision 1: Domain Model Architecture

**Decision**: Each REST resource group gets a domain class (e.g., `AccountDomain`,
`InverterDomain`) that holds a reference to `GivenergyAPIClient` and exposes named
methods for each endpoint.

**Rationale**: The user specified "every entity has a domain model which takes an instance
of the client to perform operations." This cleanly separates concerns: `GivenergyAPIClient`
handles auth and transport; domain classes handle resource-specific logic. Callers obtain
domain objects via factory methods on the client (`client.account()`,
`client.inverter("SN123")`), which is discoverable via IDE autocomplete.

**Alternatives considered**:
- All methods on `GivenergyAPIClient` (current pattern): Scales poorly to 21+ methods;
  flat namespace becomes unwieldy. Rejected for new methods; existing three methods
  preserved for backward compatibility.
- Separate client classes per resource: Would require multiple API key configurations.
  Rejected — a single authenticated client is simpler.

---

## Decision 2: Sync / Async Naming Convention

**Decision**: Sync methods use unprefixed names (`get_health()`); async methods use the
`a` prefix (`aget_health()`). This mirrors the existing `get_client()` / `aget_client()`
convention already in `client.py`.

**Rationale**: Consistency with existing code. The `a` prefix is a Python community
convention (used by SQLAlchemy, httpx, etc.) that is immediately recognisable.

**Alternatives considered**:
- `_async` suffix: Less readable, more verbose.
- Separate `AsyncAccountDomain` / `AccountDomain` classes: Code duplication; rejected.

---

## Decision 3: Exception Hierarchy

**Decision**: A new `exceptions.py` module introduces four exception classes:
- `GivEnergyAPIError(Exception)` — base class
- `AuthenticationError(GivEnergyAPIError)` — HTTP 401
- `NotFoundError(GivEnergyAPIError)` — HTTP 404
- `APIValidationError(GivEnergyAPIError)` — HTTP 422 (named to avoid clash with Pydantic)
- `ServerError(GivEnergyAPIError)` — HTTP 5xx

**Rationale**: The spec requires distinct, catchable exception types for each error
category. A shared base class (`GivEnergyAPIError`) lets callers catch all API errors
with a single `except` clause when finer discrimination is not needed.

**Alternatives considered**:
- Raising `httpx.HTTPStatusError` directly: Leaks transport details; rejected.
- Single `GivEnergyAPIError` with a `status_code` attribute: Catchable but not
  discriminable by type; rejected per spec requirement FR-005.

---

## Decision 4: Pagination Strategy

**Decision**: Paginated endpoints accept `page: int = 1` and `page_size: int = 15`
keyword arguments and return a `PaginatedResponse[T]` typed dict (or the raw
`{"data": [...], "meta": {...}}` structure) so callers control iteration.

**Rationale**: The spec notes "pagination metadata forwarded as-is rather than abstracted
into a generic `Page[T]` wrapper." The library stays thin. Callers who want to iterate
all pages do so themselves.

**Alternatives considered**:
- Auto-pagination generator: More convenient but adds complexity and hidden network
  calls; rejected per YAGNI principle.
- Returning only the data list: Loses pagination metadata (total, current page); rejected.

---

## Decision 5: datetime Serialisation

**Decision**: Time-range parameters accept `datetime.datetime` objects. The library
serialises them to ISO 8601 strings (`isoformat()`) before passing to the API.
Timezone-naive datetimes are rejected with a `ValueError`.

**Rationale**: The GivEnergy API expects ISO 8601 timestamps. Enforcing timezone-aware
datetimes at the library boundary prevents silent bugs from timezone offset errors.

**Alternatives considered**:
- Accept strings: Pushes serialisation burden to callers; loses type safety. Rejected.
- Accept Unix timestamps: Non-Pythonic; rejected.

---

## Decision 6: Energy Flow Enum Location

**Decision**: `EnergyDataFlowGrouping` and `EnergyDataFlowType` enums move from
`client.py` to `energy_flow.py`. `client.py` re-exports them for backward compatibility
during a deprecation window.

**Rationale**: These enums belong to the Inverter / energy flow domain, not to the
transport layer. Moving them aligns with "each REST entity has a python module."

**Alternatives considered**:
- Leave in `client.py`: Violates the module-per-entity principle. Rejected.
- Move to `inverter.py`: Also reasonable but `energy_flow.py` stub already exists and
  the concept maps cleanly. Chosen.

---

## Decision 7: Client Factory Methods

**Decision**: `GivenergyAPIClient` gains named factory methods that return domain instances:

```python
client.account()                       # -> AccountDomain
client.inverter(serial_number)         # -> InverterDomain
client.ev_charger(charger_uuid)        # -> EVChargerDomain
client.ems(inverter_serial_number)     # -> EMSDomain
client.inverter_preset(serial_number)  # -> InverterPresetDomain
```

**Rationale**: Factory methods keep domain-object creation simple and consistent.
They also make it obvious that domain objects share the same underlying authenticated
transport. Existing top-level methods (`get_account`, etc.) remain unchanged.

**Alternatives considered**:
- Lazy properties (`client.account` as a property): Works for parameter-free domains
  but not for parameterised ones (inverter serial number). Inconsistent; rejected.
- Direct instantiation by caller (`AccountDomain(client)`): Valid but requires callers
  to import domain classes; factory methods are more ergonomic.
