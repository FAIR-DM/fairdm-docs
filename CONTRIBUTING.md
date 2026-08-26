# Contributing to FairDM-Docs

Thank you for your interest in contributing to fairdm-docs! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/fairdm-docs.git
   cd fairdm-docs
   ```
3. **Install dependencies**:
   ```bash
   poetry install
   ```
4. **Set up pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Test your changes** with a real FairDM project:
   ```bash
   # In a test project
   poetry add --group dev /path/to/your/fairdm-docs
   cd docs
   poetry run sphinx-build -b html . _build/html
   ```

4. **Format your code**:
   ```bash
   poetry run black fairdm_docs/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** on GitHub

## Code Style Guidelines

- Follow **PEP 8** conventions
- Use **Black** for formatting (120 character line length)
- Use **type hints** where appropriate
- Write **comprehensive docstrings** for all public functions and classes
- Keep functions focused and modular

### Example Function Style

```python
def extract_metadata(toml_path: str) -> dict[str, Any]:
    """
    Extract project metadata from pyproject.toml file.

    Args:
        toml_path: Path to the pyproject.toml file

    Returns:
        Dictionary containing project metadata

    Raises:
        FileNotFoundError: If toml_path doesn't exist
        tomllib.TOMLDecodeError: If file is not valid TOML

    Example:
        >>> metadata = extract_metadata("../pyproject.toml")
        >>> metadata["name"]
        'my-project'
    """
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    return data.get("tool", {}).get("poetry", {})
```

## Documentation Guidelines

### README Updates

When adding features, update the README.md:
- Add to the feature list
- Provide usage examples
- Update configuration reference if needed

### Code Comments

- Use comments to explain **why**, not **what**
- Keep comments up-to-date with code changes
- Use docstrings for public APIs

### Examples

When adding new features, create an example in `examples/`:
- Use descriptive filename (e.g., `custom_theme_conf.md`)
- Include complete working code
- Explain what the example demonstrates
- Show expected output or directory structure

## Testing

### Manual Testing

Since this is a documentation package, testing involves:

1. **Test with minimal config**:
   ```python
   from fairdm_docs.conf import *
   ```

2. **Test with overrides**:
   ```python
   from fairdm_docs.conf import *
   html_theme = "pydata_sphinx_theme"
   ```

3. **Test extension functionality**:
   - Verify auto-generation of data model docs
   - Check that directive renders correctly
   - Ensure Django integration works

4. **Test branding detection**:
   - With project branding present
   - Without project branding (fallback)

### Build Testing

Always verify documentation builds successfully:

```bash
# In a test project
poetry run sphinx-build -b html docs docs/_build/html

# Check for warnings
poetry run sphinx-build -W -b html docs docs/_build/html
```

## Adding Dependencies

When adding new dependencies:

1. **Add to pyproject.toml**:
   ```bash
   poetry add sphinx-new-extension
   ```

2. **Update README.md** to document the new feature

3. **Add to conf.py** if it's a Sphinx extension

4. **Update classifiers** if appropriate

## Commit Message Guidelines

Use clear, descriptive commit messages:

- **Add**: New features or files
- **Update**: Changes to existing functionality
- **Fix**: Bug fixes
- **Remove**: Deleted features or files
- **Refactor**: Code restructuring without behavior change
- **Docs**: Documentation-only changes

Examples:
```
Add: PyData theme support via poetry extras
Update: Migrate all geoluminate references to fairdm
Fix: Branding detection fallback path
Remove: Incomplete modelinfo extension
Docs: Add examples for custom theme configuration
```

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All files formatted with Black
- [ ] Documentation updated (README, examples)
- [ ] Changes tested with real project
- [ ] Commit messages are clear
- [ ] No unrelated changes included

### PR Description

Include in your pull request:

1. **What changed**: Brief description
2. **Why**: Rationale for the change
3. **Testing**: How you tested it
4. **Breaking changes**: If any
5. **Related issues**: Link to issues if applicable

### Example PR Description

```markdown
## Add Support for Custom CSS Files

### What Changed
- Added `html_css_files` configuration to conf.py
- Updated README with CSS customization example
- Added example in examples/custom_css_conf.md

### Why
Users need ability to add custom styling without overriding entire theme.

### Testing
- Tested with custom.css in test project
- Verified CSS loads correctly in built docs
- Checked no conflicts with theme CSS

### Breaking Changes
None - backward compatible addition
```

## Code Review Process

1. Maintainer reviews your PR
2. Address any feedback or requested changes
3. Once approved, maintainer merges your PR
4. Your contribution is included in next release!

## Questions or Issues?

- **Questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue with reproducible example
- **Feature requests**: Open a GitHub Issue describing the use case

## License

By contributing to fairdm-docs, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub Contributors page
- Release notes for version they contributed to

Thank you for contributing to FairDM-Docs! 🎉
