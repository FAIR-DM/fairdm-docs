# ADR 0004 — A build reads the development environment, never production

**Status:** accepted

## Decision

A documentation build runs inside the portal's development environment, with its development
database available. Django is set up so that models can be inspected.

The production database is never reachable from a build and must never be assumed. Every fact
that reaches the rendered site therefore comes from one of two places:

- content generated from the portal's source, principally its registered models
- the portal's `pyproject.toml`

Database-backed portal identity is explicitly out of bounds. FairDM stores a portal's public
name, description and uploaded branding in singleton models edited through the admin, and a
build must not read them, because the values a build would find in a development database are
not the values the live portal shows.

## Why

Documentation is built from a checkout, in continuous integration or on a developer's machine,
and neither has production credentials. Anything sourced from the production database would be
absent in exactly the environments where documentation is built, and the failure would be
silent: the build would succeed and publish placeholder values.

The development database is a different matter. It is present wherever the portal's own test
suite runs, and reading models through it is inspection of code that is in the checkout anyway,
not of data that only exists in production.

`pyproject.toml` is the right home for the remaining facts because it is in version control,
because the portal already maintains it, and because the standard `[project]` table means this
package is reading a documented format rather than inventing one.

## Revisit if

FairDM gains a file-based portal identity in version control — a manifest rather than a database
singleton — which would make the portal's public name and description available to a build
without either a production database or a duplicate entry in `pyproject.toml`.
