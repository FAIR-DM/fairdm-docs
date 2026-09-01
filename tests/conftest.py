"""Fixtures for writing a temporary portal and building its documentation for real."""

import io
import sys
import threading
from contextlib import redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest
from sphinx.application import Sphinx

import fairdm_docs.cli


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
def documented_portal(tmp_path: Path):
    """Write a temporary portal from a declared name and version, with the docs/
    directory left for the caller to populate."""

    def write(name: str, version: str, populate) -> Path:
        (tmp_path / "pyproject.toml").write_text(
            f'[project]\nname = "{name}"\nversion = "{version}"\n'
        )
        docs = tmp_path / "docs"
        docs.mkdir(exist_ok=True)
        populate(docs)
        return tmp_path

    return write


@pytest.fixture
def run_fairdm_docs(monkeypatch):
    """Invoke a `fairdm-docs` command for real against a portal directory.

    Sets sys.argv and calls the CLI's entry point directly, catching the
    SystemExit Typer raises to exit. Nothing here mocks sphinx.cmd.build.main
    or any other part of the build — this runs a real Sphinx build or check.
    """

    def run(portal_dir: Path, args: list[str]) -> tuple[int, str, str]:
        monkeypatch.chdir(portal_dir)
        monkeypatch.setattr(sys, "argv", ["fairdm-docs", *args])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                fairdm_docs.cli.main()
                exit_code = 0
            except SystemExit as exc:
                exit_code = exc.code if isinstance(exc.code, int) else 0
        return exit_code, stdout.getvalue(), stderr.getvalue()

    return run


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


class _RedirectHandler(BaseHTTPRequestHandler):
    """Answers every request with a 302 redirect, so a check against it needs
    no network access."""

    def do_GET(self) -> None:
        self.send_response(302)
        self.send_header("Location", "/redirected")
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - overrides BaseHTTPRequestHandler's signature
        pass  # Silence the default per-request stderr logging.


@pytest.fixture
def redirect_server():
    """Start a tiny local HTTP server that responds to every GET with a 302
    redirect, for the `redirected_link` documentation source.

    Yields the server's base URL. No new dependency: `http.server` is stdlib.
    """
    server = HTTPServer(("127.0.0.1", 0), _RedirectHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/"
    finally:
        server.shutdown()
        thread.join()
