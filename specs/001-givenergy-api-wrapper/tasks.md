---
description: "Task list for GivEnergy API Full Coverage"
---

# Tasks: GivEnergy API Full Coverage

**Input**: Design documents from `specs/001-givenergy-api-wrapper/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅

**Organization**: Tasks grouped by user story to enable independent implementation and
testing. Each story phase is independently completable after the Foundational phase.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies in-flight)
- **[Story]**: Which user story this task belongs to (US1–US6)

---

## Phase 1: Setup

**Purpose**: Tooling configuration aligned with clarified constraints (ty, Ruff 120).

- [x] T001 Add `ty` to dev dependencies in `pyproject.toml` and verify it runs against the package (`poetry add --group dev ty`)
- [x] T002 Set Ruff line length to 120 in `pyproject.toml` `[tool.ruff]` section (replace any existing `line-length` value)
- [x] T003 [P] Verify existing tests still pass after config changes: `poetry run pytest && poetry run ruff check . && poetry run ruff format --check .`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure required by every user story phase.

⚠️ **CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Create `givenergy_api_client/exceptions.py` with the full exception hierarchy: `GivEnergyAPIError(Exception)`, `AuthenticationError`, `NotFoundError`, `APIValidationError`, `ServerError(status_code: int)` — all with typed `__init__` signatures and docstrings; ensure `ty` and Ruff pass
- [x] T005 [P] Create `givenergy_api_client/pagination.py` with `PaginationMeta(BaseModel, frozen=True)` (fields: `current_page: int`, `last_page: int`, `per_page: int`, `total: int`) and generic `PaginatedResult[T](BaseModel, Generic[T], frozen=True)` (fields: `data: list[T]`, `meta: PaginationMeta`) — use `from __future__ import annotations` and Pydantic v2 `model_config = ConfigDict(frozen=True)`
- [x] T006 Populate `givenergy_api_client/energy_flow.py` (currently a stub) with `EnergyDataFlowGrouping(IntEnum)` (HALF_HOURLY=0 … TOTAL=4) and `EnergyDataFlowType(IntEnum)` (PV_TO_HOME=0 … BATTERY_TO_GRID=6), moved from `client.py`; add re-export aliases in `client.py` (`from givenergy_api_client.energy_flow import EnergyDataFlowGrouping, EnergyDataFlowType`) to preserve backward compatibility
- [x] T007 Add `_raise_for_status(response: httpx.Response) -> None` helper in `givenergy_api_client/client.py` that inspects `response.status_code` and raises: `AuthenticationError` (401), `NotFoundError` (404), `APIValidationError` (422), `ServerError(status_code=...)` (5xx), `GivEnergyAPIError` (other 4xx); call this helper in all new domain methods immediately after every HTTP call
- [x] T008 Add typed factory methods to `GivenergyAPIClient` in `givenergy_api_client/client.py`: `account() -> Account`, `inverter(serial_number: str) -> Inverter`, `ems(inverter_serial_number: str) -> EMS`, `ev_charger(charger_uuid: str) -> EVCharger`, `inverter_preset(serial_number: str) -> InverterPreset`; add `list_ev_chargers(*, page: int = 1, page_size: int = 15) -> PaginatedResult[EVChargerData]` and `alist_ev_chargers(...)` async variant; use `TYPE_CHECKING` imports to avoid circular imports
- [x] T009 [P] Update `givenergy_api_client/__init__.py` to re-export `GivEnergyAPIError`, `AuthenticationError`, `NotFoundError`, `APIValidationError`, `ServerError`, `PaginatedResult`, `PaginationMeta`, `EnergyDataFlowGrouping`, `EnergyDataFlowType`

**Checkpoint**: Foundation ready — all user story phases can now proceed in parallel.

---

## Phase 3: User Story 1 — Account & Device Discovery (Priority: P1) 🎯 MVP

**Goal**: Expose `get()`, `get_by_id()`, `search()`, and `get_devices()` on the `Account`
domain class; handle auth errors and not-found errors correctly.

**Independent Test**: `poetry run pytest tests/test_account.py::TestAccountBasic` —
all mocked; no live network calls required.

### Implementation for User Story 1

- [x] T010 In `givenergy_api_client/account.py`, rename the existing `Account` Pydantic model class to `AccountData` (keep all fields unchanged); add `AccountDevice(BaseModel, frozen=True)` with fields `serial_number: str`, `type: str`, `site_id: int | None`, `inverter_serial: str`, `inverter_status: str`; update imports in `client.py` from `Account` → `AccountData`
- [x] T011 [P] In `givenergy_api_client/account.py`, implement the `Account` domain class with constructor `__init__(self, client: GivenergyAPIClient) -> None` and four sync methods: `get() -> AccountData` (`GET /account`), `get_by_id(*, user_id: str) -> AccountData` (`GET /account/{user_id}`), `search(*, username: str) -> AccountData` (`GET /account/search/{username}`), `get_devices(*, username: str, page: int = 1, page_size: int = 15) -> PaginatedResult[AccountDevice]` (`GET /account/{username}/devices`); every method calls `_raise_for_status()` then parses `response.json()["data"]` via `model_validate()`
- [x] T012 [P] [US1] Add async variants to the `Account` class: `aget()`, `aget_by_id(*, user_id)`, `asearch(*, username)`, `aget_devices(*, username, page, page_size)` — each uses `async with self._client.aget_client() as _client` and is otherwise identical in logic to its sync counterpart
- [x] T013 [US1] Write `tests/test_account.py` with `TestAccountBasic` class; mock `httpx` responses via `pytest-httpx`; cover: successful `get()`, successful `get_by_id()`, successful `search()`, `get_devices()` returns `PaginatedResult[AccountDevice]`, `AuthenticationError` raised on 401, `NotFoundError` raised on 404; include at least one async test using `pytest.mark.asyncio`

**Checkpoint**: User Story 1 (basic account ops) independently testable.

---

## Phase 4: User Story 2 — Inverter Monitoring & Energy Flows (Priority: P2)

**Goal**: Expose health checks and energy-flow queries on the `Inverter` domain class;
validate datetime params before any HTTP call.

**Independent Test**: `poetry run pytest tests/test_inverter.py` — all mocked.

### Implementation for User Story 2

- [x] T014 [P] Populate `givenergy_api_client/inverter.py` (currently a stub) with four Pydantic models: `InverterHealthCheck(frozen=True)` (fields: `name: str`, `value: str | int | float`, `status: str`, `unit: str | None`), `EnergyFlowPoint(frozen=True)` (`timestamp: datetime`, `value: float`), `EnergyFlowData(frozen=True)` (`type: EnergyDataFlowType`, `data: list[EnergyFlowPoint]`), `DebugCommandResult(frozen=True)` (`success: bool`, `code: int`)
- [x] T015 [US2] In `givenergy_api_client/inverter.py`, implement the `Inverter` domain class: constructor `__init__(self, client: GivenergyAPIClient, serial_number: str) -> None`; sync method `get_health() -> list[InverterHealthCheck]` (`GET /inverter/{sn}/health`, parses `response.json()["data"]` as list); sync method `get_energy_flows(*, start_time: datetime, end_time: datetime, grouping: EnergyDataFlowGrouping = EnergyDataFlowGrouping.HALF_HOURLY) -> list[EnergyFlowData]` (`POST /inverter/{sn}/energy-flows`, validates both datetimes are timezone-aware and `end_time > start_time` before HTTP call, raises `ValueError` otherwise); sync method `send_debug_command(*, hex_command: str) -> DebugCommandResult` (`POST /inverter/{sn}/debug/transparent/send`)
- [x] T016 [P] [US2] Add async variants to `Inverter`: `aget_health()`, `aget_energy_flows(...)`, `asend_debug_command(...)`
- [x] T017 [US2] Write `tests/test_inverter.py` covering: `get_health()` returns `list[InverterHealthCheck]`, `get_energy_flows()` returns `list[EnergyFlowData]`, `ValueError` raised when `end_time <= start_time`, `ValueError` raised when naive datetime passed, `NotFoundError` on 404, async variant for `aget_health()`

**Checkpoint**: User Story 2 independently testable.

---

## Phase 5: User Story 3 — EV Charger Monitoring & Control (Priority: P3)

**Goal**: Expose `EVCharger` domain class covering all 7 EV charger endpoints including
paginated meter data, charging sessions, command listing, and command execution.

**Independent Test**: `poetry run pytest tests/test_ev_charger.py` — all mocked.

### Implementation for User Story 3

- [x] T018 [P] Create `givenergy_api_client/ev_charger.py` with five Pydantic models: `EVChargerData(frozen=True)` (`uuid: str`, `serial_number: str`, `type: str`, `alias: str | None`, `online: bool`, `status: str`), `EVChargerMeasurement(frozen=True)` (`measurand: str`, `value: float`, `unit: str`), `EVChargerMeterReading(frozen=True)` (`meter_id: str`, `timestamp: datetime`, `measurements: list[EVChargerMeasurement]`), `ChargingSession(frozen=True)` (`started_by: str | None`, `meter_start: float`, `started_at: datetime`, `stopped_by: str | None`, `meter_stop: float | None`, `stopped_at: datetime | None`), `EVChargerCommandResult(frozen=True)` (`code: int`, `success: bool`, `message: str`)
- [x] T019 [US3] In `givenergy_api_client/ev_charger.py`, implement the `EVCharger` domain class: constructor `__init__(self, client: GivenergyAPIClient, charger_uuid: str) -> None`; sync methods: `get() -> EVChargerData` (`GET /ev-charger/{uuid}`), `get_meter_data(*, start_time: datetime, end_time: datetime, measurands: list[str], meter_ids: list[str], page: int = 1, page_size: int = 15) -> PaginatedResult[EVChargerMeterReading]` (`GET /ev-charger/{uuid}/meter-data`), `list_commands() -> list[str]` (`GET /ev-charger/{uuid}/commands`), `get_command(*, command_id: str) -> EVChargerCommandState` (`GET /ev-charger/{uuid}/commands/{id}` — see T020), `execute_command(*, command_id: str, payload: dict[str, str | int | float | bool | None]) -> EVChargerCommandResult` (`POST /ev-charger/{uuid}/commands/{id}`), `list_sessions(*, start_time: datetime | None = None, end_time: datetime | None = None, page: int = 1, page_size: int = 15) -> PaginatedResult[ChargingSession]` (`GET /ev-charger/{uuid}/charging-sessions`)
- [x] T020 [P] [US3] Add `EVChargerCommandState(frozen=True)` model in `givenergy_api_client/ev_charger.py` per FR-006a: declare all known fields; add `extra_fields: dict[str, str | int | float | bool | None] = {}` for dynamic keys (use `model_config = ConfigDict(frozen=True, extra="allow")` and override `model_post_init` to populate `extra_fields`); add async variants `aget()`, `aget_meter_data(...)`, `alist_commands()`, `aget_command(...)`, `aexecute_command(...)`, `alist_sessions(...)` to `EVCharger`
- [x] T021 [US3] Write `tests/test_ev_charger.py` covering: `list_ev_chargers()` on client returns `PaginatedResult[EVChargerData]`, `get()` returns `EVChargerData`, `get_meter_data()` returns `PaginatedResult[EVChargerMeterReading]`, `execute_command()` returns `EVChargerCommandResult`, `list_sessions()` returns `PaginatedResult[ChargingSession]`, `NotFoundError` on 404, `APIValidationError` on unsupported command (422), async variant for `aexecute_command()`

**Checkpoint**: User Story 3 independently testable.

---

## Phase 6: User Story 4 — Inverter Preset Control (Priority: P4)

**Goal**: Expose `InverterPreset` domain class with preset listing, inspection, and
application; handle the open-schema preset-values response with a typed model.

**Independent Test**: `poetry run pytest tests/test_inverter_preset.py` — all mocked.

### Implementation for User Story 4

- [x] T022 [P] Create `givenergy_api_client/inverter_preset.py` with models: `PresetParameter(frozen=True)` (`id: str`, `name: str`, `type: str`, `validation: dict[str, str | int | float | bool | None] | None`), `InverterPresetData(frozen=True)` (`id: int`, `identifier: str`, `name: str`, `description: str`, `parameters: list[PresetParameter]`), `PresetCurrentValues(frozen=True)` per FR-006a (declare known scalar fields; `extra_fields: dict[str, str | int | float | bool | None] = {}`), `PresetApplyResult(frozen=True)` (`success: bool`, `message: str`)
- [x] T023 [US4] In `givenergy_api_client/inverter_preset.py`, implement the `InverterPreset` domain class: constructor `__init__(self, client: GivenergyAPIClient, serial_number: str) -> None`; sync methods: `list_presets() -> list[InverterPresetData]` (`GET /inverter/{sn}/presets`), `get_preset(*, preset_id: int) -> PresetCurrentValues` (`GET /inverter/{sn}/presets/{id}`, validates using `PresetCurrentValues.model_validate()`), `apply_preset(*, preset_id: int, payload: dict[str, str | int | float | bool | None]) -> PresetApplyResult` (`POST /inverter/{sn}/presets/{preset}`)
- [x] T024 [P] [US4] Add async variants to `InverterPreset`: `alist_presets()`, `aget_preset(...)`, `aapply_preset(...)`
- [x] T025 [US4] Write `tests/test_inverter_preset.py` covering: `list_presets()` returns `list[InverterPresetData]`, `get_preset()` returns `PresetCurrentValues` with dynamic fields in `extra_fields`, `apply_preset()` returns `PresetApplyResult`, `NotFoundError` on unknown preset ID, `APIValidationError` on invalid payload, async variant for `alist_presets()`

**Checkpoint**: User Story 4 independently testable.

---

## Phase 7: User Story 5 — EMS Plant Data (Priority: P5)

**Goal**: Expose `EMS` domain class returning a typed `EMSSnapshot`.

**Independent Test**: `poetry run pytest tests/test_ems.py` — all mocked.

### Implementation for User Story 5

- [x] T026 [P] Populate `givenergy_api_client/ems.py` (currently a stub) with: `EMSInverterReading(frozen=True)` (`serial: str`, `power: float`), `EMSMeterReading(frozen=True)` (`meter_id: str`, `power: float`), `EMSSnapshot(frozen=True)` (`battery_power: float`, `battery_wh_remaining: float`, `grid_power: float`, `inverters: list[EMSInverterReading]`, `meters: list[EMSMeterReading]`)
- [x] T027 [US5] In `givenergy_api_client/ems.py`, implement the `EMS` domain class: constructor `__init__(self, client: GivenergyAPIClient, inverter_serial_number: str) -> None`; sync `get_latest() -> EMSSnapshot` (`GET /ems/{sn}/system-data/latest`, parses `response.json()["data"]`); async `aget_latest() -> EMSSnapshot`
- [x] T028 [US5] Write `tests/test_ems.py` covering: `get_latest()` returns `EMSSnapshot` with correct nested readings, `NotFoundError` on non-EMS inverter (404), async `aget_latest()`

**Checkpoint**: User Story 5 independently testable.

---

## Phase 8: User Story 6 — Multi-Account & SSO Hierarchy (Priority: P6)

**Goal**: Extend the `Account` domain class (from Phase 3) with child-account listing and
SSO-account retrieval; all return typed paginated or list results.

**Independent Test**: `poetry run pytest tests/test_account.py::TestAccountHierarchy` — all mocked.

### Implementation for User Story 6

- [x] T029 [US6] In `givenergy_api_client/account.py`, add three sync methods to the existing `Account` domain class: `list_children(*, page: int = 1, page_size: int = 15) -> PaginatedResult[AccountData]` (`GET /account-children`), `list_children_for_user(*, user_id: str, page: int = 1, page_size: int = 15) -> PaginatedResult[AccountData]` (`GET /account-children/{user_id}`), `get_sso_accounts() -> list[AccountData]` (`GET /sso/me/accounts`, parses `response.json()["data"]` as list)
- [x] T030 [P] [US6] Add async variants to `Account` for US6 methods: `alist_children(...)`, `alist_children_for_user(...)`, `aget_sso_accounts()`
- [x] T031 [US6] Extend `tests/test_account.py` with `TestAccountHierarchy` class covering: `list_children()` returns `PaginatedResult[AccountData]`, `list_children_for_user()` scoped to parent user, `get_sso_accounts()` returns `list[AccountData]`, `AuthenticationError` on 401 for hierarchy endpoints, async variant for `alist_children()`

**Checkpoint**: All user stories independently functional.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates, documentation, and final validation.

- [x] T032 Run `poetry run ty check givenergy_api_client/` and fix any type errors; confirm zero errors; update plan.md Constitution Check to reference `ty` instead of `mypy`
- [x] T033 [P] Run `poetry run ruff check --fix . && poetry run ruff format .` and resolve any remaining lint/format issues across all new and modified files
- [x] T034 [P] Update `givenergy_api_client/__init__.py` to export all new public symbols: `Account`, `AccountData`, `AccountDevice`, `Inverter`, `InverterHealthCheck`, `EnergyFlowData`, `EVCharger`, `EVChargerData`, `ChargingSession`, `EVChargerCommandResult`, `EMS`, `EMSSnapshot`, `InverterPreset`, `InverterPresetData`, `PresetApplyResult`, `PaginatedResult`, `PaginationMeta`, plus all exceptions
- [x] T035 Run the full validation suite: `poetry run pytest && poetry run ty check givenergy_api_client/ && poetry run ruff check . && poetry run ruff format --check .` — all must exit zero; document results in a one-line comment at top of `tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user story phases
- **US1 (Phase 3)**: Depends on Phase 2 — can start as soon as Foundational completes
- **US2 (Phase 4)**: Depends on Phase 2 — parallel with US1 if team capacity allows
- **US3 (Phase 5)**: Depends on Phase 2 — parallel with US1/US2
- **US4 (Phase 6)**: Depends on Phase 2 — parallel with any other US phase
- **US5 (Phase 7)**: Depends on Phase 2 — parallel with any other US phase
- **US6 (Phase 8)**: Depends on Phase 3 (US1) — Account class must exist first
- **Polish (Phase 9)**: Depends on all desired user story phases completing

### Within Each User Story

- Pydantic models (T0xx [P]) → domain class implementation → async variants [P] → tests
- Tests are written concurrently with or immediately after the domain class

### Parallel Opportunities

```bash
# Phase 2 — run these together (different files):
T004  # exceptions.py
T005  # pagination.py
T006  # energy_flow.py (enums move)
T009  # __init__.py stubs

# Phase 3 — after T010:
T011  # Account sync methods
T012  # Account async variants  (concurrent with T011)

# Phase 5 — run together:
T018  # EV charger Pydantic models
T020  # EVChargerCommandState + async variants

# All US phases after Phase 2:
Phase 3 (US1) ║ Phase 4 (US2) ║ Phase 5 (US3) ║ Phase 6 (US4) ║ Phase 7 (US5)
```

---

## Implementation Strategy

### MVP (User Story 1 only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks everything)
3. Complete Phase 3: US1 — Account & Device Discovery
4. **STOP and validate**: `poetry run pytest tests/test_account.py`
5. Demonstrates: typed domain model, error handling, sync+async parity, PaginatedResult

### Full Incremental Delivery

1. Setup + Foundational → shared infrastructure ready
2. US1 → Account domain (MVP)
3. US2 → Inverter monitoring
4. US3 → EV charger control
5. US4 → Inverter presets
6. US5 → EMS data
7. US6 → Multi-account hierarchy
8. Polish → all quality gates pass

### Parallel Team Strategy (2+ developers)

- Dev A: Phase 2 (Foundational) then US1 (Phase 3) + US6 (Phase 8)
- Dev B: Phase 2 review then US2 (Phase 4) + US5 (Phase 7)
- Dev C: Phase 2 review then US3 (Phase 5) + US4 (Phase 6)

---

## Notes

- `[P]` tasks work on different files with no in-flight dependency conflicts
- Every domain class MUST call `_raise_for_status()` before parsing JSON
- `ty` must pass on every commit; run `poetry run ty check givenergy_api_client/` locally
- Ruff line length is 120 — verify `[tool.ruff] line-length = 120` in `pyproject.toml`
- `AccountData` is the renamed Pydantic model; `Account` is the domain class — never swap
- `EVChargerData` is the Pydantic model; `EVCharger` is the domain class
- `InverterPresetData` is the Pydantic model; `InverterPreset` is the domain class
- Paginated endpoints return `PaginatedResult[T]` — never `dict`
- Open-schema endpoints use `extra_fields: dict[str, str | int | float | bool | None]`
