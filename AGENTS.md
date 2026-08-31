# AGENTS.md — Agent Configuration for fairdm-docs

<!-- Keep this a thin index. Bloat here means the whole file gets skimmed and ignored, so
     details belong in the files it points to. -->

Sphinx configuration and build tooling for FairDM portals. A portal developer installs it, runs
one command, and gets a documentation site that carries their portal's own metadata and branding
without ever configuring Sphinx. The vocabulary is pinned in `CONTEXT.md`, and the standing
decisions are in `docs/adr/`.

## Stack & commands

- **Stack:** Python 3.12+, Poetry-managed. Sphinx and MyST for rendering, Typer for the
  command-line tool. Django is a peer the portal supplies, never a runtime dependency (ADR 0003).
- **Install:** `poetry install --extras sphinx-book-theme`
- **Test:** `poetry run pytest`
- **Lint:** `poetry run ruff check .`
- **Format:** `poetry run ruff format .`
- **Type-check:** `poetry run mypy`
- **Dependency check:** `poetry run deptry .`
- **Build:** `poetry build`

## Agent skills

### Issue tracker

Issues tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix).
See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — `CONTEXT.md` at root, `docs/adr/` for decisions.
See `docs/agents/domain.md`.

### CI checks

Required status checks the pipeline reads (exact names):

- `call-build / Code Quality`
- `call-build / Security Scan`
- `call-build / Build Package`
- `call-tests / Test Python 3.12, Django 5.2`
- `call-tests / Test Python 3.13, Django 5.2`

CI calls the shared reusable workflows, pinned at `v0.4.0`. One Django version is deliberate:
this package touches Django through a narrow, long-stable surface, so the axis that matters is
Python.

## Development workflow

Feature work follows a spec-driven process: spec → plan → tasks → implement → review → PR, with
`specs/NNN-slug/` directories generated per feature. Project standards and the quality bar live
in `CONSTITUTION.md`.

Two standing cautions specific to this repo:

- **The README describes behaviour the code does not implement.** Where the two disagree, the code
  is the fact. Do not cite the README as evidence that something works.
- **Test coverage is thin where the risk is highest.** The shipped Sphinx configuration and the
  model-documentation extension have no tests at all, and the fixtures under `tests/fixtures/`
  are not referenced by any test.
