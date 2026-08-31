# Decisions — 001

This specification was written on 2026-02-10, before the project had goals or a roadmap. It was
re-examined on 2026-08-31 against [GOALS.md](../../GOALS.md) and
[docs/ROADMAP.md](../../docs/ROADMAP.md), and rewritten. This file records what the original said,
what the code did, and which way each disagreement was settled. It exists so that a later reader
can tell a deliberate change from an accident.

## D1 — The specification covered two features. It now covers one.

The original spec carried four user stories. Two of them described a portal's packaging metadata
becoming the identity of its documentation site. The other two described selecting a theme and
other settings from a `[tool.fairdm.docs]` table.

The roadmap, written afterwards, separates these. R2 is the metadata. R10 is the settings table,
and it is scheduled against a different goal for a different reason: the table is read in two
places today and roughly half of it is invisible to each reader.

**Settled:** 001 is now R2 alone. The settings table leaves this specification. Nothing about it is
lost — R10 owns it, and owns it better, because R10 is about the whole table rather than the one
key this spec happened to mention.

Requirements removed on this ground: theme selection from the settings table, precedence between
that table and a developer's own configuration, validation of a theme name, and the handling of
unrecognised keys.

## D2 — Four more requirements had already been re-scheduled elsewhere.

The roadmap assigns work this specification also claimed. Where that happened, the roadmap wins,
because it was written later and with the whole package in view.

| The original requirement | Now owned by |
|---|---|
| Which `pyproject.toml` is read, and from where | R4 — *Documentation inputs are read from the portal, not from the installed package* |
| Where branding assets are found | R4 |
| Repository, issue and edit buttons on the rendered page | R3 — *A build with nothing configured completes* |
| The extension list and the comment system | R3 and R8 |
| The absence of tests for the module as a whole | R11 — *A change here cannot silently break a portal's build* |

The line this draws is between *which file is read*, which is R4, and *what is done with what it
says*, which is R2. Likewise between *the repository address is extracted*, which is R2, and
*whether a button is drawn for it*, which is R3.

R11 keeps the systemic gap: end-to-end build tests, the model documentation, dependency bounds.
The tests for the requirements below belong to this specification and are written here.

## D3 — Errors: the specification was right about intent, wrong about the name.

The original required a `ConfigurationError`. No such class exists anywhere in the package. The
code raises `ValueError` in three places (`conf.py:87`, `:92`, `:102`).

A bare `ValueError` is the wrong outcome, and not for tidiness. `cli.py` already catches
`ConfigError` at two points (`cli.py:195`, `cli.py:298`) to print a readable message instead of a
traceback. A `ValueError` raised from configuration escapes both, so a developer who misspells a
field gets a stack trace pointing into this package.

**Settled:** the specification keeps its intent — one recognisable error type — but names the class
the package already has, `ConfigError` (`config.py:15`), rather than introducing a second name for
the same idea. The code is wrong and closing that is work.

## D4 — Warnings: neither the specification nor the code had it right.

The original required Python's `logging` module at WARNING level. The code uses `warnings.warn`
with `UserWarning` (`conf.py:122`, `:130`, `:139`).

Both put the message somewhere the reader is not. A developer building a site reads the build
output. Sphinx keeps its own log, and a message that does not go there is a message the developer
does not see. The original spec's own closing notes reached the same conclusion and recorded it as
something to consider.

**Settled:** the requirement is written in terms of the outcome — a defaulted field is named in the
build output — rather than naming an API. The mechanism is settled in the plan.

## D5 — Malformed TOML is unhandled, and the requirement stands.

The original required a descriptive message for a TOML syntax error. Nothing handles
`tomllib.TOMLDecodeError`; it propagates raw from `utils.py:97`, and the caller catches
`FileNotFoundError` only (`conf.py:309`).

**Settled:** the requirement was right and was never built. It stays, and it is work.

## D6 — Case-insensitive lookup: the code is right and the specification overstated it.

The original required that key lookups be case-insensitive, without qualification. The code applies
this to `[project.urls]` keys only (`conf.py:161-163`).

The code has the better of this. PEP 621 spells its own field names, and they are lowercase by the
standard, so matching them loosely would accept files that are not valid packaging metadata. The
keys under `[project.urls]` are different: their names are chosen by whoever wrote the file, and
`Homepage`, `homepage` and `Repository` are all common in the wild.

**Settled:** narrowed to `[project.urls]`. The rest is matched exactly as PEP 621 spells it.

## D7 — The site title mangles the portal's name.

Undocumented behaviour, found in the code and mentioned nowhere in the original specification.
`conf.py:324` builds the site title as `metadata["name"].replace("-", " ").title()`.

For `fairdm-docs` that renders "Fairdm Docs". For a portal named `GHFDB` it renders "Ghfdb". G4 asks
that the site carry the portal's own name, and a transformed name is not the portal's own name. The
transformation also cannot be undone by the developer from within this specification's surface.

**Settled:** the declared name is used exactly as declared. This is a defect against G4 and closing
it is work. A portal wanting a different display title is asking for a setting, which is R10.

## D8 — An error message prints a backslash rather than a line break.

`conf.py:103` embeds a literal `\n` in a regular string, so the message about a missing
`project.name` shows the two characters to the developer instead of breaking the line.

**Settled:** a defect. Fixed here.

## D9 — Author tables were supported but undocumented.

PEP 621 allows authors as `{name = "...", email = "..."}` tables as well as strings. The code
handles both (`conf.py:146-148`); the original specification described only the string form.

**Settled:** the code is right and the specification was incomplete. Both forms are now specified.

## D10 — The original task list is not evidence.

`tasks.md` recorded 57 items done and 15 open. Those marks were made by the run that wrote them and
nothing in this re-examination relies on them. The task list was rewritten from the specification as
though no code existed, and each item was then checked against the code and the test suite.

The threshold used: an item counts as already done only where the code does it *and* a test proves
it. Code with no test leaves its item open, and the remaining work on it is the test. On a module
measured at 0% coverage (`conf.py`, 137 statements) that threshold is what most of this run's work
comes from.

## D11 — Three artefacts of the superseded specification are removed.

`data-model.md`, `quickstart.md` and `checklists/requirements.md` were generated for the February
version of this specification and were not touched when it was rewritten. Nothing in the current
plan reads any of them, and each contradicts what was approved.

`data-model.md` states that a version cannot be dynamic, which FR-006 requires; that every key is
matched case-insensitively, which D6 narrowed to `[project.urls]`; and it names an error type this
package does not have. It also documents the theme, branding and settings entities that D1 and D2
moved to R3 and R10. `quickstart.md` repeats the case-insensitivity claim twice and documents the
same out-of-scope surface. `checklists/requirements.md` grades the text of the specification that
was replaced.

**Settled:** deleted. A directory in which the only file named for the data model contradicts the
plan is worse than one with no such file, because the contradiction is only visible to a reader who
already knows which document won. What is current is in `spec.md`, `plan.md` and this file, and what
was replaced is in the history.

## D12 — The four stories edit one new file, so they are sequential.

`metadata.py` is created by US1 and added to by US2, US3 and US4. Each story is otherwise
independent, which reads as a licence to build them side by side. A story branched before US1 has
landed would not contain the file it is supposed to extend.

**Settled:** the dependency is written into `tasks.md` as blocking edges rather than left as a
remark, and each story starts from the feature branch after the one before it has landed on it.

## D13 — US1 builds `from_toml_data` only; `conf.py` does not call `from_file`.

The plan's `conf.py` snippet shows `ProjectMetadata.from_file(find_pyproject_toml())`. `from_file`'s
whole reason to exist is FR-018 and FR-019 — converting a decode error and a missing file into
`ConfigError` — and US1's brief rules that out explicitly: "no failure handling in this story." T008
also only asks for `ProjectMetadata` and `from_toml_data`.

`conf.py` already resolves `pyproject_data` above this point, through the existing
`load_pyproject_toml` / `find_pyproject_toml(use_env_var=True)` fallback that belongs to R4 and is
untouched by this story. Calling `from_file` a second time would re-run that resolution separately,
with no `use_env_var` fallback, and could in principle land on a different file than the one
`_extract_fairdm_config` already read.

**Settled:** `conf.py` builds `metadata` with `ProjectMetadata.from_toml_data(pyproject_data)`,
reusing the file already resolved. `from_file` does not exist yet; US3 (T025) adds it together with
the failure handling that is its reason to exist.

## D14 — The theme's source buttons crash on every build until US4, sidestepped in tests rather than patched in `conf.py`.

`_apply_theme_config` and the `comments_config` block both keyed off `metadata["urls"]`, which no
longer exists — `ProjectMetadata` does not carry addresses in this story ("No addresses ... in this
story," and FR-004/005/011 are US4's). Both are changed to a literal `repository_url = ""`, the
minimum needed for the file to still parse and run with the new type; the button flags
(`use_repository_button` and its two siblings) are left exactly as they were, `True`.

That default and those flags together mean `sphinx_book_theme`'s `add_source_buttons` handler is
enabled with nothing to point it at, and it crashes the build
(`TypeError: cannot unpack non-iterable NoneType object`) — for any declaration that does not name a
`[project.urls]` entry, which is exactly the shape T013 asks for. This is not a new defect: it
reproduces against the code exactly as it stood before this story, given the same input, and is
already tracked as its own roadmap item (`docs/ROADMAP.md` R3, dated 2026-08-26, ahead of this
specification's rewrite) — the research probe behind D7/D9 sidestepped it the same way, by declaring
a repository address it did not otherwise need.

**Settled:** `conf.py`'s theme wiring is not touched beyond the mechanical `metadata["urls"]` →
`repository_url = ""` fix. The `built_portal` test fixture in `conftest.py` passes `confoverrides`
that turn the three button flags off for the duration of a test build, so `TestRenderedSite` proves
identity values reach a rendered page without also fixing, or masking, R3's defect. The trigger
condition is unchanged by this story — any declaration without `[project.urls]` crashed before this
story and still does outside a test that overrides the button flags — this story neither introduces
nor closes it. Revisit when R3 lands.

## D15 — Test declarations are written where their tests are, not gathered up front.

T003 asked for a directory of declarations built before any test reads one. In practice each was
small enough to write beside the test that needs it, as a mapping or a short string, so the first
story added none. That is the right shape: a declaration written next to its assertion is readable
without a second file open, and one written before its consumer exists is a guess about what the
consumer will want.

**Settled:** `tests/fixtures/` keeps the five declarations it already had and is not extended.
Each story writes the declarations its own tests read, inline or through `tmp_path`. T003 therefore
stays open until the last story, at which point it is satisfied by all of them together rather than
by a directory.

## D16 — Defaulting checks key presence, not truthiness.

FR-012 says a field defaults when the system "does not find" it. `version`, `description` and
`authors` are each tested with `"field" in project` rather than `if project.get("field")`.

The two disagree on a field that is present but empty — `authors = []`, `description = ""`. That
case is T033's (Phase 6, out of this story's task list), and truthiness would silently default it
today with no test covering the choice either way. Presence-checking now means this story's
behaviour is exactly what FR-012 states — declared-but-empty is not "not found" — and leaves T033
free to add its own explicit test for the empty-value case without this story having already
picked an unverified answer for it.

**Revisit if:** T033 finds that a present-but-empty value should also default; the fix is a
truthiness check in the same three `if` branches in `fairdm_docs/metadata.py`.

## D17 — `from_file` locates the file itself; it does not receive an already-found path.

The plan's `conf.py` snippet (`## The design`) shows `ProjectMetadata.from_file(find_pyproject_toml())`
— `from_file` receiving the result of a search the caller already ran. T025's brief describes the
opposite: "`from_file` locates the file with `fairdm_docs.utils.find_pyproject_toml`", i.e. the
search happens inside `from_file`. The two disagree on which side calls `find_pyproject_toml`.

T023 needs `from_file` to accept a starting directory and report it in the "where it looked"
message on a miss (FR-019). A `from_file(path: Path | None)` signature that takes an
already-resolved path has nothing to report on `None` beyond "somewhere" — the caller's search
directory is gone by the time `from_file` sees it. Doing the search inside `from_file` keeps the
starting directory in scope for the error message.

**Settled:** `from_file(cls, start_dir: Path | None = None)` calls `find_pyproject_toml(start_dir)`
itself. This is consistent with D13, which already established that `conf.py` does not call
`from_file` in this story — there is no call site this signature has to match yet. Revisit if a
later story wires `from_file` into `conf.py` and needs it to accept `use_env_var`, which
`find_pyproject_toml` supports but nothing here yet asks for.

## D18 — T026 drives the CLI's existing `ConfigError` boundary via a patched Sphinx build, not a real one.

T026 asks for a metadata failure driven through `runner.invoke(app, ["build"])` with no traceback
in the output. `conf.py` does not call `from_file` in this story (D13, D17), so there is no
in-scope production code path where a real, unmocked build would ever reach it — `cli.py:build`
only calls `load_config()` (a different failure surface, already tested in
`TestConfigurationValidationErrors`) before handing off to Sphinx.

Running a real Sphinx build against a bad declaration would exercise a different failure than the
one this story adds: Sphinx's own `eval_config_file` catches any exception conf.py raises during
import and re-wraps it in Sphinx's `ConfigError` with `traceback.format_exc()` embedded in the
message text — the opposite of what FR-015/SC-004 ask for, and not something this story's
three-file scope can fix (`conf.py` is out of scope; D14 already left its theme-wiring defect
alone for the same reason).

**Settled:** `tests/test_cli.py::TestConfigurationFailures` patches `sphinx.cmd.build.main` with a
side effect that calls the real `ProjectMetadata.from_file()` against a real bad declaration
written to `tmp_path` — proving today's existing `except ConfigError` block in `cli.py` (D3) already
turns this story's new failures into a message, without asserting anything about how a future story
wires `from_file` into `conf.py` or `cli.py`. Revisit once that wiring lands: a real, unmocked build
becomes the more direct test at that point.

## D19 — `conf.py` routes its read through `from_file`, and re-raises as Sphinx's own error type.

D13 deferred the `conf.py` wiring to US3, and US3's brief then put `conf.py` out of its scope. The
result is that `from_file` has no caller outside the tests. Two of the five failures the
specification names are therefore not reachable in a real build: an invalid `pyproject.toml` still
raises `tomllib.TOMLDecodeError` out of `load_pyproject_toml`, and an absent one still raises the
`ValueError` written at `fairdm_docs/conf.py:174`. SC-004 asks for all five, so as it stands the
specification is not satisfied and the gap is one I introduced between two briefs.

Sphinx's `eval_config_file` (`sphinx/config.py:524-542`) decides what the developer sees. It has a
bare `except ConfigError: raise` that passes an error straight through to the console untouched,
and a generic `except Exception` that re-raises with `traceback.format_exc()` embedded in the
message. The pass-through is keyed on `sphinx.errors.ConfigError`, not on ours — so ours, raised
from `conf.py`, lands in the generic branch and the developer reads a traceback. Catching our
`ConfigError` in `conf.py` and re-raising Sphinx's with the same message text takes the
pass-through branch instead, and the message reaches the console with nothing wrapped around it.

**Settled:** T032a routes `conf.py`'s read through `ProjectMetadata.from_file` and re-raises as
`sphinx.errors.ConfigError`, tested against a real build rather than a patched one. D18's note that
a real build becomes the more direct test once the wiring lands is what this task acts on.

Two constraints pull against each other here and the task has to hold both. D13 protected the
`find_pyproject_toml(use_env_var=True)` fallback, and with it the guarantee that the metadata comes
from the same file `_extract_fairdm_config` read. D17 settled that `from_file` locates the file
itself rather than receiving an already-found path, and `from_file` carries no `use_env_var`
argument today. Whichever way those are reconciled — `from_file` learning the fallback, or D17
being narrowed to admit a resolved path — the reconciliation belongs to this task and gets recorded
as its own entry. Neither constraint may be dropped in silence.

## D20 — A defaulted address is silent; version, authors and description are not.

FR-012 lists both addresses among the optional fields that default, and FR-013 reads as if every
defaulted optional field is warned about. `TestDefaults::test_one_warning_is_emitted_per_defaulted_field`
(US2, T015) asserts exactly 3 warnings for `{"project": {"name": "sample-portal"}}` — a
declaration that also has no `[project.urls]` table, so if a defaulted address warned too, this
count would be 4 or 5. That test was written by an earlier story and this one may not modify it.

**Settled:** `resolve_address` returns `""` on a miss with no warning. FR-013's "one warning per
optional field" is read as covering the three fields US2 already built warnings for, not extended
to addresses this story adds. **Revisit if:** T015's test is deliberately widened to cover
addresses too — the fix is two more `logger.warning` calls in `from_toml_data`, next to the
`homepage`/`repository` extraction.

## D21 — D13/D17 reconciled by locating the file with the original two-stage precedence, then handing `from_file` the directory it already found. `from_file`'s signature is untouched.

D19 named the conflict and left the reconciliation to T032a. The first attempt gave `from_file` a
`use_env_var` parameter passed straight through to `find_pyproject_toml`, called unconditionally
as `from_file(use_env_var=True)`. The story's own mandatory full-suite run (§5) caught what
`tests/test_conf.py` alone did not: `find_pyproject_toml`'s `use_env_var=True` branch prefers the
`FAIRDM_DOCS_PROJECT_DIR` env var over the caller's `start_dir`/cwd whenever it is set, and
`cli.py:94`/`:229` set that var with a raw `os.environ[...] =` (not `monkeypatch.setenv`), so it
survives past the end of whichever test set it. Any earlier `tests/test_cli.py` test that invoked
a build left it pointing at that test's own `tmp_path`; every `tests/test_conf.py` test run after
it — not just the new T032a ones — read the wrong portal's identity, because the env var is
consulted before cwd rather than only once cwd fails. `poetry run pytest tests/test_cli.py
tests/test_conf.py` reproduced eight failures; `tests/test_conf.py` run alone showed none.

**Settled:** locate the file exactly as D13's original `conf.py` did — `find_pyproject_toml(start_dir=None)`
(cwd) first, `find_pyproject_toml(use_env_var=True)` only when that returns `None` — then call the
unmodified `ProjectMetadata.from_file(pyproject_path.parent)`. Passing a directory (not the resolved
file) keeps D17 exactly as settled: `from_file` still does its own (now trivially short, one-entry)
search and still has a directory to report in the "searched from" message on a miss.
`tests/test_cli.py::TestConfigurationFailures::test_metadata_failure_reported_as_message_not_traceback`
(D18) calls `ProjectMetadata.from_file()` directly with no `start_dir`, unaffected by any of this.

The env-var-as-fallback branch is still reachable — genuinely, not just via the leak — whenever
Sphinx has changed cwd away from the project root and the CLI set the var for that reason, which
is its whole purpose (`utils.py`'s own docstring). `tests/test_conf.py::TestConfigurationFailures::
test_missing_pyproject_is_reported_without_a_traceback` exercises exactly that fallback path (cwd
search must fail for the "no pyproject.toml" case to trigger at all), so it is directly exposed to
the same pre-existing leak on a suite run where an earlier test left the var set. **Settled:** the
test calls `monkeypatch.delenv("FAIRDM_DOCS_PROJECT_DIR", raising=False)`, since `tests/test_cli.py`
is not mine to change and the leak is `cli.py`'s, not this story's, to fix. **Revisit if:** a later
story gives `cli.py`'s tests `monkeypatch.setenv` instead of a raw assignment — the guard in this
test would then be redundant but still harmless.

`conf.py` calls `find_pyproject_toml`/`load_pyproject_toml` a second time (via `from_file`'s own
internal, now-trivial search, plus a further explicit `load_pyproject_toml(pyproject_path)`) to get
the raw mapping `_extract_fairdm_config` reads — `from_file` returns a `ProjectMetadata`, not the
mapping, and teaching it to expose one is a change to its public surface for a caller
(`_extract_fairdm_config`, R10's) this story does not own. **Revisit if:** R10 gives
`_extract_fairdm_config` its own reason to read `pyproject.toml` independently, at which point the
double read is worth collapsing.
