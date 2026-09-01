# Decisions — 002

This specification was written on 2026-02-10, from a one-paragraph description and five
clarifying questions. It predates the project's goals, its roadmap and every architecture
decision record it now has to agree with. It was re-examined on 2026-09-01 against
[GOALS.md](../../GOALS.md), [docs/ROADMAP.md](../../docs/ROADMAP.md), the accepted decision
records under [docs/adr/](../../docs/adr/), and the code on `main` at `26ae898`.

This file records what the original said, what the code does, and which way each disagreement
was settled. It exists so a later reader can tell a deliberate change from an accident.

## D1 — This specification is the command surface, and nothing beneath it

The original spec was written when the package had one feature, so it claimed the whole of the
build: the configuration Sphinx runs, where inputs are found, what the rendered site looks like.
Six roadmap items have since taken parts of that.

| Live problem in the command's path | Owned by |
|---|---|
| A build with no configuration fails: the theme is an optional extra, `.md` is not a registered suffix, and one exclusion rule is a regular expression where the builder wants a glob | R3 |
| Documentation inputs resolve against the installed package rather than the portal | R4 |
| The Django settings module a build reads is assumed rather than nominated | R6 |
| The settings table is read by two modules with disjoint vocabularies, and an unrecognised key is silently ignored | R10 |
| Real end-to-end tests, coverage of the configuration module, version bounds on extension dependencies | R11 |
| The project-directory variable leaks between tests | issue #14 |

**Settled:** this specification covers the two commands, the `--live` flag, the settings the
commands themselves read, the messages they print, and the codes they exit with. It stops at the
point the builder is invoked. Nothing above is lost; each item owns its problem better than this
specification would, because each was written with the whole package in view.

One consequence worth stating plainly: this specification can be satisfied in full while a
zero-configuration Markdown build still fails, because that failure is R3's. What can be proven
here is the `.rst` path, which the package's own fixtures already build successfully.

**ADR:** none. A scope boundary between this specification and roadmap items. It records where
work went and constrains nothing after this run.

## D2 — The package's configuration is a default, not a mandate

The original **FR-004** required the CLI to use the package's `fairdm_docs.conf` as the base
configuration for every build. The code prefers the portal's own `docs/conf.py` when one exists
and falls back to the package's when it does not (`cli.py:82-88`, repeated at `cli.py:217-223`).

[ADR 0002](../../docs/adr/0002-configuration-is-layered-with-a-python-escape-hatch.md), accepted
2026-08-31, makes the portal's `docs/conf.py` the third layer of the configuration model and an
intentional escape hatch, deliberately all-or-nothing at file level. The decision record postdates
this specification by six months and is the standing decision.

**Settled:** the specification is stale and the code is right. The requirement is rewritten to
describe the layered model. Only the fallback branch currently has a test
(`tests/test_cli.py:263`); the branch that prefers the portal's own file has none, so proving it
is open work.

**ADR:** none. ADR 0002 already covers it; this only stops the specification contradicting it.

## D3 — Checking resolves external addresses, and says so

The original **FR-017** required link validation to detect "broken internal and external links".
The command runs Sphinx's `linkcheck` builder and nothing else (`cli.py:249-257`). That builder
resolves hyperlinks. Nothing validates internal cross-references, and nothing in the package ever
did.

The command's own help text repeats the specification's claim (`cli.py:209`), so the code
currently advertises a capability it does not have. That is worse than the gap itself.

**Settled:** the specification is narrowed to external addresses, which is what the command does
and what its name should promise. Correcting the help text is a task in this run. Internal
cross-reference validation is not scheduled anywhere and is not added here — the builder already
reports an unresolvable cross-reference as a warning during the build, and turning warnings into
failures is R7's, where it belongs with publication.

**ADR:** yes — what `check` promises constrains every validator added later. Drafted at
convergence.

## D4 — The extensibility requirement is struck

The original **FR-020** required the check command to be "extensible to support additional
validators in the future beyond link checking". There is no validator abstraction, registry, base
class or hook point in the package; `check()` is one function (`cli.py:203-296`).

The same specification's own *Out of Scope* section reads "Custom validation rules or plugins —
initial version provides built-in checks only". The requirement contradicts the document that
carries it.

**Settled:** struck. A plugin surface built for one validator is structure invented against a
need nobody has stated, and it would have to be designed again the first time a second validator
turned out not to fit. When a second validator is scheduled, the shape both need will be visible.

**ADR:** none. Declining to build something is not a decision that constrains later work; the
roadmap item that adds a second validator is free to introduce whatever it needs.

## D5 — A redirect is reported, and does not fail the check

The parsing at `cli.py:271-274` was written to catch a redirect and count it as broken, matching
on the substring `": [redirected]"`. Run against a real redirect, the builder's actual line reads
`[redirected with Found]` — the word "with" sits where the closing bracket was expected, so the
substring never matches. The probe in [research.md](research.md) confirms it: a page holding one
redirecting address exits 0 and prints "All links are valid!". The redirect is written to
`output.txt` and never reaches the developer.

So the outcome the original specification's silence on this point would have produced — a check
that fails a build because a site it links to moved — is not what the code does today, by
accident rather than intent. What is missing is the other half: nothing tells the developer a
redirect happened at all.

A redirect means the address resolved, and failing a check over another site's housekeeping would
make the check cry wolf until it gets ignored. It is still worth surfacing, because a redirect
today is sometimes a dead link next year.

**Settled:** the specification states the behaviour the code already has by chance — a redirect
does not fail the check — and adds what it lacks: the redirect is reported to the developer,
under its own heading, separate from failures.

**ADR:** yes — folded into the D3 record, since both settle what `check` treats as a failure.

## D6 — Interrupting the command exits 130, in every mode

There are three interrupt handlers. Live preview exits 0 (`cli.py:147-149`); the ordinary build
and the check command exit 130 (`cli.py:198-200`, `cli.py:301-303`).

Exit 130 is the shell convention for termination by `SIGINT` and is what a calling script tests
for. A live preview that reports success when the developer killed it is telling its caller
something untrue, and the only reason it does is that a live server has no natural completion.

**Settled:** 130 everywhere.

**ADR:** yes — an exit-code convention constrains every command added later. Drafted at
convergence.

## D7 — A malformed declaration is a configuration failure, not a traceback

A syntactically invalid `pyproject.toml` raises `tomllib.TOMLDecodeError` out of `utils.py:97`.
`load_pyproject` catches only `FileNotFoundError` (`config.py:82-85`), and both commands catch
only `ConfigError` (`cli.py:195`, `cli.py:298`), so `fairdm-docs build` prints a traceback at a
developer who mistyped a bracket.

[ADR 0008](../../docs/adr/0008-configuration-failures-are-one-error-type.md), accepted
2026-08-31, requires every way a declaration can fail to be read to arrive at the same boundary as
`ConfigError`, and names a file that is not valid TOML explicitly. `metadata.py:149` already does
this correctly on the other path.

**Settled:** a defect against a standing decision. Fixed in this run.

**ADR:** none. ADR 0008 already decided it; this is compliance.

## D8 — Two pieces of dead configuration are removed

`BuildConfiguration.config_dir` (`config.py:39`) is never read anywhere. Its docstring says it
defaults to the package location, which is a description of behaviour implemented elsewhere by
different means.

`ERROR_MESSAGES["port_conflict"]` (`config.py:58-63`) is never called; the same message is
written out by hand at `cli.py:99-105`. Two copies of one message drift, and the copy that is
never executed drifts silently.

**Settled:** the unused field is removed and the port-conflict message is used from the one place
it is defined.

**ADR:** none.

## D9 — The settings nobody wrote down are written down

Three mechanisms are load-bearing for this feature and absent from its specification.

- The **`django` setting** (`config.py:40`) becomes an environment variable (`cli.py:91`,
  `cli.py:226`) that tells the package's configuration to set Django up before the build. This
  specification records that the setting exists and what it switches on. *Which* settings module
  gets loaded is assumed today and is R6's to fix, under ADR 0003.
- The **project directory variable** (`cli.py:94`, `cli.py:229` → `utils.py:43-46`) is how the
  package's configuration finds the portal after the builder changes directory into the package.
  Without it the layered configuration model cannot work at all. It is specified here as a
  behaviour of the command, not as a variable name a developer sets.
- The **`theme` setting** is read by the package's configuration (`conf.py:141`) and is unknown to
  the module that loads the settings table. That split is exactly R10's subject and is left there.

**Settled:** the first two become requirements. The third is named as belonging elsewhere.

**ADR:** none.

## D10 — The live server's own behaviour is not re-tested here

The original specification promised that files are detected and rebuilt within two seconds, that
the browser refreshes, and that the server starts within five. Those are `sphinx-autobuild`'s
behaviours. This package contributes the command line handed to it (`cli.py:114-126`) and the
port check before it.

Re-proving another project's server loop means launching a subprocess, polling a port and
racing a file watcher, in a suite that has to stay fast enough to run on every change.

**Settled:** what this feature owns and proves is that the live server is launched against the
right source, output directory, port and configuration, and that a taken port stops the command
before anything is launched. Rebuild latency, browser opening and reload behaviour are the
upstream project's and are not asserted.

This is the one place the specification deliberately keeps a stand-in, and the reason is written
here so a later reader does not mistake it for the gap R11 describes.

**ADR:** none. A testing boundary, recorded rather than decided.

## D11 — The success criteria are replaced with ones the suite can decide

The original criteria are wall-clock thresholds on machines nobody specified ("under 30 seconds",
"within 2 seconds") and percentages of an unenumerated population ("100% of common failure
scenarios"). None of them can pass or fail; a criterion that cannot fail is not a criterion.

**Settled:** rewritten so each one names a state a test can be in.

**ADR:** none.

## D12 — Requirements are renumbered

The original numbering carried `FR-010a`, `FR-010b` and `FR-015a`, inserted after the fact. The
rewritten specification numbers straight through. The mapping:

| Original | Now | |
|---|---|---|
| FR-001 | FR-001 | |
| FR-002 | FR-002 | |
| FR-003 | FR-002 | merged; a build with no arguments is one requirement |
| FR-004 | FR-003 | rewritten per D2 |
| FR-005, FR-006, FR-007 | FR-008, FR-009 | scoped per D10 |
| FR-008, FR-015a | FR-015, FR-019 | |
| FR-009, FR-010, FR-023 | FR-016 | merged into one table of settings |
| FR-010a, FR-010b | FR-016 | |
| FR-011 | FR-006, FR-017 | |
| FR-012 | FR-005 | |
| FR-013 | FR-021 | |
| FR-014 | FR-022 | rewritten per D6 |
| FR-015, FR-021 | FR-020 | merged per D7 |
| FR-016 | FR-011 | |
| FR-017 | FR-011 | rewritten per D3 |
| FR-018 | FR-011 | |
| FR-019 | FR-012 | |
| FR-020 | — | struck per D4 |
| FR-022 | FR-010 | |
| — | FR-004, FR-007, FR-013, FR-014, FR-018 | new; behaviour the code has and the specification never described |

## D13 — These directions were settled without a sign-off round

The questions above were the maintainer's to answer, and on 2026-09-01 he handed them back to be
settled here and reviewed with the finished work rather than agreed in advance. Every direction
call in this file is therefore the author's, recorded so it can be reversed on reading rather than
discovered later. Merging remains the maintainer's.

**ADR:** none.
