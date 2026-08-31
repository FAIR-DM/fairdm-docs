# ADR 0007 — A declaration is used exactly as written

**Status:** accepted

## Decision

A value a portal has declared in its `pyproject.toml` reaches the rendered site unchanged. The
name is not re-cased, re-punctuated or otherwise prettified, and no field is rewritten on the way
through.

Matching a declaration's keys follows the same rule in reverse. Field names that PEP 621 spells
itself are matched exactly as the standard spells them. Keys under `[project.urls]` are named by
whoever wrote the file, so those are matched without regard to case.

A field that is present but empty has been declared. Only an absent field is defaulted, and a
defaulted field is named in the build output.

## Why

A portal named `GHFDB` rendered as "Ghfdb", and `fairdm-docs` as "Fairdm Docs". Neither is the
name its project answers to. A documentation site is the portal's public face, and a title the
developer never wrote and cannot change from the package's own surface is the package overruling
the project it is documenting.

The same reasoning settles the two halves of key matching, and they point in opposite directions
on purpose. Loosening the match on PEP 621's own field names would accept files that are not
valid packaging metadata, which makes this package a place where invalid declarations appear to
work. Tightening the match on `[project.urls]` would reject `homepage` and `Repository`, both
common in the wild and both correct, because the standard leaves those names to the author.

Presence rather than truthiness follows from the same idea. `authors = []` is a statement, and
replacing it with an invented author is the package deciding it knows better.

## What is not decided

Whether a developer can set a display title different from the declared name. That is a setting,
and the settings table is a separate piece of work. Nothing here forecloses it: an explicitly
declared title is a declaration too, and this decision is about what happens when the developer
has not made one.

## Revisit if

A field arrives whose declared form genuinely cannot be rendered — a name carrying markup, or a
description longer than the surface it lands on. The answer then is to reject or truncate at the
boundary with a message, not to silently rewrite.
