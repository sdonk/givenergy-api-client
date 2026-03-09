# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python client library for the [GivEnergy Cloud API v1](https://givenergy.cloud/docs/api/v1). Uses `httpx` for HTTP and Pydantic v2 for response model validation.

## Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_client.py::TestClient::test_get_account

# Lint (with auto-fix)
uv run ruff check --fix .

# Format
uv run ruff format .

# Type check
uv run ty .
```

## Architecture

`GivenergyAPIClient` (`client.py`) is the main entry point. It wraps `httpx` and exposes both sync (`get_client()`) and async (`aget_client()`) context managers that yield authenticated HTTP clients.

Each API method follows the same pattern:
1. Open a client via `with self.get_client() as _client`
2. Make the HTTP request
3. Parse the `["data"]` key of the JSON response into a Pydantic model via `Model.model_validate()`

**Model hierarchy** (`communication_device.py` contains the bulk of the nested models):
- `CommunicationDevice` → `Inverter` → `Battery` / `Warranty` / `FirmwareVersion` / `Connections` → `ConnectionBattery` / `ConnectionMeter`
- `Account` (`account.py`) is a flat model
- `energy_flow.py` and `inverter.py` are currently stubs

All Pydantic models use `ConfigDict(frozen=True)`.

## Tooling

- **Package manager**: uv (`pyproject.toml` + `uv.lock`)
- **Linter/formatter**: Ruff (line length 119, targets Python 3.12)
- **Type checker**: mypy (strict: `disallow_untyped_defs`, `warn_return_any`)
- **Tests**: pytest + `pytest-httpx` for mocking httpx calls
- **Pre-commit**: ruff + mypy run on commit

## Active Technologies
- Python 3.12+ + httpx (HTTP), Pydantic v2 (models), pytest + pytest-httpx (tests) (001-givenergy-api-wrapper)
- N/A — stateless HTTP client library (001-givenergy-api-wrapper)
- Python 3.12+ (SDK) + Markdown (docs content) + `mkdocs-material>=9.6` (MkDocs + Material theme in one package) (002-sdk-docs)
- Markdown files in `docs/`; static HTML output in `site/` (gitignored) (002-sdk-docs)

## Recent Changes
- 001-givenergy-api-wrapper: Added Python 3.12+ + httpx (HTTP), Pydantic v2 (models), pytest + pytest-httpx (tests)
