# Changelog

All notable changes to fairdm-docs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **The documentation title is now the declared project name, used verbatim.** It used to be
  reformatted for display — hyphens replaced with spaces and each word capitalized, so a project
  named `fairdm-docs` got the title `Fairdm Docs`. That reformatting guessed at a display form and
  got it wrong for any name with an acronym or deliberate casing of its own, so it is gone: the
  title is now exactly what `pyproject.toml` declares. A portal that wants a different title can
  still set `project` (or `html_title`) in its own `docs/conf.py`, after the
  `from fairdm_docs.conf import *` line.
- **Version reset to `0.0.1`.** Nothing was ever tagged, released or published, so the earlier
  numbers described intent rather than a released artefact. The package now works towards `0.1.0`
  and `1.0.0` milestones from a clean base, and `pyproject.toml` is the single source of truth for
  the version.
- **Minimum Python is now 3.12**, matching every project that consumes this package.
- **Toolchain moved to ruff** for linting and formatting, replacing black and isort. Type checking
  (`mypy`) and dependency checking (`deptry`) are now enforced.
- **Continuous integration added.** The release flow is wired up, and every pull request now runs:
  - the test suite
  - code quality checks
  - a security scan
  - a package build
- **Default branch renamed** from `master` to `main`.
- **`examples/` moved to `docs/examples/`.** It was a top-level directory holding documentation,
  which is what `docs/` is for.

### Removed

- The vendored Spec Kit tooling: `.specify/`, `.github/agents/`, `.github/prompts/` and
  `.github/instructions/`. The feature records it produced stay in `specs/`.

### Fixed

- `mypy` was configured with an unanchored `docs/` exclusion, which also matched the `fairdm_docs/`
  package directory and silently excluded the entire codebase from type checking.
- The documented lower bound for `port` was 1, while the code rejects anything below 1024.
- The README named the model documentation directive `autodoc-models`. It is `autodoc-model`.
- **pyproject.toml Search** - Fixed `conf.py` to search for `pyproject.toml` in the user's project directory instead of the installed package location
  - Now searches upward from the documentation source directory (typically `docs/`)
  - Correctly handles installation via Poetry/pip where package is in site-packages
  - Prevents `FileNotFoundError` when building documentation in other projects

### Added

- **CLI Tool (`fairdm-docs`)** - New command-line interface for simplified documentation workflows
  - `fairdm-docs build` - Build documentation with sensible defaults
  - `fairdm-docs build --live` - Live preview server with auto-reload and browser sync
  - `fairdm-docs check` - Validate documentation for broken links
- **Configuration System** - TOML-based configuration in `[tool.fairdm.docs]`
  - `source_dir` - Documentation source directory (default: "docs")
  - `build_dir` - Build output directory (default: "docs/_build/html")
  - `port` - Port for live server (default: 5000)
  - `verbosity` - Output level: "full", "quiet", or "errors-only" (default: "full")
  - `django` - Enable Django integration (default: false)
- **Zero-Configuration Workflow** - Build documentation without any configuration
- **Django Opt-In** - Django integration disabled by default, enable via `django = true`
- **Live Preview Server** - Real-time documentation preview with:
  - Auto-rebuild on file changes
  - Hot browser reload via websockets
  - Configurable port with availability checking
  - Graceful shutdown handling (Ctrl+C)
- **Link Validation** - Comprehensive link checking with:
  - Broken link detection (internal and external)
  - File and line number reporting
  - CI/CD friendly exit codes (0=success, 1=errors)
- **Comprehensive Testing** - 52 automated tests covering:
  - Configuration loading and validation
  - Build command functionality
  - Live server operation
  - Link validation
  - Error handling and user feedback
- **User Documentation** - Extensive README updates with:
  - CLI usage guide
  - Configuration reference
  - Django integration guide
  - Troubleshooting section
  - Multiple usage examples

### Changed

- Django is now opt-in via configuration instead of always enabled
- CLI provides clearer error messages with actionable guidance

### Technical

- Added dependencies: `typer` (CLI framework), `tomli` (Python <3.11 TOML support)
- New modules: `fairdm_docs/cli.py`, `fairdm_docs/config.py`
- Entry point: `fairdm-docs` command registered in `pyproject.toml`

## [0.2.0] - 2026-01-XX

### Breaking Changes

- **REQUIRED: PEP 621 [project] section** - Package now requires `[project]` section in `pyproject.toml` following PEP 621 standard
- **Python 3.11+ only** - Dropped Python 3.10 support (tomllib is now in standard library)
- Legacy `[tool.poetry]`-only metadata extraction is **no longer supported**

See [Migration Guide](#migration-from-toolpoetry-to-pep-621) below for upgrade instructions.

### Added

- **PEP 621 Auto-Configuration** - Full support for Python packaging standard metadata
  - Automatic extraction from `[project]` section in `pyproject.toml`
  - Required field: `name`
  - Optional fields: `version`, `description`, `authors`, `urls.*`
- **Case-Insensitive URL Handling** - Supports `Homepage`, `homepage`, `HOMEPAGE` variations in `[project.urls]`
- **Declarative Theme Configuration** - Use `[tool.fairdm.docs]` in `pyproject.toml`:
  ```toml
  [tool.fairdm.docs]
  theme = "pydata_sphinx_theme"
  ```
- **Smart Defaults** - Graceful handling of missing optional fields:
  - Missing `version` defaults to "0.0.0" (with warning)
  - Missing `authors` defaults to "Unknown" (with warning)
  - Missing `description` logs informational message
- **Configuration Precedence System** - Three-tier override hierarchy:
  1. `docs/conf.py` overrides (highest priority)
  2. `[tool.fairdm.docs]` in `pyproject.toml` (middle priority)
  3. Package defaults (lowest priority)
- **Comprehensive Examples** - New `examples/` directory with:
  - `basic_conf.md` - Minimal PEP 621 setup
  - `custom_theme_conf.md` - Declarative theme configuration
  - `fairdm_portal_conf.md` - Complete production portal example
- **Helper Functions** - Seven new internal functions for robust configuration:
  - `_normalize_key()` - Case-insensitive key normalization
  - `_get_case_insensitive()` - Case-insensitive dictionary lookup
  - `_load_pyproject()` - TOML loading with error handling
  - `_extract_project_metadata()` - PEP 621 metadata extraction
  - `_extract_fairdm_config()` - `[tool.fairdm.docs]` extraction
  - `_resolve_branding_assets()` - Branding detection with fallback chain
  - `_apply_theme_config()` - Theme-specific configuration

### Changed

- **Branding Path** - Updated from `../assets/img/brand/` to `docs/_static/brand/`
- **tomllib Import** - Simplified to Python 3.11+ standard library (removed `tomli` fallback)
- **Error Messages** - Improved validation messages with actionable migration guidance
- **Documentation** - Comprehensive README update documenting all PEP 621 features

### Removed

- **Python 3.10 Support** - Removed from `requires-python` and classifiers
- **tomli Fallback** - No longer needed with Python 3.11+ requirement
- **Legacy Poetry Extraction** - Projects must use PEP 621 `[project]` section

### Fixed

- Dynamic version handling for projects with `dynamic = ["version"]`
- Case-sensitivity issues with URL keys in `[project.urls]`
- Branding asset detection with correct fallback chain

## Migration from [tool.poetry] to PEP 621

If you're upgrading from v0.1.x, you **must** add a `[project]` section to your `pyproject.toml`.

### Before (v0.1.x - No longer supported)

```toml
[tool.poetry]
name = "my-fairdm-portal"
version = "1.0.0"
description = "My research data portal"
authors = ["Your Name <you@example.com>"]
```

### After (v0.2.0+ - Required)

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

# Keep [tool.poetry] for dependency management
[tool.poetry]
# ... your dependencies ...
```

### Migration Steps

1. **Add [project] section** with at minimum the `name` field
2. **Copy metadata** from `[tool.poetry]` to `[project]` (note: authors format is different in PEP 621)
3. **Move URLs** to `[project.urls]` table (keys are case-insensitive)
4. **Keep [tool.poetry]** if you're using Poetry for dependency management (both sections can coexist)
5. **Update Python** to 3.11+ if needed: `requires-python = ">=3.11"`
6. **Test build**: Run `sphinx-build docs docs/_build` to verify

### Why This Change?

- **Standards Compliance**: PEP 621 is the official Python packaging metadata standard
- **Build Backend Agnostic**: Works with Poetry, Hatch, PDM, setuptools, Flit, etc.
- **Ecosystem Alignment**: Matches what most Python tools expect
- **Simplified Code**: Eliminates legacy fallback logic

## [0.1.0] - 2025-11-26

### Added
- Complete package restructure and overhaul
- Comprehensive README.md with installation, usage, and customization guide
- Configuration examples in `examples/` directory:
  - Basic configuration
  - Custom theme configuration
  - With additional extensions
  - Complete FairDM portal example
- CONTRIBUTING.md with development guidelines
- AI coding agent instructions in `.github/instructions/`
- Examples README for easy navigation

### Changed
- **BREAKING**: Renamed package from `docs/` to `fairdm_docs/` to avoid namespace conflicts
- **BREAKING**: Import path changed from `from docs.conf import *` to `from fairdm_docs.conf import *`
- Migrated all `geoluminate_*` naming to `fairdm_*` throughout codebase
- Updated package metadata in `pyproject.toml`:
  - Repository URL to FAIR-DM organization
  - Version bumped from 0.0.1 to 0.1.0
  - Improved classifiers
  - Removed obsolete includes
- Updated project status from "Planning" to "Alpha"
- Improved code documentation and docstrings

### Removed
- Incomplete `modelinfo.py` extension
- Legacy `geoluminate` references
- Old minimal README content
- Commented-out code sections

### Fixed
- Branding detection now uses correct `fairdm_*` variable names
- Repository URLs now point to FAIR-DM organization
- Package structure now follows Python packaging best practices

## [0.0.1] - Previous

Initial release with basic Sphinx configuration extraction from pyproject.toml.
