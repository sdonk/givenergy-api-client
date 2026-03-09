<!--
Sync Impact Report
==================
Version change:      1.0.0 → 1.1.0
Bump type:           MINOR (TDD mandate added as non-negotiable rule; tooling corrected)

Modified principles:
  - II. Testing Standards: added explicit TDD mandate (tests MUST be written first,
    MUST fail before any implementation begins); added TDD as named NON-NEGOTIABLE.

Tooling corrections (PATCH-level, bundled into this MINOR bump):
  - Type checker: mypy → ty (Astral ty; command: uv run ty check givenergy_api_client/)
  - Line length: 119 → 120 (matches pyproject.toml [tool.ruff] line-length = 120)
  - Quality Gates table updated accordingly.

Added sections:      None
Removed sections:    None

Templates reviewed:
  - .specify/templates/plan-template.md     ✅ Constitution Check gate is generic; compatible
  - .specify/templates/spec-template.md     ✅ No constitution-specific references; compatible
  - .specify/templates/tasks-template.md    ✅ Updated — TDD note added; OPTIONAL tests
                                               label changed to reflect constitution mandate
  - CLAUDE.md                               ⚠ Still references mypy; update separately

Follow-up TODOs:
  - Update CLAUDE.md to replace `mypy` references with `ty` and line-length 119 → 120.
-->

# GivEnergy API Client Constitution

## Core Principles

### I. Code Quality (NON-NEGOTIABLE)

All code MUST pass Ruff linting and formatting checks (line length 120, Python 3.12
target) and ty strict type checking before merge. Pydantic v2 models MUST use
`ConfigDict(frozen=True)` to enforce immutability. No untyped functions or missing
return annotations are permitted. Pre-commit hooks enforce linting and type checks
automatically on every commit.

**Rationale**: A client library is a published surface relied on by downstream
consumers. Strict typing and immutable models eliminate runtime surprises and make
the API contract explicit and machine-verifiable.

### II. Testing Standards — TDD (NON-NEGOTIABLE)

Test-Driven Development MUST be followed on all new code. The required sequence is:

1. **Write tests first** — before writing any implementation code for a new method,
   class, or behaviour, write the corresponding test(s).
2. **Tests MUST fail** — run the tests and confirm they fail (red) before writing
   implementation. A test that passes before implementation indicates a mis-specified
   test.
3. **Implement to pass** — write the minimum implementation to make the tests pass
   (green).
4. **Refactor** — clean up the code while keeping all tests green.

All public API methods MUST have corresponding tests using pytest and `pytest-httpx`
to mock HTTP interactions. Tests MUST cover:

- Successful response parsing via `Model.model_validate()`
- HTTP error conditions (4xx, 5xx, network errors)
- Correct endpoint URL construction and request headers/auth

Test coverage MUST NOT regress between commits. Tests MUST be independently runnable
without network access or live credentials.

**Rationale**: The library wraps an external API whose live responses cannot be
controlled in CI. TDD ensures correctness is verified before code exists and that
`pytest-httpx` mocking accurately reflects request construction and response parsing.

### III. API Consistency

Every public API method MUST follow the established three-step pattern:

1. Open a client via `with self.get_client() as _client` (sync) or
   `async with self.aget_client() as _client` (async).
2. Make the HTTP request using the authenticated client.
3. Parse the `["data"]` key of the JSON response via `Model.model_validate()`.

Sync and async variants MUST expose equivalent functionality. Public interface
breaking changes (signature, behaviour, or removed methods) MUST increment the
library MAJOR version. Internal helpers are exempt from this rule.

**Rationale**: A consistent, predictable interface reduces cognitive load for
consumers and ensures sync/async parity is maintained as new endpoints are added.

### IV. Performance Requirements

- HTTP connections MUST use `httpx` connection pooling through context managers;
  ad-hoc `httpx.Client()` instantiation outside `get_client()` / `aget_client()`
  is forbidden.
- Response parsing MUST use Pydantic v2 `model_validate()` directly on the API
  payload — no intermediate dict manipulation beyond accessing the `["data"]` key.
- Async methods (`aget_client()`) MUST be used when the caller operates in an
  async context; synchronous blocking I/O is forbidden inside async code paths.
- No unnecessary copies of response data are permitted; frozen Pydantic models
  serve as the single authoritative representation of each API resource.

**Rationale**: As a library, GivEnergy API Client must not impose latency, blocking
behaviour, or memory overhead beyond what the underlying HTTP transport requires.

## Development Standards

- **Language**: Python 3.12+
- **Package manager**: Poetry (`pyproject.toml`)
- **HTTP client**: httpx (sync and async context managers)
- **Data validation**: Pydantic v2 — all models MUST set `ConfigDict(frozen=True)`
- **Linter / formatter**: Ruff (line length 120, Python 3.12 target)
- **Type checker**: ty (Astral — `uv run ty check givenergy_api_client/`)
- **Test framework**: pytest + pytest-httpx (no live network calls in tests)
- **TDD**: Tests MUST be written and confirmed failing before implementation
- **Pre-commit**: Ruff + ty enforced on every commit via `.pre-commit-config.yaml`

All dependencies MUST be declared and pinned through Poetry. Manual edits to
`pyproject.toml` outside of Poetry commands require explicit justification in the
PR description.

## Quality Gates

The following gates MUST all pass before any code is merged to `main`:

| Gate    | Command                                    | Failure threshold             |
|---------|--------------------------------------------|-------------------------------|
| Lint    | `uv run ruff check .`                      | Any error                     |
| Format  | `uv run ruff format --check .`             | Any diff                      |
| Types   | `uv run ty check givenergy_api_client/`    | Any error                     |
| Tests   | `uv run pytest`                            | Any failure or coverage regress |

Gates 1–3 are enforced by pre-commit hooks. Gate 4 MUST be verified in CI
(`.github/workflows/tests.yml`). A PR that bypasses any gate requires explicit
documented justification and maintainer approval.

## Governance

This constitution supersedes all other development practices for this repository.
Amendments require:

1. A documented rationale for why the change is necessary.
2. A version increment per semantic versioning:
   - **MAJOR**: Principle removal, redefinition, or governance incompatibility.
   - **MINOR**: New principle, section, or materially expanded guidance.
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements.
3. A migration plan if existing code violates the amended principle.

All PRs MUST verify compliance with the Constitution Check gate defined in
`.specify/templates/plan-template.md`. Complexity violations (e.g., deviations
from the three-step API method pattern) MUST be justified in the Complexity
Tracking table of the feature implementation plan.

`CLAUDE.md` serves as the runtime development guidance document and MUST remain
in sync with this constitution. Any amendment to a principle that affects commands,
tooling, or architecture described in `CLAUDE.md` MUST include a corresponding
update to that file.

**Version**: 1.1.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07
