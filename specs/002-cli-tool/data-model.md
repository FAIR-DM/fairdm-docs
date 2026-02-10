# Data Model: CLI Configuration and Structure

**Feature**: FairDM-Docs CLI Tool  
**Phase**: 1 (Design & Contracts)  
**Date**: February 10, 2026

## Configuration Schema

### Entity: BuildConfiguration

Represents the merged configuration for documentation builds, combining defaults with user overrides from `pyproject.toml`.

**Attributes:**

| Field | Type | Default | Description | Validation |
|-------|------|---------|-------------|------------|
| `source_dir` | Path | `Path("docs")` | Documentation source directory | Must exist or error |
| `build_dir` | Path | `Path("docs/_build/html")` | Build output directory | Created if doesn't exist |
| `port` | int | `5000` | Port for live preview server | 1024-65535, must be available |
| `verbosity` | str | `"full"` | Sphinx output verbosity level | One of: "full", "quiet", "errors-only" |
| `config_dir` | Path | `source_dir` | Directory containing conf.py | Must contain conf.py |

**Relationships:**

- Loaded from `[tool.fairdm.docs]` section in `pyproject.toml`
- User values override defaults (precedence: user > defaults)
- Missing pyproject.toml causes immediate error

**State Transitions:**

```
[Load Attempt] → [pyproject.toml Found?]
    ├─ Yes → [Parse TOML] → [Extract tool.fairdm.docs] → [Merge with Defaults] → [Validate] → [Ready]
    └─ No  → [Error: "pyproject.toml required"]

[Validate] → [Check Constraints]
    ├─ source_dir exists?     → [No]  → [Error: "Source directory not found, configure in pyproject.toml"]
    ├─ port in range?         → [No]  → [Error: "Invalid port number"]
    ├─ verbosity valid?       → [No]  → [Error: "Invalid verbosity level"]
    └─ All valid             → [Ready]
```

### Entity: CLICommand

Abstract representation of a CLI command invocation.

**Subtypes:**

1. **BuildCommand**
   - Attributes: `live: bool`, `config: BuildConfiguration`
   - Behavior: Invoke Sphinx build or sphinx-autobuild
   
2. **CheckCommand**
   - Attributes: `config: BuildConfiguration`
   - Behavior: Run validation suite (linkcheck, future validators)

**State Machine (BuildCommand):**

```
[BuildCommand.execute()]
    ├─ live=False → [Static Build Path]
    │   ├─ [Load Config] → [Validate Paths] → [Run sphinx-build] → [Success/Error]
    │   
    └─ live=True  → [Live Server Path]
        ├─ [Load Config] → [Validate Paths] → [Check Port Available?]
        │   ├─ Yes → [Start sphinx-autobuild] → [Handle Ctrl+C] → [Graceful Shutdown]
        │   └─ No  → [Error: Port conflict, show config guidance]
```

**State Machine (CheckCommand):**

```
[CheckCommand.execute()]
    ├─ [Load Config] → [Validate Source Dir] → [Run Validators]
    ├─ LinkValidator → [sphinx-build -b linkcheck] → [Parse Results]
    └─ [Aggregate Errors] → [Display Report] → [Exit Code: 0 if clean, 1 if errors]
```

## CLI Structure

### Command Tree

```
fairdm-docs (Typer app)
├── build            # Build documentation
│   └── --live      # Optional: Start live preview server
└── check            # Validate documentation quality
```

### Command Signatures

```python
# Type-safe command signatures (Typer)

@app.command()
def build(
    live: bool = typer.Option(
        False,
        "--live",
        help="Start live preview server with auto-reload"
    ),
) -> None:
    """
    Build Sphinx documentation with sensible defaults.
    
    Reads configuration from [tool.fairdm.docs] in pyproject.toml.
    Falls back to convention-based defaults if not configured.
    """
    pass

@app.command()
def check() -> None:
    """
    Validate documentation for quality issues.
    
    Currently checks:
    - Broken internal and external links
    
    Future validators can be added without breaking changes.
    """
    pass
```

## Error Taxonomy

### Error Categories

| Code | Category | Exit Code | Example |
|------|----------|-----------|---------|
| E001 | Missing Project | 1 | "pyproject.toml not found in current directory or parents" |
| E002 | Invalid Config | 1 | "Invalid port number: must be between 1024-65535" |
| E003 | Missing Source | 1 | "Source directory 'docs/' not found. Configure in [tool.fairdm.docs]" |
| E004 | Port Conflict | 1 | "Port 5000 already in use. Configure custom port in [tool.fairdm.docs]" |
| E005 | Build Failure | Non-zero from Sphinx | "Sphinx build failed. See errors above." |
| E006 | Validation Errors | 1 | "Found 3 broken links. See report above." |

### Error Message Templates

```python
ERROR_MESSAGES = {
    "no_pyproject": (
        "❌ Error: No pyproject.toml found.\n"
        "   fairdm-docs requires a Python project with pyproject.toml.\n"
        "   Run this command from your project root directory."
    ),
    "missing_source": lambda dir: (
        f"❌ Error: Source directory '{dir}' not found.\n"
        f"   Specify source directory in pyproject.toml:\n\n"
        f"   [tool.fairdm.docs]\n"
        f"   source_dir = \"path/to/docs\"\n"
    ),
    "port_conflict": lambda port: (
        f"❌ Error: Port {port} is already in use.\n"
        f"   Configure a different port in pyproject.toml:\n\n"
        f"   [tool.fairdm.docs]\n"
        f"   port = {port + 1}\n"
    ),
}
```

## Validation Rules

### Configuration Validation

```python
def validate_config(config: BuildConfiguration) -> None:
    """Validate configuration, raise clear errors on issues."""
    
    # Rule 1: Source directory must exist
    if not config.source_dir.exists():
        raise ConfigError(ERROR_MESSAGES["missing_source"](config.source_dir))
    
    # Rule 2: Source directory must contain conf.py (directly or via package)
    # (Allows fairdm_docs.conf to be used)
    
    # Rule 3: Port must be in valid range
    if not (1024 <= config.port <= 65535):
        raise ConfigError(f"Invalid port: {config.port}. Must be 1024-65535.")
    
    # Rule 4: Verbosity must be valid option
    if config.verbosity not in ["full", "quiet", "errors-only"]:
        raise ConfigError(
            f"Invalid verbosity: {config.verbosity}. "
            f"Must be one of: full, quiet, errors-only"
        )
```

### Runtime Validation

```python
def validate_runtime(config: BuildConfiguration, live: bool) -> None:
    """Validate runtime conditions before executing command."""
    
    # Rule 1: Port must be available (live mode only)
    if live and not is_port_available(config.port):
        raise RuntimeError(ERROR_MESSAGES["port_conflict"](config.port))
    
    # Rule 2: Build directory must be writable
    if config.build_dir.exists() and not os.access(config.build_dir, os.W_OK):
        raise RuntimeError(
            f"Build directory '{config.build_dir}' is not writable."
        )
```

## Future Extensibility

### Validator Plugin Pattern

```python
from abc import ABC, abstractmethod

class Validator(ABC):
    """Abstract base class for documentation validators."""
    
    @abstractmethod
    def name(self) -> str:
        """Human-readable validator name."""
        pass
    
    @abstractmethod
    def validate(self, source_dir: Path, config: BuildConfiguration) -> list[str]:
        """
        Run validation and return list of error messages.
        Empty list = no errors.
        """
        pass

class LinkValidator(Validator):
    def name(self) -> str:
        return "Link Checker"
    
    def validate(self, source_dir: Path, config: BuildConfiguration) -> list[str]:
        # Run sphinx-build -b linkcheck
        # Parse output
        # Return list of broken link messages
        pass

# Future validators:
# class SpellCheckValidator(Validator): ...
# class AccessibilityValidator(Validator): ...
# class CodeBlockValidator(Validator): ...
```

### Configuration Extension Points

Future configuration options (extensible without breaking changes):

```toml
[tool.fairdm.docs]
# Current
source_dir = "docs"
build_dir = "docs/_build/html"
port = 5000
verbosity = "full"

# Future (backward compatible additions)
# check_external_links = true
# max_link_timeout = 30
# spell_check_enabled = false
# custom_validators = ["myproject.validators.CustomValidator"]
```

## Summary

- **Configuration**: Single `BuildConfiguration` entity with clear defaults and user override pattern
- **Commands**: Two simple commands (`build`, `check`) with minimal flags
- **Validation**: Strict upfront validation with clear error messages and guidance
- **Errors**: Categorized with consistent formatting and actionable instructions
- **Extensibility**: Validator plugin pattern allows future quality checks without breaking changes
- **State Management**: Clear state transitions with no persistence (stateless CLI)
