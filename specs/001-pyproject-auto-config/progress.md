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

## 2026-08-31T14:35:00Z · Implementer US2 · T014

Did: `ProjectMetadata.from_toml_data` now defaults `version` to `"0.0.0"`, `authors` to
`["Unknown"]` and `description` to `""` when the `[project]` table omits them, using `"field" in
project` presence checks rather than truthiness (see `decisions.md` D16). Nothing raises when all
three are absent.
Verified: `poetry run pytest tests/test_metadata.py::TestDefaults -x -q` — 1 passed. RED observed
first (`KeyError: 'authors'`) before the change.
Next: T015 (warnings), T016 (dynamic-version fallback) — both already covered by this same slice;
writing their tests next to prove it rather than assume it.

## 2026-08-31T14:38:00Z · Implementer US2 · T015

Did: each defaulted field logs one `sphinx.util.logging.getLogger(__name__).warning(...)` call
naming the field, matching the mechanism `extensions/autodoc_models.py` already uses (FR-014).
Verified: `poetry run pytest tests/test_metadata.py::TestDefaults -q` — 2 passed, via `caplog`.
Landed already-green (the T014 slice implemented all three warnings together); probed rather than
assumed — temporarily removed the `authors` warning call and confirmed the test dropped to
`2 == 3` before reverting.

## 2026-08-31T14:41:00Z · Implementer US2 · T016

Did: `ProjectMetadata.resolve_version` returns the `[project]` version if declared, else the
`[tool.poetry]` version when `"version"` is in `[project.dynamic]`, else `None` (which
`from_toml_data` then defaults and warns on).
Verified: `poetry run pytest tests/test_metadata.py::TestDefaults -q` — 3 passed. Also
already-green from the same slice; probed by removing the dynamic-fallback branch and confirming
the test failed (`'0.0.0' == '2.5.0'`) before reverting.

## 2026-08-31T14:44:00Z · Implementer US2 · T017

Did: no separate change — its full scope (defaults, per-field warnings, dynamic-version fallback,
all in `fairdm_docs/metadata.py`) landed in the T014 commit and is proven by the T014-T016 tests
above. Recorded as its own progress entry because the task list names it separately; the code and
test evidence are identical to T014-T016's.

## 2026-08-31T14:47:00Z · Implementer US2 · T018

Did: `tests/test_conf.py::TestRenderedSite` gained a real build from a declaration carrying only
`name`, asserting the build succeeds and that `version`, `authors` and `description` each appear
in the build output (the Sphinx warning stream `built_portal` returns).
Verified: `poetry run pytest tests/test_conf.py::TestRenderedSite -q` — 2 passed. Probed rather
than assumed: with all three warning calls temporarily removed, the same test failed
(`assert 'version' in '...'`) against real Sphinx build output, ruling out a false-positive match
on unrelated output (e.g. "Running Sphinx v8.1.3").

## 2026-08-31T14:50:00Z · Implementer US2 · report

Did: full repo test suite, lint, typecheck, build and conformance via the story's verify command.
Verified: see completion report `report-us2.json`.

## 2026-08-31T15:04:50Z · Implementer US3 · T019-T025

Did: `ProjectMetadata.from_toml_data` now checks for the `[project]` table before reading it,
raising `ConfigError` naming what to add — with a link to the README's migration guide when a
`[tool.poetry]` table is present instead — and raising `ConfigError` naming the `name` field when
`[project]` has no `name`. `ProjectMetadata.from_file` is new: it locates the file with
`fairdm_docs.utils.find_pyproject_toml`, reads it with `tomllib`, converts a missing file or a
`tomllib.TOMLDecodeError` into `ConfigError`, and otherwise delegates to `from_toml_data`. See
`decisions.md` D17 for the `from_file` signature, which departs from the plan's literal snippet.
Verified: `poetry run pytest tests/test_metadata.py::TestFailures -v` — RED first (`KeyError` on
the three `from_toml_data` cases, `AttributeError: no attribute 'from_file'` on the two `from_file`
cases), then 6 passed after the change. Each acceptance criterion probed per `craft-tdd`: T022's
test asserts the parser's own `TOMLDecodeError` text appears verbatim inside the `ConfigError`
message, not just the word "TOML"; T024's test asserts `type(exc_info.value) is ConfigError`
across all five conditions, not just `isinstance`, so a new subclass would fail it.
Next: T026.

## 2026-08-31T15:04:50Z · Implementer US3 · T026

Did: `tests/test_cli.py::TestConfigurationFailures` drives a `[tool.poetry]`-only declaration
through `runner.invoke(app, ["build"])`, with `sphinx.cmd.build.main` patched to call the real
`ProjectMetadata.from_file()` as its side effect (conf.py does not call `from_file` in this story —
D13, D18 — so there is no in-scope production seam to drive this through unmocked). No change to
`cli.py`: FR-015 already holds because `from_file` raises the same `ConfigError` the command's
existing `except ConfigError` block at `cli.py:195` catches and echoes as a message.
Verified: `poetry run pytest tests/test_cli.py::TestConfigurationFailures -v` — passed on first
write, so probed per `craft-tdd` rather than accepted: reverted the `from_file()` call in the
test's side effect and confirmed `result.exit_code != 0` failed (`assert 0 != 0`) before restoring
it, ruling out a vacuous pass. Full `tests/test_cli.py` — 31 passed, no regressions.
Next: story report.

## 2026-08-31T15:04:50Z · Implementer US3 · report

Did: full repo test suite, lint, typecheck and build via the story's verify command.
Verified: see completion report `report-us3.json`.

## 2026-08-31T15:32:46Z · Implementer US4 · T027-T031

Did: `ProjectMetadata` gained `homepage` and `repository` fields, a `resolve_address` static
method for the case-insensitive `[project.urls]` lookup (D6 — narrowed to that one table), and an
`address` property preferring `repository` over `homepage` for contexts that need a single value
(FR-005). `from_toml_data` extracts both from `project.get("urls", {})`; a declaration with no
`[project.urls]` table leaves both empty and raises nothing.
No warning is emitted when an address defaults, unlike version/authors/description: `TestDefaults`
(US2, T015) asserts exactly 3 warnings for a name-only declaration, which has no `[project.urls]`
table either — a 4th or 5th warning would fail a test I may not modify. Recorded as `decisions.md`
D20.
Verified: `poetry run pytest tests/test_metadata.py::TestAddresses -v` — RED first (6 failed,
`AttributeError: 'ProjectMetadata' object has no attribute 'repository'`/`'homepage'`/`'address'`),
then 6 passed after the change. Full `tests/test_metadata.py` — 21 passed, no regressions,
including the T015 warning-count test above. `ruff check` and `mypy` on both changed files clean.
Next: T032, T032a.

## 2026-08-31T15:35:00Z · Implementer US4 · T032

Did: `_apply_theme_config`'s `repository_url = ""` (line 82) and the module-level
`repository_url = ""` above `comments_config` (line 213) — both D14 placeholders — now read
`metadata.address`.
Verified: `poetry run pytest tests/test_conf.py::TestSiteIdentity -v` — RED first
(`assert '' == 'https://github.com/example/sample-portal'`), then 5 passed after the change. Full
`tests/test_conf.py` — 7 passed. `ruff check` and `mypy` on both changed files clean.
Next: T032a.

## 2026-08-31T15:35:44Z · Implementer US4 · T032a

Did: `conf.py`'s project-information block builds `metadata` with
`ProjectMetadata.from_file(...)`, catching `ConfigError` and re-raising `sphinx.errors.ConfigError`
with the same message text so Sphinx's pass-through branch handles it (D19) instead of the generic
branch that embeds a traceback. `pyproject_data` for `_extract_fairdm_config` is fetched with an
explicit `find_pyproject_toml`/`load_pyproject_toml` call, deliberately (D21) rather than reusing
`from_file`'s internal read. The dead `raise ValueError(...)` fallback is gone.
Verified: `tests/test_conf.py::TestConfigurationFailures`, two tests — RED first (both raised
`sphinx.errors.ConfigError` already, since Sphinx's generic branch wraps any exception, but the
message asserted "syntax"/no "Traceback" and failed against the wrapped traceback text), then 2
passed after the change. Full `tests/test_conf.py`, `tests/test_metadata.py` and `tests/test_cli.py`
— 61 passed, no regressions (`tests/test_cli.py::TestConfigurationFailures`, D18's patched-build
test, still passes unmodified). `ruff check` and `mypy` on both changed files clean.
Next: story report.

## 2026-08-31T15:50:00Z · Implementer US4 · T032a fix, found by the §5 full-suite run

Did: the design above first shipped as `ProjectMetadata.from_file(use_env_var=True)` called
unconditionally, with `from_file` given a new `use_env_var` parameter passed straight through to
`find_pyproject_toml`. `./forge verify`'s `poetry:test` step failed — not on the two new tests, on
eight, including `TestSiteIdentity` and `TestRenderedSite` tests unrelated to T032a — because
`find_pyproject_toml(use_env_var=True)` prefers `FAIRDM_DOCS_PROJECT_DIR` over cwd whenever the var
is set, and `cli.py` sets it with a raw `os.environ[...] =` that a `tests/test_cli.py` build test
never unsets, so it leaks into whatever runs after it in the same suite. Every scoped run I'd used
while looping on this task (`tests/test_conf.py` alone, `tests/test_metadata.py` alone) started
with that var unset and never showed it; only the full-suite run did, exactly why §5 mandates it
run before the report rather than being inferred from narrower runs. See D21 for the reproduction
and the full account.
Fixed: reverted `from_file`'s signature. `conf.py` now locates the file itself with the same
two-stage precedence D13's original code used — cwd first, `use_env_var=True` only as a fallback
once cwd search returns `None` — then calls the unmodified `from_file(pyproject_path.parent)`.
`tests/test_conf.py::TestConfigurationFailures::test_missing_pyproject_is_reported_without_a_traceback`
is the one test that genuinely reaches that fallback branch (the "no pyproject.toml" case requires
cwd search to fail), so it is still exposed to the same pre-existing leak on an unlucky suite order;
it now calls `monkeypatch.delenv("FAIRDM_DOCS_PROJECT_DIR", raising=False)` to control for that,
since `tests/test_cli.py` is not mine to change.
Verified: `poetry run pytest tests/test_cli.py tests/test_conf.py -v` — reproduced the 8 failures
against the buggy version, then 40 passed after the fix, in that same cross-file order. Full
`./forge verify` — all steps passed, including `poetry:test` (previously the one that caught this).
`ruff check` and `mypy` clean on the re-touched files.

## 2026-08-31T15:56:00Z · Implementer SHARED · T033

Did: added `tests/test_metadata.py::TestEdgeCases`, eight characterisation tests over the eight
declarations Phase 6 names, touching no production code. An empty `[project]` table fails the same
way as no name. An empty `authors` list is kept as `[]` with no warning (D16: presence, not
truthiness). An author string with no email keeps the string; one that is only an email, and an
author table with an email and no name, both produce `""` as the display name —
`display_name` (metadata.py:42) splits on `"<"` and keeps only what comes before it, so there is
nothing before it to keep either way. A `dynamic = ["version"]` declaration with no
`[tool.poetry]` version falls back to the default and warns, same as no version declared at all.
`Repository` and `repository` both present resolve to whichever is declared first in the table —
`resolve_address` returns on the first case-insensitive match, and TOML preserves declaration
order, so this is about position, not spelling. A name that is not a valid distribution name is
used verbatim; FR-007 does not validate it.
Verified RED first on the two least obvious cases (the empty-authors-no-warning assertion and the
first-wins address, each temporarily flipped to the wrong expected value) — both failed for the
right reason, then restored and green. Full `tests/test_metadata.py` — 29 passed, no regressions.
`ruff check`, `ruff format --check` and `mypy` on the changed file clean.
Next: T034.
