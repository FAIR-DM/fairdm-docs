"""Generate a front page for a documentation source that has none of its own.

Sphinx requires a root document (`index.rst` or `index.md`) to build at all.
A portal that has written its own pages but no landing page or contents
listing gets one assembled from facts the build already has — its name, its
description, and the pages already in its source — for the duration of the
build only. A portal that has written its own root document keeps it.
"""

from pathlib import Path
from types import TracebackType

from fairdm_docs.metadata import ProjectMetadata

DOC_SUFFIXES = (".rst", ".md")
EXCLUDED_DIR_PREFIXES = ("_", ".")


class GeneratedFrontPage:
    """A front page for `source_dir`, generated only when it has no root
    document of its own, and only for the lifetime of a `with` block.

    Use as a context manager around a build or check:

        with GeneratedFrontPage(source_dir, metadata):
            run_the_build()

    A developer's own `index.rst` or `index.md` is never written to or
    removed. The generated file, when one was written, is removed again on
    exit, so a developer's checkout never carries it between builds.
    """

    def __init__(self, source_dir: Path, metadata: ProjectMetadata) -> None:
        self.source_dir = source_dir
        self.metadata = metadata
        self._path = source_dir / "index.md"
        self._generated = False

    def has_root_document(self) -> bool:
        """Whether the source directory already declares its own root document."""
        return any(
            (self.source_dir / f"index{suffix}").exists() for suffix in DOC_SUFFIXES
        )

    def discover_docnames(self) -> list[str]:
        """Every documentation page already in the source, as Sphinx docnames.

        A docname is the page's path relative to the source directory,
        without its extension, using forward slashes. Pages under a
        directory whose name starts with `_` (`_static`, `_templates`,
        `_build`) or `.` are excluded, and so is a root document itself.
        """
        docnames = []
        for path in self.source_dir.rglob("*"):
            if path.suffix not in DOC_SUFFIXES or not path.is_file():
                continue
            relative = path.relative_to(self.source_dir)
            if any(
                part.startswith(EXCLUDED_DIR_PREFIXES) for part in relative.parts[:-1]
            ):
                continue
            docname = relative.with_suffix("").as_posix()
            if docname == "index":
                continue
            docnames.append(docname)
        return sorted(docnames)

    def render(self) -> str:
        """The generated front page's Markdown: the portal's name and
        description, and a contents listing of every other page found."""
        lines = [f"# {self.metadata.name}", ""]
        if self.metadata.description:
            lines += [self.metadata.description, ""]
        docnames = self.discover_docnames()
        if docnames:
            lines += ["```{toctree}", ":maxdepth: 2", ""]
            lines += docnames
            lines += ["```", ""]
        return "\n".join(lines)

    def __enter__(self) -> "GeneratedFrontPage":
        if not self.has_root_document():
            self._path.write_text(self.render())
            self._generated = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._generated:
            self._path.unlink(missing_ok=True)
