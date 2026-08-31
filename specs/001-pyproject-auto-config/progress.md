# Progress — 001, US1

## 2026-08-31T12:52:54Z · Implementer US1 · T001, T002

Did: added `tests/conftest.py` with two fixtures — `portal` (writes a temporary portal from a
declaration given as a string or a mapping) and `built_portal` (builds one for real with
`sphinx.application.Sphinx`, returning the rendered HTML and the build output).
Verified: exercised by every test in `tests/test_conf.py` (below); no dedicated test of the
fixtures themselves, per Article X (fixtures are proven by their consumers).
Next: T003 fixtures, then T004-T008 (`ProjectMetadata`).
Watch: `docs/conf.py` does `from fairdm_docs.conf import *`, which reuses a cached module across
tests in the same process rather than re-executing it. `built_portal` pops
`sys.modules["fairdm_docs.conf"]` before each build; found by a genuinely failing assertion
(declared version not reaching the rendered page) rather than by inspection.

## 2026-08-31T12:52:54Z · Implementer US1 · T003

Did: no new file added to `tests/fixtures/`. Every declaration T004-T013 need is either a small,
single-purpose inline mapping/string (T004-T007, T009) or a short inline TOML string reused by
`TestSiteIdentity`/`TestRenderedSite` (T010, T011, T013) — none is complex or reused widely enough
to earn a file, and the prohibition is explicit that the five already there are untouched.
Watch: `reconciliation.md`'s "Settled: T003 replaces them" is superseded by this story's brief,
which requires the five to stay; followed the brief.

## 2026-08-31T12:52:54Z · Implementer US1 · T004, T005, T006, T007, T008

Did: added `fairdm_docs/metadata.py` — `ProjectMetadata` (name, version, description, authors),
`from_toml_data`, `display_name` (staticmethod, both PEP 621 author forms), and a `copyright`
property.
Verified: `poetry run pytest tests/test_metadata.py -v` — 5 passed. RED observed first
(`ModuleNotFoundError`) before the implementation existed.
Next: T009-T012 (`conf.py`).

## 2026-08-31T12:52:54Z · Implementer US1 · T009, T010, T011, T012

Did: `conf.py` now builds `metadata = ProjectMetadata.from_toml_data(pyproject_data)` and assigns
`project`, `version`, `release`, `author`, `copyright` from it verbatim (D7 closed: no
`.replace("-", " ").title()`; D9-noted `author` gap closed: it is now actually set). Removed
`_normalize_key`, `_get_case_insensitive`, `_extract_project_metadata`. Every other `metadata[...]`
/ `authors[...]` reference in the file (`htmlhelp_basename`, the LaTeX/man/Texinfo tuples,
`_apply_theme_config`) switched to attribute access on the same object — a syntax change forced by
the type change, not a behaviour change; see `decisions.md` D13, D14 for the two departures from
the plan's literal snippet this forced.
Verified: `poetry run pytest tests/test_conf.py::TestSiteIdentity -v` — RED first (title mangled,
`author` attribute missing), then 4 passed after the change.
Next: T013.

## 2026-08-31T12:52:54Z · Implementer US1 · T013

Did: `TestRenderedSite` builds a real site from a declaration with name, version, description and
authors, and asserts the name, version and an author's display name all appear in the rendered
HTML.
Verified: `poetry run pytest tests/test_conf.py -v` — RED first
(`sphinx.errors.ExtensionError` / `TypeError: cannot unpack non-iterable NoneType object`, from
`sphinx_book_theme`'s source-button handler on an empty repository URL — reproduced against the
pre-story code too, with the same input; see `decisions.md` D14), then 5 passed after
`built_portal` added `confoverrides` disabling the three button flags for the build.

## 2026-08-31T12:52:54Z · Implementer US1 · report

Did: full repo test suite, lint, typecheck and build.
Verified: `poetry run pytest -q` — 66 passed (56 pre-existing + 10 new). `ruff check`, `mypy`,
`deptry` via `pre-commit run` on every changed file — all passed. Story verify command below.
