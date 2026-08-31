# Architectural decisions

Each file here records one decision that constrains future work on this package. A decision is
never rewritten once it has landed. When a later decision overturns an earlier one, the earlier
one's status changes to point at its replacement and both stay in place.

| # | Decision | Status |
|---|---|---|
| [0001](0001-the-audience-is-the-portal-developer.md) | The audience is the FairDM portal developer | accepted |
| [0002](0002-configuration-is-layered-with-a-python-escape-hatch.md) | Configuration is layered, with a Python escape hatch | accepted |
| [0003](0003-django-is-a-peer-the-portal-supplies.md) | Django is a peer the portal supplies | accepted |
| [0004](0004-a-build-reads-the-development-environment-never-production.md) | A build reads the development environment, never production | accepted |
| [0005](0005-brand-assets-are-taken-from-the-portal.md) | Brand assets are taken from the portal, not restated | accepted, not yet implemented |
| [0006](0006-model-documentation-stays-in-scope.md) | Model documentation stays in scope | accepted, not yet implemented |
| [0007](0007-a-declaration-is-used-exactly-as-written.md) | A declaration is used exactly as written | accepted |
| [0008](0008-configuration-failures-are-one-error-type.md) | Configuration failures are one error type, surfaced where the developer is reading | accepted |
