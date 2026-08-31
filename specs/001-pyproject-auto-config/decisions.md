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
