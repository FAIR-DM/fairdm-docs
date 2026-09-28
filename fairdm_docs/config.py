"""The command's build configuration, read from `[tool.fairdm.docs]` in pyproject.toml."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fairdm_docs.utils import find_pyproject_toml, load_pyproject_toml


class ConfigError(Exception):
    """Raised when configuration validation fails."""

    pass


@dataclass
class BuildConfiguration:
    """Configuration for documentation builds.

    Attributes:
        source_dir: Documentation source directory
        build_dir: Build output directory
        port: Port for live preview server
        verbosity: Sphinx output verbosity level
        django: Whether to import and setup Django (default: False)
    """

    source_dir: Path = field(default_factory=lambda: Path("docs"))
    build_dir: Path = field(default_factory=lambda: Path("docs/_build/html"))
    port: int = 5000
    verbosity: str = "full"
    django: bool = False


# A mix of ready-made strings and templates that need a value interpolated,
# so the annotation has to admit both.
ERROR_MESSAGES: dict[str, Any] = {
    "no_pyproject": (
        "❌ Error: No pyproject.toml found.\n"
        "   fairdm-docs requires a Python project with pyproject.toml.\n"
        "   Run this command from your project root directory."
    ),
    "missing_source": lambda source_dir: (
        f"❌ Error: Source directory '{source_dir}' not found.\n"
        f"   Specify source directory in pyproject.toml:\n\n"
        f"   [tool.fairdm.docs]\n"
        f'   source_dir = "path/to/docs"\n'
    ),
    "port_conflict": lambda port: (
        f"❌ Error: Port {port} is already in use.\n"
        f"   Configure a different port in pyproject.toml:\n\n"
        f"   [tool.fairdm.docs]\n"
        f"   port = {port + 1}\n"
    ),
    "invalid_toml": lambda path, exc: (
        f"❌ Error: {path} is not valid TOML.\n"
        f"   fairdm-docs could not parse this file: {exc}\n"
        f"   Fix the syntax and try again."
    ),
}


def load_pyproject() -> dict[str, Any]:
    """Load and parse pyproject.toml.

    Returns:
        Parsed TOML data as dictionary

    Raises:
        ConfigError: If pyproject.toml not found or not valid TOML
    """
    pyproject_path = find_pyproject_toml()

    if pyproject_path is None:
        raise ConfigError(ERROR_MESSAGES["no_pyproject"])

    try:
        return load_pyproject_toml(pyproject_path)
    except FileNotFoundError:
        raise ConfigError(ERROR_MESSAGES["no_pyproject"]) from None
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(ERROR_MESSAGES["invalid_toml"](pyproject_path, exc)) from None


def load_config() -> BuildConfiguration:
    """Load configuration from pyproject.toml and merge with defaults.

    Reads [tool.fairdm.docs] section if present, otherwise uses all defaults.
    User configuration always takes precedence over defaults.

    Returns:
        BuildConfiguration with merged settings

    Raises:
        ConfigError: If pyproject.toml not found or configuration invalid
    """
    data = load_pyproject()
    config = BuildConfiguration()
    tool_config = data.get("tool", {}).get("fairdm", {}).get("docs", {})

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

    validate_config(config)

    return config


def validate_config(config: BuildConfiguration) -> None:
    """Check a merged configuration and raise a clear error for the first problem.

    Args:
        config: Configuration to validate

    Raises:
        ConfigError: If validation fails
    """
    if not config.source_dir.exists():
        raise ConfigError(ERROR_MESSAGES["missing_source"](config.source_dir))

    if not (1024 <= config.port <= 65535):
        raise ConfigError(f"❌ Error: Invalid port: {config.port}. Must be 1024-65535.")

    valid_verbosity = ["full", "quiet", "errors-only"]
    if config.verbosity not in valid_verbosity:
        raise ConfigError(
            f"❌ Error: Invalid verbosity: {config.verbosity}. Must be one of: {', '.join(valid_verbosity)}"
        )
