# FairDM Documentation Tools

Standardized documentation configuration and tooling for FairDM-powered research data portals.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Overview

`fairdm-docs` is a reusable Sphinx configuration package that provides:

- **Zero-config documentation** - Automatically extracts project metadata from `pyproject.toml` (PEP 621)
- **Smart defaults** - Missing optional fields don't block builds, sensible defaults provided
- **Case-insensitive** - Handles URL case variations (Homepage/homepage, Repository/repository)
- **Flexible theming** - Pre-configured support for Sphinx Book Theme and PyData Sphinx Theme
- **Declarative configuration** - Configure theme and options via `[tool.fairdm.docs]` in pyproject.toml
- **Django model documentation** - Custom directives for auto-documenting Sample and Measurement models
- **Modern features** - MyST Markdown, math support, code copy buttons, social sharing, and more
- **Developer-friendly** - One-line import with easy customization

## Installation

Add `fairdm-docs` to your development dependencies:

```bash
poetry add --group dev git+https://github.com/FAIR-DM/fairdm-docs
```

Or with a specific theme:

```bash
poetry add --group dev "git+https://github.com/FAIR-DM/fairdm-docs[pydata-sphinx-theme]"
```

## Quick Start

### 1. Create your documentation directory structure

```
your-project/
├── docs/
│   ├── conf.py
│   ├── index.md
│   └── _static/      # Optional: custom CSS/images
├── pyproject.toml
└── ...
```

### 2. Configure Sphinx

In your `docs/conf.py`, import the base configuration:

```python
from fairdm_docs.conf import *

# Optional: Override specific settings
project = "My Custom Project Name"  # Overrides pyproject.toml if needed
html_theme = "pydata_sphinx_theme"  # Change theme
```

That's it! The configuration automatically:

- Reads project metadata from PEP 621 `[project]` section in `pyproject.toml`
- Configures your chosen theme (Sphinx Book Theme by default) with GitHub integration
- Enables MyST Markdown with extended features
- Sets up all recommended extensions
- Handles missing optional fields gracefully with sensible defaults

### 3. Build your documentation

```bash
cd docs
poetry run sphinx-build -b html . _build/html
```

Or use autobuild for live reloading:

```bash
poetry run sphinx-autobuild docs docs/_build/html
```

## Features

### PEP 621 Auto-Configuration

The package automatically extracts metadata from the PEP 621 standard `[project]` section in your `pyproject.toml`:

**Required fields:**
- `name` - Project name (used for documentation title)

**Optional fields** (with sensible defaults if missing):
- `version` - Project version (default: "0.0.0")
- `authors` - Author names for copyright (default: ["Unknown"])
- `description` - Short description for meta tags
- `urls.homepage` - Homepage URL
- `urls.repository` - Repository URL for GitHub integration

**Example `pyproject.toml`:**

```toml
[project]
name = "my-research-portal"
version = "1.0.0"
description = "A research data management portal"
authors = [
    {name = "Jane Doe", email = "jane@example.com"},
    {name = "John Smith"}
]

[project.urls]
homepage = "https://github.com/myorg/my-portal"  # or Homepage (case-insensitive)
repository = "https://github.com/myorg/my-portal"  # or Repository
```

**Case-insensitive handling:** URL keys like `Homepage`/`homepage` and `Repository`/`repository` are automatically normalized.

### Declarative Configuration

Configure documentation settings in your `pyproject.toml` without writing Python code:

```toml
[tool.fairdm.docs]
theme = "pydata_sphinx_theme"  # or "sphinx_book_theme"
```

**Configuration precedence:**
1. Your `docs/conf.py` overrides (highest priority)
2. `[tool.fairdm.docs]` in pyproject.toml
3. Package defaults (lowest priority)

### Automatic Metadata Extraction

**Legacy format note:** This package requires PEP 621 `[project]` section. Projects using only `[tool.poetry]` metadata must migrate. See [Migration Guide](#migration-from-toolpoetry) below.

The package automatically extracts the following from your `pyproject.toml`:

- Project name and version
- Authors and copyright
- Homepage URL (for repository links)
- Package description

### Pre-configured Extensions

The following Sphinx extensions are enabled by default:

- **sphinx.ext.autodoc** - API documentation from docstrings
- **autodoc2** - Modern API documentation with MyST rendering
- **myst-parser** - Markdown support with rich features
- **sphinx-copybutton** - Copy buttons on code blocks
- **sphinx-design** - UI components (cards, tabs, grids)
- **sphinxext-opengraph** - Social media preview cards
- **sphinxcontrib-bibtex** - Citations and bibliographies
- **sphinx-comments** - Utterances-based documentation comments

### MyST Markdown Features

The following MyST extensions are enabled:

- Math equations (amsmath, dollarmath)
- Admonitions and callouts
- Definition lists
- Task lists
- Tables
- HTML elements
- Smart quotes and replacements

### Branding

The package automatically detects project branding with a fallback chain:

1. Checks for `docs/_static/brand/logo.svg` and `docs/_static/brand/icon.svg` in your project
2. Falls back to default FairDM branding in `fairdm_docs/_static/`

To use custom branding, simply place your logo and icon files in `docs/_static/brand/`.

### Django Model Documentation

For FairDM portals, use the `autodoc-model` directive to document models:

```markdown
# My Sample Types

```{autodoc-model} myapp.MySample
```
```

This generates complete documentation including:
- Model metadata (verbose name, description, keywords)
- Field listings with types, help text, and validators
- Relationships and constraints
- Custom methods
- Automatically ordered based on model configuration

The extension uses Jinja2 templates located in `fairdm_docs/_templates/model.md.jinja` and auto-generates documentation files for all registered models in the `data_models/` directory during the build process.

## Customization

### Override Theme Options

```python
# docs/conf.py
from fairdm_docs.conf import *

html_theme_options.update({
    "show_toc_level": 2,
    "navbar_align": "left",
    "show_nav_level": 1,
})
```

### Add Custom Extensions

```python
# docs/conf.py
from fairdm_docs.conf import *

extensions.extend([
    "sphinx.ext.graphviz",
    "sphinxcontrib.mermaid",
])
```

### Customize Static Files

```python
# docs/conf.py
from fairdm_docs.conf import *

html_css_files = [
    "custom.css",
]
```

### Disable Comments

```python
# docs/conf.py
from fairdm_docs.conf import *

comments_config = {}  # Disable Utterances
```

## Theme Support

The package supports multiple Sphinx themes via poetry extras:

```bash
# Sphinx Book Theme (default, always installed)
poetry add --group dev git+https://github.com/FAIR-DM/fairdm-docs

# PyData Sphinx Theme
poetry add --group dev "git+https://github.com/FAIR-DM/fairdm-docs[pydata-sphinx-theme]"
```

To change themes:

```python
# docs/conf.py
from fairdm_docs.conf import *

html_theme = "pydata_sphinx_theme"
```

## Project Structure Requirements

For best results, your project should have:

- `pyproject.toml` with PEP 621 `[project]` section at project root
- `docs/` directory at project root (sibling to `pyproject.toml`)
- `docs/_static/brand/` for custom logo/icon (optional)
- GitHub repository for Utterances comments and edit links

**Migration note:** Projects using only `[tool.poetry]` metadata must add the `[project]` section. See [Migration Guide](#migration-from-toolpoetry) below.

## Configuration Reference

### Auto-extracted from pyproject.toml (PEP 621)

| Sphinx Config                           | Source                   | Example                |
|-----------------------------------------|--------------------------|------------------------|
| `project`                               | `project.name`           | "fairdm"               |
| `version`                               | `project.version`        | "0.1.0"                |
| `copyright`                             | `project.authors`        | "2026, Sam"            |
| `html_theme_options["repository_url"]`  | `project.urls.repository`| "github.com/org/repo"  |

**Note:** URL keys are case-insensitive (e.g., `homepage`, `Homepage`, `HOMEPAGE` all work).

### Default Values

| Config | Default Value |
|--------|---------------|
| `language` | "en" |
| `html_theme` | "sphinx_book_theme" |
| `master_doc` | "index" |
| `autodoc2_render_plugin` | "myst" |

## Migration from [tool.poetry]

**Breaking change:** Version 0.2.0+ requires PEP 621 `[project]` section in your `pyproject.toml`.

### Before (Legacy - NOT SUPPORTED)

```toml
[tool.poetry]
name = "my-fairdm-portal"
version = "1.0.0"
description = "My research data portal"
authors = ["Your Name <you@example.com>"]
```

### After (PEP 621 - REQUIRED)

```toml
[project]
name = "my-fairdm-portal"
version = "1.0.0"
description = "My research data portal"
authors = [
    {name = "Your Name", email = "you@example.com"}
]

[project.urls]
Homepage = "https://my-portal.org"
Repository = "https://github.com/myorg/my-portal"
```

### Migration Steps

1. **Add [project] section** to `pyproject.toml` with required `name` field
2. **Copy metadata** from `[tool.poetry]` to `[project]` (use PEP 621 format for authors)
3. **Move URLs** to `[project.urls]` table (keys are case-insensitive)
4. **Keep [tool.poetry]** if you're still using Poetry for dependency management (both sections can coexist)
5. **Test build**: Run `sphinx-build docs docs/_build` to verify

### Why This Change?

PEP 621 is the Python packaging standard for project metadata. This migration:
- Aligns with community standards
- Supports build backends beyond Poetry
- Enables case-insensitive URL key handling
- Simplifies metadata extraction logic

## Contributing

Issues and pull requests are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built for the [FairDM](https://github.com/FAIR-DM) ecosystem to standardize documentation across research data portals.
