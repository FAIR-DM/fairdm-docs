# Research: CLI Framework Selection

**Feature**: FairDM-Docs CLI Tool  
**Phase**: 0 (Outline & Research)  
**Date**: February 10, 2026

## Research Questions

1. Which modern Python CLI framework is best suited for this project?
2. How should configuration be loaded from pyproject.toml?
3. How to invoke Sphinx build and sphinx-autobuild programmatically?
4. How to handle port conflicts and graceful shutdown?
5. How to implement extensible validation system for check command?

## Decision 1: CLI Framework → **Typer**

### Candidates Evaluated

- **Typer** (^0.12.0) - Modern type-hint based CLI framework
- **Click** (^8.1.0) - Mature decorator-based framework (Typer's foundation)
- **argparse** (stdlib) - Standard library solution
- **Fire** (^0.6.0) - Google's auto-generation framework

### Decision Rationale

**Selected: Typer**

**Why:**

- Modern Pythonic API using type hints (aligns with Python 3.10+ target)
- Minimal boilerplate - commands are just typed functions
- Built on Click (inherits stability) with better DX
- Rich console output out-of-the-box (progress, colors, formatting)
- Auto-generates comprehensive help from type hints and docstrings
- Excellent testing support via CliRunner
- Growing adoption in modern Python projects (23.5k+ GitHub stars)
- Created by Sebastián Ramírez (FastAPI author) - active maintenance

**Alternatives Considered:**

- **Click**: More verbose, no type hint support, but more mature
  - **Rejected because**: Typer provides all Click benefits with better DX
- **argparse**: No external dependencies, but very verbose imperative style
  - **Rejected because**: Too much boilerplate, poor testability
- **Fire**: Minimal code via auto-generation, but less control over interface
  - **Rejected because**: Magic behavior, less polished help output

### Code Example

```python
import typer
from pathlib import Path

app = typer.Typer(name="fairdm-docs", help="FairDM documentation CLI tool")

@app.command()
def build(
    live: bool = typer.Option(False, "--live", help="Start live preview server"),
    source_dir: Path = typer.Option(Path("docs"), help="Source directory"),
):
    """Build Sphinx documentation with sensible defaults."""
    if live:
        typer.echo("🔴 Starting live server...")
    else:
        typer.echo("📚 Building documentation...")

@app.command()
def check():
    """Validate documentation for broken links."""
    typer.echo("✓ Checking documentation...")
```

## Decision 2: Configuration Loading → **tomli/tomllib**

### Approach

- Python 3.11+: Use stdlib `tomllib` (read-only TOML parser)
- Python 3.10: Use `tomli` backport (read-only)
- Search for pyproject.toml from current directory upward
- Parse `[tool.fairdm.docs]` section
- Merge with defaults (user config takes precedence)

### Implementation Strategy

```python
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

def find_pyproject() -> Path:
    """Search for pyproject.toml in current dir and parents."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        candidate = parent / "pyproject.toml"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("pyproject.toml not found")

def load_config() -> dict:
    """Load configuration from [tool.fairdm.docs] section."""
    pyproject_path = find_pyproject()
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    
    defaults = {
        "source_dir": "docs",
        "build_dir": "docs/_build/html",
        "port": 5000,
        "verbosity": "full",
    }
    
    user_config = data.get("tool", {}).get("fairdm", {}).get("docs", {})
    return {**defaults, **user_config}  # User overrides defaults
```

## Decision 3: Sphinx Integration → **Subprocess + sphinx.cmd**

### Build Command (static)

Use `sphinx.cmd.build.main()` programmatically:

```python
from sphinx.cmd.build import main as sphinx_build
import sys

def run_sphinx_build(source_dir, build_dir, config_path):
    """Run sphinx-build programmatically."""
    args = [
        "-c", str(config_path.parent),  # config directory (contains conf.py)
        "-b", "html",                   # builder (HTML)
        str(source_dir),                # source directory
        str(build_dir),                 # output directory
    ]
    
    exit_code = sphinx_build(args)
    if exit_code != 0:
        raise typer.Exit(exit_code)
```

### Live Server Command

Use `sphinx_autobuild` subprocess (cleaner than programmatic):

```python
import subprocess
import webbrowser

def run_live_server(source_dir, build_dir, port):
    """Run sphinx-autobuild live server."""
    cmd = [
        "sphinx-autobuild",
        str(source_dir),
        str(build_dir),
        "--port", str(port),
        "--open-browser",
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        typer.echo("\n\n👋 Shutting down live server...")
        raise typer.Exit(0)
```

## Decision 4: Check Command → **sphinx-build -b linkcheck**

### Approach

Sphinx has built-in linkcheck builder:

```python
def run_link_check(source_dir, build_dir):
    """Run Sphinx linkcheck builder."""
    from sphinx.cmd.build import main as sphinx_build
    
    args = [
        "-b", "linkcheck",              # linkcheck builder
        "-W", "--keep-going",           # Treat warnings as errors, continue
        str(source_dir),
        str(build_dir / "linkcheck"),
    ]
    
    exit_code = sphinx_build(args)
    return exit_code
```

### Extensibility Design

```python
# Future: Add more validators
class Validator:
    def validate(self, source_dir) -> list[str]:
        """Return list of error messages."""
        pass

class LinkValidator(Validator):
    def validate(self, source_dir):
        # Run linkcheck
        pass

class SpellCheckValidator(Validator):  # Future
    def validate(self, source_dir):
        # Run spell check
        pass

def run_all_validators(source_dir, validators: list[Validator]):
    errors = []
    for validator in validators:
        errors.extend(validator.validate(source_dir))
    return errors
```

## Decision 5: Port Conflict Handling → **Try/Except with Error Message**

### Approach

Check port availability before starting server:

```python
import socket

def is_port_available(port: int) -> bool:
    """Check if port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False

def start_live_server(port: int):
    """Start live server, error if port unavailable."""
    if not is_port_available(port):
        typer.echo(
            f"❌ Error: Port {port} is already in use.\n"
            f"   Configure a different port in pyproject.toml:\n\n"
            f"   [tool.fairdm.docs]\n"
            f"   port = 5001\n",
            err=True
        )
        raise typer.Exit(1)
    
    # Start server...
```

## Dependencies Summary

### Required

- `typer[all]` (^0.12.0) - CLI framework with rich output
- `tomli` (^2.0.0) - TOML parser for Python 3.10 (stdlib tomllib for 3.11+)

### Already Present

- `sphinx` (>=8.1) - Documentation engine
- `sphinx-autobuild` (>=2024.10) - Live reload server

### Testing

- `pytest` (existing) - Test framework
- `pytest-mock` (existing) - Mocking support

## Configuration Schema

```toml
[tool.fairdm.docs]
source_dir = "docs"                    # Default: docs/
build_dir = "docs/_build/html"         # Default: docs/_build/html
port = 5000                            # Default: 5000 (for live server)
verbosity = "full"                     # Options: "full", "quiet", "errors-only"
```

## Open Questions

None - All research questions resolved.

## Summary

- **CLI Framework**: Typer (modern, type-safe, minimal boilerplate)
- **Config Loading**: tomli/tomllib from pyproject.toml
- **Sphinx Integration**: Programmatic API for builds, subprocess for live server
- **Check Command**: Sphinx linkcheck builder with extensible validator pattern
- **Port Handling**: Pre-check availability, error with config guidance
- **Testing**: Typer's CliRunner for isolated CLI tests

All decisions align with FairDM-Docs constitution principles (convention over configuration, zero-config philosophy, extensibility).
