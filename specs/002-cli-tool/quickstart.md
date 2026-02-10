# Quick Start Guide: FairDM-Docs CLI

**Feature**: FairDM-Docs CLI Tool  
**Audience**: Documentation contributors and maintainers  
**Prerequisites**: fairdm-docs package installed, Python 3.10+

## Installation

```bash
# Install/update fairdm-docs (includes CLI)
poetry add --group dev git+https://github.com/FAIR-DM/fairdm-docs

# Or with pip
pip install git+https://github.com/FAIR-DM/fairdm-docs
```

## Basic Usage

### Build Documentation

The simplest way to build your documentation:

```bash
fairdm-docs build
```

This command:
- Looks for documentation in `docs/` directory (your content: `.md`, `.rst` files)
- Builds HTML output to `docs/_build/html`
- Uses the package's built-in Sphinx configuration (no `conf.py` needed in your project)
- Displays full build output including warnings

**Expected output:**

```
📚 Building documentation...
Running Sphinx v8.1.0
loading pickled environment... done
building [mo]: targets for 0 po files that are out of date
building [html]: targets for 2 source files that are out of date
updating environment: 0 added, 1 changed, 0 removed
reading sources... [100%] index
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [100%] index
generating indices... genindex done
writing additional pages... search done
copying static files... done
copying extra files... done
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded.

✅ Build complete! Output: docs/_build/html
```

### Live Preview with Auto-Reload

For documentation authoring, start a live preview server:

```bash
fairdm-docs build --live
```

This command:
- Starts a development server on port 5000
- Opens documentation in your default browser
- Watches for file changes and rebuilds automatically
- Hot-reloads browser when changes detected

**Expected output:**

```
🔴 Starting live preview server on port 5000...
[sphinx-autobuild] > sphinx-build -b html docs docs/_build/html
[sphinx-autobuild] Running Sphinx v8.1.0
[sphinx-autobuild] build succeeded.
[sphinx-autobuild] Serving on http://127.0.0.1:5000
[sphinx-autobuild] Opening browser...

Watching for changes...
  (Press Ctrl+C to stop)
```

**Editing workflow:**
1. Edit `.md` or `.rst` files in `docs/`
2. Save changes
3. Browser automatically refreshes with updated content

**Stop server:**
Press `Ctrl+C` in terminal. Server shuts down gracefully.

### Validate Documentation

Check for broken links before publishing:

```bash
fairdm-docs check
```

This command:
- Validates all internal links (cross-references)
- Checks external URLs (with timeout)
- Reports broken links with file locations
- Exits with error code if issues found

**Expected output (success):**

```
✓ Checking documentation...
Running Sphinx linkcheck...
[linkcheck] Building... done.
[linkcheck] Checked 24 internal links: all valid
[linkcheck] Checked 15 external links: all valid

✅ No broken links found!
```

**Expected output (errors found):**

```
✓ Checking documentation...
Running Sphinx linkcheck...
[linkcheck] Building... done.

❌ Found 2 broken links:

  docs/api/reference.md:45
    https://example.com/missing-page
    → 404 Not Found

  docs/guide/install.md:12
    https://outdated-domain.com/docs
    → Timeout after 30s

Exit code: 1
```

## Configuration

### Zero Configuration

For standard FairDM projects, no configuration is needed:

```bash
# Just works if you have:
# - pyproject.toml in current/parent directory
# - Documentation source files in docs/ directory (*.md, *.rst)
# NO conf.py needed - the package provides it!
fairdm-docs build
```

### Custom Configuration

Create `[tool.fairdm.docs]` section in `pyproject.toml`:

```toml
[tool.fairdm.docs]
source_dir = "documentation"        # Custom source location
build_dir = "build/html"            # Custom output location
port = 5001                         # Custom live server port
verbosity = "quiet"                 # Output level: "full", "quiet", "errors-only"
```

**Configuration precedence:**  
User config (pyproject.toml) > Package defaults

## Common Scenarios

### Scenario 1: First-Time Setup

```bash
# 1. Navigate to your project
cd my-fairdm-project

# 2. Ensure pyproject.toml exists
ls pyproject.toml

# 3. Build docs
fairdm-docs build

# 4. Open in browser
open docs/_build/html/index.html
```

### Scenario 2: Documentation Development

```bash
# Start live server for iterative editing
fairdm-docs build --live

# Edit docs in your editor
# Save changes → browser auto-refreshes
# Repeat until satisfied

# Stop server when done (Ctrl+C)
```

### Scenario 3: Pre-Publish Validation

```bash
# Check for issues before committing
fairdm-docs check

# If errors found, fix them
# Re-check until clean
fairdm-docs check
# ✅ No broken links found!

# Safe to commit and publish
git add docs/
git commit -m "Update documentation"
```

### Scenario 4: CI/CD Integration

```yaml
# .github/workflows/docs.yml
name: Build Documentation

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Build documentation
        run: poetry run fairdm-docs build
      
      - name: Check for broken links
        run: poetry run fairdm-docs check
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: docs/_build/html/
```

## Troubleshooting

### Error: "pyproject.toml not found"

**Problem:** CLI requires a Python project with pyproject.toml

**Solution:**
```bash
# Ensure you're in project root
pwd
ls pyproject.toml

# Or create minimal pyproject.toml
cat > pyproject.toml << EOF
[tool.poetry]
name = "my-project"
version = "0.1.0"
EOF
```

### Error: "Source directory 'docs/' not found"

**Problem:** Default docs/ directory doesn't exist or is named differently

**Solution:**
```bash
# Option 1: Create docs/ directory
mkdir -p docs

# Option 2: Configure custom location in pyproject.toml
# [tool.fairdm.docs]
# source_dir = "documentation"  # or wherever your docs are
```

### Error: "Port 5000 already in use"

**Problem:** Another service is using port 5000 (common with Flask/Django)

**Solution:**
```toml
# In pyproject.toml
[tool.fairdm.docs]
port = 5001  # Or any available port 1024-65535
```

Then:
```bash
fairdm-docs build --live
# 🔴 Starting live preview server on port 5001...
```

### Build Warnings/Errors

**Problem:** Sphinx reports warnings or errors during build

**Solution:**
1. Review the specific error messages (shown in full by default)
2. Fix the issues in your documentation source files
3. Rebuild to verify fixes

Common issues:
- Missing cross-references: Update internal links
- Invalid RST/Markdown syntax: Fix formatting
- Missing image files: Add referenced images

### Advanced: Custom conf.py

**Question:** Can I override the package's configuration with my own `conf.py`?

**Answer:** Not in the initial CLI version. The CLI always uses the package's built-in configuration for consistency. 

For advanced customization:
- Override settings via `[tool.fairdm.docs]` in `pyproject.toml`
- For full Sphinx control, call `sphinx-build` directly instead of using the CLI

**Future:** Custom conf.py support may be added in a future version if there's demand.

## Next Steps

- Read the [Configuration Reference](../contracts/config-schema.toml) for all options
- See [CLI Interface](../contracts/cli-interface.md) for detailed command documentation
- Review [Data Model](../data-model.md) for understanding internal behavior

## Getting Help

- Check existing [GitHub Issues](https://github.com/FAIR-DM/fairdm-docs/issues)
- Review [fairdm-docs README](../../../../README.md)
- Ask in project discussions
