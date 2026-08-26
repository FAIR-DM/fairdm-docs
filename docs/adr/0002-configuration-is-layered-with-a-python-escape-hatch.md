# ADR 0002 — Configuration is layered, with a Python escape hatch

**Status:** accepted

## Decision

Configuration comes in three layers, and a portal developer meets them in order of increasing
effort.

1. **Defaults.** A portal with no configuration at all gets a complete, working documentation
   site. Nothing is required beyond the documentation source and the standard `[project]` table
   the portal already has.
2. **Declarative settings.** `[tool.fairdm.docs]` in the portal's `pyproject.toml` covers the
   changes developers actually make, without writing Python.
3. **Python override.** The portal's own `docs/conf.py` is the escape hatch. Anything the first
   two layers do not reach is reachable here, and a developer who opens this layer is expected
   to have read this package's documentation first.

Layer three is deliberately all-or-nothing at the file level: it is a supported interface with a
documented contract, not a partial merge. Getting it wrong is a documentation problem for this
package to solve, not a reason to constrain the layer.

## Why

FairDM already made this choice for Django, and a portal developer should not have to learn two
different philosophies to configure one portal. In FairDM, `fairdm.setup()` establishes a
layered baseline in the portal's settings module and the developer overrides by plain assignment
afterwards, with the layer that produced each value recorded and inspectable. The shape here is
the same: sensible defaults the developer never sees, a small declarative surface for the common
case, and unrestricted Python underneath for anyone who needs it.

The alternative — exposing every Sphinx setting through declarative keys — was rejected because
it re-creates Sphinx's configuration surface in a second syntax, which is more to learn rather
than less, and it can never be complete.

The layering is a philosophy, not a copy of FairDM's implementation. This package does not have
Django's settings module to inject into, and the mechanism that realises these layers is not
settled by this decision.

## Revisit if

The declarative layer grows past the handful of settings that portal developers genuinely change,
which would be evidence that the escape hatch is too hard to reach and the layers are in the
wrong place.
