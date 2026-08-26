# CLI Usage Examples

Comprehensive examples for using the `fairdm-docs` command-line tool.

## Basic Usage

### Zero-Configuration Build

The simplest way to build documentation - no configuration required:

```bash
cd your-project
fairdm-docs build
```

**Requirements:**
- `pyproject.toml` in project root (can be empty)
- `docs/` directory with at least `index.md`

**Output:** `docs/_build/html/`

### Live Preview During Development

Start a live-reloading server for real-time preview:

```bash
fairdm-docs build --live
```

This will:
1. Build your documentation
2. Start a web server on http://localhost:5000
3. Open your browser automatically
4. Watch for file changes
5. Rebuild and reload browser on changes

Press `Ctrl+C` to stop the server.

### Validate Documentation Links

Check all links before publishing:

```bash
fairdm-docs check
```

**Exit codes:**
- `0` - All links valid
- `1` - Broken links found

Use in CI/CD pipelines to catch broken links early.

## Configuration Examples

### Custom Directories

Configure non-standard directory structure:

```toml
# pyproject.toml
[tool.fairdm.docs]
source_dir = "documentation"  # Instead of "docs"
build_dir = "public"          # Instead of "docs/_build/html"
```

### Custom Port for Live Server

If port 5000 is in use:

```toml
# pyproject.toml
[tool.fairdm.docs]
port = 8080
```

Then run:
```bash
fairdm-docs build --live  # Opens on http://localhost:8080
```

### Verbosity Control

#### Quiet Mode (CI/CD)

Minimal output, only warnings and errors:

```toml
# pyproject.toml
[tool.fairdm.docs]
verbosity = "quiet"
```

```bash
fairdm-docs build
# Output:
# 📚 Building documentation...
# ✅ Build complete! Output: docs/_build/html
```

#### Errors Only

Show only critical errors:

```toml
# pyproject.toml
[tool.fairdm.docs]
verbosity = "errors-only"
```

#### Full Verbose Output (Default)

Show all Sphinx build output:

```toml
# pyproject.toml
[tool.fairdm.docs]
verbosity = "full"  # This is the default
```

### Django Integration

Enable Django model documentation:

```toml
# pyproject.toml
[tool.fairdm.docs]
django = true
```

**Requirements when `django = true`:**
- Django must be installed: `poetry add Django`
- Django settings must be configured (via `DJANGO_SETTINGS_MODULE`)

**Without Django:**
```toml
[tool.fairdm.docs]
django = false  # Default - no Django dependency required
```

## Workflow Examples

### Development Workflow

```bash
# 1. Start live preview
fairdm-docs build --live

# 2. Edit documentation in your editor
# - Server automatically rebuilds
# - Browser auto-reloads

# 3. Press Ctrl+C when done
```

### Pre-Commit Hook

Validate links before committing:

```bash
# .git/hooks/pre-commit
#!/bin/bash
fairdm-docs check || {
    echo "❌ Broken links found! Fix before committing."
    exit 1
}
```

### CI/CD Pipeline

#### GitHub Actions

```yaml
# .github/workflows/docs.yml
name: Documentation

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install --with dev

      - name: Build documentation
        run: poetry run fairdm-docs build

      - name: Validate links
        run: poetry run fairdm-docs check

      - name: Upload documentation
        uses: actions/upload-artifact@v4
        with:
          name: documentation
          path: docs/_build/html
```

#### GitLab CI

```yaml
# .gitlab-ci.yml
docs:
  image: python:3.11
  script:
    - pip install poetry
    - poetry install --with dev
    - poetry run fairdm-docs build
    - poetry run fairdm-docs check
  artifacts:
    paths:
      - docs/_build/html
```

### Local Testing Workflow

```bash
# 1. Clean build
rm -rf docs/_build

# 2. Build documentation
fairdm-docs build

# 3. Validate links
fairdm-docs check

# 4. Preview in browser
python -m http.server -d docs/_build/html 8000
# Visit http://localhost:8000
```

## Advanced Scenarios

### Multiple Documentation Sets

Use different configurations for different doc sets:

```bash
# Main documentation
fairdm-docs build

# API reference (custom source)
fairdm-docs build --source-dir api-docs --build-dir docs/_build/api
```

**Note:** Currently source/build dirs are configured via `pyproject.toml` only.
Command-line flags for these options may be added in a future release.

### Port Conflict Resolution

If you get "Port 5000 is already in use":

1. **Option 1:** Find and stop the service using port 5000
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F

   # Linux/Mac
   lsof -i :5000
   kill <PID>
   ```

2. **Option 2:** Use a different port
   ```toml
   [tool.fairdm.docs]
   port = 8080
   ```

### Debugging Build Issues

Enable full Sphinx output:

```toml
# pyproject.toml
[tool.fairdm.docs]
verbosity = "full"
```

Then build:
```bash
fairdm-docs build
# You'll see all Sphinx warnings, info, and debug messages
```

## Comparison: CLI vs Direct Sphinx

### Before (Direct Sphinx)

```bash
sphinx-build -b html -c path/to/conf.py docs docs/_build/html
sphinx-autobuild --port 5000 docs docs/_build/html
sphinx-build -b linkcheck docs docs/_build/linkcheck
```

### After (fairdm-docs CLI)

```bash
fairdm-docs build
fairdm-docs build --live
fairdm-docs check
```

**Benefits:**
- ✅ No need to remember Sphinx arguments
- ✅ Consistent configuration via `pyproject.toml`
- ✅ Sensible defaults out of the box
- ✅ Clear error messages
- ✅ Auto-detects project structure

## Common Patterns

### Documentation-Only Projects

For projects that are just documentation (no Python code):

```toml
# pyproject.toml
[project]
name = "my-docs"
version = "1.0.0"

[tool.fairdm.docs]
# No special configuration needed
```

```bash
fairdm-docs build --live
```

### Django Project Documentation

For FairDM portals and Django projects:

```toml
# pyproject.toml
[project]
name = "my-portal"
version = "0.1.0"

[tool.fairdm.docs]
django = true  # Enable Django model auto-documentation
```

```bash
# Make sure Django is installed
poetry add Django

# Set Django settings
export DJANGO_SETTINGS_MODULE=myproject.settings

# Build
fairdm-docs build
```

### Monorepo with Multiple Doc Sets

Structure:
```
project/
├── pyproject.toml
├── docs/           # Main docs
├── api-docs/       # API reference
└── guides/         # User guides
```

Build each set separately by temporarily changing config:

```toml
# For main docs (default)
[tool.fairdm.docs]
source_dir = "docs"
build_dir = "docs/_build/html"
```

Then manually build others:
```bash
# This requires changing pyproject.toml each time
# OR using separate config files (future enhancement)
```

## Tips and Best Practices

1. **Use `--live` during writing** - See changes immediately
2. **Run `check` before pushing** - Catch broken links early
3. **Use `quiet` in CI** - Reduce log noise
4. **Keep port configurable** - Different developers may need different ports
5. **Document your setup** - Add a README note about `django = true` if needed
6. **Use version control** - Commit `pyproject.toml` configuration
7. **Test locally first** - Run build + check before CI/CD
8. **Monitor build times** - Use `time fairdm-docs build` to track performance

## Getting Help

- **Error messages** - Read carefully, they include fix suggestions
- **Troubleshooting** - See main [README.md](../../README.md#troubleshooting)
- **Examples** - Check [examples/](.) for configuration samples
- **Issues** - Report bugs at [GitHub Issues](https://github.com/FAIR-DM/fairdm-docs/issues)
