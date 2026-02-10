# Quick Start Guide: Zero-Config Documentation

**Feature**: PEP 621 pyproject.toml Auto-Configuration  
**Target Audience**: FairDM Portal Developers

## Prerequisites

- Python 3.11 or higher
- Poetry or pip for package management
- Existing project with `pyproject.toml` using PEP 621 `[project]` section

## Installation

### Using Poetry (Recommended)

```bash
poetry add --group dev fairdm-docs
```

### Using pip

```bash
pip install git+https://github.com/FAIR-DM/fairdm-docs
```

## Minimal Setup (1 Minute)

### Step 1: Create Documentation Directory

```bash
mkdir docs
cd docs
```

### Step 2: Create Configuration File

Create `docs/conf.py` with a single line:

```python
from fairdm_docs.conf import *  # noqa: F401, F403
```

That's it! No additional configuration needed.

### Step 3: Ensure pyproject.toml Has Required Fields

Your `pyproject.toml` **must** have a `[project]` section with at least a `name`:

```toml
[project]
name = "my-fairdm-portal"
```

### Step 4: Build Documentation

```bash
# From docs directory
sphinx-build . _build/html

# Or with auto-reload during development
sphinx-autobuild . _build/html
```

Open `_build/html/index.html` in your browser to see your documentation!

## Recommended Setup (Full Metadata)

For best results, populate all recommended PEP 621 fields:

```toml
[project]
name = "my-fairdm-portal"
version = "1.0.0"
description = "A research data management portal for..."
authors = [
    "Your Name <you@example.com>",
    "Collaborator Name <them@example.com>"
]

[project.urls]
homepage = "https://github.com/your-org/your-portal"
repository = "https://github.com/your-org/your-portal"
documentation = "https://your-portal.readthedocs.io"
```

This automatically configures:
- Project title and version
- Copyright notice with your names
- GitHub repository buttons and links
- Issue tracker integration
- "Edit on GitHub" buttons

## Optional: Custom Theme

If you want to use PyData Sphinx Theme instead of the default Book theme:

### Option 1: Using pyproject.toml (Recommended)

Add to your `pyproject.toml`:

```toml
[tool.fairdm.docs]
theme = "pydata_sphinx_theme"
```

Install the theme:

```bash
poetry add --group dev "fairdm-docs[pydata-sphinx-theme]"
```

### Option 2: Using conf.py

Add after the import in `docs/conf.py`:

```python
from fairdm_docs.conf import *

# Override theme
html_theme = "pydata_sphinx_theme"
```

## Optional: Custom Branding

To use your own logo and icon:

1. Create branding directory in docs:

```bash
mkdir -p docs/_static/brand
```

2. Add your files:
   - `docs/_static/brand/logo.svg` - Logo for documentation header
   - `docs/_static/brand/icon.svg` - Favicon

The system automatically detects and uses your branding. If not present, it falls back to FairDM defaults.

## What Gets Auto-Configured

From your `pyproject.toml`, the following Sphinx settings are automatically populated:

**Note**: All pyproject.toml keys are read case-insensitively (e.g., "Homepage" or "homepage" both work).

| Sphinx Variable | Source | Default if Missing |
|-----------------|--------|-------------------|
| `project` | `[project].name` | ❌ Error (required) |
| `version` | `[project].version` | "0.0.0" (warning) |
| `release` | Same as version | "0.0.0" |
| `copyright` | `[project].authors` + current year | "2026, Unknown" |
| `html_theme_options['repository_url']` | `[project].urls.repository` | "" (empty) |
| `html_logo` | `docs/_static/brand/logo.svg` | Package default |
| `html_favicon` | `docs/_static/brand/icon.svg` | Package default |

## Pre-Configured Extensions

These Sphinx extensions are enabled automatically:

- **sphinx.ext.viewcode** - Link to source code
- **sphinx.ext.intersphinx** - Link to other documentation
- **sphinx.ext.napoleon** - Google/NumPy style docstrings
- **sphinx.ext.autosectionlabel** - Reference sections by title
- **myst_parser** - Markdown support with math, admonitions, etc.
- **sphinx_copybutton** - Copy buttons on code blocks
- **sphinxext.opengraph** - Social media preview cards
- **sphinx_comments** - Utterances-based comments
- **sphinx_design** - UI components (cards, tabs, grids)
- **autodoc2** - Modern API documentation

## Troubleshooting

### Error: "Missing required 'project.name' in pyproject.toml"

**Solution**: Add `[project]` section with `name` field:

```toml
[project]
name = "your-project-name"
```

### Error: "PEP 621 [project] section required. Legacy [tool.poetry] format is not supported."

**Solution**: Migrate to PEP 621 standard. Change from:

```toml
[tool.poetry]
name = "my-project"
version = "1.0.0"
```

To:

```toml
[project]
name = "my-project"
version = "1.0.0"
```

See: <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>

**Note**: Keys like `Homepage`, `homepage`, or `HOMEPAGE` are all handled correctly (case-insensitive).

### Warning: "Missing optional field 'project.version'"

**Non-blocking**: Build succeeds with version "0.0.0". Add version to remove warning:

```toml
[project]
version = "1.0.0"
```

### Error: "pyproject.toml not found"

**Solution**: Ensure `pyproject.toml` is at repository root (one directory up from `docs/`):

```
your-project/
├── pyproject.toml    ← Must be here
├── docs/
│   ├── conf.py
│   └── _static/
│       └── brand/    ← Optional: custom branding
│           ├── logo.svg
│           └── icon.svg
```

## Next Steps

1. **Add Content**: Create `docs/index.md` as your documentation home page
2. **Customize Theme**: Override settings in `conf.py` or `[tool.fairdm.docs]`
3. **Add Pages**: Create more `.md` or `.rst` files in `docs/`
4. **Configure TOC**: Create `_toctree.yml` or use MyST syntax
5. **Deploy**: Set up GitHub Actions, Read the Docs, or other hosting

## Examples

See the `examples/` directory for:
- **basic_conf.md** - Minimal configuration example
- **custom_theme_conf.md** - Theme customization examples
- **fairdm_portal_conf.md** - Complete FairDM portal setup

## Getting Help

- **Documentation**: <https://github.com/FAIR-DM/fairdm-docs#readme>
- **Issues**: <https://github.com/FAIR-DM/fairdm-docs/issues>
- **PEP 621 Guide**: <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>
