# Custom Theme Configuration Example

This example shows how to use **declarative configuration** via `[tool.fairdm.docs]` in your `pyproject.toml`.

## Choosing a Different Theme

By default, `fairdm-docs` uses the PyData Sphinx Theme, which it installs. To use another theme, install it and name it:

### pyproject.toml

```toml
[project]
name = "my-research-portal"
version = "2.1.0"
description = "Advanced research data portal"
authors = [
    {name = "Research Team", email = "team@research.org"}
]

[project.urls]
Homepage = "https://research-portal.org"
Repository = "https://github.com/research-org/portal"
Documentation = "https://docs.research-portal.org"

[tool.fairdm.docs]
title = "Research Portal"
theme = "furo"

[tool.fairdm.docs.theme_options]
sidebar_hide_name = true
```

### docs/conf.py

```python
# Still just one line!
from fairdm_docs.conf import *
```

`theme` takes the name of any installed Sphinx theme. A theme that is not installed stops the build with Sphinx's own error. Under any theme but PyData the package sets no theme options of its own, so the site gets exactly the options declared under `[tool.fairdm.docs.theme_options]`.

`title` is the name the site shows. Without it, the declared project name is used.

## How the Repository Address Is Found

Keys under `[project.urls]` are matched without regard to case, so `Repository`, `repository` and `REPOSITORY` all work. PEP 621's own field names elsewhere in `[project]` are matched exactly as the standard spells them.

Where both are declared the repository address wins; where only a homepage is declared, that is used. Declare neither and the navbar carries no GitHub icon and no Changelog entry.

## Reading Your Own Metadata

The import brings a `metadata` object with it, an instance of `ProjectMetadata`, carrying what the declaration said:

```python
from fairdm_docs.conf import *

html_theme_options["announcement"] = f"Version {metadata.version} is out."
```

Its fields are `name`, `version`, `description`, `authors`, `homepage` and `repository`, plus `copyright` and `address` — the single address the theme is configured with.

## Configuration Precedence

You can override any setting in your `docs/conf.py` after the import:

```python
# Import all fairdm_docs settings
from fairdm_docs.conf import *

# Override specific settings
html_theme_options["navbar_start"] = ["custom-widget"]
html_sidebars = {
    "**": ["custom-sidebar.html"]
}
```

**Precedence order** (highest to lowest):
1. Your `docs/conf.py` overrides (after the import)
2. `[tool.fairdm.docs]` in `pyproject.toml`
3. Package defaults in `fairdm_docs/conf.py`

## The PyData Defaults

Under the PyData theme the package sets these theme options:

- `navbar_align = "left"` and `header_links_before_dropdown = 6`
- `navbar_end` with the theme switcher and the icon links
- `icon_links` with one GitHub link, where an address is declared
- `external_links` with a "Changelog" entry pointing at `CHANGELOG.md` in the repository, where
  the file exists at the project root and an address is declared

It also adds a stylesheet that highlights the homepage's own navbar entry on the homepage.

Each key under `[tool.fairdm.docs.theme_options]` replaces the default of the same name and leaves
the others alone:

```toml
[tool.fairdm.docs.theme_options]
header_links_before_dropdown = 8
```

## Custom Branding

Place your logo and icon in `docs/_static/brand/`:

```
my-project/
├── pyproject.toml
└── docs/
    ├── conf.py
    ├── index.md
    └── _static/
        └── brand/
            ├── logo.svg    # Full logo with text
            └── icon.svg    # Square icon/mark
```

The package automatically detects and uses these files. If not found, it falls back to default FairDM branding.

## Example: Full Customization

```toml
[project]
name = "geospatial-data-hub"
version = "3.0.0"
description = "Open geospatial research data repository"
authors = [
    {name = "GeoHub Team", email = "contact@geohub.org"}
]
license = {text = "MIT"}
requires-python = ">=3.11"

[project.urls]
Homepage = "https://geohub.org"
Repository = "https://github.com/geohub/platform"
Documentation = "https://docs.geohub.org"
"Bug Tracker" = "https://github.com/geohub/platform/issues"

[tool.fairdm.docs]
theme = "pydata_sphinx_theme"
```

Then in `docs/conf.py`, add only what you need to change:

```python
from fairdm_docs.conf import *

# Add custom CSS, keeping the package's own
html_css_files.append("custom.css")

# Customize theme options
html_theme_options["footer_start"] = ["copyright"]
html_theme_options["footer_end"] = ["theme-version"]
```

## Next Steps

- [Full FairDM Portal Example](fairdm_portal_conf.md)
- [Main Documentation](../../README.md)
- [Migration Guide](../../README.md#migration-from-toolpoetry)
