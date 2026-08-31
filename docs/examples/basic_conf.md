# Basic Configuration Example

This example shows the **absolute minimum** setup required to use `fairdm-docs`.

## pyproject.toml

```toml
[project]
name = "my-docs"
```

That's it! With just a project name, `fairdm-docs` will:

- Title the documentation `my-docs`, exactly as declared — the name is never re-cased or re-punctuated
- Default version to "0.0.0"
- Generate copyright as "2026, Unknown"
- Apply the Sphinx Book Theme with default settings

The build also says what it had to invent. A declaration carrying only a name produces one warning per defaulted field:

```
WARNING: No version declared in [project]; defaulting to '0.0.0'.
WARNING: No description declared in [project]; defaulting to ''.
WARNING: No authors declared in [project]; defaulting to ['Unknown'].
```

Each names its field, so filling one in is a one-line edit.

## docs/conf.py

```python
# All configuration comes from fairdm_docs
from fairdm_docs.conf import *
```

## Project Structure

```
my-docs/
├── pyproject.toml    # Minimal [project] section
└── docs/
    ├── conf.py       # Single-line import
    └── index.md      # Your documentation content
```

## Build

```bash
cd docs
sphinx-build . _build
```

## Adding More Metadata (Optional)

To get better documentation, add more PEP 621 fields:

```toml
[project]
name = "my-docs"
version = "1.0.0"
description = "My project documentation"
authors = [
    {name = "Your Name", email = "you@example.com"}
]

[project.urls]
Homepage = "https://my-project.org"
Repository = "https://github.com/myorg/my-project"
```

This will:
- Show version "1.0.0" in docs
- Generate copyright "2026, Your Name"
- Point the theme's repository buttons at the declared `Repository` address
- Enable Utterances comments (if repository is public)

Where both a `Homepage` and a `Repository` are declared, the repository address is the one used. Declare only a `Homepage` and that is used instead.

## What a Declaration It Cannot Read Produces

A `pyproject.toml` with no `[project]` table, no `name`, or invalid TOML syntax stops the build with a message naming what to fix, not a traceback. A file carrying only `[tool.poetry]` is told that PEP 621 metadata is required and pointed at the [migration guide](../../README.md#migration-from-toolpoetry).

## Next Steps

- [Custom Theme Configuration](custom_theme_conf.md)
- [Full FairDM Portal Example](fairdm_portal_conf.md)
- [Main Documentation](../../README.md)
