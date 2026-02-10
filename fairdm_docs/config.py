"""
Configuration loading and validation for FairDM-Docs CLI.

Reads configuration from [tool.fairdm.docs] section in pyproject.toml,
merges with sensible defaults, and validates all settings.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

# Use tomllib for Python 3.11+, tomli for 3.10
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "tomli is required for Python < 3.11. "
            "Install with: pip install tomli"
        )


class ConfigError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class BuildConfiguration:
    """
    Configuration for documentation builds.
    
    Attributes:
        source_dir: Documentation source directory
        build_dir: Build output directory
        port: Port for live preview server
        verbosity: Sphinx output verbosity level
        config_dir: Directory containing conf.py (defaults to package location)
        django: Whether to import and setup Django (default: False)
    """
    source_dir: Path = field(default_factory=lambda: Path("docs"))
    build_dir: Path = field(default_factory=lambda: Path("docs/_build/html"))
    port: int = 5000
    verbosity: str = "full"
    config_dir: Optional[Path] = None
    django: bool = False


# Error message templates from data-model.md
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


def find_pyproject() -> Optional[Path]:
    """
    Find pyproject.toml in current directory or parents.
    
    Returns:
        Path to pyproject.toml if found, None otherwise
    """
    current = Path.cwd()
    
    # Check current directory and all parents
    for parent in [current] + list(current.parents):
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            return pyproject
    
    return None


def load_pyproject() -> Dict[str, Any]:
    """
    Load and parse pyproject.toml.
    
    Returns:
        Parsed TOML data as dictionary
        
    Raises:
        ConfigError: If pyproject.toml not found
    """
    pyproject_path = find_pyproject()
    
    if pyproject_path is None:
        raise ConfigError(ERROR_MESSAGES["no_pyproject"])
    
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def load_config() -> BuildConfiguration:
    """
    Load configuration from pyproject.toml and merge with defaults.
    
    Reads [tool.fairdm.docs] section if present, otherwise uses all defaults.
    User configuration always takes precedence over defaults.
    
    Returns:
        BuildConfiguration with merged settings
        
    Raises:
        ConfigError: If pyproject.toml not found or configuration invalid
    """
    # Load pyproject.toml (raises ConfigError if not found)
    data = load_pyproject()
    
    # Start with defaults
    config = BuildConfiguration()
    
    # Extract user configuration if present
    tool_config = data.get("tool", {}).get("fairdm", {}).get("docs", {})
    
    # Merge user config (user values override defaults)
    if "source_dir" in tool_config:
        config.source_dir = Path(tool_config["source_dir"])
    
    if "build_dir" in tool_config:
        config.build_dir = Path(tool_config["build_dir"])
    
    if "port" in tool_config:
        config.port = int(tool_config["port"])
    
    if "verbosity" in tool_config:
        config.verbosity = tool_config["verbosity"]
    
    if "django" in tool_config:
        config.django = bool(tool_config["django"])
    
    # Validate merged configuration
    validate_config(config)
    
    return config


def validate_config(config: BuildConfiguration) -> None:
    """
    Validate configuration, raise clear errors on issues.
    
    Args:
        config: Configuration to validate
        
    Raises:
        ConfigError: If validation fails
    """
    # Rule 1: Source directory must exist
    if not config.source_dir.exists():
        raise ConfigError(ERROR_MESSAGES["missing_source"](config.source_dir))
    
    # Rule 2: Port must be in valid range
    if not (1024 <= config.port <= 65535):
        raise ConfigError(
            f"❌ Error: Invalid port: {config.port}. Must be 1024-65535."
        )
    
    # Rule 3: Verbosity must be valid option
    valid_verbosity = ["full", "quiet", "errors-only"]
    if config.verbosity not in valid_verbosity:
        raise ConfigError(
            f"❌ Error: Invalid verbosity: {config.verbosity}. "
            f"Must be one of: {', '.join(valid_verbosity)}"
        )
