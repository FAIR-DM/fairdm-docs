---
applyTo: '**/*'
---

# FairDM-Docs — AI Coding Agent Instructions

## Package Overview

**fairdm-docs** is a reusable Sphinx configuration package that standardizes documentation across FairDM-powered research data portals. It provides zero-config documentation setup by automatically extracting metadata from `pyproject.toml` and offering pre-configured themes, extensions, and custom directives for Django models.

## Core Principles

- **Convention over configuration**: Provide sensible defaults that work out-of-the-box
- **Metadata extraction**: Read from `pyproject.toml` to avoid duplication
- **Extensibility**: Allow easy customization through standard Python imports and overrides
- **Documentation quality**: Maintain comprehensive examples and clear documentation

## Project Structure

```
fairdm-docs/
├── fairdm_docs/              # Main package (NOT 'docs/')
│   ├── __init__.py
│   ├── cli.py               # CLI tool with Typer
│   ├── conf.py              # Base Sphinx configuration
│   ├── config.py            # Configuration loading from pyproject.toml
│   ├── utils.py             # Shared utilities (pyproject finding/loading)
│   ├── _static/             # Default branding assets
│   │   ├── logo.svg
│   │   └── icon.svg
│   ├── _templates/          # Jinja2 templates for model documentation
│   │   └── model.md.jinja   # Template for rendering Django models
│   └── extensions/          # Custom Sphinx extensions
│       ├── __init__.py
│       └── autodoc_models.py  # Jinja2-based Django model documentation
├── examples/                # Configuration examples
├── pyproject.toml
├── README.md
└── LICENSE
```

## Key Files

### `fairdm_docs/conf.py`

This is the core configuration file that:
- Reads metadata from `../pyproject.toml` using `tomllib`
- Configures Sphinx extensions, theme, and behavior
- Sets up automatic branding detection
- Provides sensible defaults for all settings

**Important naming conventions**:
- Use `fairdm_*` prefix for package-specific variables (e.g., `fairdm_docs_static`, `fairdm_project_brand`)
- Never use legacy `geoluminate_*` naming

### `fairdm_docs/utils.py`

Shared utility functions for the package.

**Key functions**:
- `find_pyproject_toml()`: Searches upward for pyproject.toml
- `load_pyproject_toml()`: Loads and parses TOML file
- Handles both standard search and environment variable-based search (for Sphinx context)

### `fairdm_docs/cli.py`

Command-line interface built with Typer.

**Key features**:
- `build` command: Build docs or start live preview server
- `check` command: Validate documentation for broken links
- Sets environment variables for Sphinx context
- Port availability checking
- Comprehensive error handling

### `fairdm_docs/config.py`

Configuration loading and validation from pyproject.toml.

**Key features**:
- `BuildConfiguration` dataclass with sensible defaults
- Reads `[tool.fairdm.docs]` section
- Validates configuration values
- Error messages with actionable guidance

### `fairdm_docs/extensions/autodoc_models.py`

Jinja2-based extension that provides the `{autodoc-model}` directive for documenting Django models from the FairDM registry.

**Key features**:
- Uses Jinja2 templates from `fairdm_docs/_templates/`
- Receives only a Django model class as context
- Renders complete model documentation including fields, relationships, and methods
- Auto-generates index files for samples and measurements

## Development Guidelines

### Code Style

- Follow PEP 8 with 120 character line length
- Use Black for formatting
- Type hints where appropriate
- Comprehensive docstrings for all public functions

### Configuration Philosophy

1. **Auto-extraction first**: Always try to extract from `pyproject.toml`
2. **Sensible defaults**: Provide working defaults for all settings
3. **Easy overrides**: Allow users to override any setting in their `conf.py`
4. **No surprises**: Changes should be backward compatible

### Adding New Features

When adding new features:

1. **Check pyproject.toml first**: Can the information be extracted automatically?
2. **Document in README**: Update README.md with usage examples
3. **Add example**: Create an example in `examples/` directory
4. **Update conf.py**: Ensure default configuration is sensible
5. **Test with real project**: Verify it works with actual FairDM portals

### Extension Development

When creating or modifying Sphinx extensions:

- Follow Sphinx extension conventions
- Use proper logging via `sphinx.util.logging.getLogger`
- Handle errors gracefully with helpful messages
- Document the directive usage in README
- Ensure Django apps are properly initialized

### Testing Changes

Before committing changes:

1. Test with a minimal `conf.py` (just `from fairdm_docs.conf import *`)
2. Test with custom overrides
3. Verify builds succeed with `sphinx-build`
4. Check that auto-generated docs render correctly
5. Validate that branding detection works

## Dependencies

### Core Dependencies

- **sphinx** (>=8.1): Documentation engine
- **myst-parser** (>=4.0): Markdown support
- **sphinx-autobuild** (>=2024.10): Live reloading
- **sphinx-autodoc2** (>=0.5): Modern API docs
- **sphinx-copybutton** (>=0.5): Code copy buttons
- **sphinx-design** (>=0.6): UI components
- **sphinx-comments** (>=0.0.3): Utterances integration
- **sphinxext-opengraph** (>=0.9): Social media cards
- **sphinxcontrib-bibtex** (^2.6.3): Citations

### Optional Dependencies (via extras)

- **pydata-sphinx-theme**: Alternative theme
- **sphinx-book-theme**: Default theme

### Development Dependencies

- **black**: Code formatting (120 line length)
- **invoke**: Task automation
- **pre-commit**: Git hooks

## Common Tasks

### Updating Theme Configuration

When modifying `html_theme_options`:
- Document all available options in README
- Provide sensible defaults
- Show override examples in `examples/`

### Adding Extensions

When adding new Sphinx extensions:
1. Add to `dependencies` in `pyproject.toml`
2. Add to `extensions` list in `conf.py`
3. Configure with sensible defaults
4. Document in README with example
5. Update classifiers if needed

### Metadata Extraction

When extracting new metadata from `pyproject.toml`:
```python
with open("../pyproject.toml", "rb") as f:
    data = tomllib.load(f)

package_meta = data["tool"]["poetry"]
value = package_meta.get("key", "default_value")
```

## Versioning

Follow semantic versioning:
- **MAJOR**: Breaking changes to configuration API
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, documentation updates

Current version: `0.3.0` (unreleased - includes CLI tool)

## Package Distribution

The package is distributed via Git:
```bash
poetry add --group dev git+https://github.com/FAIR-DM/fairdm-docs
```

No PyPI distribution planned at this time.

## Integration with FairDM

This package is designed to work seamlessly with FairDM portals:

- Imports `fairdm.registry` for model documentation
- Understands FairDM model structure (Sample, Measurement)
- Provides auto-documentation for registered models
- Follows FairDM naming conventions

## Documentation Standards

### README.md

The README should contain:
- Clear overview and feature list
- Installation instructions
- Quick start guide
- Feature documentation
- Customization examples
- Configuration reference
- Contributing guidelines

### Examples

Each example should:
- Have a descriptive filename
- Include complete, working code
- Explain what it demonstrates
- Show expected output or structure

### Inline Documentation

- Use docstrings for all public functions and classes
- Include type hints
- Explain parameters and return values
- Provide usage examples in docstrings

## Anti-patterns to Avoid

❌ **Don't**: Hard-code project-specific values
✅ **Do**: Extract from `pyproject.toml` or allow overrides

❌ **Don't**: Use `geoluminate_*` naming
✅ **Do**: Use `fairdm_*` naming

❌ **Don't**: Assume directory structure
✅ **Do**: Use relative paths from `conf.py` location

❌ **Don't**: Silently fail
✅ **Do**: Log warnings and provide helpful error messages

❌ **Don't**: Make breaking changes without major version bump
✅ **Do**: Maintain backward compatibility

## Future Enhancements

Potential improvements to consider:

- [ ] Add CLI tool for initializing docs structure
- [ ] Create project templates for different portal types
- [ ] Add automated tests for extension functionality
- [ ] Support for multiple Sphinx builders (PDF, ePub)
- [ ] Integration with RTD/GitHub Pages deployment
- [ ] Custom CSS themes for different research domains
- [ ] Automated changelog generation from commits

## Getting Help

When working with this package:
- Check the examples/ directory first
- Review README.md for configuration options
- Look at fairdm-docs usage in actual FairDM portals
- Test changes with minimal and complex configurations
