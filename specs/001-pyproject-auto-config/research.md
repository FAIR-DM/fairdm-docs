# Research — 001

Three questions had to be answered before the plan could be written. Each was settled by running
something, not by reading.

## Q1 — Where can a message written while the configuration is being read actually appear?

FR-014 requires that a warning about a defaulted field reaches the developer reading the build. The
original specification said Python's `logging`; the code uses `warnings.warn`. Neither was verified.

**Probe.** A minimal Sphinx project whose `conf.py` emits both, at module level, then a build.

```python
from sphinx.util import logging as sphinx_logging
sphinx_logging.getLogger("conf-probe").warning("PROBE-SPHINX-LOGGER at module exec")
warnings.warn("PROBE-WARNINGS-WARN at module exec", UserWarning, stacklevel=2)
```

**Result.**

```
WARNING: PROBE-SPHINX-LOGGER at module exec
.../sphinx/config.py:529: UserWarning: PROBE-WARNINGS-WARN at module exec
  exec(code, namespace)  # NoQA: S102
```

Sphinx's own logger works at the moment `conf.py` is executed, and produces a properly formed build
warning. `warnings.warn` produces Python's warning format, pointing at a line inside Sphinx that
means nothing to the reader.

The difference is not only cosmetic. Sphinx counts its own warnings, reports the total at the end of
a build, and `-W` turns them into failures. A `UserWarning` participates in none of that, so a build
with `-W` passes while the site is missing its version and its authors.

**Settled:** `sphinx.util.logging.getLogger(__name__)`. FR-014 is met by that and nothing else is
required.

## Q2 — Can a test assert on a rendered site, or only on the values on the way to it?

SC-006 requires at least one test that reads a rendered site. Article IV is explicit that a test
which mocks the Sphinx entry point away has verified the arguments and nothing else. Whether a real
build driven from `fairdm_docs.conf` is feasible inside the suite was unknown, because the module
does its work at import and pulls in a theme, several extensions and an optional Django setup.

**Probe.** A temporary project declaring name, version, description, an author table and a
repository address, with `docs/conf.py` containing only `from fairdm_docs.conf import *`, built with
`sphinx-build`.

**Result.** `build succeeded, 2 warnings.` in 0.012s of reading time. The two warnings are
`html_static_path entry '_static' does not exist` and `autodoc2_packages must not be empty`, both of
which belong to R3 and neither of which fails the build.

**Settled:** feasible and fast. The end-to-end tests build a real site and read the HTML.

**One constraint.** The index page must be `index.rst`. `conf.py` registers `.rst` alone as a source
suffix while loading the Markdown parser, so a project whose only page is `index.md` fails with
*Sphinx is unable to load the master document*. That is R3's defect and fixing it here would be out
of scope, so these tests use an `.rst` index. They are testing which values reach the page, not which
markup languages are read.

## Q3 — What does a rendered site actually say today?

The same probe, read back out of the generated HTML:

| | Rendered | Declared |
|---|---|---|
| Title | `Probe — Ghfdb 2.5.1 documentation` | name `GHFDB` |
| Version | `2.5.1` | `2.5.1` |
| Copyright | `© Copyright 2026, Ada Lovelace.` | author table, `Ada Lovelace` |

Version and copyright are right, and the author table form is handled correctly, which confirms D9.

The title confirms D7 against a real build rather than by reading the code: `GHFDB` reaches the page
as `Ghfdb`. `conf.py:324` lowercases every letter after the first of each word. For a portal whose
name is an acronym the site advertises a word that does not exist.

## Structure

The reason none of this is currently tested is structural rather than an oversight. `conf.py` does
its extraction in functions but performs the assembly as bare module-level statements from line 305
onward. Importing anything from it runs the whole chain, including reading a file from disk and
raising if it is absent, so there is no way to exercise the extraction in isolation.

The plan moves the extraction into its own module and leaves `conf.py` as the Sphinx-facing surface
that consumes it. That is a module split rather than a new layer: no wrapper, no base class, and the
concrete present use is that the behaviour becomes reachable by a test, which SC-006 requires.

The two readers of `pyproject.toml` are deliberately **not** unified here. That is R10's subject, and
it covers the whole settings table rather than the metadata alone.
