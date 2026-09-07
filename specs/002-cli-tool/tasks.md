# Tasks — 002

**Specification**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Written from the specification alone, as though the repository contained no code. Nothing was
carried over from the previous version of this file — the pre-pipeline `tasks.md` and its `T0xx`
ids, some of which are still cited in code comments. A comment citing a task id is not evidence
that the task is done ([decisions.md](decisions.md), D13; [plan.md](plan.md), Notes). Which of
these are already satisfied is settled afterwards, in `reconciliation.md`, against the code and
the test suite together — never against these comments.

`[P]` marks a task that touches a file no other `[P]` task in the same group touches, so it can be
worked in parallel with them.

Article I governs the order: within each story the test tasks come before the implementation task
they cover, and they are expected to fail when written.

## Phase 1 — Shared test infrastructure

- **T001** `tests/conftest.py` — a fixture that writes a temporary portal: a `pyproject.toml`
  declaring `[project]` `name` and `version`, and a `docs/` directory. Callers supply the
  documentation source files and, optionally, the `[tool.fairdm.docs]` table.
- **T002** `tests/conftest.py` — a fixture that invokes `fairdm-docs build` or `fairdm-docs check`
  for real against such a portal, by setting `sys.argv` and calling the command's entry point, and
  returns the exit code together with stdout and stderr. Required by SC-007 and Article IV.
- **T003** [P] `tests/fixtures/` — a documentation source with one root page and nothing else; one
  with a page linking an address that does not resolve; one with a page linking an address served
  by a local test server that responds with a 302 redirect, so the redirect test needs no network
  access; one with its own `docs/conf.py`.

## Phase 2 — US1: a portal's documentation renders from one command (P1)

**Goal**: `fairdm-docs build` with no arguments and no configuration file renders a site.
**Independently testable**: run the command against a project with a documentation source
containing a root page, and read the rendered HTML back off disk.

- **T004** [P] `tests/test_cli.py::TestBuild` — a project with a documentation source containing a
  root page: `fairdm-docs build` exits 0 and rendered HTML naming the page's own content appears
  under the default output directory. (FR-002, SC-001)
- **T005** [P] `tests/test_cli.py::TestBuild` — a documentation source containing its own
  `docs/conf.py`: that file configures the build, and content only that file's configuration would
  produce appears in the rendered output. (FR-003, SC-002)
- **T006** [P] `tests/test_cli.py::TestBuild` — a documentation source containing no `conf.py`: the
  build succeeds using the package's own configuration. (FR-003, SC-002)
- **T007** [P] `tests/test_cli.py::TestBuild` — an output directory whose parent does not exist:
  the directory is created and the build succeeds. (FR-007)
- **T008** [P] `tests/test_cli.py::TestBuild` — the command's own output names the build as started
  and, on success, names where the site was written. (FR-005)
- **T009** [P] `tests/test_cli.py::TestBuild` — a documentation source built with the default
  `verbosity`: the builder's own output reaches the developer unaltered. (FR-006)
- **T010** `fairdm_docs/cli.py` — whatever T004 to T009 find unmet, covering FR-002, FR-003,
  FR-005, FR-006, FR-007. Also asserts, on the real build one of T004/T006 already runs, that the
  invocation directory reaches the configuration as `FAIRDM_DOCS_PROJECT_DIR` — the one mechanism
  FR-004 names that had no task tagging it. (FR-004)

**Checkpoint**: a portal with nothing configured gets a rendered site from one command.

## Phase 3 — US5: every failure arrives as a message a developer can act on (P2)

Ordered before US2 and US3 because both of them depend on configuration being loaded, and a
failure in loading it is where each of their own error paths bottoms out.

**Goal**: every way the command can fail produces one message, never a traceback.
**Independently testable**: produce each failure in turn and assert on the message and the
absence of a traceback.

Each of T011 through T015 is written against "either command", but the reconciliation below found
that the code proves only `build`'s side of each — `check()` calls the identical `load_config()`
at the top of its own try block, so this is unlikely to be a live defect, but it is unproven and
stays unproven until T017 closes it (S3R REC-001).

- **T011** [P] `tests/test_cli.py::TestConfigurationFailures` — no `pyproject.toml` anywhere above
  the working directory: either command stops with a message saying a Python project is required,
  and exits non-zero. (FR-020)
- **T012** [P] `tests/test_cli.py::TestConfigurationFailures` — a `pyproject.toml` that is not
  valid TOML: either command stops with a message naming the file as unreadable, with no traceback
  anywhere in stdout or stderr. (FR-020)
- **T013** [P] `tests/test_cli.py::TestConfigurationFailures` — a configured source directory that
  does not exist: either command stops with a message naming the directory and the setting that
  changes it. (FR-020)
- **T014** [P] `tests/test_cli.py::TestConfigurationFailures` — a configured port outside
  1024–65535: either command stops with a message naming the value and the accepted range.
  (FR-020)
- **T015** [P] `tests/test_cli.py::TestConfigurationFailures` — a configured verbosity that is not
  `full`, `quiet` or `errors-only`: either command stops with a message naming the value and what
  is accepted. (FR-020)
- **T016** `fairdm_docs/config.py` — a single failure boundary covering T011 to T015, so every one
  of these arrives at the same message shape. (FR-020, SC-004)
- **T017** [P] `tests/test_cli.py::TestExitCodes` — every failure in T011 to T015 exits non-zero
  **for both `build` and `check`** — the existing coverage of T011–T015 only invokes `build`, and
  this task is where the `check` half of each is proven, rather than reopening those four; a
  successful build and a successful check each exit 0. (FR-021)
- **T018** [P] `tests/test_cli.py::TestInterrupt` — an interrupt during an ordinary build, during a
  live preview, and during a check each stop the command without a traceback and exit 130.
  (FR-022, SC-005)
- **T019** `fairdm_docs/cli.py` — whatever T017 and T018 find unmet, covering FR-021, FR-022.

**Checkpoint**: no failure this specification names can reach a developer as a stack trace.

## Phase 4 — US4: the command bends to the portal that runs it (P4)

**Goal**: each setting in `[tool.fairdm.docs]` changes the build in the way it names, and every
setting a portal does not name keeps its default.
**Independently testable**: set each setting in turn and assert the build changed accordingly.

- **T020** [P] `tests/test_cli.py::TestSettings` — `source_dir` named in the table is read from
  instead of `docs`. (FR-016, SC-003)
- **T021** [P] `tests/test_cli.py::TestSettings` — `build_dir` named in the table is written to
  instead of `docs/_build/html`. (FR-016, SC-003)
- **T022** [P] `tests/test_cli.py::TestSettings` — `port` named in the table is the port
  `--live` binds, provable by occupying the default and observing the build proceed unobstructed
  when a different port is configured. (FR-016, SC-003)
- **T023** [P] `tests/test_cli.py::TestSettings` — `verbosity` set to `quiet` suppresses
  informational output, and set to `errors-only` suppresses everything but errors, each checked
  against a real build. (FR-016, FR-017, SC-003)
- **T024** [P] `tests/test_cli.py::TestSettings` — `django` set to `true` results in Django being
  set up before the build runs; `false` and absent both leave it untouched. (FR-016, FR-018,
  SC-003)
- **T025** [P] `tests/test_cli.py::TestSettings` — a project with no `[tool.fairdm.docs]` table at
  all builds successfully with every default applied. (FR-015)
- **T026** [P] `tests/test_cli.py::TestSettings` — a table naming one setting leaves every other
  setting at its default. (FR-015, FR-019)
- **T027** `fairdm_docs/config.py` and `fairdm_docs/cli.py` — whatever T020 to T026 find unmet,
  covering FR-015 through FR-019.

**Checkpoint**: every requirement in the settings table has a test that changes real build
behaviour, not just an asserted attribute on a configuration object.

## Phase 5 — US2: writing with a live preview (P2)

**Goal**: `--live` launches a preview server correctly configured, and a taken port stops the
command before one starts.
**Independently testable**: run with the flag and assert the server is launched against the right
arguments; separately, occupy the port and assert nothing starts.

- **T028** [P] `tests/test_cli.py::TestLivePreview` — `fairdm-docs build --live` launches the
  preview server against the configured source directory, output directory and port, and asks it
  to open a browser. This is one of the two places in the suite where asserting on the arguments
  handed to the server is correct rather than a stand-in for a real assertion — the server's own
  rebuild and reload behaviour is out of scope by D10 and is not this task's to prove. (FR-008,
  FR-009)
- **T029** [P] `tests/test_cli.py::TestLivePreview` — a configured port that is already occupied:
  `--live` stops with a message naming the port and the setting that changes it, and no server
  process is started. (FR-010, SC-006 partial)
- **T030** `fairdm_docs/cli.py` — whatever T028 and T029 find unmet, covering FR-008 through
  FR-010.

**Checkpoint**: the live preview launches correctly, and cannot collide silently with something
already listening.

## Phase 6 — US3: broken addresses are found before publication (P3)

**Goal**: `fairdm-docs check` resolves external addresses, reports what does not resolve, reports
a redirect separately, and never fails on a redirect alone.
**Independently testable**: run against a documentation source with one address that does not
resolve and one that redirects, and read the exit code and the report.

- **T031** [P] `tests/test_cli.py::TestCheck` — documentation whose external addresses all resolve:
  `fairdm-docs check` reports success and exits 0. (FR-011, FR-012, SC-006)
- **T032** [P] `tests/test_cli.py::TestCheck` — documentation containing an address that does not
  resolve: the command names that address and the file it appears in, and exits non-zero. (FR-011,
  FR-012, SC-006)
- **T033** [P] `tests/test_cli.py::TestCheck` — documentation containing an address that redirects,
  served by the local test server from T003: the command reports the redirect under its own
  heading, separately from any failures, and exits 0 when nothing else failed. (FR-013, SC-006)
- **T034** [P] `tests/test_cli.py::TestCheck` — any run of the command: its report has been written
  to a file alongside the HTML output, not inside it. (FR-014)
- **T035** `fairdm_docs/cli.py` — whatever T031 to T034 find unmet, covering FR-011, FR-013,
  FR-014.

**Checkpoint**: a maintainer running `check` learns about a redirect instead of losing it, and a
redirect never fails a build on its own.

## Phase 7 — Polish

- **T036** [P] `README.md` and `CHANGELOG.md` — corrected wherever they repeat a claim this
  specification narrowed or struck (internal link validation, check extensibility), and updated
  for the exit-code and settings-table behaviour this run adds tests for. (Article VI)
- **T038** `fairdm_docs/config.py` and `fairdm_docs/cli.py` — the two dead-code removals decisions.md
  D8 commits to and that no earlier task covers (S3R ARCH-001): delete `BuildConfiguration.config_dir`
  and its docstring line, and drop `tests/test_config.py`'s assertion on it; then make `cli.py`'s
  hand-written port-conflict message call `ERROR_MESSAGES["port_conflict"]` instead of duplicating
  it — the two are not identical text today (the hand-written copy uses a single `\n` before
  `[tool.fairdm.docs]` and no trailing newline; `ERROR_MESSAGES["port_conflict"]` uses `\n\n` and a
  trailing `\n`), so this task normalizes the whitespace before wiring the call site, checked
  against `test_build_live_error_when_port_occupied`'s substring assertions.
- **T037** The whole suite, lint, type-check and `deptry`, and coverage against the constitution's
  floors. (Quality bar)

## Dependencies

- Phase 1 blocks everything.
- T010 blocks Phase 3 (a failure boundary is only worth adding once the success path exists to
  compare it against).
- T016 blocks T027 (US4's settings validation extends the one failure boundary US5 builds).
- T019 blocks T030 (the exit-code and interrupt handling US5 establishes is what US2's port-taken
  path exits through).
- T027 blocks T030 (US2 reads the `port` setting US4 wires up).
- Phase 6 has no dependency on Phases 2 through 5 beyond T001–T003; it can be built in parallel
  with any of them once the shared fixtures exist.
- Phase 7 comes last.

Every phase after Phase 1 touches `fairdm_docs/cli.py`, so the stories are built one after
another on the feature branch, each starting once the story before it has landed, never side by
side in separate checkouts.
