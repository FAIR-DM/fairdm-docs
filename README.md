# FairDM Documentation Tools

Sphinx configuration and build tooling for FairDM research data portals.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Overview

`fairdm-docs` is a reusable Sphinx configuration package that provides:

- **Simple CLI tool** - Build, preview, and validate documentation with `fairdm-docs` command
- **Zero-config documentation** - Automatically extracts project metadata from `pyproject.toml` (PEP 621)
- **Live preview server** - Real-time documentation updates with `fairdm-docs build --live`
- **Link validation** - Check for broken links with `fairdm-docs check`
- **Smart defaults** - Missing optional fields don't block builds, sensible defaults provided
- **Flexible theming** - Pre-configured support for Sphinx Book Theme and PyData Sphinx Theme
- **Django model documentation** - Custom directives for auto-documenting Sample and Measurement models
- **Modern features** - MyST Markdown, math support, code copy buttons, social sharing, and more
- **Developer-friendly** - Works out of the box, easy to customize when needed

## Status

Early. The version is `0.0.1` and the package is working towards a `0.1.0` milestone.

Parts of this README describe intent rather than current behaviour — Django model documentation
in particular is not wired up in the shipped configuration, so the `autodoc-model` directive is
not registered by a normal build. Where the README and the code disagree, the code is the fact.
Open an issue when you hit one.

## Scope & philosophy

This is a documentation setup for FairDM portals, built for a portal developer who wants a good
documentation site and has no interest in learning Sphinx. It reads the portal's own metadata,
branding and registered models, and turns them into a rendered site with nothing configured.

It is not a general-purpose Sphinx distribution, and it is not a thin wrapper that exposes
Sphinx's configuration surface in TOML. Full control over the configuration is traded away for
ease of use, on purpose. Other kinds of project can install it and several do, but a portal's
needs decide every question.

Configuration comes in three layers, in order of increasing effort:

1. Defaults, which cover a portal that configures nothing.
2. `[tool.fairdm.docs]` in `pyproject.toml`, for the settings developers actually change.
3. A `docs/conf.py` of your own, which is the escape hatch and gives you all of Sphinx back.

This mirrors how FairDM itself treats Django settings, so that configuring a portal and
configuring its documentation feel like the same activity.

When those layers pull against each other, the tie-breaks are:

- a working default beats a configurable one
- a portal beats a standalone package
- a fact read from the portal beats a fact restated in configuration

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

### Option 1: Zero-Config (Recommended)

The simplest way to get started - no configuration files needed!

**Prerequisites:** Ensure you have a `pyproject.toml` with at least a `[project]` section containing `name`:

```toml
[project]
name = "my-project"
version = "0.1.0"  # Optional
```

**1. Create documentation structure:**

```plain
your-project/
├── docs/
│   ├── index.md          # Required: main documentation file
│   ├── conf.py           # Optional: advanced customization
│   └── _static/          # Optional: custom CSS/images
│       └── brand/        # Optional: logo.svg and icon.svg
├── pyproject.toml        # Required: project metadata
└── ...
```

**2. Build documentation:**

```bash
poetry run fairdm-docs build
```

That's it! Documentation will be built to `docs/_build/html/`.

**For live preview during development:**

```bash
poetry run fairdm-docs build --live
```

This automatically:

- Reads project metadata from `pyproject.toml`
- Uses sensible defaults for everything
- Opens a browser with live-reloading

### Option 2: Add Configuration

Configure behavior via `pyproject.toml`:

```toml
[tool.fairdm.docs]
source_dir = "docs"              # Documentation source (default: "docs")
build_dir = "docs/_build/html"   # Output directory (default: "docs/_build/html")
port = 5000                      # Live server port (default: 5000)
verbosity = "full"               # Options: "full", "quiet", "errors-only"
django = false                   # Enable Django integration (default: false)
```

Then build as before:

```bash
poetry run fairdm-docs build
```

### Option 3: Advanced Customization

For advanced users who need to override Sphinx settings directly, create a `docs/conf.py`:

```python
from fairdm_docs.conf import *

# Override specific settings
project = "My Custom Project Name"  # Override name from pyproject.toml
html_theme = "pydata_sphinx_theme"  # Change theme

# Add custom extensions
extensions.extend([
    "sphinx.ext.graphviz",
    "sphinxcontrib.mermaid",
])

# Customize theme options
html_theme_options.update({
    "show_toc_level": 2,
    "navbar_align": "left",
})
```

**Configuration precedence** (highest to lowest):

1. Settings in `docs/conf.py` (if file exists)
2. `[tool.fairdm.docs]` in `pyproject.toml`
3. Package defaults

**Minimum requirements:**

- `pyproject.toml` with `[project]` section containing `name`
- `docs/index.md` with some content

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

**Note:** These customization options require creating a `docs/conf.py` file (see [Quick Start Option 3](#option-3-advanced-customization)). For simple configuration changes, use `[tool.fairdm.docs]` in `pyproject.toml` instead.

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

## CLI Usage

The `fairdm-docs` command-line tool provides a simplified interface for building documentation with sensible defaults.

### Basic Build

```bash
fairdm-docs build
```

This command:

- Reads configuration from `[tool.fairdm.docs]` in `pyproject.toml` (optional)
- Uses the package's built-in Sphinx configuration
- Builds HTML documentation to `docs/_build/html` by default
- Works without any configuration in `pyproject.toml`

### Live Preview Server

Start a live-reloading preview server for real-time documentation development:

```bash
fairdm-docs build --live
```

This command:

- Starts a web server on `http://localhost:5000` (configurable)
- Automatically opens your documentation in a browser
- Watches for file changes and rebuilds automatically
- Hot-reloads the browser when changes are detected
- Press `Ctrl+C` to stop the server

**Port Configuration**: If port 5000 is already in use, configure a different port:

```toml
[tool.fairdm.docs]
port = 8080  # Use any available port
```

The server will then start on `http://localhost:8080`.

### Documentation Validation

Validate your documentation for broken links before publishing:

```bash
fairdm-docs check
```

This command:

- Checks all internal and external links in your documentation
- Reports broken links with file locations and line numbers
- Exits with code 0 if all links are valid
- Exits with code 1 if broken links are found (useful for CI/CD)

**Example output** when broken links are found:

```
🔍 Checking documentation for broken links...
❌ Found 2 broken link(s):

   docs/api.md:42: [broken] https://nowhere.invalid/: Connection failed
   docs/guide.md:15: [broken] https://example.broken/: 404 Not Found
```

**CI/CD Integration**: Use in your continuous integration pipeline:

```yaml
# Example GitHub Actions workflow
- name: Check documentation links
  run: poetry run fairdm-docs check
```

### Configuration Options

Add configuration to your `pyproject.toml`:

```toml
[tool.fairdm.docs]
source_dir = "docs"              # Source directory (default: "docs")
build_dir = "docs/_build/html"   # Output directory (default: "docs/_build/html")
port = 5000                      # Port for live server (default: 5000)
verbosity = "full"               # Output verbosity: "full", "quiet", or "errors-only"
django = false                   # Enable Django integration (default: false)
```

### Django Integration

By default, Django is **disabled** to allow documentation builds without Django installed. Enable it when documenting Django models:

```toml
[tool.fairdm.docs]
django = true  # Enables Django model auto-documentation extensions
```

When `django = true`:

- Django is imported and configured automatically
- the `autodoc-model` directive becomes available for documenting Django models
- Requires Django to be installed: `poetry add Django`

When `django = false` (default):

- No Django dependency required
- Works in non-Django projects
- Suitable for pure documentation sites

### Examples

**Zero-config build** (no pyproject.toml changes needed):

```bash
cd your-project
fairdm-docs build
```

**Live preview for development**:

```bash
fairdm-docs build --live  # Opens browser, auto-reloads on changes
```

**Custom output directory**:

```toml
[tool.fairdm.docs]
build_dir = "build/html"
```

**Custom port for live server**:

```toml
[tool.fairdm.docs]
port = 8080
```

**Quiet mode for CI/CD**:

```toml
[tool.fairdm.docs]
verbosity = "quiet"
```

**Django project**:

```toml
[tool.fairdm.docs]
django = true
source_dir = "documentation"
```

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

## Troubleshooting

### Common Issues

#### "No module named 'django'"

**Cause**: Django integration is enabled but Django is not installed.

**Solution**: Either install Django or disable the integration:

```toml
[tool.fairdm.docs]
django = false  # Disable Django integration
```

Or install Django:

```bash
poetry add Django  # If using Poetry
pip install Django  # If using pip
```

#### "Port 5000 is already in use"

**Cause**: Another service is using port 5000 (default live server port).

**Solution**: Configure a different port:

```toml
[tool.fairdm.docs]
port = 8080  # Or any available port
```

#### "sphinx-autobuild not found"

**Cause**: sphinx-autobuild is not installed (required for `--live` flag).

**Solution**: Install sphinx-autobuild:

```bash
poetry add --group dev sphinx-autobuild
# or
pip install sphinx-autobuild
```

#### "Source directory 'docs' not found"

**Cause**: Documentation source directory doesn't exist.

**Solution**: Create the directory and add at least an `index.md`:

```bash
mkdir docs
echo "# My Documentation" > docs/index.md
```

Or configure a different source directory:

```toml
[tool.fairdm.docs]
source_dir = "documentation"  # Use your actual docs directory
```

#### "No pyproject.toml found"

**Cause**: `fairdm-docs` cannot locate your project's `pyproject.toml` file.

**How it searches**:

- Starts from the documentation source directory (usually `docs/`)
- Searches upward through parent directories until it finds `pyproject.toml`
- Stops at the filesystem root if not found

**Solution**:

1. Ensure `pyproject.toml` exists in your project root directory
2. Run `fairdm-docs build` from within your project (or any subdirectory)
3. Verify the file is named exactly `pyproject.toml` (lowercase, no typos)

```bash
cd /path/to/your/project
fairdm-docs build
```

#### Configuration validation errors

**Cause**: Invalid values in `[tool.fairdm.docs]` configuration.

**Solution**: Check error message for specific field and valid values:

- `port`: Must be between 1024 and 65535
- `verbosity`: Must be "full", "quiet", or "errors-only"
- `source_dir` and `build_dir`: Must be valid directory paths

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/FAIR-DM/fairdm-docs/issues)
2. Review the [examples/](examples/) directory for working configurations
3. Open a new issue with details about your setup and error message

## Migration from [tool.poetry]

1. **Add [project] section** to `pyproject.toml` with required `name` field
2. **Copy metadata** from `[tool.poetry]` to `[project]` (use PEP 621 format for authors)
3. **Move URLs** to `[project.urls]` table (keys are case-insensitive)
4. **Keep [tool.poetry]** if you're still using Poetry for dependency management (both sections can coexist)
5. **Test build**: Run `fairdm-docs build` to verify

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
