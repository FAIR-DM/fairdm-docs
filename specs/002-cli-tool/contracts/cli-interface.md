# CLI Interface Contract

**Feature**: FairDM-Docs CLI Tool  
**Version**: 1.0.0  
**Entry Point**: `fairdm-docs`

## Command Reference

### `fairdm-docs build`

Build Sphinx documentation with sensible defaults.

**Signature:**
```bash
fairdm-docs build [--live]
```

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--live` | boolean | `false` | Start live preview server with auto-reload |
| `--help` | boolean | N/A | Show command help and exit |

**Behavior:**

1. **Configuration Loading**:
   - Search for `pyproject.toml` in current directory and parents
   - Load `[tool.fairdm.docs]` section if present
   - Merge user config with defaults (user values take precedence)
   - Validate configuration values

2. **Build Process** (when `--live` is false):
   - Invoke `sphinx.cmd.build.main()` with:
     - Builder: `html`
     - Source: `config.source_dir`
     - Output: `config.build_dir`
     - Config dir: Directory containing `fairdm_docs.conf`
   - Stream all Sphinx output to console (respects verbosity setting)
   - Exit with Sphinx's exit code (0 = success, non-zero = errors)

3. **Live Server Process** (when `--live` is true):
   - Check if port is available
   - If unavailable: Error with configuration guidance
   - Start `sphinx-autobuild` subprocess:
     - Source: `config.source_dir`
     - Output: `config.build_dir`
     - Port: `config.port`
     - Auto-open browser
   - Watch for file changes
   - Handle Ctrl+C for graceful shutdown

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Build succeeded |
| 1 | Configuration error, port conflict, or missing pyproject.toml |
| Non-zero | Sphinx build failed (code from Sphinx) |

**Examples:**

```bash
# Basic build
$ fairdm-docs build
📚 Building documentation...
Running Sphinx v8.1.0
...
build succeeded.
✅ Build complete! Output: docs/_build/html

# Live preview
$ fairdm-docs build --live
🔴 Starting live preview server on port 5000...
[sphinx-autobuild] Serving on http://127.0.0.1:5000
[sphinx-autobuild] Opening browser...
Watching for changes...
  (Press Ctrl+C to stop)
```

**Error Examples:**

```bash
# No pyproject.toml
$ fairdm-docs build
❌ Error: No pyproject.toml found.
   fairdm-docs requires a Python project with pyproject.toml.
   Run this command from your project root directory.

# Missing source directory
$ fairdm-docs build
❌ Error: Source directory 'docs/' not found.
   Specify source directory in pyproject.toml:

   [tool.fairdm.docs]
   source_dir = "path/to/docs"

# Port conflict
$ fairdm-docs build --live
❌ Error: Port 5000 is already in use.
   Configure a different port in pyproject.toml:

   [tool.fairdm.docs]
   port = 5001
```

---

### `fairdm-docs check`

Validate documentation for broken links and quality issues.

**Signature:**
```bash
fairdm-docs check
```

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--help` | boolean | N/A | Show command help and exit |

**Behavior:**

1. **Configuration Loading**: Same as `build` command

2. **Validation Process**:
   - Run Link Validator (Sphinx linkcheck builder):
     - Invoke `sphinx.cmd.build.main()` with builder `linkcheck`
     - Check all internal links (cross-references)
     - Check all external URLs (with timeout)
   - Parse linkcheck output for broken links
   - Format results with file locations and error details
   - Aggregate error count

3. **Result Reporting**:
   - Success: Display summary of checks performed
   - Errors: Display each broken link with:
     - File path and line number
     - URL that failed
     - Error reason (404, timeout, etc.)
   - Exit with code 0 if no errors, 1 if errors found

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | All validations passed |
| 1 | Validation errors found or configuration error |

**Examples:**

```bash
# All checks pass
$ fairdm-docs check
✓ Checking documentation...
Running Sphinx linkcheck...
[linkcheck] Building... done.
[linkcheck] Checked 24 internal links: all valid
[linkcheck] Checked 15 external links: all valid

✅ No broken links found!

# Errors found
$ fairdm-docs check
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

---

## Global Behavior

### Help Output

```bash
$ fairdm-docs --help
Usage: fairdm-docs [OPTIONS] COMMAND [ARGS]...

  FairDM documentation CLI tool

Options:
  --help  Show this message and exit.

Commands:
  build  Build Sphinx documentation with sensible defaults.
  check  Validate documentation for broken links and quality issues.

$ fairdm-docs build --help
Usage: fairdm-docs build [OPTIONS]

  Build Sphinx documentation with sensible defaults.

  Reads configuration from [tool.fairdm.docs] in pyproject.toml.
  Falls back to convention-based defaults if not configured.

Options:
  --live  Start live preview server with auto-reload
  --help  Show this message and exit.
```

### Configuration Search Path

```
Current Working Directory
├─ pyproject.toml  ← Check here first
├─ ../pyproject.toml
├─ ../../pyproject.toml
└─ ... (up to filesystem root)

If not found → Error
```

### Verbosity Levels

**`full` (default)**:
- All Sphinx output (warnings, errors, progress)
- Build summary
- Status messages

**`quiet`**:
- Only errors and final status
- Suppresses warnings and progress

**`errors-only`**:
- Only errors
- No warnings, no progress, minimal status

---

## Integration Points

### Entry Point Registration

In `pyproject.toml`:

```toml
[tool.poetry.scripts]
fairdm-docs = "fairdm_docs.cli:main"
```

### Python API (Internal)

```python
# fairdm_docs/cli.py
import typer

app = typer.Typer(
    name="fairdm-docs",
    help="FairDM documentation CLI tool",
    add_completion=False,
)

@app.command()
def build(live: bool = typer.Option(False, "--live", ...)):
    """Build command implementation."""
    pass

@app.command()
def check():
    """Check command implementation."""
    pass

def main():
    """Entry point for CLI."""
    app()
```

### Testing Interface

```python
# tests/test_cli.py
from typer.testing import CliRunner
from fairdm_docs.cli import app

runner = CliRunner()

def test_build_command():
    result = runner.invoke(app, ["build"])
    assert result.exit_code == 0
    assert "Building documentation" in result.output

def test_build_live():
    result = runner.invoke(app, ["build", "--live"])
    # Test live server startup...

def test_check_command():
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0
```

---

## Compatibility

### Supported Platforms

- Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- macOS (11+)
- Windows (10+, 11)

### Python Versions

- Python 3.10
- Python 3.11
- Python 3.12

### Terminal Requirements

- UTF-8 encoding support (for emoji output)
- ANSI color support (optional, gracefully degrades)
- Interactive TTY for live server (optional)

---

## Future Extensions

Planned commands (not yet implemented):

```bash
# Deploy documentation
fairdm-docs deploy [--target github-pages|readthedocs]

# Initialize documentation structure
fairdm-docs init [--template basic|api|portal]

# Clean build artifacts
fairdm-docs clean
```

All future commands will follow same patterns:
- Configuration from pyproject.toml
- Clear error messages with guidance
- Consistent output formatting
- Testable via CliRunner
