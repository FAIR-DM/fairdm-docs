# Basic Configuration Example

This example shows the **absolute minimum** setup required to use `fairdm-docs`.

## pyproject.toml

```toml
[project]
name = "my-docs"
```

That's it! With just a project name, `fairdm-docs` will:

- Use the project name for documentation title
- Default version to "0.0.0"
- Generate copyright as "2026, Unknown"
- Apply the Sphinx Book Theme with default settings

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
- Add "Edit on GitHub" and "View Source" links
- Enable Utterances comments (if repository is public)

## Next Steps

- [Custom Theme Configuration](custom_theme_conf.md)
- [Full FairDM Portal Example](fairdm_portal_conf.md)
- [Main Documentation](../README.md)
