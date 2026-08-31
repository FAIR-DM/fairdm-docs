# Implementation Plan — 001

**Specification**: [spec.md](spec.md) · **Research**: [research.md](research.md) ·
**Prior version and what changed**: [decisions.md](decisions.md)

## Summary

A portal's PEP 621 declaration becomes one value object, and the Sphinx configuration module reads
its identity off that object. Everything the specification requires — the two author forms, the
case-insensitive address keys, the defaults, the warnings and the five failures — belongs to the
value object and is tested directly. The configuration module keeps only the assignments Sphinx
reads, and one test builds a real site and reads the values back out of the HTML.

## Technical context

| | |
|---|---|
| Language | Python 3.11+ (`tomllib` is stdlib from 3.11) |
| Primary dependencies | Sphinx, sphinx-book-theme, myst-parser, autodoc2 |
| Testing | pytest, pytest-cov |
| Storage | none — one file read |
| Target | a Sphinx build on a developer's machine or in CI |
| Performance | not a factor; the file is read once per build |
| Constraints | the module is executed by Sphinx as a configuration file, so its module-level namespace is the interface (Article XI) |

## Constitution check

| Article | How this plan meets it |
|---|---|
| I — Test-First | Every task below writes its test before its implementation, and the task list is ordered so the test task precedes the implementation task it covers. |
| II — Simplicity | One new module, one class, no configuration surface added. |
| III — Anti-Abstraction | See Complexity Tracking. |
| IV — Integration-First | SC-006 requires a test that reads a rendered site, and the research probe proved a real build is feasible in-suite. Three tasks build real sites. |
| VI — Documentation | The title change is user-visible behaviour, so README and CHANGELOG ship in this change. |
| VII — Dependency discipline | Nothing is added. `sphinx` is already a runtime dependency. |
| X — Test structure | `fairdm_docs/metadata.py` → `tests/test_metadata.py`; the configuration module → `tests/test_conf.py`; `Test<Subject>` classes; shared setup in a new `conftest.py`, which the repository currently lacks. |
| XI — Cohesion | The extraction is three module-level functions sharing one subject, which this article puts on a class. The configuration module's module-level namespace is this article's named exception and stays as it is. |
| XIII — Zero configuration is the measured path | US2 is that path, and it becomes a test that builds a site from a project declaring one field. |
| XIV — Backward compatibility | The title change is breaking in the sense the article means. The package is below 1.0.0, so the deprecation window is advisory, and CHANGELOG carries the change with what a portal does if it wants the old title. |
| XVI — Never assume a production environment | Nothing here reaches outside the file being read. |

## Project structure

```
fairdm_docs/
├── metadata.py      NEW — the declaration as a value object
├── conf.py          keeps the Sphinx namespace, loses the extraction
├── config.py        unchanged — supplies ConfigError
└── utils.py         unchanged — finding and parsing the file stays R4's

tests/
├── conftest.py      NEW — a temporary portal, and a real build of one
├── test_metadata.py NEW — every requirement, directly
├── test_conf.py     NEW — the values that reach a rendered site
└── fixtures/        extended with the declarations these tests need
```

## The design

### `fairdm_docs/metadata.py`

One class, `ProjectMetadata`, holding what a portal declared: `name`, `version`, `description`,
`authors` as display names, `homepage` and `repository`. Two constructors:

- `from_toml_data(data)` — takes an already-parsed mapping. This is where FR-001 to FR-006, FR-012,
  FR-013, FR-016 and FR-017 live, and it is the reason the behaviour becomes testable without
  touching the filesystem.
- `from_file(path)` — reads and parses, then delegates. FR-018 and FR-019 live here, converting
  `tomllib.TOMLDecodeError` and a missing file into the package's own error.

One derived value, `copyright`, from the current year and the display names (FR-009).

Failures raise `ConfigError` from `fairdm_docs.config` (FR-015), which `cli.py` already catches at
two points and reports as a message. No new error type is introduced. The import direction is
`metadata` → `config` → `utils`, which is acyclic, verified against the current imports.

Warnings go through `sphinx.util.logging.getLogger(__name__)` (FR-014), which the research probe
proved is the only mechanism that reaches the build output. This repository already uses that logger
in `extensions/autodoc_models.py`.

Names carry no leading underscore. The class is the boundary; what is on it is on it.

### `fairdm_docs/conf.py`

Loses `normalize_key`, `get_case_insensitive`, `extract_project_metadata` and the defaults and
warnings that go with them. Keeps the module-level namespace Sphinx reads, now assigned from the
value object:

```python
metadata = ProjectMetadata.from_file(find_pyproject_toml())

project = metadata.name          # verbatim — FR-007, and the D7 defect closed
version = metadata.version       # FR-008
release = metadata.version
author = ", ".join(metadata.authors)   # FR-010
copyright = metadata.copyright   # FR-009
```

The theme configuration reads `metadata.repository` and `metadata.homepage` (FR-011). Whether
buttons are drawn from them is R3's and is not touched.

Everything else in the module — the extension list, `source_suffix`, `html_static_path`, the
autodoc2 and Django blocks, the LaTeX and epub sections — is out of scope and is left alone. Several
are defective; R3, R4, R5 and R6 own them.

### `tests/conftest.py`

Two fixtures, because Article X puts construction boilerplate here rather than in the assertions:

- one that writes a temporary project from a declaration given as a string or a mapping,
- one that builds such a project's documentation for real, through `from fairdm_docs.conf import *`,
  and returns the rendered HTML together with the build output.

The built project's index is `index.rst`. `conf.py` registers `.rst` alone as a source suffix, which
is R3's defect; using it here keeps these tests about which values reach the page.

## Complexity tracking

**A new module, where the specification could have been met by editing one.**

Article III asks what a new piece of structure buys, and refuses it if the answer is future
flexibility. The answer here is present and concrete: SC-006 requires that every requirement is
covered by a test, and today none of them can be, because `conf.py` performs its work as
module-level statements that read a file from disk and raise when it is absent. Importing anything
from it runs the whole chain. That is measured, not asserted — the module is 137 statements at 0%
coverage, and the coverage is 0% because there is no way in.

What is being added is one concrete class with two constructors, directly instantiated. No base
class, no interface, no registry, no indirection, and no second way to do anything. Article XI
independently requires the class, because the three functions being moved share one subject.

**What is deliberately not done.** `pyproject.toml` is read in two places in this package, and the
two readers disagree about roughly half of what they read. Unifying them is R10's subject and it
covers the settings table as well as the metadata. Doing it here would be the larger, vaguer change
Article II warns about, and it would put this change on the critical path of an item scheduled
separately.

## Notes carried into the tasks

- The suite currently has no `conftest.py`, so the shared-fixture task creates one.
- `tests/fixtures/` holds five declarations already; the new ones extend that directory rather than
  starting another.
- The old task list for this specification is not evidence and no line of it is carried over
  (decisions.md, D10).
