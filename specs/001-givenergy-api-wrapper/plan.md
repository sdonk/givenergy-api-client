# Implementation Plan: GivEnergy API Full Coverage

**Branch**: `001-givenergy-api-wrapper` | **Date**: 2026-03-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-givenergy-api-wrapper/spec.md`

## Summary

Extend the existing `givenergy-api-client` Python library to cover all 21 endpoints
in the GivEnergy Cloud API v1 spec. Three endpoints already exist (`get_account`,
`get_communication_devices`, `get_communication_device`); this plan adds the remaining
18. All new code follows the domain-model architecture: one Python module per REST
resource group, each containing Pydantic v2 frozen models and a domain class that
accepts a `GivenergyAPIClient` instance to perform sync and async operations.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: httpx (HTTP), Pydantic v2 (models), pytest + pytest-httpx (tests)
**Storage**: N/A — stateless HTTP client library
**Testing**: pytest + pytest-httpx (all tests MUST run without live network access)
**Target Platform**: Any Python 3.12+ runtime (library — no deployment target)
**Project Type**: Library
**Performance Goals**: No blocking I/O in async paths; httpx connection pooling via
context managers; response parsing in a single `model_validate()` call
**Constraints**: No transitive dependencies beyond httpx and Pydantic v2; all public
methods must be fully typed; mypy strict mode must pass
**Scale/Scope**: ~18 new methods (sync + async variants = ~36 callables); 6 new/extended
modules; ~13 new Pydantic models; 1 new exceptions module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Code Quality | All code passes Ruff + mypy strict before merge | ✅ Plan compliant — same toolchain |
| I. Code Quality | All models use `ConfigDict(frozen=True)` | ✅ Enforced for all new models |
| II. Testing Standards | Every public method has pytest-httpx tests | ✅ Test files scoped per domain |
| II. Testing Standards | Tests run without live network access | ✅ All tests mock httpx |
| III. API Consistency | Three-step pattern: open client → request → `model_validate()` | ✅ All domain methods follow this |
| III. API Consistency | Sync/async parity (`method()` / `amethod()`) | ✅ Every method has both variants |
| IV. Performance | httpx pooling via context managers only | ✅ Domain classes use `get_client()` / `aget_client()` |
| IV. Performance | No intermediate dict manipulation beyond `["data"]` | ✅ Direct `model_validate()` on payload |

**Result**: ✅ All gates pass. No complexity violations. No justification table needed.

*Post-design re-check*: Architecture confirmed in Phase 1 — domain model pattern adds
zero complexity violations; it is an extension of the existing three-step pattern,
not a replacement.

## Project Structure

### Documentation (this feature)

```text
specs/001-givenergy-api-wrapper/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── account-domain.md
│   ├── inverter-domain.md
│   ├── ev-charger-domain.md
│   ├── ems-domain.md
│   ├── inverter-preset-domain.md
│   └── exceptions.md
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
givenergy_api_client/
├── __init__.py                  # re-export public surface (EXTEND)
├── client.py                    # GivenergyAPIClient auth + context managers (EXTEND)
├── exceptions.py                # AuthenticationError, NotFoundError,
│                                #   ValidationError, ServerError (NEW)
├── account.py                   # Account, AccountDevice models + AccountDomain (EXTEND)
├── communication_device.py      # existing models — no changes needed
├── inverter.py                  # InverterHealthCheck, EnergyFlowPoint,
│                                #   DebugResult + Inverter domain class (EXTEND stub)
├── energy_flow.py               # EnergyDataFlowGrouping, EnergyDataFlowType enums
│                                #   (EXTEND stub — move enums from client.py)
├── ev_charger.py                # EVChargerData, EVChargerMeterReading, ChargingSession,
│                                #   EVChargerCommandResult + EVCharger domain class (NEW)
├── ems.py                       # EMSSnapshot + nested models + EMS domain class (EXTEND stub)
└── inverter_preset.py           # InverterPresetData, PresetParameter,
                                 #   PresetApplyResult + InverterPreset domain class (NEW)

tests/
├── __init__.py
├── test_client.py               # EXISTS — extend with error-handling tests
├── test_account.py              # NEW — Account domain sync + async
├── test_inverter.py             # NEW — Inverter domain sync + async
├── test_ev_charger.py           # NEW — EVCharger domain sync + async
├── test_ems.py                  # NEW — EMS domain sync + async
└── test_inverter_preset.py      # NEW — InverterPreset domain sync + async
```

**Structure Decision**: Single project (Option 1), following the existing layout.
Each REST resource group maps to one module. Domain classes live in the same module
as their Pydantic models. `GivenergyAPIClient` is extended with factory methods that
return domain instances bound to `self`. Domain classes are named after the resource
without a suffix (`Account`, `Inverter`, `EVCharger`, `EMS`, `InverterPreset`). Where
a Pydantic data model and domain class would share a name, the data model is renamed
with a `Data` suffix (e.g. `AccountData`, `EVChargerData`, `InverterPresetData`).

## Complexity Tracking

> No constitution violations — table not required.
