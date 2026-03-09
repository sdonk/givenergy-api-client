# Data Model: SDK Documentation

This feature produces documentation content, not data entities. The "model" here
describes the structure and required content of each documentation page.

---

## Page: Getting Started (`docs/index.md`)

**Purpose**: First contact. Zero-to-working-call in <5 minutes.

**Required sections**:
1. Installation — single command
2. Authentication — create `GivenergyAPIClient` with API key
3. First API call — retrieve account details with full working snippet
4. Next steps — links to resource pages

**Constraints**:
- No optional parameters in examples (keep it minimal)
- Code snippet must be runnable with a valid API key only

---

## Page: Account Operations (`docs/account.md`)

**Required sections**:
1. Getting your account (`account().get()`)
2. Looking up by ID (`get_by_id()`)
3. Searching by username (`search()`)
4. Listing devices (`get_devices()`) — includes pagination metadata example
5. Child accounts (`list_children()`, `list_children_for_user()`)
6. SSO accounts (`get_sso_accounts()`)

**Sync/async tabs**: Required on each method example.

---

## Page: Inverter Operations (`docs/inverter.md`)

**Required sections**:
1. Health checks (`get_health()`) — iterate results
2. Energy flows (`get_energy_flows()`) — MUST include timezone-aware datetime callout
3. Debug commands (`send_debug_command()`) — MUST include caution admonition

**Sync/async tabs**: Required on each method example.

**Special requirements**:
- Admonition (`!!! warning`) on the naive datetime error
- Admonition (`!!! danger`) on debug command risks

---

## Page: EMS Operations (`docs/ems.md`)

**Required sections**:
1. Getting the latest snapshot (`get_latest()`) — show all snapshot fields

**Sync/async tabs**: Required.

**Special requirements**:
- Note that EMS is only available on compatible inverters (404 otherwise)

---

## Page: EV Charger Operations (`docs/ev-charger.md`)

**Required sections**:
1. Listing all chargers (`list_ev_chargers()`)
2. Getting charger details (`ev_charger(uuid).get()`)
3. Meter data (`get_meter_data()`) — required params called out
4. Available commands (`list_commands()`)
5. Command state (`get_command()`) — includes `extra_fields` reference
6. Executing a command (`execute_command()`)
7. Charging sessions (`list_sessions()`) — show both with and without time filters

**Sync/async tabs**: Required on each method example.

---

## Page: Inverter Presets (`docs/inverter-presets.md`)

**Required sections**:
1. Listing presets (`list_presets()`) — iterate and show fields
2. Reading current values (`get_preset()`) — includes `extra_fields` reference
3. Applying a preset (`apply_preset()`)

**Sync/async tabs**: Required on each method example.

---

## Page: Error Handling (`docs/error-handling.md`)

**Required sections**:
1. Exception hierarchy — visual or table showing base → typed exceptions
2. Per-exception reference:
   - `AuthenticationError` — when raised, what to do
   - `NotFoundError` — when raised, what to do
   - `APIValidationError` — when raised, includes `.args[0]` message
   - `ServerError` — when raised, includes `.status_code`
   - `GivEnergyAPIError` — catch-all base class
3. Complete try/except example covering all cases

---

## Page: Async Usage (`docs/async.md`)

**Required sections**:
1. Pattern explanation — every sync method has an `a`-prefixed async counterpart
2. Single-resource async example (account)
3. Concurrent multi-resource example (using `asyncio.gather`)
4. When to use async vs sync guidance

---

## Page: Advanced Topics (`docs/advanced.md`)

**Required sections**:
1. Pagination — `PaginatedResult`, `meta.last_page`, looping over pages
2. Open-schema responses — `extra_fields` dict, when it appears, how to access
3. Timezone-aware datetimes — full explanation with correct/incorrect examples
4. Using a custom base URL (if applicable)
