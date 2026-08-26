# ADR 0003 — Django is a peer the portal supplies

**Status:** accepted

## Decision

Django is never a runtime dependency of this package. A portal already has Django installed, at
the version it has chosen, and this package uses whatever it finds.

Django is declared as a development dependency so the model-documentation code can be exercised
by this repository's own test suite, and it is imported only along paths a portal build reaches.
A build that does not need Django must succeed without it installed.

The portal's Django settings module is the portal's to nominate. This package does not decide it.

## Why

Depending on Django directly would let this package's version range constrain a portal's, which
inverts the relationship — the portal is the application and this is a build-time tool for it.
It would also force Django on anything else that installs the package, for a capability those
users will never reach.

Declaring it in the development group and importing it from the source is the honest description
of a peer dependency, which is why the dependency checker is told to expect it rather than being
satisfied by moving the declaration.

## Revisit if

Python packaging grows a peer-dependency concept that Poetry supports, at which point the
declaration should say what it means instead of being an ignored rule.
