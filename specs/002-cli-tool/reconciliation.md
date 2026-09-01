# Reconciliation — 002

`tasks.md` was written from the specification alone, without reading the code. This file checks
each task against `main` at `26ae898` and the test suite that ships there. Marked done only where
a citation and a passing, unmocked test both exist; the old `tasks.md` and its `T0xx` ids carry no
weight here, including where a current test's own docstring cites one (`tests/test_cli.py:418`
says "T026"; the test proves a different failure than the one T026 in this file describes).

Two probes ran to settle marginal cases rather than guessing from the source: whether a real
build actually succeeds through the command (it does — `research.md` Q1), and whether the
existing check-command tests actually exercise a real link resolution (they do not — every one of
them mocks `sphinx.cmd.build.main` and, where a broken-link message is asserted, hand-writes
`output.txt` rather than letting the builder produce it).

**38 tasks. 4 done. 34 open.**

## Done

| Task | Evidence |
|---|---|
| T011 | `tests/test_cli.py:111-123` — unmocked, asserts the message and exit code for a missing `pyproject.toml`. `config.py:80` is the code path. |
| T013 | `tests/test_cli.py:125-142` — unmocked, asserts the message and exit code for a missing source directory. `config.py:143-144`. |
| T014 | `tests/test_cli.py:336-359` — unmocked, a port outside range fails before Sphinx runs. `config.py:147-149`. |
| T015 | `tests/test_cli.py:361-384` — unmocked, an unrecognised verbosity fails before Sphinx runs. `config.py:151-155`. |

These four are the whole of the configuration-validation surface, and they are the reason A1 found
the configuration half of this package genuinely covered. Nothing else is.

**Correction from the design review (S3R REC-001):** each of these four is written against
"either command", and the evidence above proves only `build`'s side of each — every cited test
calls `runner.invoke(app, ["build"])`, and no test in the suite runs `check` against any of these
four failure conditions. `check()` calls the identical `load_config()` at the top of its own try
block, so this is unlikely to be a live defect, but it is unproven. Rather than reopening these
four, `tasks.md` T017 was reworded to close the `check` half explicitly.

## Open, with what exists and what is missing

**Phase 2 — US1.** Nothing here is done. Every existing build test
(`tests/test_cli.py:26-330`) mocks `sphinx.cmd.build.main` and writes `index.md`, which the
package's registered source suffix cannot even find (R3). `research.md` Q1 proves the command
works end to end against a real `.rst` index; no test in the shipped suite does this. T004
through T010 are all open.

**Phase 3 — US5.** T011, T013, T014, T015 close above. **T012 is open and is a defect, not a gap**
— `research.md` Q2 ran a malformed `pyproject.toml` through `fairdm-docs build` and got a
15-frame traceback, not a message; nothing in the suite exercises this path at all. T016 (the
single failure boundary) is open in the one respect T012 names: `load_pyproject`
(`config.py:67-85`) catches `FileNotFoundError` and not `tomllib.TOMLDecodeError`. T017 is partly
evidenced — `test_build_exits_zero_on_success` and `test_build_failure_returns_nonzero` prove
build's two directions, and `test_check_exits_zero_on_success` / `test_check_exits_one_on_errors`
(`tests/test_cli.py:506-545`) already prove check's exit codes for broken-link outcomes — but
nothing proves check's exit code for a T011-T015-style configuration failure specifically, which
is the narrower gap it stays open for. T018 is open — `grep` for `KeyboardInterrupt` in the test
tree returns nothing. T019 is open.

**Phase 4 — US4.** `tests/test_cli.py:144-330` proves that each of `source_dir`, `build_dir`,
`verbosity` and `django` changes the *arguments* Sphinx is called with, every one of them behind a
mock of `sphinx.cmd.build.main`. That is evidence the settings are read and forwarded — it is not
evidence the build changes, which is what FR-016 through FR-019 require and what the tasks in this
phase ask for. T020 through T027 are open. T025 and T026 (no table at all; one key set, the rest
default) have no test that asserts on the untouched defaults explicitly — several tests happen to
omit the table, which is not the same claim.

**Phase 5 — US2.** `test_build_live_starts_server` (`tests/test_cli.py:580-608`) proves `--live`
launches `sphinx_autobuild` with `--port` and `--open-browser`, which is legitimate evidence under
D10 for the half of FR-008 that is this package's rather than the upstream server's — but it does
not assert `source_dir` or `build_dir` reach the argv, which the same requirement also names, so
T028 stays open rather than closing on partial coverage. T029 is open on a sharper ground: every
port-conflict test mocks `is_port_available` itself (`tests/test_cli.py:635-656`); nothing in the
suite ever binds a real socket and proves the function detects it, which is what `research.md` Q3
ran and confirmed works. The function is correct; it is untested. T030 is open.

**Phase 6 — US3.** Every `check` test mocks `sphinx.cmd.build.main` outright
(`tests/test_cli.py:445-575`); three of them prove the *parsing* of a hand-written `output.txt`
correctly finds a `[broken]` line, names its file and line, and drives the exit code — genuine
unit coverage of the parser, not of the command. None of them run a real `linkcheck`, and none
touch a redirect in any form. `research.md` Q4 is the only place a redirect has been run through
this code, and it found the report is silently dropped rather than shown. T031 through T035 are
all open; T031, T032 and T034 have partial parser-level coverage worth preserving when they are
rewritten, T033 has none.

**Phase 7.** T036, T037 and T038 are open; all three depend on everything above. T038 (S3R
ARCH-001) removes two pieces of dead configuration `decisions.md` D8 commits to and that no
earlier task covered.

## What this changes about the roadmap tag

R1 in `docs/ROADMAP.md` reads `needs verification`. 4 of 38 tasks closing does not clear that —
it is dropped only if this run finishes and the open list above is empty. Recorded here so the
decision is made from this table at S8, not asserted before the work is done.
