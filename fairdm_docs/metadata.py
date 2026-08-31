"""The portal's declared identity, read once from its pyproject.toml."""

import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from sphinx.util.logging import getLogger

from fairdm_docs.config import ConfigError
from fairdm_docs.utils import find_pyproject_toml

logger = getLogger(__name__)

DEFAULT_VERSION = "0.0.0"
DEFAULT_AUTHORS = ["Unknown"]
DEFAULT_DESCRIPTION = ""
MIGRATION_GUIDE = "https://github.com/FAIR-DM/fairdm-docs#migration-from-toolpoetry"


@dataclass
class ProjectMetadata:
    """What a portal declared about itself, in its `[project]` table."""

    name: str
    version: str
    description: str
    authors: list[str]
    homepage: str
    repository: str

    @property
    def copyright(self) -> str:
        return f"{datetime.now().year}, {', '.join(self.authors)}"

    @property
    def address(self) -> str:
        """The address to use where a single one is required: repository, else homepage (FR-005)."""
        return self.repository or self.homepage

    @staticmethod
    def display_name(author: str | dict[str, Any]) -> str:
        """The display name for one PEP 621 author entry, string or table."""
        if isinstance(author, dict):
            return str(author.get("name", ""))
        if "<" in author:
            return author.split("<")[0].strip()
        return author.strip()

    @staticmethod
    def resolve_address(urls: dict[str, Any], key: str) -> str:
        """The [project.urls] value for key, matched without regard to case (FR-004); empty if absent."""
        for name, value in urls.items():
            if name.lower() == key:
                return str(value)
        return ""

    @staticmethod
    def resolve_version(project: dict[str, Any], data: dict[str, Any]) -> str | None:
        """The declared version, or its `[tool.poetry]` fallback when dynamic, or None."""
        if "version" in project:
            return str(project["version"])
        if "version" in project.get("dynamic", []):
            poetry_version = data.get("tool", {}).get("poetry", {}).get("version")
            if poetry_version is not None:
                return str(poetry_version)
        return None

    @classmethod
    def from_toml_data(cls, data: dict[str, Any]) -> "ProjectMetadata":
        """Build a ProjectMetadata from an already-parsed pyproject.toml mapping."""
        if "project" not in data:
            if "poetry" in data.get("tool", {}):
                raise ConfigError(
                    "This project's pyproject.toml has a [tool.poetry] table but no "
                    "[project] table.\n"
                    "fairdm-docs requires PEP 621 project metadata; the legacy "
                    "[tool.poetry] format is not read.\n"
                    f"See the migration guide: {MIGRATION_GUIDE}"
                )
            raise ConfigError(
                "This project's pyproject.toml has no [project] table.\n"
                "Add one with at least a name:\n"
                "\n"
                "[project]\n"
                'name = "your-portal-name"\n'
            )

        project = data["project"]

        if "name" not in project:
            raise ConfigError(
                "The [project] table in pyproject.toml has no name.\n"
                "Add a name field:\n"
                "\n"
                "[project]\n"
                'name = "your-portal-name"\n'
            )

        version = cls.resolve_version(project, data)
        if version is None:
            logger.warning(
                f"No version declared in [project]; defaulting to {DEFAULT_VERSION!r}."
            )
            version = DEFAULT_VERSION

        if "description" in project:
            description = project["description"]
        else:
            logger.warning(
                f"No description declared in [project]; defaulting to {DEFAULT_DESCRIPTION!r}."
            )
            description = DEFAULT_DESCRIPTION

        if "authors" in project:
            authors = [cls.display_name(author) for author in project["authors"]]
        else:
            logger.warning(
                f"No authors declared in [project]; defaulting to {DEFAULT_AUTHORS!r}."
            )
            authors = list(DEFAULT_AUTHORS)

        urls = project.get("urls", {})
        homepage = cls.resolve_address(urls, "homepage")
        repository = cls.resolve_address(urls, "repository")

        return cls(
            name=project["name"],
            version=version,
            description=description,
            authors=authors,
            homepage=homepage,
            repository=repository,
        )

    @classmethod
    def from_file(cls, start_dir: Path | None = None) -> "ProjectMetadata":
        """Locate, read and parse a portal's pyproject.toml, then build from it."""
        path = find_pyproject_toml(start_dir)
        if path is None:
            searched_from = start_dir if start_dir is not None else Path.cwd()
            raise ConfigError(
                f"No pyproject.toml found. Searched from: {searched_from}"
            )

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"{path} is not valid TOML syntax: {exc}") from exc

        return cls.from_toml_data(data)
