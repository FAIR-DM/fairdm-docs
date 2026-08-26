"""
Shared utility functions for FairDM-Docs package.

Provides common functionality for finding and loading pyproject.toml files
used across the package (conf.py, config.py, CLI, etc.).
"""

import os

# Use tomllib for Python 3.11+, tomli for 3.10
import tomllib
from pathlib import Path
from typing import Any


def find_pyproject_toml(start_dir: Path | None = None, use_env_var: bool = False) -> Path | None:
    """
    Find pyproject.toml by searching upward from a starting directory.

    Args:
        start_dir: Directory to start search from. If None, uses current working directory.
        use_env_var: If True, checks FAIRDM_DOCS_PROJECT_DIR environment variable first.
                     This is useful when Sphinx changes cwd to the conf.py location.

    Returns:
        Path to pyproject.toml if found, None otherwise

    Examples:
        >>> # Find from current directory
        >>> find_pyproject_toml()
        PosixPath('/home/user/project/pyproject.toml')

        >>> # Find using environment variable (for Sphinx)
        >>> find_pyproject_toml(use_env_var=True)
        PosixPath('/home/user/project/pyproject.toml')

        >>> # Find from specific directory
        >>> find_pyproject_toml(Path('/home/user/project/docs'))
        PosixPath('/home/user/project/pyproject.toml')
    """
    # Use project dir from environment variable if requested (set by CLI for Sphinx)
    if use_env_var:
        project_dir = os.environ.get("FAIRDM_DOCS_PROJECT_DIR")
        if project_dir:
            start_dir = Path(project_dir)

    # Default to current working directory
    if start_dir is None:
        start_dir = Path.cwd()

    # Search current directory and all parents
    for parent in [start_dir, *list(start_dir.parents)]:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            return pyproject

    return None


def load_pyproject_toml(pyproject_path: Path | None = None, start_dir: Path | None = None) -> dict[str, Any]:
    """
    Load and parse pyproject.toml file.

    Args:
        pyproject_path: Direct path to pyproject.toml. If None, will search for it.
        start_dir: Directory to start search from (only used if pyproject_path is None)

    Returns:
        Parsed TOML data as dictionary

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
        tomllib.TOMLDecodeError: If TOML syntax is invalid

    Examples:
        >>> # Load from found location
        >>> data = load_pyproject_toml()
        >>> data['project']['name']
        'fairdm-docs'

        >>> # Load from specific path
        >>> data = load_pyproject_toml(Path('/path/to/pyproject.toml'))
    """
    if pyproject_path is None:
        pyproject_path = find_pyproject_toml(start_dir)

    if pyproject_path is None:
        search_from = start_dir or Path.cwd()
        raise FileNotFoundError(
            f"pyproject.toml not found. Ensure it exists at your project root directory. Searched from: {search_from}"
        )

    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)
