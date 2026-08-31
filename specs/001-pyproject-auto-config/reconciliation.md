# Reconciliation — 001

[tasks.md](tasks.md) was written from [spec.md](spec.md) as though the repository were empty, and
committed before this file was started, so that what follows could not have been shaped by what the
code happens to do. This file walks that list against the code and the test suite together.

**The threshold.** A task counts as already satisfied only where the code does it *and* a test
proves it. A citation with no test leaves the task open, and the remaining work on that task is the
test. This is the constitution's own position: Article IV records that the gaps between this
package's README and its behaviour survived a passing suite.

**Measured, 2026-08-31, on `d7acc35`:** 56 tests pass. `fairdm_docs/conf.py` is 137 statements at
**0% coverage**. No test in the suite imports it. Every requirement in this specification is
implemented in that module.

## The split

| | Tasks |
|---|---|
| Total | 35 |
| Satisfied — code and a test | **0** |
| Open | **35** |

Of the 35 open:

| Reason | Count | Tasks |
|---|---|---|
| Never built | 14 | T001, T002, T003, T008, T012, T013, T018, T022, T025, T026, T031, T033, T034, T035 |
| Built, no test proves it | 12 | T004, T005, T006, T007, T010, T014, T016, T027, T028, T029, T030, T032 |
| Built differently, and the audit ruled against the code | 9 | T009, T011, T015, T017, T019, T020, T021, T023, T024 |

A zero in the satisfied column is not a claim that nothing works. Most of this specification is
implemented and, from the evidence of a real build, much of it behaves correctly. It is a statement
about what is *proven*, and on a module with no tests at all the answer is nothing.

## Built, but nothing proves it

Each of these is implemented and looks right on inspection. The work remaining is the test.

| Task | Code | Requirement |
|---|---|---|
| T004 | `fairdm_docs/conf.py:71` | Name, version and description read from `[project]` |
| T005 | `fairdm_docs/conf.py:149` | Author strings, with and without an email |
| T006 | `fairdm_docs/conf.py:146` | Author tables |
| T007 | `fairdm_docs/conf.py:328` | Copyright from the year and the display names |
| T010 | `fairdm_docs/conf.py:325` | Version and release |
| T014 | `fairdm_docs/conf.py:105` | Defaults for absent optional fields |
| T016 | `fairdm_docs/conf.py:108` | Dynamic version falling back to `[tool.poetry]` |
| T027 | `fairdm_docs/conf.py:159` | Addresses read from `[project.urls]` |
| T028 | `fairdm_docs/conf.py:52` | Case-insensitive lookup of address keys |
| T029 | `fairdm_docs/conf.py:224` | Repository preferred over homepage |
| T030 | `fairdm_docs/conf.py:159` | No `[project.urls]` table leaves both empty |
| T032 | `fairdm_docs/conf.py:243` | Addresses reach the theme configuration |

## Built differently, and the audit ruled against the code

| Task | Code | What it does instead |
|---|---|---|
| T009 | `fairdm_docs/conf.py:324` | Titlecases the declared name. `GHFDB` renders as `Ghfdb`, confirmed against a real build (research, Q3). D7. |
| T011 | `fairdm_docs/conf.py:327` | See below — the site's author is never set. |
| T015 | `fairdm_docs/conf.py:122` | Warns for a defaulted version, description and authors. A defaulted address produces no warning, so FR-013's one-per-field does not hold. |
| T017 | `fairdm_docs/conf.py:122` | Uses `warnings.warn`, which does not reach the build output. D4, and settled empirically in research Q1. |
| T019 | `fairdm_docs/conf.py:85` | Right message, wrong type: `ValueError`. D3. |
| T020 | `fairdm_docs/conf.py:92` | Right message, wrong type. D3. |
| T021 | `fairdm_docs/conf.py:100` | Wrong type, and the message carries a literal backslash-n rather than a line break. D3, D8. |
| T023 | `fairdm_docs/conf.py:317` | Wrong type. D3. |
| T024 | — | Follows from the four above: no failure in this specification raises the type `cli.py` catches. |

## Two things this pass found that the rewrite had not

### The site's author is never set

`conf.py:327` assigns `authors`. Sphinx's configuration value is `author`, singular
(`sphinx/config.py:206`, default `'Author name not set'`). `authors` is not a configuration value
and Sphinx does not read it. The list is used one line later to build the copyright, which is why
the copyright is right, and that is what made this survive: the value that is visible on the front
page is correct and the value that is not is wrong.

Where it shows: the EPUB and LaTeX builds, and any theme or extension that reads `author`.

FR-010 therefore has no implementation, rather than a drifted one. T011 is open on that ground.

This was not visible from reading the code and it is not in [decisions.md](decisions.md), because
finding it needed the requirement to be written out on its own first and then looked for. That is
the argument for writing the task list before reading the implementation rather than after.

### Every fixture file in the suite is dead

`tests/fixtures/` holds five declarations. No test in the repository loads any of them; the
configuration and command tests write their TOML inline. Article X: *"A fixture file no test loads
is not test data, it is dead weight that reads as coverage."*

They are also all about the settings table rather than the metadata, so none of them is a
declaration this specification's tests need.

**Settled:** T003 replaces them. The declarations this specification reads go in, and the five that
nothing loads come out. R10 will write its own when it has tests to load them.

## What this run therefore does

The specification is largely implemented and almost entirely unproven. The work is:

1. Make it testable — the extraction moves to its own module, per [plan.md](plan.md).
2. Test all of it, including a build of a real site, per SC-006.
3. Fix the nine the audit ruled against, of which two are user-visible: the mangled title and the
   unset author.
4. Build the three that were never built at all: the TOML syntax failure, the command reporting
   these as messages, and the documentation of the title change.
