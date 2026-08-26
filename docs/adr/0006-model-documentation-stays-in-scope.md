# ADR 0006 — Model documentation stays in scope

**Status:** accepted — not yet implemented

## Decision

Generating documentation for a portal's registered models is a capability this package delivers.
It is not abandoned and its code is not to be removed on the grounds that it does not currently
run.

How it is delivered is open. Writing and maintaining a bespoke Sphinx extension for Django models
is not the preferred answer, and an existing package that already does this job is to be assessed
before any further work goes into the code that is here.

## Why

Turning a portal's own model definitions into documentation is the part of this package that
cannot be obtained anywhere else. The portal developer has already described their data model to
the framework, in the registry, and asking them to describe it a second time in prose is the
duplication this package exists to remove.

The current implementation has never run: the line that would load the extension is commented out
in the shipped Sphinx configuration, so the directive is never registered no matter how a portal
is configured. That makes the code an unfinished intention rather than a working feature, and it
is easy to mistake for something that was tried and dropped. This decision exists to say
otherwise.

Preferring an existing package follows from the same reasoning applied one level up. Documenting
Django models is a general problem that other people have already solved, and maintaining a
private answer to a general problem is a cost this package should only take on if the available
ones genuinely do not fit.

## Revisit if

An assessment finds nothing that fits a portal's registry-driven model, in which case the bespoke
extension becomes the answer and needs finishing properly rather than reviving as-is.
