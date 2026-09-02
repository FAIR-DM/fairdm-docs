# Progress — 002

## 2026-09-01T10:07:00Z · Spec gate

Sam delegated the run in full: "I don't want to be involved. Please answer the questions yourself
and preform the full spec audit yourself. See you at the merge gate." Every adjudication normally
raised at grilling and at the Spec gate is self-resolved and recorded in `decisions.md`; the gate
is closed as delegated rather than waited on. `feature-state.json` records `gates.spec` with the
delegation timestamp and the self-resolved list.

## 2026-09-01T10:20:00Z · Setup

Epic #15 and five story sub-issues (#16-#20) filed per `kit/checklists/issue-contract.md`;
`forge check-issue-titles` green. Draft PR #21 opened against `main`, `Closes` block seeded for
all six issues. Branch `002-cli-tool` pushed as the bot (push actor confirmed).

## 2026-09-01T11:19:05Z · Plan

`plan.md`, `research.md` written. Four probes ran against real, temporary projects rather than
being inferred from the source: a real build through `fairdm-docs build` (succeeds, closing
whether US1 can be tested end to end); a malformed `pyproject.toml` through the same command
(confirms the ADR 0008 defect — a 15-frame traceback, not a message); a real socket held on the
default port with `--live` (confirms the port-conflict path already works); and a real redirect
through `fairdm-docs check` (corrects an A1 finding — the code does not fail on a redirect, by
accident, and drops the redirect from the report entirely rather than showing it).

`tasks.md` written from `spec.md` alone, without reading the code, per the audit's standing rule.
`reconciliation.md` then checked all 37 tasks against `main` at `26ae898`: 4 done
(`T011`, `T013`, `T014`, `T015` — the configuration-validation surface, all with unmocked tests),
33 open. Every build and check test in the current suite mocks `sphinx.cmd.build.main`; none
proves a real build or a real link resolution.

Plan notification (veto window, not a gate) folded into this entry per the delegation — no
separate wait.

## 2026-09-01T12:42:00Z · S3R design review

One reviewer, four lenses (spec-compliance, security, architecture, reconciliation), dispatched
via `sessions_spawn` on the Sonnet tier. All three craft skills loaded with receipts. Verdict
**approve, risk low** — 3 findings, all medium or low, none verified critical or high, so nothing
forced a re-plan. All 4 tasks reconciliation.md marked done were independently re-verified by the
reviewer rather than trusted.

Findings applied directly, no re-review round per protocol:
- **REC-001** (medium) — T011/T013/T014/T015's evidence proves `build` only, though their text
  reads "either command". `reconciliation.md` corrected; `tasks.md` T017 reworded to close the
  `check` half rather than reopening the four.
- **ARCH-001** (medium) — `decisions.md` D8's dead-code removal had no task, and `plan.md`
  wrongly assumed the two port-conflict message templates are already identical text. Added T038;
  corrected the premise in `plan.md`.
- **SPEC-001** (low) — FR-004 had no task tag. Folded into T010's real-build assertion.

Three wording-drift notes corrected (a citation off by one line, an FR mistag on T031/T032, an
overstated exit-code claim in `reconciliation.md`'s T017 discussion).

Findings file: `design-review-findings.json`.

Next: S4 implementation starting from US0 (shared test infrastructure).

## 2026-09-01T14:50:06+02:00 · Implementer US0 · T001–T003, T036, T038

Did: built the shared test infrastructure Phase 1 blocks on, plus the two Phase 7 tasks scoped to
this story. `documented_portal` (T001) writes a portal from a declared name/version and a
docs-callback. `run_fairdm_docs` (T002) invokes `fairdm_docs.cli.main()` for real — sets argv,
catches `SystemExit`, captures stdout/stderr — with no mocking of `sphinx.cmd.build.main`. T003
added four documentation-source fixtures (`single_page`, `broken_link`, `redirected_link`,
`with_own_conf`) and a stdlib `http.server`-based `redirect_server` fixture; see decisions.md D14
for why the redirect source carries a placeholder rather than a live address. T038 deleted
`BuildConfiguration.config_dir` (and its `tests/test_config.py:38` assertion) and wired `cli.py`'s
port-conflict message to `ERROR_MESSAGES["port_conflict"]`. T036 corrected the `check` command's
internal-link claim and the CHANGELOG's matching "internal and external" claim per D3, and added
an Exit Codes section to the README per FR-021/FR-022 — with the live-server gap called out rather
than papered over (D14).

Verified: `poetry run pytest` 105 passed (was 96 at baseline; +9 in `tests/test_conftest.py`).
`poetry run ruff check .` clean on every touched file at each commit.

Next: full verify (T037) before the completion report.

Watch: the worktree's venv did not have the `sphinx-book-theme` extra installed at session start
(`poetry install --extras sphinx-book-theme` fixed it) — the baseline suite was red for that
reason before any code was touched, not because of an existing defect.

## 2026-09-01T16:43:09+02:00 · Implementer US1 · T004–T010

Did: added `TestBuild` alongside the existing `TestBuildCommand` in `tests/test_cli.py` (T004-T009),
one commit per task, each a real `fairdm-docs build` via `run_fairdm_docs` against `single_page` or
`with_own_conf` — no mocking of `sphinx.cmd.build.main`. T004 reads rendered HTML for the page's
own content; T005/T006 assert on markers each conf.py alone produces (`with-own-conf`'s hardcoded
`project`, and `sphinx-book-theme.css` for the package's own theme); T007 proves the build
directory's missing parent gets created; T008 asserts the command's own started/destination
messages, distinguished from Sphinx's own similarly-worded output; T009 proves full verbosity
doesn't suppress Sphinx's own "build succeeded" text. T010 added the FR-004 assertion S3R
SPEC-001 folded in here (`FAIRDM_DOCS_PROJECT_DIR` equals the portal's own directory) — no
`fairdm_docs/cli.py` change was needed for any of T004-T010; every acceptance criterion was
already met by the existing implementation.

Every one of the seven new tests was mutation-probed per `craft-tdd`'s pre-report checklist:
edited the mechanism each test claims to cover, watched the test fail for the right reason, then
reverted. T007's probe found `cli.py`'s own `build_dir.parent.mkdir(...)` call is redundant —
Sphinx's own `ensuredir(outdir)` already creates the whole path — logged in `decisions.md` rather
than removed, since a simplification is outside this story's task list. T008's first draft
(`"docs/_build/html" in stdout`) turned out to pass even with the command's own destination
message replaced, because Sphinx prints an unrelated line containing the same substring; tightened
to the command's own `"Output: docs/_build/html"` and re-probed.

Verified: `poetry run pytest tests/test_cli.py::TestBuild -q` 7 passed at each commit.
`poetry run pytest -q` 112 passed (was 105 at baseline; +7 in `tests/test_cli.py`). `poetry run
ruff check .` clean.

Next: S4 gate — Forge re-verifies and reports.

## 2026-09-01T20:04:17+02:00 · Implementer US5 · T012, T016–T019

Did: `load_pyproject` (`config.py`) gained a second `except tomllib.TOMLDecodeError`, raising
`ConfigError` with the file path and the parser's own message (T012) — the ADR 0008 defect
`research.md` Q2 traced, previously a 15-frame traceback. T016 verified the five configuration
failures (no pyproject, missing source dir, bad port, bad verbosity, malformed TOML) already
share that one boundary. T017 added six tests proving `check` exits non-zero for the same five
failures `build`'s tests already covered, and zero on success — closing S3R REC-001's build-only
gap. T018/T019: `cli.py`'s live-preview interrupt handler exited 0; now exits 130, matching
`build` and `check` (D6).

Verified: `poetry run pytest -q` green at each commit. Full verify caught one ruff-format-only
diff (a single `raise` line rewrapped) — committed separately, then green.

Watch: this story's own report omitted `decisions.md`/`progress.md` entries; this entry and the
ledger update were written by Forge from the diff and the completion report rather than by the
Implementer. Nothing in the diff itself was affected.

Next: US4 (the settings table).

## 2026-09-01T20:52:44+02:00 · Implementer US4 · T020–T027

Did: added `TestSettings` to `tests/test_cli.py`, one real, end-to-end test per setting
(`source_dir`, `build_dir`, `port`, `verbosity` × 2, `django` × 2, no-table defaults, partial
override) — nine tests total (T020-T026), all via `run_fairdm_docs` against real portals, none
against a stand-in for Sphinx. T022 occupies the real default port 5000 with a bound socket and
configures a free port, going beyond the existing argv-mocked
`test_build_live_uses_custom_port_from_config`. T023 distinguishes `quiet` from `errors-only` by a
real Sphinx warning (a toctree entry pointing at a nonexisting document) appearing on stderr for
`quiet` and being suppressed for `errors-only`. T024 spies on the real `django.setup` (wrapped, so
it still runs) to prove `django = true` actually invokes it, and that `django = false` never does
— a portal-local minimal settings module was needed because the package's own fallback
`config.settings` doesn't exist in this repo.

T027: no `fairdm_docs/config.py` or `fairdm_docs/cli.py` change was needed. Every one of the seven
mechanisms (T020-T026) already worked; each new test was mutation-probed per `craft-tdd`'s
pre-report checklist (broke the corresponding merge branch or verbosity/Django mechanism in
`config.py`/`cli.py`/`conf.py`, watched the test fail for the right reason, reverted) before being
accepted as a real assertion.

Verified: `poetry run pytest -q tests/test_cli.py::TestSettings` 9 passed at each commit. `poetry
run ruff format --check .` initially flagged one line in the new tests (T020's first commit);
reformatted and committed separately. `poetry run pytest -q` 131 passed (was 122 at baseline; +9
in `tests/test_cli.py`). `poetry run ruff check .`, `poetry run ruff format --check .`, `poetry
run mypy`, and `poetry run deptry .` all clean.

Next: US2 (live preview) per `tasks.md` Phase 5, or convergence if this was the last open story.

## 2026-09-02T09:24:34+02:00 · Implementer US2 · T028–T030

Did: added `TestLivePreview` to `tests/test_cli.py`, closing the two gaps `reconciliation.md`
flagged in `TestLiveServerCommand`. T028 configures non-default `source_dir`, `build_dir` and
`port` together and asserts all four (plus `--open-browser`) reach `subprocess.run`'s argv — the
existing `test_build_live_starts_server` only checked port and `--open-browser`. T029 binds a real
socket on the configured port before invoking `--live`, exercising `is_port_available`'s actual
`socket.bind()` detection rather than a mock of its return value, and asserts `subprocess.run` is
never called.

T030: no `fairdm_docs/cli.py` change was needed. Both mechanisms already worked — `cli.py:121-122`
already places `str(config.source_dir)` and `str(config.build_dir)` in the live-server argv, and
`is_port_available` (`cli.py:26-41`) already does a real `socket.bind()` check, not a stand-in.
Per `craft-tdd`'s pre-report checklist, each new test was mutation-probed before being accepted:
T028 was run against a `cli.py` with the `source_dir`/`build_dir` argv lines removed (failed on
the right assertion), T029 was run against `is_port_available` hard-coded to `return True` (failed
on `exit_code == 1`) — both reverted to the unmodified baseline (`diff` confirmed byte-identical)
before committing. See `decisions.md` for the mini-ADR.

Verified: `poetry run pytest -q tests/test_cli.py::TestLivePreview` 2 passed at each commit.
`poetry run pytest -q` 133 passed (was 131 at baseline; +2 in `tests/test_cli.py`). `poetry run
ruff check .`, `poetry run ruff format --check .`, `poetry run mypy`, and `poetry run deptry .` all
clean.

Next: US3 (`check` / broken addresses) per `tasks.md` Phase 6, or convergence if this was the last
open story.
