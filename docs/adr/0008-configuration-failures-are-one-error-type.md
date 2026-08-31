# ADR 0008 — Configuration failures are one error type, surfaced where the developer is reading

**Status:** accepted

## Decision

Every way a portal's declaration can fail to be read raises one error type, `ConfigError`. A
missing file, a file that is not valid TOML, an absent `[project]` table and an absent `name` all
arrive at the same boundary and are rendered the same way.

Two boundaries render it. The command-line interface catches `ConfigError` and prints the message
on its own. The Sphinx configuration module catches it and re-raises Sphinx's own `ConfigError`
carrying the same text.

A defaulted field is reported through the build's log rather than through Python's warning
machinery, so it appears where the developer is already looking.

## Why

A configuration mistake is the developer's to fix, and a traceback is a report about this
package's internals. Anything that escapes as a bare `ValueError` reaches the console as a stack
trace pointing into code the reader did not write, for a fault that is one line away in a file
they did.

The second boundary is not redundant with the first. Sphinx evaluates `conf.py` inside a handler
that passes its own `ConfigError` straight through to the console and wraps everything else with
a formatted traceback. An error raised from `conf.py` therefore reads as a crash unless it is
re-raised as the type that handler is looking for. The same message travels either path; only the
type decides whether the reader sees it plainly.

Warnings follow the same principle one step down. A build's output is what the developer reads,
and Python's warning stream is not part of it.

## What is not decided

Whether the errors carry structure beyond their message — a code, a field name, a machine-readable
form. Nothing consumes them today except a human reading a console.

## Revisit if

A caller needs to distinguish one failure from another programmatically, at which point the single
type gains subclasses rather than the callers matching on message text.
