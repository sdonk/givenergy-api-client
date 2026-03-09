# Tasks: SDK Documentation

**Input**: Design documents from `/specs/002-sdk-docs/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Per the project constitution (Principle II — TDD), the doctest validation infrastructure
(`conftest.py`) MUST be in place and confirmed working before any documentation page is written.
Each page's snippets MUST be validated passing (`pytest --doctest-glob`) after writing.

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths are included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies, configure MkDocs, and establish the doctest validation
framework that every subsequent phase depends on.

- [ ] T001 Add `mkdocs-material>=9.6` to dev dependencies in `pyproject.toml`
- [ ] T002 Configure `mkdocs.yml` with Material theme features (`content.code.copy`, `content.tabs.link`, `navigation.tabs`, `navigation.sections`, `search.highlight`) and full `nav` order per `contracts/page-contract.md`
- [ ] T003 Create `tests/conftest.py` with a mocked `GivenergyAPIClient` doctest fixture that intercepts all HTTP calls so snippets run without a live API key

**Checkpoint**: `uv run mkdocs build` exits 0 (empty `docs/` is fine at this stage); `uv run pytest tests/conftest.py` imports cleanly.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify the doctest validation pipeline end-to-end before writing any page content.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Add a minimal smoke-test snippet to `docs/index.md` (just the client import and instantiation) and confirm `uv run pytest docs/ --doctest-glob="*.md" -v` finds and runs it — this validates the conftest fixture is wired correctly

**Checkpoint**: Doctest pipeline is green for a trivial snippet — page authoring can now begin.

---

## Phase 3: User Story 1 — Getting Started (Priority: P1) 🎯 MVP

**Goal**: A developer with zero prior SDK knowledge can make a successful API call within
5 minutes of reading `docs/index.md`.

**Independent Test**: Copy the snippets from `docs/index.md`, substitute a real API key,
and receive a valid account response with no other documentation consulted.

### Tests for User Story 1 (REQUIRED — TDD)

> **Write the conftest fixture stubs for the account endpoint BEFORE writing prose.**
> Run `uv run pytest docs/ --doctest-glob="*.md" -v` to confirm it finds the snippet and passes.

- [ ] T005 [US1] Extend `tests/conftest.py` to mock the `GET /account` endpoint so the getting-started snippet can run in doctest mode

### Implementation for User Story 1

- [ ] T006 [US1] Write `docs/index.md` — sections: Installation (single `pip install` command), Authentication (instantiate `GivenergyAPIClient`), First API call (`client.account().get()`), Next Steps (links to resource pages); include `!!! tip` admonition after authentication snippet per `contracts/page-contract.md`
- [ ] T007 [US1] Validate `docs/index.md` snippets: `uv run pytest docs/index.md --doctest-glob="*.md" -v` must exit 0

**Checkpoint**: `docs/index.md` passes doctest validation and satisfies all items on the
getting-started page checklist in `specs/002-sdk-docs/quickstart.md`.

---

## Phase 4: User Story 2 — Domain-by-Domain Usage Reference (Priority: P2)

**Goal**: A developer can find and successfully use any of the five resource types by reading
only that resource's documentation section.

**Independent Test**: Read `docs/account.md` only and successfully call every `Account` method;
repeat for each of the other four resource pages.

### Tests for User Story 2 (REQUIRED — TDD)

> **Extend conftest mocks for all five resource endpoints BEFORE writing any resource page.**

- [ ] T008 [P] [US2] Extend `tests/conftest.py` to mock all `Account` endpoints (`GET /account`, `GET /account/{id}`, `GET /accounts`, `GET /account/devices`, `GET /account/children`, `GET /account/children/{id}`, `GET /account/sso`)
- [ ] T009 [P] [US2] Extend `tests/conftest.py` to mock all `Inverter` endpoints (`GET /inverter/{sn}/health`, `GET /inverter/{sn}/energy-flows`, `POST /inverter/{sn}/debug`)
- [ ] T010 [P] [US2] Extend `tests/conftest.py` to mock the `EMS` endpoint (`GET /inverter/{sn}/ems/snapshot`)
- [ ] T011 [P] [US2] Extend `tests/conftest.py` to mock all `EV Charger` endpoints (`GET /ev-chargers`, `GET /ev-charger/{uuid}`, `GET /ev-charger/{uuid}/meter`, `GET /ev-charger/{uuid}/commands`, `GET /ev-charger/{uuid}/command/{id}`, `POST /ev-charger/{uuid}/command`, `GET /ev-charger/{uuid}/sessions`)
- [ ] T012 [P] [US2] Extend `tests/conftest.py` to mock all `Inverter Preset` endpoints (`GET /inverter/{sn}/presets`, `GET /inverter/{sn}/preset/{id}`, `POST /inverter/{sn}/preset/{id}`)

### Implementation for User Story 2

- [ ] T013 [P] [US2] Write `docs/account.md` — sections: `get()`, `get_by_id()`, `search()`, `get_devices()` (pagination metadata), `list_children()`, `list_children_for_user()`, `get_sso_accounts()`; sync/async tabs on every method
- [ ] T014 [P] [US2] Write `docs/inverter.md` — sections: `get_health()`, `get_energy_flows()`, `send_debug_command()`; include `!!! warning` before energy-flows example (timezone-aware datetimes) and `!!! danger` before debug command example per `contracts/page-contract.md`; sync/async tabs on every method
- [ ] T015 [P] [US2] Write `docs/ems.md` — section: `get_latest()` with all snapshot fields shown; include `!!! note` in intro paragraph noting EMS requires a compatible inverter (404 otherwise) per `contracts/page-contract.md`; sync/async tabs
- [ ] T016 [P] [US2] Write `docs/ev-charger.md` — sections: `list_ev_chargers()`, `ev_charger(uuid).get()`, `get_meter_data()`, `list_commands()`, `get_command()` (with `extra_fields` reference), `execute_command()`, `list_sessions()` (with and without time filters); sync/async tabs on every method
- [ ] T017 [P] [US2] Write `docs/inverter-presets.md` — sections: `list_presets()`, `get_preset()` (with `extra_fields` reference), `apply_preset()`; sync/async tabs on every method
- [ ] T018 [US2] Validate all five resource pages: `uv run pytest docs/account.md docs/inverter.md docs/ems.md docs/ev-charger.md docs/inverter-presets.md --doctest-glob="*.md" -v` must exit 0

**Checkpoint**: All five resource pages pass doctest validation and satisfy the sync/async tab
and admonition requirements in `contracts/page-contract.md`.

---

## Phase 5: User Story 3 — Error Handling Reference (Priority: P3)

**Goal**: A developer can identify the correct exception class for each HTTP error scenario
and write appropriate handling code from `docs/error-handling.md` alone.

**Independent Test**: Read `docs/error-handling.md` and write correct `try/except` blocks for
`AuthenticationError`, `NotFoundError`, `APIValidationError`, `ServerError`, and the base
`GivEnergyAPIError` without consulting any other page.

### Tests for User Story 3 (REQUIRED — TDD)

- [ ] T019 [US3] Extend `tests/conftest.py` to mock 401, 404, 422, and 500 error responses so error-handling snippets can execute in doctest mode

### Implementation for User Story 3

- [ ] T020 [US3] Write `docs/error-handling.md` — sections: exception hierarchy (table or diagram), per-exception reference (`AuthenticationError`, `NotFoundError`, `APIValidationError` with `.args[0]`, `ServerError` with `.status_code`, `GivEnergyAPIError` base), complete `try/except` example covering all cases
- [ ] T021 [US3] Validate `docs/error-handling.md` snippets: `uv run pytest docs/error-handling.md --doctest-glob="*.md" -v` must exit 0

**Checkpoint**: `docs/error-handling.md` passes doctest validation and covers all exception
types with runnable examples.

---

## Phase 6: User Story 4 — Async Usage Guide (Priority: P4)

**Goal**: A developer can convert any sync example to its async counterpart using only
`docs/async.md`.

**Independent Test**: Read `docs/async.md` and rewrite the account retrieval snippet from
`docs/index.md` as an async function using `asyncio.gather` without consulting any other page.

### Tests for User Story 4 (REQUIRED — TDD)

- [ ] T022 [US4] Extend `tests/conftest.py` with async-aware mock stubs so async snippets in `docs/async.md` can be validated via `--doctest-glob`

### Implementation for User Story 4

- [ ] T023 [US4] Write `docs/async.md` — sections: pattern explanation (every sync method has an `a`-prefixed async counterpart with identical signature), single-resource async example (`account`), concurrent multi-resource example using `asyncio.gather`, guidance on when to choose async vs sync
- [ ] T024 [US4] Validate `docs/async.md` snippets: `uv run pytest docs/async.md --doctest-glob="*.md" -v` must exit 0

**Checkpoint**: `docs/async.md` passes doctest validation including the `asyncio.gather` example.

---

## Phase 7: User Story 5 — Advanced Topics Reference (Priority: P5)

**Goal**: A developer can iterate paginated results, access open-schema `extra_fields`, and
construct timezone-aware datetimes correctly using only `docs/advanced.md`.

**Independent Test**: Read `docs/advanced.md` and write a loop that fetches all pages of
`account.get_devices()` and prints every serial number without consulting any other page.

### Tests for User Story 5 (REQUIRED — TDD)

- [ ] T025 [US5] Extend `tests/conftest.py` to mock multi-page responses (with `meta.last_page > 1`) so the pagination loop snippet can execute in doctest mode

### Implementation for User Story 5

- [ ] T026 [US5] Write `docs/advanced.md` — sections: Pagination (`PaginatedResult`, `meta.last_page`, full page-loop example), Open-schema responses (`extra_fields` dict, when it appears, how to access), Timezone-aware datetimes (correct `datetime.now(UTC)` vs incorrect `datetime.now()`, explicit error message shown)
- [ ] T027 [US5] Validate `docs/advanced.md` snippets: `uv run pytest docs/advanced.md --doctest-glob="*.md" -v` must exit 0

**Checkpoint**: `docs/advanced.md` passes doctest validation for all three advanced topic snippets.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Full-site validation and contract compliance review across all pages.

- [ ] T028 [P] Run `uv run mkdocs build` and confirm it exits 0 with no broken links or missing pages
- [ ] T029 [P] Run `uv run pytest docs/ --doctest-glob="*.md" -v` across all nine pages in one pass and confirm 0 failures
- [ ] T030 Verify every page satisfies the full checklist in `specs/002-sdk-docs/quickstart.md` (intro paragraph, sync/async tabs, imports in every snippet, placeholder values, required admonitions)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **User Stories (Phases 3–7)**: All depend on Phase 2 completion
  - US1 has no dependency on US2–US5
  - US2–US5 have no dependency on each other (fully parallel)
  - Within US2, all five resource pages [P] are independent of each other
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends on | Independently testable |
|-------|-----------|------------------------|
| US1 (P1) | Phase 2 only | ✅ Yes — `docs/index.md` alone |
| US2 (P2) | Phase 2 only | ✅ Yes — each resource page is self-contained |
| US3 (P3) | Phase 2 only | ✅ Yes — `docs/error-handling.md` alone |
| US4 (P4) | Phase 2 only | ✅ Yes — `docs/async.md` alone |
| US5 (P5) | Phase 2 only | ✅ Yes — `docs/advanced.md` alone |

### Within Each User Story

1. Extend conftest mocks (TDD infrastructure) — must fail first, then pass
2. Write the page with all snippets
3. Validate snippets pass (`pytest --doctest-glob`)
4. Checkpoint before moving on

### Parallel Opportunities

- T008–T012 (conftest extensions for US2) can all run in parallel
- T013–T017 (resource pages for US2) can all run in parallel
- Once Phase 2 is complete, all five user stories can be worked in parallel
- T028–T029 (final validation) can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all conftest extensions for US2 in parallel:
Task: "T008 — Extend conftest for Account endpoints"
Task: "T009 — Extend conftest for Inverter endpoints"
Task: "T010 — Extend conftest for EMS endpoint"
Task: "T011 — Extend conftest for EV Charger endpoints"
Task: "T012 — Extend conftest for Inverter Preset endpoints"

# Once T008-T012 are done, launch all five resource pages in parallel:
Task: "T013 — Write docs/account.md"
Task: "T014 — Write docs/inverter.md"
Task: "T015 — Write docs/ems.md"
Task: "T016 — Write docs/ev-charger.md"
Task: "T017 — Write docs/inverter-presets.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004)
3. Complete Phase 3: US1 (T005–T007)
4. **STOP and VALIDATE**: `mkdocs build` + `pytest docs/index.md --doctest-glob`
5. Deploy or share `docs/index.md` preview

### Incremental Delivery

1. Setup + Foundational → pipeline ready
2. US1 → Getting Started live → MVP deliverable
3. US2 → All five resource pages → developers can reference every method
4. US3 → Error handling complete → production-safe integrations
5. US4 → Async guide complete → async-first developers covered
6. US5 → Advanced topics complete → all edge cases documented

### Parallel Team Strategy

With multiple contributors:

1. All complete Phase 1 + Phase 2 together
2. Once Foundational is done:
   - Contributor A: US1 + US3 (getting started + error handling)
   - Contributor B: US2 account + inverter pages
   - Contributor C: US2 ems + ev-charger + inverter-presets pages
   - Contributor D: US4 + US5 (async + advanced topics)

---

## Task Summary

| Phase | Tasks | Story | Parallelizable |
|-------|-------|-------|----------------|
| 1 — Setup | T001–T003 | — | T001, T002, T003 independent |
| 2 — Foundational | T004 | — | Sequential after Phase 1 |
| 3 — US1 Getting Started | T005–T007 | US1 | T005 then T006 then T007 |
| 4 — US2 Domain Reference | T008–T018 | US2 | T008–T012 parallel; T013–T017 parallel |
| 5 — US3 Error Handling | T019–T021 | US3 | Sequential within story |
| 6 — US4 Async Guide | T022–T024 | US4 | Sequential within story |
| 7 — US5 Advanced Topics | T025–T027 | US5 | Sequential within story |
| 8 — Polish | T028–T030 | — | T028, T029 parallel |

**Total tasks**: 30
**Parallel opportunities**: 12 tasks marked [P]
**Suggested MVP scope**: Phase 1 + Phase 2 + Phase 3 (US1 only — 7 tasks)

---

## Notes

- `[P]` tasks operate on different files and have no shared state — safe to run concurrently
- `[Story]` label maps each task to its user story for traceability and independent delivery
- Each story is independently completable: conftest mock → write page → validate snippets
- Never write page content before extending `conftest.py` for that page's endpoints (TDD)
- Commit after each checkpoint (T007, T018, T021, T024, T027, T030)
- Stop at any checkpoint to validate the story independently before continuing
