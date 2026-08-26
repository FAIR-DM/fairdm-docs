# ADR 0005 — Brand assets are taken from the portal, not restated

**Status:** accepted — not yet implemented

## Decision

A portal's documentation carries the portal's own logo and icon. The developer supplies them once,
where their portal already keeps them, and the build makes them available to the rendered site.
Copying files into a second location by hand is not an acceptable answer.

When the portal has no assets of its own, the build falls back to the ones this package ships.

## Why

The portal and its documentation are the same product to a reader, and a documentation site
wearing the framework's default branding looks like it belongs to someone else. The developer has
already done this work for the web interface, so asking again is asking twice.

The assets have to come from files in the checkout rather than from uploaded ones, because a
build cannot read the production database (ADR 0004). That makes this a build-time file
operation, not a runtime lookup.

## What is not decided

Where the build looks. Portals disagree today: one keeps `assets/brand/` and `assets/img/brand/`,
another `assets/images/` alongside an application's `static/brand/`, and FairDM itself ships
`static/brand/` inside the framework. A hardcoded path would be wrong for most of them.

Resolving assets through Django's static-file finders is the obvious candidate, since Django is
already set up during a portal build and the finders honour the portal's own precedence over the
framework's. It has not been tested and is not ratified here.

## Revisit if

The set of assets grows beyond a logo and an icon — colours, fonts or a full theme — at which
point copying individual files stops scaling and the question becomes how the documentation
inherits the portal's theme rather than its images.
