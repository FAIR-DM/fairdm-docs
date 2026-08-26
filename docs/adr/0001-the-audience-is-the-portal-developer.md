# ADR 0001 — The audience is the FairDM portal developer

**Status:** accepted

## Decision

This package is designed for one user: a developer building a FairDM portal who wants
documentation for it. Every default, every error message and every trade-off is settled in that
person's favour.

Other projects may install it, and several packages in the ecosystem currently do. They are
tolerated users, not supported ones. When a portal's needs and a standalone package's needs
disagree, the portal wins, and the package's case is not a defect.

Assume the portal developer has never configured Sphinx and does not want to. Ease of use is
bought at the cost of full control over the configuration, deliberately.

## Why

The package described itself as being for portals while most of its actual installations were
standalone Django packages. That left every question about defaults undecidable — a theme, a
directory layout or a metadata source that suits a portal does not always suit a library, and
without a ranked audience each one was argued from scratch.

Naming a single audience makes the questions answerable. It also matches where the value is: a
portal has a data model, branding and an identity that documentation can be generated from,
which is the part of this that cannot be bought off the shelf. A standalone package gets a
reasonable Sphinx setup and little else, and there are plenty of those.

## Revisit if

The ecosystem's standalone packages come to outnumber portal installations by enough that a
shared documentation standard across both is worth more than depth on portals. Or if the
portal-specific generation never materialises, at which point this is a generic Sphinx
configuration and should say so.
