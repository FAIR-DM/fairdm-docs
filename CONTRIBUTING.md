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
   uv sync
   ```
4. **Set up pre-commit hooks**:
   ```bash
   uv run pre-commit install
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
   uv add --dev /path/to/your/fairdm-docs
   cd docs
   uv run sphinx-build -b html . _build/html
   ```

4. **Format your code**:
   ```bash
   uv run ruff format fairdm_docs/
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

- Format and lint with `uv run ruff format .` and `uv run ruff check .` (88 columns).
- Use type hints. Types live in the annotations, not in docstrings.
- Docstrings and comments follow
  [docs/contributing/standards/code-documentation.md](docs/contributing/standards/code-documentation.md).

## Documentation Guidelines

### README Updates

When adding features, update the README.md:
- Add to the feature list
- Provide usage examples
- Update configuration reference if needed

### Code Comments

Comments explain why, never what. The full rules are in
[docs/contributing/standards/code-documentation.md](docs/contributing/standards/code-documentation.md).

### Examples

When adding new features, create an example in `docs/examples/`:
- Use descriptive filename (e.g., `custom_theme_conf.md`)
- Include complete working code
- Explain what the example demonstrates
- Show expected output or directory structure

## Testing

Tests follow [docs/contributing/standards/testing.md](docs/contributing/standards/testing.md):
what gets a test, the test-first cycle, test structure and the coverage floors. Run the full
suite with `uv run pytest -n auto --dist loadscope`.

### Build Testing

Always verify documentation builds successfully:

```bash
# In a test project
uv run sphinx-build -b html docs docs/_build/html

# Check for warnings
uv run sphinx-build -W -b html docs docs/_build/html
```

## Adding Dependencies

When adding new dependencies:

1. **Add to pyproject.toml**:
   ```bash
   uv add sphinx-new-extension
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
Add: PyData theme support via extras
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
- Added example in docs/examples/custom_css_conf.md

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
