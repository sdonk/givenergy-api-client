# Quickstart: SDK Documentation Feature

This guide describes how to build, serve, and validate the SDK documentation locally.

---

## Prerequisites

```bash
uv add --dev mkdocs-material
```

---

## Serve Locally

```bash
uv run mkdocs serve
```

Open `http://127.0.0.1:8000` in your browser. The site hot-reloads on file changes.

---

## Build Static Site

```bash
uv run mkdocs build
```

Output is written to `site/`. The build fails on broken links or missing pages.

---

## Validate Code Snippets

Code snippets embedded in Markdown are validated via pytest's `--doctest-glob` mode.
A shared `conftest.py` provides a mocked `GivenergyAPIClient` so snippets run without
a live API key.

```bash
uv run pytest docs/ --doctest-glob="*.md" -v
```

All snippets MUST pass before a docs PR is merged.

---

## Page Checklist (per page before merge)

- [ ] Intro paragraph present
- [ ] All method examples have sync/async tabs
- [ ] All imports included in every snippet
- [ ] Placeholder values used (`"your-api-key"`, `"CE2345G123"`, etc.)
- [ ] Required admonitions present (see contracts/page-contract.md)
- [ ] `uv run mkdocs build` exits 0
- [ ] `uv run pytest docs/ --doctest-glob="*.md"` exits 0

---

## Adding a New Page

1. Create `docs/<page-name>.md`
2. Add it to the `nav` section in `mkdocs.yml`
3. Write content following the page contract (`specs/002-sdk-docs/contracts/page-contract.md`)
4. Run build and snippet validation before opening a PR
