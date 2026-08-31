"""Fixtures for writing a temporary portal and building its documentation for real."""

import io
import sys
from pathlib import Path
from typing import Any

import pytest
from sphinx.application import Sphinx


def toml_value(value: Any) -> str:
    """Render a Python value as TOML text."""
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        fields = ", ".join(f"{key} = {toml_value(val)}" for key, val in value.items())
        return "{ " + fields + " }"
    return str(value)


def render_declaration(declaration: str | dict[str, Any]) -> str:
    """Render a declaration given as TOML text, or as a mapping of table name to fields."""
    if isinstance(declaration, str):
        return declaration

    lines = []
    for table, fields in declaration.items():
        lines.append(f"[{table}]")
        for key, value in fields.items():
            lines.append(f"{key} = {toml_value(value)}")
    return "\n".join(lines) + "\n"


@pytest.fixture
def portal(tmp_path: Path):
    """Write a temporary portal from a declaration, given as a string or a mapping."""

    def write(declaration: str | dict[str, Any]) -> Path:
        (tmp_path / "pyproject.toml").write_text(render_declaration(declaration))
        docs = tmp_path / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "index.rst").write_text("Portal\n======\n")
        (docs / "conf.py").write_text("from fairdm_docs.conf import *\n")
        return tmp_path

    return write


@pytest.fixture
def built_portal(portal):
    """Build a temporary portal's documentation for real.

    Returns the rendered HTML of its index page together with the build output.
    """

    def build(declaration: str | dict[str, Any]) -> tuple[str, str]:
        portal_dir = portal(declaration)
        docs_dir = portal_dir / "docs"
        outdir = portal_dir / "_build" / "html"
        doctreedir = portal_dir / "_build" / "doctrees"

        # docs/conf.py does `from fairdm_docs.conf import *`, which reuses a
        # cached module rather than re-executing it against this portal.
        sys.modules.pop("fairdm_docs.conf", None)

        status = io.StringIO()
        warning = io.StringIO()
        app = Sphinx(
            srcdir=str(docs_dir),
            confdir=str(docs_dir),
            outdir=str(outdir),
            doctreedir=str(doctreedir),
            buildername="html",
            status=status,
            warning=warning,
            # sphinx_book_theme's source buttons crash on a build with no
            # repository address (tracked separately, docs/ROADMAP.md R3).
            # This story does not read addresses, so every build hits it;
            # the override keeps this test about identity, not that defect.
            confoverrides={
                "html_theme_options.use_repository_button": False,
                "html_theme_options.use_issues_button": False,
                "html_theme_options.use_edit_page_button": False,
            },
        )
        app.build()

        html = (outdir / "index.html").read_text()
        return html, status.getvalue() + warning.getvalue()

    return build
