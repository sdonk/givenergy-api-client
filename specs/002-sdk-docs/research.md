# Research: SDK Documentation

## Decision 1: Documentation Tool

**Decision**: MkDocs with Material theme (already specified by user; `mkdocs.yml` exists).

**Rationale**: Material for MkDocs is the de-facto standard for Python library documentation.
It provides first-class support for code tabs, admonitions, search, and dark/light mode
with zero custom CSS.

**Alternatives considered**: Sphinx (heavier, RST-by-default), Docusaurus (Node.js dependency),
plain README (insufficient for multi-section developer docs).

---

## Decision 2: Page Structure

**Decision**: One Markdown file per user story topic, with a dedicated nav entry in `mkdocs.yml`.

```
docs/
├── index.md              # Getting Started (US1)
├── account.md            # Account operations (US2)
├── inverter.md           # Inverter operations (US2)
├── ems.md                # EMS operations (US2)
├── ev-charger.md         # EV Charger operations (US2)
├── inverter-presets.md   # Inverter Presets operations (US2)
├── error-handling.md     # Error Handling (US3)
├── async.md              # Async Usage (US4)
└── advanced.md           # Advanced Topics (US5)
```

**Rationale**: One page per resource type matches the SDK's domain model and allows
developers to bookmark exactly the page they need. Separating error handling and async
into their own pages prevents the getting-started page from becoming overwhelming.

**Alternatives considered**: Single long README (no nav, hard to scan), auto-generated
API reference only (no usage narrative or examples).

---

## Decision 3: Code Snippet Validation (FR-008)

**Decision**: Validate all Python code snippets using `pytest --doctest-glob="docs/*.md"`
with a shared fixture providing a mocked client.

**Rationale**: Running doctests directly against the Markdown files ensures every snippet
in the docs is exercised on every CI run. The mocked client (via `pytest-httpx`) means
no live network calls are needed, keeping validation fast and deterministic.

**Alternatives considered**:
- Manual review only (not automated, violates FR-008)
- `mdformat` + `ruff` only (validates syntax, not runtime correctness)
- Separate example scripts (harder to keep in sync with docs prose)

---

## Decision 4: MkDocs Material Features to Use

**Decision**: Enable the following Material for MkDocs features:

| Feature | Purpose |
|---------|---------|
| `content.code.copy` | Copy button on all code blocks |
| `content.tabs.link` | Sync tab selection across page (sync/async tabs) |
| `navigation.tabs` | Top-level nav tabs |
| `navigation.sections` | Grouped sidebar sections |
| `search.highlight` | Highlight search terms in results |

**Rationale**: Code copy buttons and linked tabs (sync vs async) are the two highest-value
UX improvements for a developer-facing SDK docs site.

---

## Decision 5: Sync / Async Code Presentation

**Decision**: Use Material for MkDocs content tabs (`=== "Sync"` / `=== "Async"`) to
show sync and async variants side-by-side on every resource page. Tab state is linked
so choosing "Async" on one page keeps "Async" selected on navigation.

**Rationale**: Inline tabs keep sync/async examples directly comparable without
duplicating prose. A single dedicated async page (US4) provides the overall pattern
reference; resource pages show the specific call in tab form.

**Alternatives considered**: Separate async section on each page (verbose), async page
only (forces cross-page navigation for every lookup).

---

## Decision 6: mkdocstrings (API reference)

**Decision**: Defer auto-generated API reference (`mkdocstrings`) to a future iteration.
This plan covers narrative + example documentation only (US1–US5).

**Rationale**: `mkdocstrings` requires docstrings on all public methods. The current
codebase has minimal docstrings. Adding both docstrings and narrative docs in one pass
is high risk; the narrative docs deliver most of the user value (SC-001 to SC-004).

---

## Decision 7: Dependencies

New dev dependency: `mkdocs-material>=9.6` (covers MkDocs + theme in one package).
Existing `mkdocs.yml` already declares `theme.name: material`.

No new runtime dependencies required — documentation is a build-time artifact.
