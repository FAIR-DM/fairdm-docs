# Implementation Plan: PEP 621 pyproject.toml Auto-Configuration

**Branch**: `001-pyproject-auto-config` | **Date**: 2026-02-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-pyproject-auto-config/spec.md`

## Summary

Refactor `fairdm_docs/conf.py` to extract documentation configuration from PEP 621 standard `[project]` section in `pyproject.toml`, with optional `[tool.fairdm.docs]` customization, smart defaults for missing optional fields, and clear errors for missing critical fields. Support two official themes (sphinx-book-theme, pydata-sphinx-theme) with automatic theme-specific configuration.

**Primary requirement**: Zero-config documentation - users import one line and get fully-configured docs  
**Technical approach**: Read pyproject.toml with tomllib, extract PEP 621 metadata with case-insensitive key lookups, apply precedence chain (conf.py > [tool.fairdm.docs] > defaults), configure theme-specific options

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: 
- sphinx (>=8.1)
- myst-parser (>=4.0)
- sphinx-autobuild (>=2024.10)
- sphinx-autodoc2 (>=0.5)
- sphinx-comments (>=0.0.3)
- sphinx-copybutton (>=0.5)
- sphinx-design (>=0.6)
- sphinx-exec-code (>=0.16,<0.17)
- sphinxext-opengraph (>=0.9)
- sphinxcontrib-bibtex (>=2.6.3,<3.0.0)
- sphinx-book-theme (>1.1) - default
- pydata-sphinx-theme (>=0.16.1) - optional

**Storage**: File-based (pyproject.toml reading, branding asset detection at docs/_static/brand/)  
**Testing**: Manual testing with sample projects (minimal PEP 621, full metadata, theme variants)  
**Target Platform**: Cross-platform (Windows, Linux, macOS) - Python package  
**Project Type**: Single library (fairdm_docs package)  
**Performance Goals**: Configuration loading <100ms, file parsing <50ms  
**Constraints**: 
- Must not break existing users (backward compatibility)
- Must work with Django integration (keep django.setup())
- Must support both Poetry and pip package managers
- Must handle case variations in pyproject.toml keys (Homepage vs homepage)

**Scale/Scope**: Single configuration module refactor affecting ~350 lines in fairdm_docs/conf.py

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Convention Over Configuration ✅

**Compliance**: Feature core purpose - automatic metadata extraction from pyproject.toml with smart defaults

**Verification**: 
- FR-002: Extracts project metadata automatically
- FR-004: Provides defaults (version="0.0.0", authors=["Unknown"])
- No manual configuration required for basic usage

### II. Zero-Config Philosophy ✅

**Compliance**: Single import line (`from fairdm_docs.conf import *`) provides full functionality

**Verification**:
- US1: One-line conf.py creates working documentation
- SC-001: Functional docs in under 1 minute
- Abstracts Sphinx, MyST, theme complexities

### III. Backward Compatibility ⚠️ REQUIRES JUSTIFICATION

**Violation**: Legacy `[tool.poetry]` format support removed (strict PEP 621)

**Justification**: 
- PEP 621 is Python packaging standard since 2021 (5 years old)
- Current implementation already uses `[tool.poetry]` - this is **migration within same package**, not breaking external API
- Clear error message with migration guide provided (FR-005a)
- Users can migrate pyproject.toml before upgrading fairdm-docs version
- This is a **MINOR version bump** (0.1.0 → 0.2.0) with migration guide in CHANGELOG

**Mitigation**:
- Document migration path in CHANGELOG.md
- Provide example PEP 621 pyproject.toml in README
- Error message includes migration guide link

**Decision**: Acceptable - internal refactoring with clear migration path

### IV. Documentation-First ✅

**Compliance**: 
- Feature documented in spec.md with examples
- Will update README.md with PEP 621 examples (Phase 1)
- Error messages pre-written in spec (FR-005, FR-012, FR-013)

### V. Extensibility with Sensible Defaults ✅

**Compliance**:
- Two official themes supported
- `[tool.fairdm.docs]` allows TOML-based customization
- conf.py overrides still work (precedence chain FR-017)
- Unknown config keys ignored gracefully (FR-019)

**GATE STATUS**: ✅ PASS (with justified backward compatibility consideration)

## Project Structure

### Documentation (this feature)

```text
specs/001-pyproject-auto-config/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (SKIPPED)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── checklists/
    └── requirements.md  # Validation checklist
```

### Source Code (repository root)

```text
fairdm_docs/
├── __init__.py
├── conf.py              # PRIMARY: Refactor metadata extraction
├── _static/             # Default branding assets
│   ├── logo.svg
│   └── icon.svg
├── _templates/
│   └── model.md.jinja
└── extensions/
    ├── __init__.py
    ├── auto_django_model.py
    └── autodoc_models.py

examples/
├── basic_conf.md        # UPDATE: Show PEP 621 usage
├── custom_theme_conf.md # UPDATE: Add [tool.fairdm.docs] example
└── fairdm_portal_conf.md

tests/ (not in current structure - add if requested)
├── fixtures/
│   ├── minimal_pep621_pyproject.toml
│   ├── full_pep621_pyproject.toml
│   ├── legacy_poetry_pyproject.toml
│   └── fairdm_docs_config_pyproject.toml
└── test_conf_extraction.py

README.md                # UPDATE: PEP 621 examples
CHANGELOG.md             # UPDATE: Document breaking change
```

**Structure Decision**: Single project layout. Primary work in `fairdm_docs/conf.py`. Examples and documentation updates. Optional test fixtures if manual testing proves insufficient.

## Phase 0: Research (SKIPPED)

**Decision**: Skip Phase 0 research. All technical decisions are clear:

- ✅ PEP 621 standard documented: <https://packaging.python.org/en/latest/specifications/pyproject-toml/>
- ✅ tomllib available in Python 3.11+, tomli backport for 3.10 (already in use)
- ✅ Sphinx theme configuration patterns known (existing implementation)
- ✅ Configuration precedence pattern standard (env vars > config file > defaults)

**No unknowns requiring research**. Proceeding directly to Phase 1.

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](data-model.md) for detailed entity definitions:

- **ProjectMetadata**: name, version, authors[], description, urls{homepage, repository}
- **FairDMDocsConfig**: theme (optional)
- **ThemeConfig**: theme_name, theme_options{}, logo_path, favicon_path
- **BrandingAssets**: logo_path (with fallback chain), icon_path

### API Contracts

**Internal Module API** (no REST/GraphQL - this is a configuration module):

```python
# fairdm_docs/conf.py - Public exports (imported via `from fairdm_docs.conf import *`)

# Sphinx configuration variables (auto-populated)
project: str                    # From [project].name
version: str                    # From [project].version or "0.0.0"
release: str                    # Same as version
copyright: str                  # Generated from [project].authors + current year
authors: list[str]             # From [project].authors
language: str = "en"           # Default

html_theme: str                # From [tool.fairdm.docs].theme or "sphinx_book_theme"
html_theme_options: dict       # Theme-specific, auto-configured
html_static_path: list[str]    # ["_static"]
html_logo: str                 # Branding asset path or fallback
html_favicon: str              # Branding asset path or fallback

extensions: list[str]          # Pre-configured Sphinx extensions
myst_enable_extensions: list[str]  # MyST parser features

# Internal helper functions (not exported)
def _load_pyproject() -> dict
def _extract_project_metadata(data: dict) -> ProjectMetadata
def _extract_fairdm_config(data: dict) -> FairDMDocsConfig
def _resolve_branding_assets() -> BrandingAssets
def _apply_theme_config(theme: str, metadata: ProjectMetadata) -> dict
def _get_config_precedence(pyproject_config, module_defaults) -> dict
```

**Configuration Precedence**:
1. User's `conf.py` overrides (Python code after import)
2. `[tool.fairdm.docs]` section in pyproject.toml
3. Package defaults in `fairdm_docs/conf.py`

### Quickstart Guide

See [quickstart.md](quickstart.md) for user-facing setup instructions.

Key steps:
1. Install: `poetry add --group dev fairdm-docs`
2. Create `docs/conf.py` with one line: `from fairdm_docs.conf import *`
3. Ensure `pyproject.toml` has `[project]` section with `name`
4. Run: `sphinx-build docs docs/_build/html`

## Testing Strategy

**Manual Testing Approach** (no automated tests in current structure):

Create test fixtures in `specs/001-pyproject-auto-config/fixtures/`:

1. **minimal_pyproject.toml**: Only `[project]` with `name`
2. **full_pyproject.toml**: All PEP 621 fields populated
3. **fairdm_config_pyproject.toml**: With `[tool.fairdm.docs]` section
4. **legacy_pyproject.toml**: Only `[tool.poetry]` (should error)
5. **no_project_pyproject.toml**: Missing both sections (should error)

**Test Procedure**:
1. Create minimal docs/ directory with test fixture as pyproject.toml
2. Create conf.py with `from fairdm_docs.conf import *`
3. Run `sphinx-build` and verify output
4. Check HTML contains correct metadata
5. Verify appropriate warnings/errors logged

**Test Matrix**:

| Fixture | Expected Result |
|---------|-----------------|
| minimal | Success with defaults, warnings for missing optional fields |
| full | Success with all metadata populated |
| fairdm_config | Success with pydata theme applied |
| legacy | ConfigurationError with migration message |
| no_project | ConfigurationError requesting [project] section |

## Risk Mitigation

### Risk: Configuration precedence confusion

**Mitigation**: 
- Add DEBUG-level logging showing config source for each setting
- Document precedence clearly in docstrings
- Show examples in README

### Risk: Theme options clash when switching

**Mitigation**:
- Separate theme option dictionaries per theme
- Auto-detect theme before applying options
- Test both themes in fixture matrix

### Risk: Dynamic versioning breaks extraction

**Mitigation**:
- Detect `dynamic = ["version"]` in pyproject.toml
- Raise clear error: "Dynamic versioning not supported. Set static version in [project].version"
- Document requirement in README

## Definition of Done

- [ ] All functional requirements (FR-001 through FR-019) implemented
- [ ] Constitution principles validated (zero-config, convention over configuration)
- [ ] All 4 user stories testable and demonstrated
- [ ] Test matrix passes (5 fixtures)
- [ ] README.md updated with PEP 621 examples
- [ ] CHANGELOG.md documents migration from [tool.poetry]
- [ ] examples/ directory updated
- [ ] quickstart.md created
- [ ] No breaking changes to public API (conf.py variables)
- [ ] Error messages match spec exactly (FR-005, FR-005a, FR-012, FR-013, FR-018)

## Next Steps

1. Review and approve this implementation plan
2. Run `/speckit.tasks` to generate detailed task breakdown
3. Begin Phase 2.1 implementation (core metadata extraction)
4. Test with fixtures after each phase
5. Update documentation incrementally

**Estimated Effort**: 
- Phase 2.1-2.2: 4-6 hours (core extraction + themes)
- Phase 2.3-2.4: 2-3 hours (optional config + branding)
- Phase 2.5: 2-3 hours (documentation)
- Phase 2.6: 1-2 hours (legacy handling)
- **Total**: ~10-14 hours development + testing
