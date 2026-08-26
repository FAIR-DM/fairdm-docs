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
- Configure the repository URL from `project.urls.Repository`
- Apply theme-specific defaults

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
- `repository_url` from `project.urls.Repository`
- `use_repository_button = true`
- `use_edit_page_button = true`
- Utterances comments enabled (if public GitHub repo)

### pydata_sphinx_theme

```toml
[tool.fairdm.docs]
theme = "pydata_sphinx_theme"
```

Auto-configured options:
- `icon_links` with GitHub repository link
- `use_edit_page_button = true`
- `navigation_with_keys = false`

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
