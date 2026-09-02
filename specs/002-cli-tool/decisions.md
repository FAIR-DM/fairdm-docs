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

A syntactically invalid `pyproject.toml` raises `tomllib.TOMLDecodeError` out of `utils.py:98`.
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

## D14 — US0 implementation notes (S4)

**Decision:** the `redirected_link` documentation source (`tests/fixtures/redirected_link/index.rst`,
T003) holds a literal `__REDIRECT_URL__` placeholder rather than a live address, because the
address it needs to link to only exists once the `redirect_server` fixture (also T003, an
`http.server`-based fixture in `tests/conftest.py`) has bound an ephemeral port for the running
test. A story that builds a portal from this source should read the file, replace the placeholder
with the URL `redirect_server` yields, and hand the result to `documented_portal`'s populate
callback.

**Why:** the source has to be a static file for the other four fixtures' pattern to stay uniform,
but the one thing this source is *for* — a redirect a real check can follow — cannot be known
until test time.

**Revisit if:** a second dynamic-content source is needed; at that point a small helper that does
the placeholder substitution is worth adding to `conftest.py` rather than leaving every caller to
repeat it.

---

**Decision:** README's new "Exit Codes" section (T036) documents `130` on interrupt for `build`
and `check`, but says explicitly that the live preview server's `Ctrl+C` still exits `0`
(`cli.py:146`) rather than folding it into the general claim.

**Why:** D6 commits to unifying this, but the fix is not in US0's task list and this worktree does
not carry it. Documenting the target behaviour without the caveat would have made the README wrong
again in the same task that was correcting it for D3/D4.

**Revisit if:** the story that implements D6 lands — the caveat sentence should come out of the
README in that same change.

**ADR:** none — implementation notes, not specification decisions.

---

**Decision:** T007's test (`test_creates_a_missing_parent_of_the_build_directory`) asserts the
observable behaviour FR-007 names — the build directory's parent exists and the build succeeds —
rather than asserting that `cli.py`'s own `config.build_dir.parent.mkdir(...)` call ran. Left
`cli.py` untouched.

**Why:** mutation-probing this line (per `craft-tdd`'s pre-report checklist) showed the test still
passes with it removed — Sphinx's own `Sphinx.__init__` calls `ensuredir(outdir)`
(`os.makedirs(path, exist_ok=True)`), which already creates the whole `build_dir` path, parent
included, independent of this line. The line is not incorrect and FR-007 holds either way, so
removing it is a simplification call outside this story's task list (T004-T010), not a defect
T010's "whatever is unmet" scope covers.

**Revisit if:** a simplification pass touches `cli.py`'s build path — worth removing then, with a
mutation-probe re-run to confirm Sphinx's own directory creation still covers it on whatever
Sphinx version is pinned at that point.

**ADR:** none — implementation notes, not specification decisions.

---

**Decision:** T024's `django = true` test supplies its own portal-local Django settings module
(`portal_django_settings.py`, `INSTALLED_APPS = []`) via `DJANGO_SETTINGS_MODULE`, rather than
relying on `conf.py`'s own fallback default of `config.settings`.

**Why:** `conf.py` only does `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")`
— that module doesn't exist anywhere in this repo (it's the convention of a real Django project
this package documents, not of `fairdm-docs` itself), so a real `django.setup()` call would raise
`ModuleNotFoundError`, which `conf.py`'s `except ImportError` clause happens to swallow (it's an
`ImportError` subclass) as a warning rather than a build failure. That masks the true test: with
the fallback settings module, `django.setup()` never completes, so `django.apps.apps.ready` never
becomes `True`, and the test could not tell "Django set up" from "Django setup silently failed."
Pre-setting `DJANGO_SETTINGS_MODULE` to a working module (the code's `setdefault` leaves an
already-set value alone) lets `django.setup()` actually succeed, so the test can assert the real
effect FR-018 names instead of just the env var.

**Revisit if:** a future story gives `fairdm-docs` its own bundled minimal settings module for
this purpose — at that point this test's one-off module could be replaced by the shared one.

**ADR:** none — implementation notes, not specification decisions.

---

**Decision:** T030 made no change to `fairdm_docs/cli.py`. Both gaps T028 and T029 were written to
close (source_dir/build_dir missing from the live-server argv assertion; no test proving
`is_port_available`'s real socket detection rather than its mocked return value) turned out to be
gaps in test coverage only — the implementation at `cli.py:121-122` and `cli.py:26-41` already did
the right thing.

**Why:** `reconciliation.md`'s Phase 5 note reads as coverage-gap language ("does not assert",
"nothing in the suite ever binds a real socket") rather than a claim the behaviour was broken, and
that reading held up under a mutation probe: T028 failed for the right reason with the argv lines
removed, T029 failed for the right reason with `is_port_available` hard-coded `True`, and `cli.py`
was restored byte-identical (`diff` confirmed) after each probe before committing either test.
Writing a no-op "fix" against working code would be busywork at best and a guardrail trip at worst
(tamper-check runs against the story's base, not a mid-story detour).

**Revisit if:** a later story finds `cli.py:121-122` or `is_port_available` actually wrong for some
input this task's tests don't cover — that would be new evidence, not a reopening of T028/T029.

**ADR:** none — a coverage-completion task that found nothing to fix, not a specification
decision.

---

**Decision:** T033's real end-to-end redirect test uses a locally-defined, self-terminating HTTP
server (`_TerminatingRedirectHandler` / `terminating_redirect_server`, added in
`tests/test_cli.py`), not `tests/conftest.py`'s existing `redirect_server` fixture (T003, US0),
even though the brief named `redirect_server` specifically.

**Why:** `redirect_server`'s handler (`tests/conftest.py:145-152`) answers every path, including
its own redirect target `/redirected`, with another `302 Location: /redirected`. Followed through
`requests`' automatic redirect-following — which Sphinx's linkcheck relies on for both its HEAD and
GET retrieval attempts (`sphinx/builders/linkcheck.py:464-465`, confirmed by reading the installed
package source) — that is a self-referential loop with no terminal response. Reproduced directly:
`requests.get(url, allow_redirects=True)` against a bare-bones copy of the same handler raises
`TooManyRedirects: Exceeded 30 redirects.` after 30 hops; a real `fairdm-docs check` against it via
`run_fairdm_docs` confirms the same end-to-end — Sphinx's linkcheck reports the line
`[broken] ... Exceeded 30 redirects`, never `[redirected with ...]`. `research.md` Q4's probe used
an external service (`httpbin.org/redirect-to`) precisely because it terminates in one hop;
`redirect_server` was never exercised against a real Sphinx build before this story. This is a
defect in the T003 fixture, not in this story's `cli.py` change, and `tests/conftest.py` is outside
this story's two-file scope (`fairdm_docs/cli.py`, `tests/test_cli.py`), so it is recorded here
rather than fixed in place.

**Revisit if:** a later story fixes `redirect_server` to terminate (e.g., a second path answering
200) — at that point T033 can switch to it and `_TerminatingRedirectHandler` /
`terminating_redirect_server` can be removed from `tests/test_cli.py`.

**ADR:** none — implementation note (test-infrastructure defect and workaround), not a
specification decision.
