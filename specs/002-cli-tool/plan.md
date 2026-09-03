# Implementation Plan — 002

**Specification**: [spec.md](spec.md) · **Research**: [research.md](research.md) ·
**Prior version and what changed**: [decisions.md](decisions.md)

## Summary

`cli.py` and `config.py` already carry most of this specification's behaviour, proven by A1 and
by the probes in `research.md`. What is missing splits into four kinds of work: real end-to-end
tests to replace the argument-inspecting stand-ins, a defect fix so a malformed declaration
reaches the developer as one message instead of a traceback, a rewrite of the linkcheck output
parser so a redirect is reported rather than silently dropped, and small corrections — an
unmatched exit code, a lying docstring, two pieces of dead configuration — that fell out of A1's
per-requirement pass. No new module is needed; this is a specification catching up to code that
was already mostly right, plus three real fixes.

## Technical context

| | |
|---|---|
| Language | Python 3.12+ |
| Primary dependencies | Typer, Sphinx, sphinx-autobuild, tomllib (stdlib) |
| Testing | pytest, pytest-cov |
| Storage | none |
| Target | a developer's machine or CI, invoking an installed console script |
| Performance | not a factor; each command runs once per invocation |
| Constraints | `check()`'s redirect handling has to be proven against a real Sphinx `linkcheck` run — the failure in Q4 of `research.md` was invisible to a test that mocks the builder |

## Constitution check

| Article | How this plan meets it |
|---|---|
| I — Test-First | Every task below writes its test before its fix, where a fix exists; the reporting tasks are pure test tasks against existing correct behaviour. |
| II — Simplicity | No new module, no new class. The one structural change — splitting the linkcheck parser into three classifications instead of one broken-or-not list — is the minimum the requirement needs. |
| III — Anti-Abstraction | FR-020's plugin surface is struck (D4); nothing here builds toward a second validator that has not been asked for. |
| IV — Integration-First | Every acceptance scenario in US1 through US3 is proven by running the real command against a real project, per `research.md` Q1 and Q4. The one exception is US2's rebuild/reload behaviour, scoped out in D10. |
| VI — Documentation | The `check` command's docstring currently claims internal-link validation it does not perform (A1); corrected in the same change that narrows FR-011. README's CLI section is checked against the rewritten requirements and updated wherever it repeats the old claim. |
| VII — Dependency discipline | Nothing added. |
| X — Test structure | `fairdm_docs/cli.py` → `tests/test_cli.py` (existing); `fairdm_docs/config.py` → `tests/test_config.py` (existing). Real-build tests join the existing modules rather than starting new ones — Article X asks for one module per source module, not one per test *kind*. |
| XI — Cohesion | `cli.py`'s two commands are Typer callbacks, the article's named exception. No change to that shape. |
| XIII — Zero configuration is the measured path | US1's P1 acceptance scenario — build with no arguments, no configuration file — is the first real-build test written. |
| XIV — Backward compatibility | FR-022's exit-code unification (130 in every mode, D6) changes live behaviour: today a live-mode interrupt exits 0. Below 1.0.0 this is advisory; recorded in CHANGELOG as a fix, not silently. |
| XVI — Never assume a production environment | Every test here runs against a temporary project on disk; nothing reaches a running portal. |

## Project structure

```
fairdm_docs/
├── cli.py       CHANGED — malformed-TOML handling, linkcheck parser, exit-code
│                unification, dead port_conflict duplication removed, docstring fix
├── config.py    CHANGED — config_dir field removed
└── utils.py     unchanged

tests/
├── conftest.py       CHANGED — a fixture that runs a real build and returns the result
├── test_cli.py       CHANGED — real-build tests added alongside the existing mocked ones;
│                     existing mocked tests kept where they test argv construction itself
└── fixtures/         extended with a redirecting-link and a broken-link fixture
```

## The design

### Malformed declaration → `ConfigError` (D7, FR-020)

`load_pyproject` (`config.py:67-85`) currently catches only `FileNotFoundError` around
`load_pyproject_toml`. It gains a second `except tomllib.TOMLDecodeError`, raising `ConfigError`
with a message naming the file and pointing at the syntax problem `tomllib` reported — the same
shape `ERROR_MESSAGES["no_pyproject"]` already uses. `metadata.py:149` in the 001 work is the
precedent for the message shape.

### Linkcheck output classification (D3, D5, FR-011, FR-013, FR-014)

The parsing loop at `cli.py:262-296` is rewritten from one pass that appends to a single
`broken_links` list into a pass that classifies each line as `broken`, `redirected`, or neither,
using the markers `research.md` Q4 confirmed against a real build: `": [broken]"` and
`": [redirected with "` (not `": [redirected]"`, which never matches). Redirected lines are
reported under their own heading and excluded from the exit-code decision; broken lines behave as
they do today. The report — both classifications — is written to a file alongside the HTML output
(`build_dir.parent / "check-report.txt"`, mirroring where `linkcheck_dir` already sits), meeting
FR-014.

The docstring at `cli.py:205-211` currently reads "Broken internal and external links
(linkcheck)". It is corrected to say what `linkcheck` actually resolves: external addresses.

### Exit code unification (D6, FR-022)

`cli.py:147-149`'s live-mode `KeyboardInterrupt` handler currently calls `typer.Exit(code=0)`. It
changes to `typer.Exit(code=130)`, matching the other two handlers already in the file.

### Dead configuration removed (D8, T038)

`BuildConfiguration.config_dir` (`config.py:39`) is deleted along with its docstring line and the
assertion on it at `tests/test_config.py:38`; nothing else reads the field. `ERROR_MESSAGES
["port_conflict"]` (`config.py:58-63`) is called from `cli.py:99-105` instead of duplicated by
hand — the two are not identical text today (the hand-written copy uses a single `\n` before
`[tool.fairdm.docs]` and no trailing newline; the template uses `\n\n` and a trailing `\n`), so the
whitespace is normalized as part of wiring the call site, checked against
`test_build_live_error_when_port_occupied`'s substring assertions, and the hand-written copy is
deleted once that holds.

### Real end-to-end tests (Q1)

One fixture in `conftest.py`, following 001's precedent: writes a temporary project from a
declaration and a documentation source, and returns the path. A second fixture builds it for real
through `fairdm_docs.cli.main()` with `sys.argv` set, returning the exit code and the output
directory. US1's three acceptance scenarios, US4's four, and US5's five are proven against this
fixture rather than against a mocked `sphinx.cmd.build.main`.

The existing mocked tests that assert on the argv Sphinx is handed are kept — they are the right
tool for proving *which* arguments reach the builder (verbosity flags, `-c` pointing at the right
config directory), which a real build cannot isolate as cleanly. What changes is that a real build
now also exists to prove the build *works*, closing the gap A1 found.

## Complexity tracking

Nothing added. The linkcheck parser goes from one list to three named outcomes — broken,
redirected, ignored — which is the minimum shape FR-011 and FR-013 both need to exist at once; a
single list cannot report a redirect and also decide the exit code independently of it.

**What is deliberately not done.** FR-020's validator extensibility is struck outright (D4), not
built and left unused — Article III's present-use test fails it entirely, since nothing in this
run needs a second validator. Rebuild latency, browser opening and reload behaviour are not
tested (D10); they are `sphinx-autobuild`'s contract, not this package's.

## Notes carried into the tasks

- The old task list for this specification (`tasks.md`, task ids `T0xx`) is not evidence and no
  line of it is carried over — several of its ids are cited in code comments (`cli.py:97`,
  `cli.py:286`) but a comment citing a task id is not a test, and A1 found no test behind the
  comments at those two lines specifically.
- `tests/fixtures/` already holds documentation-source fixtures from 001; the redirect and
  broken-link fixtures this plan adds join that directory.
- Q4's redirect probe hit a live URL (`httpbin.org`). The test suite cannot depend on network
  access or on that service staying up; the task list uses a local HTTP server serving a 302, so
  the redirect test is hermetic.
