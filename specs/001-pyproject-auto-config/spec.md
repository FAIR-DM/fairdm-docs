# Feature Specification: PEP 621 pyproject.toml Auto-Configuration

**Feature Branch**: `001-pyproject-auto-config`  
**Created**: 2026-02-10  
**Status**: Draft  
**Input**: User description: "Abstract away complexities in building Sphinx documentation site by auto-extracting config from pyproject.toml using PEP 621 standard, with smart defaults and error handling for two themes"

## Clarifications

### Session 2026-02-10

- Q: Legacy Format Support Strategy → A: Strict PEP 621 only - Raise error if only `[tool.poetry]` exists, force immediate migration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Zero-Config Documentation Setup (Priority: P1)

A portal developer creates a new FairDM portal and wants documentation without learning Sphinx configuration. They create a `docs/` directory with `conf.py` containing one line: `from fairdm_docs.conf import *`, then run `sphinx-build` and get fully-configured documentation with their project's name, version, authors, and repository link automatically populated.

**Why this priority**: This is the core value proposition - eliminating configuration overhead. Without this, the package has no purpose.

**Independent Test**: Create a minimal FairDM portal with only a `pyproject.toml` (PEP 621 format) and the one-line `conf.py`, run `sphinx-build`, verify the generated HTML contains correct project metadata and renders without errors.

**Acceptance Scenarios**:

1. **Given** a project with PEP 621 `pyproject.toml` containing `project.name`, `project.version`, `project.authors`, **When** user imports `fairdm_docs.conf`, **Then** Sphinx variables `project`, `version`, `copyright`, and `html_theme_options['repository_url']` are populated automatically
2. **Given** a project with minimal `pyproject.toml` (only `project.name`), **When** user builds docs, **Then** sensible defaults are used (version="0.0.0", authors="Unknown", etc.) with warning logs for missing optional fields
3. **Given** a project missing critical field `project.name`, **When** user builds docs, **Then** a descriptive `ConfigurationError` is raised explaining which field is required and where to add it

---

### User Story 2 - PEP 621 Standard Compliance (Priority: P2)

A developer migrates from Poetry's legacy `[tool.poetry]` format to the modern PEP 621 `[project]` standard. They update their `pyproject.toml` to use `[project]` sections, and their documentation continues working without changes to `conf.py`, with all metadata correctly extracted from the new standard format.

**Why this priority**: Supporting only PEP 621 ensures long-term maintainability and aligns with Python packaging standards. This is essential for future-proofing but can be implemented after core extraction works.

**Independent Test**: Create test projects with both legacy and PEP 621 formats, verify that PEP 621 extraction works correctly while legacy format either shows deprecation warnings or is not supported.

**Acceptance Scenarios**:

1. **Given** a `pyproject.toml` with `[project]` section (PEP 621), **When** `fairdm_docs.conf` extracts metadata, **Then** it reads from `project.name`, `project.version`, `project.authors`, `project.urls.homepage`, `project.urls.repository`
2. **Given** a `pyproject.toml` with only `[tool.poetry]` (legacy), **When** `fairdm_docs.conf` loads, **Then** a `ConfigurationError` is raised: "PEP 621 [project] section required. Legacy [tool.poetry] format is not supported. Please migrate: <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>"
3. **Given** a `pyproject.toml` missing both `[project]` and `[tool.poetry]`, **When** `fairdm_docs.conf` loads, **Then** a `ConfigurationError` is raised with guidance on creating a PEP 621 `[project]` section

---

### User Story 3 - Theme Selection and Configuration (Priority: P3)

A developer wants to use `pydata-sphinx-theme` instead of the default `sphinx-book-theme`. They add `pydata-sphinx-theme` to their dev dependencies and set `html_theme = "pydata_sphinx_theme"` in their `conf.py` after the import. The configuration automatically adapts theme-specific options (like navigation buttons and repository links) to work with the selected theme.

**Why this priority**: Theme flexibility is important for branding but not critical for MVP. Most users will use the default theme initially.

**Independent Test**: Create two test projects - one using `sphinx-book-theme` (default), one explicitly setting `pydata_sphinx_theme`. Build both and verify theme-specific options are correctly configured.

**Acceptance Scenarios**:

1. **Given** user imports `fairdm_docs.conf` without overriding `html_theme`, **When** docs build, **Then** `sphinx-book-theme` is used with pre-configured options for repository buttons, edit page links, and utterances comments
2. **Given** user sets `html_theme = "pydata_sphinx_theme"` after import, **When** docs build, **Then** theme-specific options compatible with PyData theme are applied (navigation links, GitHub integration)
3. **Given** user installs custom theme via dependencies, **When** user overrides `html_theme` to custom theme, **Then** basic Sphinx options are set but theme-specific options gracefully degrade (no errors)

---

### User Story 4 - Simple Configuration in pyproject.toml (Priority: P4)

A developer wants to configure documentation settings (like theme selection) without creating Python code in `conf.py`. They add a `[tool.fairdm.docs]` section to their `pyproject.toml` with settings like `theme = "pydata_sphinx_theme"`, and the documentation system respects these settings automatically, eliminating the need to override variables in `conf.py`.

**Why this priority**: This is a convenience feature that improves user experience for common customizations but isn't essential for MVP. Users can already override settings in `conf.py`, so this is about providing a more declarative, configuration-first approach that keeps settings alongside project metadata.

**Independent Test**: Create a project with `[tool.fairdm.docs]` section containing `theme = "pydata_sphinx_theme"`, import `fairdm_docs.conf` with no overrides in `conf.py`, verify the PyData theme is used instead of the default Book theme.

**Acceptance Scenarios**:

1. **Given** a `pyproject.toml` with `[tool.fairdm.docs]` containing `theme = "pydata_sphinx_theme"`, **When** user imports `fairdm_docs.conf` without overriding `html_theme`, **Then** PyData theme is used with appropriate theme-specific options
2. **Given** a `pyproject.toml` with `[tool.fairdm.docs]` settings and user overrides in `conf.py`, **When** docs build, **Then** `conf.py` overrides take precedence (Python code wins over TOML config)
3. **Given** a `pyproject.toml` without `[tool.fairdm.docs]` section, **When** docs build, **Then** defaults are used with no warnings (optional section)
4. **Given** invalid theme name in `[tool.fairdm.docs]`, **When** docs build, **Then** a warning is logged and default theme is used as fallback

---

### Edge Cases

- What happens when `pyproject.toml` file doesn't exist in `../pyproject.toml` relative to `docs/conf.py`?
- How does the system handle malformed TOML syntax?
- What if `project.authors` is empty array or has non-standard format?
- How to handle projects with multiple `project.urls` (homepage vs Homepage, repository vs Repository)?
- What if branding assets (`docs/_static/brand/logo.svg`) exist but are corrupted/invalid?
- How to handle `project.version` with dynamic versioning (e.g., `dynamic = ["version"]`)?
- What if `[tool.fairdm.docs]` contains unknown/unsupported configuration keys?
- How to handle conflicts between `[tool.fairdm.docs]` settings and `conf.py` overrides?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read `pyproject.toml` from `../pyproject.toml` relative to the directory containing the importing `conf.py`
- **FR-002**: System MUST extract metadata from PEP 621 `[project]` section: `name`, `version`, `authors`, `description`, `urls.homepage`, `urls.repository`
  - Key lookups MUST be case-insensitive (e.g., accept both "Homepage" and "homepage")
- **FR-003**: System MUST generate Sphinx configuration variables: `project` (string), `version` (string), `release` (string), `copyright` (string with year and authors), `html_theme_options['repository_url']` (string)
- **FR-004**: System MUST provide sensible defaults for optional fields:
  - `version`: "0.0.0" if missing
  - `authors`: ["Unknown"] if missing
  - `description`: "" (empty string) if missing
  - `urls.homepage`: "" if missing
- **FR-005**: System MUST raise descriptive `ConfigurationError` for missing critical fields:
  - `project.name`: "Missing required 'project.name' in pyproject.toml. Add [project]\nname = 'your-project-name'"
- **FR-005a**: System MUST raise `ConfigurationError` if `pyproject.toml` contains only `[tool.poetry]` (legacy format) without `[project]` section: "PEP 621 [project] section required. Legacy [tool.poetry] format is not supported. Please migrate: <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>"
- **FR-006**: System MUST log warnings for missing optional fields using Python's `logging` module at WARNING level
- **FR-007**: System MUST detect project branding assets at `_static/brand/` (within docs directory):
  - Check for `logo.svg` and `icon.svg`
  - Use project branding if found
  - Fallback to `fairdm_docs/_static/` defaults if not found
- **FR-008**: System MUST configure theme-specific options for `sphinx-book-theme` by default:
  - `repository_url`, `use_repository_button`, `use_issues_button`, `use_edit_page_button`, `home_page_in_toc`, `collapse_navbar`, `extra_footer` (CC license)
- **FR-009**: System MUST configure theme-specific options for `pydata-sphinx-theme` when selected:
  - `github_url`, `navbar_end`, `icon_links`
- **FR-010**: System MUST configure Sphinx extensions with sensible defaults:
  - Core extensions: `sphinx.ext.viewcode`, `sphinx.ext.intersphinx`, `sphinx.ext.napoleon`, `sphinx.ext.autosectionlabel`
  - MyST extensions: `myst_parser` with enabled features (amsmath, dollarmath, colon_fence, etc.)
  - Third-party: `sphinx_copybutton`, `sphinxext.opengraph`, `sphinx_comments`, `sphinx_design`, `autodoc2`
- **FR-011**: System MUST configure utterances-based comments with repository auto-detected from `project.urls.repository`
- **FR-012**: System MUST handle `tomllib.TOMLDecodeError` with descriptive message: "Invalid TOML syntax in pyproject.toml: {error_details}"
- **FR-013**: System MUST handle missing `pyproject.toml` file with descriptive error: "pyproject.toml not found at {expected_path}. Ensure it exists at repository root."
- **FR-014**: System MUST support both `project.urls.homepage` and `project.urls.repository`, preferring `repository` for GitHub integration features
- **FR-015**: System MUST parse `project.authors` as array of strings (format: `"Name <email>"` or `"Name"`) and extract names for copyright
- **FR-016**: System SHOULD read optional `[tool.fairdm.docs]` section from `pyproject.toml` for user configuration:
  - `theme`: String value for `html_theme` (e.g., "pydata_sphinx_theme", "sphinx_book_theme")
  - Additional configuration keys may be added in future versions
- **FR-017**: System MUST apply configuration precedence: `conf.py` overrides > `[tool.fairdm.docs]` > package defaults
- **FR-018**: System MUST validate `[tool.fairdm.docs].theme` against known themes (sphinx_book_theme, pydata_sphinx_theme):
  - If valid: apply theme and theme-specific options
  - If invalid: log warning "Unknown theme '{theme}' in [tool.fairdm.docs], using default sphinx_book_theme" and use default
- **FR-019**: System MUST ignore unknown keys in `[tool.fairdm.docs]` section with DEBUG-level log message

### Key Entities

- **Project Metadata**: Represents information extracted from `pyproject.toml` - name, version, authors list, description, URLs (homepage, repository)
- **FairDM Docs Configuration**: Represents optional user configuration from `[tool.fairdm.docs]` section - theme selection, future customization options
- **Theme Configuration**: Represents theme-specific settings - theme name, theme options dictionary, static paths, logo/favicon paths
- **Extension Configuration**: Represents Sphinx extension settings - enabled extensions list, MyST parser features, autodoc options
- **Branding Assets**: Represents visual identity files - logo path, icon path, with fallback chain (project assets → package defaults)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can create functional documentation with only a one-line `conf.py` import in under 1 minute (excluding Sphinx installation time)
- **SC-002**: All required Sphinx configuration variables are automatically populated from PEP 621 standard `pyproject.toml` without user intervention
- **SC-003**: Missing optional fields generate warning logs but do not block documentation build - builds succeed with sensible defaults
- **SC-004**: Missing critical fields (`project.name`) generate clear error messages that guide users to fix the issue in under 30 seconds
- **SC-005**: Users can switch between `sphinx-book-theme` and `pydata-sphinx-theme` with no configuration errors or broken features (via `conf.py` or `[tool.fairdm.docs]`)
- **SC-006**: Documentation builds succeed for projects following PEP 621 standard without requiring any Sphinx knowledge from the developer
- **SC-007**: Users can configure common settings (theme) in `pyproject.toml` without writing Python code, maintaining declarative configuration style

## Scope & Boundaries *(mandatory)*

### In Scope

- Automatic extraction from PEP 621 `[project]` section
- Optional `[tool.fairdm.docs]` configuration section for user customization
- Support for two official themes: `sphinx-book-theme` (default) and `pydata-sphinx-theme`
- Smart defaults for all optional fields
- Descriptive errors for missing critical fields
- Warning logs for missing optional fields
- Branding asset detection with fallback chain
- Pre-configured Sphinx extensions for modern documentation
- Utterances comment system configuration
- GitHub/repository integration features

### Out of Scope

- Support for legacy `[tool.poetry]` metadata format - strict PEP 621 requirement enforced with clear migration error message
- Custom theme support beyond the two official themes (users can override but theme-specific options not guaranteed)
- Dynamic version extraction from `__version__` or Git tags (must be static in `pyproject.toml`)
- Multilingual documentation configuration
- Custom Sphinx extension development (only configuration of existing extensions)
- PDF/LaTeX/EPUB output format customization (basic defaults provided)
- GitLab, Bitbucket, or non-GitHub repository integrations
- Advanced `[tool.fairdm.docs]` configuration beyond theme selection (future enhancement)

## Assumptions *(mandatory)*

- Users are using Python 3.10+ (PEP 621 is widely supported)
- Users have Poetry or pip managing their dependencies
- Project repository structure follows convention: `docs/` subdirectory with `pyproject.toml` at repository root
- Users are documenting Python projects (Django integration already present)
- Users want GitHub integration features (utterances comments, edit page buttons, issues links)
- Branding assets, if provided, are in SVG format at `docs/_static/brand/`
- Users accept MIT license for documentation tooling
- Default theme (sphinx-book-theme) is acceptable for 80%+ of users

## Dependencies

- **Python**: 3.10+ (for `tomllib` standard library)
- **Sphinx**: >=8.1
- **sphinx-book-theme**: >1.1 (default theme)
- **pydata-sphinx-theme**: >=0.16.1 (optional theme)
- **myst-parser**: >=4.0 (Markdown support)
- **Third-party extensions**: sphinx-copybutton, sphinx-design, sphinxext-opengraph, sphinx-comments, autodoc2, sphinxcontrib-bibtex

## Risks *(mandatory)*

- **Risk**: Projects still using `[tool.poetry]` will experience hard migration requirement  
  **Mitigation**: Provide clear error message with migration guide link, emphasize PEP 621 as Python packaging standard since 2021

- **Risk**: `tomllib` not available in Python <3.11 (though project requires 3.10+)  
  **Mitigation**: Use `tomli` backport for Python 3.10 if needed

- **Risk**: Dynamic versioning breaks simple extraction (e.g., `dynamic = ["version"]`)  
  **Mitigation**: Raise descriptive error asking users to use static version or implement `__version__` extraction in future

- **Risk**: Malformed author strings cause parsing errors  
  **Mitigation**: Use defensive parsing with try-except, fallback to raw string if parsing fails

- **Risk**: Theme-specific options clash when users switch themes  
  **Mitigation**: Provide separate option dictionaries per theme, auto-detect theme and apply correct options

- **Risk**: Branding asset paths are invalid/corrupted  
  **Mitigation**: Use `Path.exists()` check before using, catch image loading errors and fallback to defaults

- **Risk**: Configuration precedence confusion (pyproject.toml vs conf.py)  
  **Mitigation**: Document precedence clearly: conf.py always wins, log which source is being used for each setting at DEBUG level

- **Risk**: Invalid configuration in `[tool.fairdm.docs]` breaks documentation build  
  **Mitigation**: Validate all settings, fallback to defaults with warnings for invalid values, never raise errors for optional config section

## Notes

- Current implementation already extracts from `[tool.poetry]` - this feature migrates to PEP 621 standard
- Existing `fairdm_docs.conf` has Django-specific setup (`django.setup()`) - keep this for FairDM portal compatibility
- Configuration already supports both themes but lacks clear documentation on switching
- Utterances configuration already implemented but hardcoded - needs to be more flexible
- Consider adding `sphinx.util.logging.getLogger` for consistent Sphinx-style logging instead of Python's logging module
- `[tool.fairdm.docs]` section follows Python convention for tool-specific configuration (like `[tool.poetry]`, `[tool.black]`, etc.)
- Configuration precedence design allows gradual migration: start with defaults, customize via pyproject.toml, override in conf.py for complex cases
