# Contract: Documentation Page Structure

Every documentation page MUST satisfy this contract before it is considered complete.

---

## Required Elements (all pages)

| Element | Requirement |
|---------|-------------|
| Page title | H1 heading matching the `nav` entry in `mkdocs.yml` |
| Intro paragraph | 1–3 sentences explaining what this page covers |
| Code snippets | Runnable with a valid API key (placeholder values used) |
| Imports | All necessary imports included at the top of each snippet |
| Sync/async tabs | Present on every method example (except Getting Started) |

---

## Code Snippet Contract

Every code snippet MUST:

1. Be fenced with ` ```python ` (enables syntax highlighting)
2. Begin with all required imports for that snippet
3. Use placeholder values: `"your-api-key"`, `"CE2345G123"`, `"uuid-1234-abcd"`
4. Be self-contained — runnable in isolation after imports
5. Show the return value being used (assigned or iterated), not just called

```python
# CORRECT — imports included, return value used, placeholder values
from givenergy_api_client.client import GivenergyAPIClient

client = GivenergyAPIClient(api_key="your-api-key")
result = client.account().get()
print(result.email)

# WRONG — missing imports, return value discarded, no client setup shown
client.account().get()
```

---

## Admonition Contract

The following admonitions MUST appear in the specified locations:

| Admonition | Type | Location |
|------------|------|----------|
| Timezone warning | `!!! warning` | `inverter.md` before `get_energy_flows()` example |
| Debug command danger | `!!! danger` | `inverter.md` before `send_debug_command()` example |
| EMS compatibility note | `!!! note` | `ems.md` intro paragraph |
| Placeholder reminder | `!!! tip` | `index.md` after authentication snippet |

---

## Sync/Async Tab Contract

Resource pages MUST present sync and async variants using Material content tabs:

```markdown
=== "Sync"

    ```python
    result = client.account().get()
    ```

=== "Async"

    ```python
    result = await client.account().aget()
    ```
```

Tab labels MUST be exactly `"Sync"` and `"Async"` (capitalised, no variation) so that
Material's linked tabs feature works correctly across pages.

---

## Navigation Contract (`mkdocs.yml`)

The `nav` section MUST list pages in this order:

```yaml
nav:
  - Getting Started: index.md
  - Resources:
    - Account: account.md
    - Inverter: inverter.md
    - EMS: ems.md
    - EV Charger: ev-charger.md
    - Inverter Presets: inverter-presets.md
  - Error Handling: error-handling.md
  - Async Usage: async.md
  - Advanced Topics: advanced.md
```

---

## Validation Contract (FR-008)

All snippets MUST pass automated validation via `conftest.py` doctest fixtures
before the documentation is published. A failing snippet blocks the docs build.
