# FairDM Portal Configuration Example

This example shows a **complete production setup** for a FairDM-powered research data portal with full metadata extraction.

## Full pyproject.toml

```toml
[build-system]
requires = ["poetry-core>=2.0.0"]
build-backend = "poetry.core.masonry.api"

[project]
name = "aus-geoscience-portal"
version = "2.5.1"
description = "Australian Geoscience Data Portal - Open access to geological and geophysical research data"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Australian Geoscience Collaboration", email = "data@ausgeo.org"}
]
maintainers = [
    {name = "Data Team", email = "team@ausgeo.org"}
]
keywords = ["geoscience", "research-data", "fairdm", "django"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Framework :: Django :: 5.0",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.urls]
Homepage = "https://ausgeo.org"
Repository = "https://github.com/ausgeo/portal"
Documentation = "https://docs.ausgeo.org"
"Bug Tracker" = "https://github.com/ausgeo/portal/issues"
"Changelog" = "https://github.com/ausgeo/portal/blob/main/CHANGELOG.md"

# Dependencies managed by Poetry
[tool.poetry.dependencies]
python = "^3.11"
django = "^5.0"
fairdm = "^2.0"
# ... other dependencies

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
fairdm-docs = {git = "https://github.com/FAIR-DM/fairdm-docs"}
# ... other dev dependencies

# Configure fairdm-docs theme
[tool.fairdm.docs]
theme = "pydata_sphinx_theme"
```

## Minimal docs/conf.py

```python
"""
Sphinx configuration for Australian Geoscience Data Portal.

All metadata is automatically extracted from pyproject.toml.
"""

from fairdm_docs.conf import *

# Optional: Add custom extensions
extensions.append("sphinx.ext.intersphinx")

# Optional: Configure intersphinx
intersphinx_mapping = {
    "django": ("https://docs.djangoproject.com/en/stable/", None),
    "fairdm": ("https://fairdm.readthedocs.io/en/latest/", None),
}

# Optional: Customize theme options
html_theme_options["announcement"] = (
    "🚀 Version 2.5.1 released! Check the <a href='/changelog'>changelog</a>."
)
```

## What Gets Auto-Configured

With this `pyproject.toml`, `fairdm-docs` automatically sets up:

### Basic Sphinx Settings

- `project = "aus-geoscience-portal"` — the declared name, exactly as written
- `version = "2.5.1"`
- `copyright = "2026, Australian Geoscience Collaboration"`
- `author = "Australian Geoscience Collaboration"`
- `language = "en"`

### Theme Configuration (PyData Sphinx Theme)

```python
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/ausgeo/portal",
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/ausgeo/portal",
            "icon": "fa-brands fa-github",
        },
    ],
}
```

The address comes from `[project.urls]`: the repository where one is declared, the homepage
otherwise. Declare neither and `icon_links` is empty rather than pointing nowhere.

### Branding

The package looks for custom branding in order:

1. `docs/_static/brand/logo.svg` ✓ (your custom logo)
2. `docs/_static/brand/icon.svg` ✓ (your custom icon)
3. Falls back to default FairDM branding if not found

### Extensions

All these extensions come pre-configured:

- `myst_parser` - Markdown support
- `sphinx_design` - Cards, tabs, grids
- `sphinx_copybutton` - Copy code blocks
- `autodoc2` - API documentation from your source
- `sphinxext.opengraph` - Social media cards
- `sphinx_comments` - Utterances comments
- `sphinx.ext.napoleon` - Google and NumPy docstring styles
- `sphinx.ext.intersphinx` - Links into other projects' documentation
- `sphinx.ext.viewcode`, `sphinx.ext.todo`, `sphinx.ext.duration`, `sphinx.ext.githubpages`, `sphinx.ext.autosectionlabel`

### MyST Features

- Math equations with `$...$` and `$$...$$`
- Admonitions (note, warning, etc.)
- Definition lists
- Task lists with `- [ ]` and `- [x]`
- Smart quotes and replacements

## Custom Branding Files

Place your custom branding in `docs/_static/brand/`:

### docs/_static/brand/logo.svg

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60">
  <!-- Your organization's full logo with text -->
  <rect fill="#1E3A8A" width="200" height="60"/>
  <text x="10" y="40" fill="white" font-size="24" font-weight="bold">
    AusGeo
  </text>
</svg>
```

### docs/_static/brand/icon.svg

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <!-- Your organization's icon/mark (square aspect ratio) -->
  <circle cx="32" cy="32" r="30" fill="#1E3A8A"/>
  <text x="32" y="42" text-anchor="middle" fill="white" font-size="32" font-weight="bold">
    AG
  </text>
</svg>
```

## Documentation Structure

```
aus-geoscience-portal/
├── pyproject.toml          # Full PEP 621 metadata
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── conf.py             # Minimal configuration
│   ├── index.md            # Landing page
│   ├── quickstart.md       # Getting started guide
│   ├── api/
│   │   ├── index.md        # API overview
│   │   ├── samples.md      # Sample model docs
│   │   └── measurements.md # Measurement model docs
│   ├── guides/
│   │   ├── data-upload.md
│   │   ├── querying.md
│   │   └── contributing.md
│   ├── _static/
│   │   ├── brand/
│   │   │   ├── logo.svg    # Custom logo
│   │   │   └── icon.svg    # Custom icon
│   │   └── custom.css      # Optional custom styles
│   └── _templates/         # Optional custom templates
└── src/
    └── aus_geoscience/     # Your Django app
```

## Build Commands

```bash
# Development with live reload
cd docs
sphinx-autobuild . _build --open-browser

# Production build
sphinx-build docs docs/_build -b html

# Check for broken links
sphinx-build docs docs/_build -b linkcheck
```

## Continuous Integration (.github/workflows/docs.yml)

```yaml
name: Documentation

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: pipx install poetry

      - name: Install dependencies
        run: poetry install --with dev

      - name: Build docs
        run: |
          cd docs
          poetry run sphinx-build . _build -W --keep-going

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/_build

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Result

With this setup, you get:

✅ **Zero-config documentation** - Just write Markdown files
✅ **Professional theme** - PyData Sphinx Theme with GitHub integration
✅ **Custom branding** - Your logo and icon throughout docs
✅ **Social sharing** - OpenGraph cards for Twitter/LinkedIn
✅ **Community engagement** - Utterances comments on each page
✅ **Edit workflow** - "Edit on GitHub" button on every page
✅ **Auto-deployment** - GitHub Pages via Actions
✅ **Search** - Full-text search built-in
✅ **Mobile-responsive** - Works on all devices
✅ **Accessibility** - WCAG 2.1 AA compliant

## Next Steps

- [Basic Configuration](basic_conf.md)
- [Custom Theme Configuration](custom_theme_conf.md)
- [Main Documentation](../../README.md)
- [PEP 621 Specification](https://peps.python.org/pep-0621/)
