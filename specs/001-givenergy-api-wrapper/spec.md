# Feature Specification: GivEnergy API Full Coverage

**Feature Branch**: `001-givenergy-api-wrapper`
**Created**: 2026-03-07
**Status**: Draft
**Input**: User description: "Build a python library that wraps the Givenergy inverter API. Implementing all the operations described in the openspec api https://givenergy.cloud/docs/api/v1.openapi"

## Context

The library already exposes three operations (`get_account`, `get_communication_devices`,
`get_communication_device`). This feature extends it to cover every endpoint in the
GivEnergy Cloud API v1 spec, grouped into six capability areas. All additions MUST follow
the established three-step pattern and pass the quality gates defined in the constitution.

## Clarifications

### Session 2026-03-07

- Q: What type checker must all code pass? → A: `ty` (Astral's ty checker, not mypy)
- Q: What is the Ruff line length limit? → A: 120 characters
- Q: How should paginated and open-schema endpoints return results? → A: Generic `PaginatedResult[T]` Pydantic model with `data: list[T]` and `meta: PaginationMeta` fields — fully typed and `ty`-safe

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Account & Device Discovery (Priority: P1)

A developer building a home-energy dashboard needs to look up account details and discover
all registered communication devices (dongles) for one or more accounts. They need to search
for accounts by username, fetch an account by ID, and list all devices belonging to a specific
account.

**Why this priority**: Account discovery is the entry point for every other operation — serial
numbers and UUIDs required by downstream calls are obtained here. An MVP with only account
coverage already delivers navigable value.

**Independent Test**: Create a client with a valid API key, call `get_account_by_id()` and
`get_account_devices()`, and verify structured account and device objects are returned without
making any other API calls.

**Acceptance Scenarios**:

1. **Given** a valid API key, **When** `get_account_by_id(user_id="…")` is called,
   **Then** a typed Account object with id, name, email, address, postcode, and timezone
   fields is returned.
2. **Given** a valid API key, **When** `search_account(username="…")` is called,
   **Then** the matching Account object is returned or a clear not-found error is raised.
3. **Given** a valid username, **When** `get_account_devices(username="…")` is called,
   **Then** a list of typed device objects each containing serial number, type, and linked
   inverter details is returned.
4. **Given** an invalid API key, **When** any account method is called, **Then** an
   authentication error is raised with a descriptive message.

---

### User Story 2 - Inverter Monitoring & Energy Flows (Priority: P2)

A developer building an energy monitoring tool needs to retrieve the health status of one or
more inverters, and to query historical energy-flow data (PV-to-home, battery-to-grid, etc.)
between any two timestamps.

**Why this priority**: Inverter telemetry is the primary data source for energy dashboards;
it is the most frequently requested capability after account discovery.

**Independent Test**: Call `get_inverter_health(serial_number="…")` and
`get_energy_flows(serial_number="…", start_time=…, end_time=…)` against a mocked client
and verify typed health-check and energy-flow objects are returned.

**Acceptance Scenarios**:

1. **Given** a valid inverter serial number, **When** `get_inverter_health()` is called,
   **Then** a list of typed health-check objects is returned, each with a name, value,
   status, and unit.
2. **Given** a valid inverter serial number and a time range, **When** `get_energy_flows()`
   is called, **Then** energy-flow data points grouped by flow type (PV-to-home,
   battery-to-grid, etc.) are returned for the requested interval.
3. **Given** an unrecognised serial number, **When** either method is called, **Then** a
   clear not-found error is raised.

---

### User Story 3 - EV Charger Monitoring & Control (Priority: P3)

A developer integrating with an EV charger fleet needs to list all chargers, retrieve their
current status, fetch historical meter data and charging sessions, and execute control
commands (e.g., start/stop charging, change charging mode).

**Why this priority**: EV charger control is a key commercial capability not yet covered by
the library; it blocks integrators building smart-charging automations.

**Independent Test**: Call `list_ev_chargers()`, `get_ev_charger(uuid="…")`,
`get_ev_charger_meter_data(…)`, `list_charging_sessions(…)`, and
`execute_ev_charger_command(uuid="…", command_id="…", payload={…})` against a mocked
client and verify correctness of each returned type.

**Acceptance Scenarios**:

1. **Given** a valid API key, **When** `list_ev_chargers()` is called, **Then** a list
   of typed EV charger objects with uuid, serial number, alias, online status, and
   current status is returned.
2. **Given** a charger UUID, start/end timestamps, measurands, and meter IDs,
   **When** `get_ev_charger_meter_data()` is called, **Then** a paginated list of
   meter measurement objects is returned.
3. **Given** a charger UUID and a supported command ID plus payload, **When**
   `execute_ev_charger_command()` is called, **Then** a typed result indicating success
   or failure with a message is returned.
4. **Given** a charger UUID, **When** `list_charging_sessions()` is called with optional
   start/end filters, **Then** a paginated list of session objects is returned with start,
   stop, and energy-delivered information.

---

### User Story 4 - Inverter Preset Control (Priority: P4)

A developer building an inverter automation tool needs to list available configuration
presets (e.g., eco mode, timed charge), read the current values of a preset, and apply
a preset to put the inverter into a desired operating mode.

**Why this priority**: Preset-based control is the sanctioned way to configure inverters;
without it the library cannot be used for any automation or scheduling use case.

**Independent Test**: Call `list_inverter_presets()`, `get_inverter_preset()`, and
`apply_inverter_preset()` against mocked responses and verify typed preset objects and
success/failure results are returned.

**Acceptance Scenarios**:

1. **Given** a valid inverter serial number, **When** `list_inverter_presets()` is called,
   **Then** a list of typed preset objects with id, identifier, name, description, and
   parameters is returned.
2. **Given** a valid serial number and preset ID, **When** `get_inverter_preset()` is
   called, **Then** the preset's current configured values are returned.
3. **Given** a valid serial number, preset ID, and parameter values, **When**
   `apply_inverter_preset()` is called, **Then** a typed result with success flag and
   message is returned and the inverter adopts the new configuration.

---

### User Story 5 - EMS Plant Data (Priority: P5)

A developer monitoring a plant-level Energy Management System needs to retrieve the latest
aggregate metrics (battery power/remaining, grid power, inverter array data, meter readings)
for a given inverter.

**Why this priority**: EMS data is specific to plant installations; lower priority than
individual inverter monitoring but needed for plant-scale dashboards.

**Independent Test**: Call `get_ems_latest(inverter_serial_number="…")` against a mocked
response and verify a typed EMS snapshot object is returned.

**Acceptance Scenarios**:

1. **Given** a valid inverter serial number (EMS-enabled), **When** `get_ems_latest()` is
   called, **Then** a typed EMS snapshot with battery_power, battery_wh_remaining,
   grid_power, inverters array, and meters array is returned.
2. **Given** a non-EMS inverter serial number, **When** `get_ems_latest()` is called,
   **Then** a clear, descriptive error is raised.

---

### User Story 6 - Multi-Account & SSO Hierarchy (Priority: P6)

A developer building a multi-tenant installer portal needs to list child accounts
accessible to their credentials, retrieve child accounts for a specific parent user, and
fetch all accounts linked to an SSO identity.

**Why this priority**: Multi-account navigation is a secondary capability needed for
installer or aggregator platforms; individual account operations (P1) must work first.

**Independent Test**: Call `list_child_accounts()`, `list_child_accounts_for_user()`, and
`get_sso_accounts()` against mocked responses and verify lists of typed account objects
are returned.

**Acceptance Scenarios**:

1. **Given** a valid API key with child-account access, **When** `list_child_accounts()` is
   called with optional pagination params, **Then** a paginated list of child account
   objects is returned.
2. **Given** a specific parent user ID, **When** `list_child_accounts_for_user(user_id="…")`
   is called, **Then** only that user's child accounts are returned.
3. **Given** an SSO-authenticated API key, **When** `get_sso_accounts()` is called,
   **Then** all accounts linked to the SSO identity are returned as a list.

---

### Edge Cases

- Paginated endpoints receive `page` and `page_size` parameters; callers passing
  out-of-range page numbers receive an empty list, not an error.
- HTTP 401 (invalid/expired API key) MUST raise a distinct `AuthenticationError`.
- HTTP 404 (resource not found — unknown serial, UUID, or user ID) MUST raise a
  distinct `NotFoundError`.
- HTTP 422 / validation errors from the API MUST surface as an `APIValidationError` with
  the original API message preserved (named to avoid clash with Pydantic's own `ValidationError`).
- HTTP 5xx responses MUST raise a `ServerError` with status code included.
- `get_energy_flows()` called with `end_time` before `start_time` MUST raise a
  `ValueError` before making any network call.
- EV charger command execution with an unsupported `command_id` MUST surface the
  API-returned failure message rather than raising a generic error.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The library MUST expose a method for each of the 21 endpoints defined in
  the GivEnergy Cloud API v1 spec.
- **FR-002**: Every method MUST accept keyword-only arguments for path parameters and
  optional query parameters (pagination, time ranges, filters).
- **FR-003**: Every method MUST return a typed Pydantic v2 model (or list thereof);
  raw `dict` returns are forbidden. No method return type annotation may be `Any` or `dict`.
- **FR-004**: Every method MUST have both a synchronous and an asynchronous variant,
  following the `get_X()` / `aget_X()` naming convention.
- **FR-005**: The library MUST raise distinct, typed exceptions for authentication
  failures, resource-not-found, validation errors, and server errors.
- **FR-006**: Paginated endpoints MUST accept `page` (int, default 1) and `page_size`
  (int, default 15) keyword arguments and MUST return a `PaginatedResult[T]` typed
  Pydantic generic model containing `data: list[T]` and `meta: PaginationMeta` fields.
  No endpoint may return an untyped `dict`.
- **FR-006a**: Open-schema endpoint responses (e.g. preset current values, command
  state) where the schema varies by resource MUST return a typed Pydantic model with
  all known fields declared; any genuinely dynamic remainder MUST be captured in a
  typed `extra_fields: dict[str, str | int | float | bool | None]` field rather than
  an untyped `dict`.
- **FR-007**: Time-range parameters (`start_time`, `end_time`) MUST accept
  `datetime` objects and serialize them to the format required by the API.
- **FR-008**: The `execute_ev_charger_command()` method MUST accept an arbitrary dict
  payload forwarded as the JSON request body.
- **FR-009**: The `send_inverter_debug_command()` method MUST accept a raw hex string
  and return a typed result indicating success or failure.
- **FR-010**: All new Pydantic models MUST use `ConfigDict(frozen=True)`.
- **FR-011**: The library MUST be installable as a single package with no mandatory
  dependencies beyond those already declared (httpx, Pydantic v2).

### Key Entities

- **PaginationMeta**: Pagination metadata (current_page, last_page, per_page, total);
  used by `PaginatedResult[T]`.
- **PaginatedResult[T]**: Generic Pydantic v2 model — `data: list[T]`, `meta: PaginationMeta`;
  returned by all paginated endpoints; fully typed and `ty`-safe.
- **Account**: Represents a GivEnergy user account (id, name, email, address, postcode,
  timezone). Already partially modelled.
- **CommunicationDevice**: Dongle/gateway device linking to an inverter; already modelled.
- **AccountDevice**: Lightweight device record returned by the account-devices endpoint
  (serial number, type, linked inverter serial and status, site_id).
- **InverterHealthCheck**: Single health metric (name, value, status, unit).
- **EnergyFlowPoint**: Single data point for a flow type within a requested time range.
- **EVCharger**: EV charger record (uuid, serial_number, type, alias, online, status).
- **EVChargerMeterReading**: Timestamped measurement from a charger meter (measurand,
  value, unit).
- **ChargingSession**: A single EV charging session (started_by, meter_start, started_at,
  stopped_by, meter_stop, stopped_at).
- **EVChargerCommandResult**: Result of executing a charger command (code, success, message).
- **InverterPreset**: Configuration preset descriptor (id, identifier, name, description,
  parameters).
- **PresetValues**: Current configured values for a specific preset.
- **PresetApplyResult**: Result of applying a preset (success, message).
- **EMSSnapshot**: Latest EMS plant metrics (battery_power, battery_wh_remaining,
  grid_power, inverters array, meters array).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 21 GivEnergy API v1 endpoints have a corresponding callable method in
  the library; coverage is verified by a test suite that runs without live network access.
- **SC-002**: A developer can discover and call any endpoint by reading only docstrings
  and type signatures — no additional documentation lookup required.
- **SC-003**: All methods return typed objects; no method return type is `Any`, `dict`,
  or untyped.
- **SC-004**: The full test suite (including all new tests) passes with zero failures,
  zero `ty` type-checker errors, and zero Ruff linting errors (line length 120).
- **SC-005**: Adding the library to a project requires no transitive dependencies beyond
  httpx and Pydantic v2.
- **SC-006**: Each error condition (401, 404, 422, 5xx) produces a distinct, catchable
  exception type so callers can handle errors programmatically without parsing strings.

---

## Assumptions

- The API base URL remains `https://api.givenergy.cloud/v1`.
- Bearer token authentication is the only supported auth method; no OAuth2 flow is needed.
- Pagination metadata beyond the `data` array (e.g. total count, links) will be forwarded
  to callers as-is rather than abstracted into a generic `Page[T]` wrapper, keeping the
  library thin.
- The `send_inverter_debug_command` endpoint is included for completeness but will be
  documented as an advanced/unsafe operation.
- Async variants share the same Pydantic models as sync variants; no async-specific models
  are needed.
