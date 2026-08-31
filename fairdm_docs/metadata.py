"""The portal's declared identity, read once from its pyproject.toml."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sphinx.util.logging import getLogger

logger = getLogger(__name__)

DEFAULT_VERSION = "0.0.0"
DEFAULT_AUTHORS = ["Unknown"]
DEFAULT_DESCRIPTION = ""


@dataclass
class ProjectMetadata:
    """What a portal declared about itself, in its `[project]` table."""

    name: str
    version: str
    description: str
    authors: list[str]

    @property
    def copyright(self) -> str:
        return f"{datetime.now().year}, {', '.join(self.authors)}"

    @staticmethod
    def display_name(author: str | dict[str, Any]) -> str:
        """The display name for one PEP 621 author entry, string or table."""
        if isinstance(author, dict):
            return str(author.get("name", ""))
        if "<" in author:
            return author.split("<")[0].strip()
        return author.strip()

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
        project = data["project"]

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

        return cls(
            name=project["name"],
            version=version,
            description=description,
            authors=authors,
        )
