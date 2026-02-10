# Data Model: PEP 621 pyproject.toml Auto-Configuration

**Feature**: 001-pyproject-auto-config  
**Created**: 2026-02-10

## Entities

### ProjectMetadata

Represents project information extracted from PEP 621 `[project]` section in pyproject.toml.

**Attributes**:
- `name`: string (required) - Project name for documentation title
- `version`: string (optional, default: "0.0.0") - Project version number
- `authors`: list[string] (optional, default: ["Unknown"]) - List of author names
- `description`: string (optional, default: "") - Short project description
- `urls`: dict (optional) - URL mappings
  - `homepage`: string (optional, default: "") - Project homepage URL
  - `repository`: string (optional, default: "") - Git repository URL

**Validation Rules**:
- `name` is required (raise ConfigurationError if missing)
- `authors` can be strings in format "Name <email>" or just "Name"
- Extract name portion from author strings for copyright generation
- `version` cannot be dynamic (no `dynamic = ["version"]` support)
- All key lookups are case-insensitive (handle "Homepage", "homepage", "HOMEPAGE", etc.)

**Source**: `pyproject.toml` → `[project]` section

**Example**:
```toml
[project]
name = "my-fairdm-portal"
version = "1.2.3"
authors = [
    "Jane Doe <jane@example.com>",
    "John Smith"
]
description = "Research data portal for..."

[project.urls]
homepage = "https://github.com/org/my-portal"
repository = "https://github.com/org/my-portal"
```

---

### FairDMDocsConfig

Represents optional user configuration from `[tool.fairdm.docs]` section.

**Attributes**:
- `theme`: string (optional) - HTML theme name
  - Valid values: "sphinx_book_theme", "pydata_sphinx_theme"
  - Invalid values trigger warning and fallback to default

**Validation Rules**:
- Section is entirely optional (no warnings if missing)
- Unknown keys are ignored with DEBUG-level log
- Invalid theme values log warning and use default

**Source**: `pyproject.toml` → `[tool.fairdm.docs]` section

**Example**:
```toml
[tool.fairdm.docs]
theme = "pydata_sphinx_theme"
```

---

### ThemeConfig

Represents theme-specific Sphinx configuration.

**Attributes**:
- `theme_name`: string - Active theme identifier
- `theme_options`: dict - Theme-specific options
  - For sphinx_book_theme: repository_url, use_repository_button, use_issues_button, use_edit_page_button, home_page_in_toc, collapse_navbar, extra_footer
  - For pydata_sphinx_theme: github_url, navbar_end, icon_links
- `logo_path`: string - Path to logo file
- `favicon_path`: string - Path to favicon file

**Relationships**:
- Derived from ProjectMetadata.urls.repository (for GitHub integration)
- Derived from BrandingAssets paths
- Influenced by FairDMDocsConfig.theme

**Business Rules**:
- Theme options auto-configured based on detected theme
- Repository URL extracted from ProjectMetadata.urls
- Graceful degradation for custom themes (basic options only)

---

### BrandingAssets

Represents visual identity files with fallback chain.

**Attributes**:
- `logo_path`: string - Path to logo SVG
- `icon_path`: string - Path to icon/favicon SVG

**Fallback Chain**:
1. Project assets: `docs/_static/brand/logo.svg` and `icon.svg`
2. Package defaults: `fairdm_docs/_static/logo.svg` and `icon.svg`

**Validation Rules**:
- Check `Path.exists()` before using project assets
- Silently fall back to defaults if project assets missing
- Log warning if project assets exist but are unreadable/corrupted

**Source**: File system detection within docs directory (_static/brand/ subdirectory)

---

### ExtensionConfiguration

Represents Sphinx extension settings.

**Attributes**:
- `extensions`: list[string] - Enabled Sphinx extensions
- `myst_features`: list[string] - Enabled MyST parser features
- `autodoc_options`: dict - Autodoc configuration

**Defaults**:
- Core extensions: sphinx.ext.viewcode, sphinx.ext.intersphinx, sphinx.ext.napoleon, sphinx.ext.autosectionlabel
- MyST features: amsmath, dollarmath, colon_fence, deflist, attrs_inline, html_admonition, etc.
- Third-party: sphinx_copybutton, sphinxext.opengraph, sphinx_comments, sphinx_design, autodoc2

**Business Rules**:
- Extensions list is pre-configured (no user customization via pyproject.toml in MVP)
- MyST features enable modern Markdown syntax
- Autodoc excludes __weakref__ by default

---

## Entity Relationships

```
ProjectMetadata
  ├─> ThemeConfig.theme_options (repository URL)
  └─> copyright generation (authors + current year)

FairDMDocsConfig
  └─> ThemeConfig.theme_name (theme selection)

BrandingAssets
  ├─> ThemeConfig.logo_path
  └─> ThemeConfig.favicon_path

ThemeConfig
  └─> html_theme, html_theme_options (Sphinx config)

ExtensionConfiguration
  └─> extensions, myst_enable_extensions (Sphinx config)
```

## Configuration Precedence

```
User conf.py overrides (highest precedence)
  ↓
[tool.fairdm.docs] in pyproject.toml
  ↓
Package defaults in fairdm_docs/conf.py (lowest precedence)
```

## State Transitions

Not applicable - this is a configuration module with no runtime state changes. All values are computed once at import time.

## Data Validation

| Field | Validation | Error Handling |
|-------|------------|----------------|
| project.name | Required | Raise ConfigurationError |
| project.version | Optional, static only | Default "0.0.0", error if dynamic |
| project.authors | Optional | Default ["Unknown"] |
| [tool.fairdm.docs].theme | Optional, enum | Warn + fallback if invalid |
| Branding assets | Optional | Silent fallback to defaults |
| TOML syntax | Valid TOML | Raise ConfigurationError |
| File existence | pyproject.toml must exist | Raise ConfigurationError |
