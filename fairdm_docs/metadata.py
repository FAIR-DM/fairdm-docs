"""The portal's declared identity, read once from its pyproject.toml."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


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

    @classmethod
    def from_toml_data(cls, data: dict[str, Any]) -> "ProjectMetadata":
        """Build a ProjectMetadata from an already-parsed pyproject.toml mapping."""
        project = data["project"]
        authors = [cls.display_name(author) for author in project["authors"]]
        return cls(
            name=project["name"],
            version=project["version"],
            description=project["description"],
            authors=authors,
        )
