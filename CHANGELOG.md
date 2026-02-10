# Changelog

All notable changes to fairdm-docs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
