# Custom Theme Configuration Example

This example shows how to use **declarative configuration** via `[tool.fairdm.docs]` in your `pyproject.toml`.

## Choosing a Different Theme

By default, `fairdm-docs` uses `sphinx_book_theme`. To use PyData Sphinx Theme instead:

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
theme = "pydata_sphinx_theme"
```

### docs/conf.py

```python
# Still just one line!
from fairdm_docs.conf import *
```

The package will automatically:
- Install and configure PyData Sphinx Theme
- Set up GitHub integration with "Edit on GitHub" button
- Configure the repository URL from `[project.urls]`
- Apply theme-specific defaults

## How the Repository Address Is Found

Keys under `[project.urls]` are matched without regard to case, so `Repository`, `repository` and `REPOSITORY` all work. PEP 621's own field names elsewhere in `[project]` are matched exactly as the standard spells them.

Where both are declared the repository address wins; where only a homepage is declared, that is used. Declare neither and the theme is configured without an address.

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

## Supported Themes

Currently supported themes:

### sphinx_book_theme (default)

```toml
[tool.fairdm.docs]
theme = "sphinx_book_theme"  # or omit this line entirely
```

Auto-configured options:
- `repository_url` from `[project.urls]`
- `use_repository_button = true`
- `use_issues_button = true`
- `use_edit_page_button = true`
- Utterances comments enabled (if public GitHub repo)

### pydata_sphinx_theme

```toml
[tool.fairdm.docs]
theme = "pydata_sphinx_theme"
```

Auto-configured options:
- `github_url` from `[project.urls]`
- `icon_links` with a GitHub link, where an address is declared
- `navbar_end` with the theme switcher and the icon links

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

# Add custom CSS
html_static_path = ['_static']
html_css_files = ['custom.css']

# Customize theme options
html_theme_options["footer_start"] = ["copyright"]
html_theme_options["footer_end"] = ["theme-version"]
```

## Next Steps

- [Full FairDM Portal Example](fairdm_portal_conf.md)
- [Main Documentation](../../README.md)
- [Migration Guide](../../README.md#migration-from-toolpoetry)
