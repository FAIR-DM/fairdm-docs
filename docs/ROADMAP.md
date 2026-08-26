# Roadmap — fairdm-docs

**Date:** 2026-08-26

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md) for domain terminology and [memory/constitution.md](../memory/constitution.md) for project standards.

The first two items have code behind them. They are carried here so the sequence reads whole, from an empty repository onwards, and neither is claimed as finished until it has been checked against the specification that describes it.

## Versioning

Releases are gated on how important a goal is, not on how many features have landed.

| Version | What it means |
|---------|---------------|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, install from a git pin rather than an index. |
| `0.1.0` | Every Essential goal delivered. The minimum usable release and the first publish. |
| `0.1.x` → `0.x` | The Expected goals, at whatever granularity the work takes. Patch releases are fixes. |
| `1.0.0` | Every Expected goal delivered. The complete, dependable release. |
| `1.x` | Stable line. Fixes and additive features only. |
| `2.0` | The next major, where breaking changes go. |

Two rules follow from that table. A goal is not one minor release: some take several, and one release can move two goals at once. Once `1.0` ships, a breaking change never goes out on the `1.x` line and waits for the next major instead.

Aspirational goals may be developed against v2 or v1 as required. None are recorded yet, so this roadmap ends at `1.0.0`.

## Built, not yet verified

Each of these describes a capability the code already attempts. Whether it does so well enough to count is decided by a check against its specification, not here.

### R1 — A command that builds a portal's documentation

*needs verification · advances G1*

A single command turns a directory of Markdown into a rendered HTML site, with a live-reloading variant for writing and a second command that checks the site's links. A small set of settings in the portal's `pyproject.toml` moves the source directory, the output directory, the preview port and how much the build says as it runs.

Serves G1.

### R2 — The portal's own metadata becomes the site's identity

*needs verification · advances G4*

The name, version, description, authors and repository address a portal already declares for packaging are read straight out of that declaration and become the site's title, version line, copyright and repository links. A portal that has stated a fact once is never asked to state it again, and a missing optional fact warns rather than stopping the build.

Serves G4.

## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R3 — A build with nothing configured completes

*resolve · advances G1*

The path the README puts first — a project name, a page of Markdown, one command — does not currently produce a site. It stops with an error from the theme, because a portal that has declared no repository address is still given repository, issue and edit buttons to render. Every build also warns about an API-documentation setting that is switched on and left empty, and one of the exclusion rules is written in a syntax the builder does not read, so it excludes nothing. Nothing further on this roadmap is worth building on top of an advertised path that fails, so this comes first.

**Deliverables:**

- The documented minimum, a project name plus one page, builds to a rendered site and exits successfully.
- Optional page furniture appears only when the portal has supplied what it needs, and is absent otherwise.
- A build against a correct portal emits no warnings the developer cannot act on.
- Settings that do nothing in their current form are either made to work or removed.
- A test that builds a minimum project end to end, so this failure cannot return unnoticed.

Serves G1. Out of scope: where the build looks for the portal's files, which is R4.

### R4 — Documentation inputs are read from the portal, not from the installed package

*feature · advances G1, G4, G5*

When a portal supplies no settings module of its own, the build reads its inputs relative to the installed package rather than to the portal. Three consequences follow, and they are the same fault three times. A portal's logo and icon are ignored and the framework's own are used in their place. A portal's stylesheets and images are not copied into the site. And the metadata behind the site's identity can be read from an entirely different project, so a portal's documentation is published carrying another project's name, version and comment thread. Each of those disappears the moment the developer writes a settings module of their own, which inverts the intended order: the simplest path is the one that misbehaves.

**Deliverables:**

- Brand assets, stylesheets and images are found in the portal's documentation source on the zero-configuration path, and the framework's defaults apply only when the portal has none.
- The portal being documented is identified unambiguously, and a build cannot pick up an unrelated project's metadata.
- The behaviour is identical whether or not the portal supplies a settings module of its own.
- Tests that build a portal from a location where the wrong answer was previously returned, and assert the portal's own inputs are used.

Serves G1, G4 and G5. Out of scope: bibliography and other inputs beyond branding and static files, which are R8.

### R5 — The site has a front page and a structure without one being written by hand

*feature · advances G1*

A documentation source holding only the pages a developer wrote does not build: the builder asks for a root page by a filename in a markup language this package does not otherwise use. So the promise of a complete site with nothing configured stops one step short: the developer must still hand-write a landing page and a table of contents before anything renders. The portal has already said what it is called and what it is for, and the build already knows which pages exist, so the front page and the navigation are facts it can assemble rather than chores to hand back. This also gives the generated model pages somewhere to be reached from, which is why it comes before R6.

**Deliverables:**

- A build succeeds against a documentation source containing only the developer's own pages, with no root page or contents listing written by hand.
- The generated front page carries the portal's name and description and links every page in the source.
- A developer who writes their own root page keeps it, and nothing is generated over the top.
- Tests covering both cases: a source with a root page, and one without.

Serves G1. Out of scope: what a portal's pages say, which stays the portal's business.

### R6 — The data model is documented from the registry

*feature · advances G2*

A portal registers its sample and measurement types with the framework, which makes the shape of its data a fact the framework already holds. Documenting that shape a second time by hand is the duplication this goal exists to remove, and today none of it happens: the code that would generate model pages is not loaded by any build, and where it does read the registry it expects a different shape from the one the registry returns, so it could not run if it were loaded. One portal has already worked around the absence by generating a diagram with separate tooling. This is the largest untouched Essential goal and the one that most distinguishes this package from a general-purpose documentation setup.

**Deliverables:**

- A portal's registered sample and measurement types are rendered as documentation pages describing their fields, relationships and metadata.
- The pages are reachable from the site's navigation without the developer wiring them in.
- A developer can place a single model's documentation on a page of their own writing.
- The Django settings a build reads are nominated by the portal rather than assumed, and a failure to load them says so plainly instead of reporting Django as missing.
- Tests that build a portal with registered models and assert the generated pages describe them.

Serves G2. Out of scope: changes to the framework's registry itself, which belong to that project — this item may need one, and the need should be raised there rather than worked around here.

### R7 — The site is published from the portal's own continuous integration

*feature · advances G3*

Building a site locally is where the work happens, but a portal's documentation is only useful once it is on the web, and nothing in this package puts it there. Portals attempting it today share a workflow that publishes the documentation source rather than the rendered site, so the deployment either fails or serves raw Markdown. Two consumers' documentation jobs have failed on every recent run. This is the last Essential goal because the thing being published has to be correct first.

**Deliverables:**

- A documented path that takes a portal from a source checkout to a published site on GitHub Pages, driven by its continuous integration.
- The rendered site is what gets published, whatever directory the portal builds into.
- A build can be made to fail on warnings, so a broken site is caught before it is published rather than after.
- Portals already consuming this package can adopt the path without rewriting their documentation source.
- The path is documented in this package's own documentation.

Serves G3. Out of scope: hosting anywhere other than GitHub Pages, and a site served by the portal itself, both of which stay the developer's own to arrange.

## Expected goals: v1.0.0

What a complete and dependable version is expected to have.

### R8 — Citations and the remaining documentation inputs are found without wiring

*feature · advances G5*

Research documentation cites things, and a portal building on a research data framework will have a bibliography before it has a documentation site. Citation support is currently a declared dependency that no build switches on, so a developer who wants it has to reach past the package and configure it themselves. The same holds for the other inputs a portal already has lying in known places. Branding and static files belong to R4. This item covers what is left.

**Deliverables:**

- A bibliography file in the portal's documentation source is picked up and citation syntax works in its pages, with no configuration.
- The remaining inputs a portal already keeps in a known location are found the same way, and the set is written down rather than discovered by reading the code.
- A portal with none of them builds exactly as it does today.
- Dependencies that no build switches on are either switched on or removed.

Serves G5.

### R9 — The package documents itself with its own tooling

*feature · advances G6*

This package cannot currently build its own documentation site, which is a plain statement about how well it serves anyone else's. What exists is a long README describing behaviour the code does not have, and a set of examples that present the advanced path as the simplest one. There is no guide, no reference for the settings a developer can change, and no worked example of doing well the things this package has opinions about. Fixing this both serves the goal directly and is the most honest test of R3 through R7.

**Deliverables:**

- This package's documentation is built by its own command and published by the path R7 establishes.
- A guide that takes a portal developer from installation to a published site.
- A reference for every setting a developer can change, and what happens when they change it.
- Guidance on the subjects worth getting right, branding and citations among them.
- The README reduced to what is true, with the detail moved into the documentation it now has.
- The examples corrected so the simplest path is presented first.

Serves G6.

### R10 — One vocabulary for the settings a developer can change

*resolve · advances G1*

The settings table in a portal's `pyproject.toml` is read in two places that know nothing of each other's vocabulary, so roughly half its settings are invisible to each reader. Neither reader says anything about a name it does not recognise, so a misspelled setting is silently ignored and the developer sees a build that succeeds while doing the opposite of what they asked. A configuration surface this small should be impossible to get subtly wrong.

**Deliverables:**

- One definition of the settings table, used by everything that reads it.
- An unrecognised setting is reported to the developer rather than ignored.
- The reference written for R9 is generated from, or checked against, that single definition.

Serves G1.

### R11 — A change here cannot silently break a portal's build

*feature · advances G1, G3*

Seven repositories install this package from a moving branch, so a change lands in all of them at once with nothing between it and their documentation builds. The suite does not currently protect them: the module holding most of the package's behaviour has no tests at all, and every test of the build command replaces the builder with a stand-in and checks the arguments it was handed. That is precisely how the failure in R3 shipped and stayed shipped. Several extension dependencies are also accepted at any future version, so a release by any one of them can break every portal without a change here at all.

**Deliverables:**

- Tests that run a real build against a real project and assert on the site that comes out.
- Coverage of the settings module and the model documentation, the two places where behaviour currently goes unchecked.
- Version bounds on the dependencies that can break a build, so an upstream release cannot reach portals unannounced.
- Test fixtures that are actually loaded, and shared setup written once.

Serves G1 and G3. Out of scope: what this package's own continuous integration runs, which is repository configuration rather than a goal.
