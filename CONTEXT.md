# CONTEXT.md — the vocabulary of this package

This file pins the words this repository uses, so that specifications, issues, code and
documentation all mean the same thing by them. When a term here conflicts with a name in the
current code, the term here is the target and the code is what changes.

## Who this is for

**Portal developer** — the person this package exists to serve. They are building a FairDM
portal and want documentation for it. Assume they know their own research domain and their own
portal, and know nothing about Sphinx. They should never have to learn Sphinx to get a good
documentation site, and should be able to learn as much of it as they like when they want to
change one.

## The core nouns

**Portal** — a research data application built on the FairDM framework. Always a Django project.
This is the only kind of thing this package is designed to document. Packages in the wider
ecosystem may use it, but their needs never outrank a portal's.

**Portal documentation** — the documentation site a portal publishes about itself: what the
portal is for, how to use it, and what data it holds. Not to be confused with the documentation
of this package, or with FairDM's own framework documentation.

**Documentation build** — one run that turns a portal's documentation source into a rendered
site. It happens in a development environment, from a source checkout, using the command-line
tool this package installs.

**Documentation source** — the directory of Markdown the portal developer writes, `docs/` by
default. Its counterpart is the **build directory**, where the rendered site is written.

**Project metadata** — the facts about the portal that live in its `pyproject.toml`, in the
standard `[project]` table: name, version, description, authors and URLs. This package reads
them so the developer never restates them.

**Declarative configuration** — the `[tool.fairdm.docs]` table in the portal's `pyproject.toml`.
The small set of settings a developer can change without writing Python.

**Override** — a Python-level change the developer makes in their own `docs/conf.py`, for
anything the declarative configuration does not reach. Overrides are for advanced users and are
expected to be rarer than declarative configuration.

**Brand assets** — the portal's own logo and icon. A portal already has them for its web
interface, and its documentation is expected to carry the same ones without the developer
copying files by hand.

**Theme** — the Sphinx theme the rendered site uses. This package supports a fixed, small set of
them and ships one as the default.

## The Django-facing nouns

**Registry** — FairDM's model registry, the object a portal's models are registered against. It
is the channel through which a portal tells the framework about itself, and therefore the channel
through which this package learns what to document.

**Sample** and **Measurement** — the two families of model a FairDM portal registers. A portal's
own models subclass them. They are the subject of model documentation.

**Model documentation** — pages generated from a portal's registered models, describing their
fields, relationships and metadata, so that the portal's data model is documented without anyone
writing it out a second time.

## Words to avoid, and what to say instead

**"Config"** — currently means four unrelated things in this codebase:

- the build settings module
- a raw table read out of `pyproject.toml`
- an entry in FairDM's registry
- a Django settings package

Never use it unqualified. Say *declarative configuration*, *build settings*, *registry entry* or
*Django settings* instead.

**"Docs"** — ambiguous between the portal's documentation, this package's own, and the `docs/`
directory. Say *portal documentation* or *documentation source*.

**"autodoc-models"** — the extension module is named `autodoc_models`, but the thing a developer
writes in Markdown is the singular directive `autodoc-model`. Write the directive name exactly,
and refer to the capability as *model documentation*.

**"Project"** — in this repository, prefer *portal*. "Project" collides with Sphinx's own
`project` variable and with the standard `[project]` table, and both of those appear in the same
files.

**"Config directory" and "source directory"** — Sphinx calls the directory holding `conf.py` the
*configuration directory*, and it is not necessarily the documentation source. Keep them
distinct, and never abbreviate either to "dir".
