"""
Tests for CLI commands.

Tests the build and check commands using Typer's CliRunner
for isolated testing.
"""

import os
import shutil
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fairdm_docs.cli import app
from fairdm_docs.metadata import ProjectMetadata

# Colour codes land inside option names in rich-formatted help ("--live" becomes
# "-\x1b[0m\x1b[1;36m-live"), so a substring assertion fails wherever the
# environment asks for colour, as CI does. Ask for plain output instead.
runner = CliRunner(env={"FORCE_COLOR": None, "NO_COLOR": "1", "TERM": "dumb"})

FIXTURES_DIR = Path(__file__).parent / "fixtures"

BUILD_SETTINGS = ("FAIRDM_DOCS_DJANGO", "FAIRDM_DOCS_PROJECT_DIR")


class _TerminatingRedirectHandler(BaseHTTPRequestHandler):
    """Redirects `/` to `/target` once, then answers `/target` with 200 —
    unlike conftest.py's `redirect_server`, which redirects every path
    (including its own target) and so never terminates. See decisions.md for
    why TestCheck.test_reports_a_redirect_under_its_own_heading_and_exits_zero
    uses this instead."""

    def do_GET(self) -> None:
        if self.path == "/target":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(302)
            self.send_header("Location", "/target")
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - overrides BaseHTTPRequestHandler's signature
        pass  # Silence the default per-request stderr logging.


@pytest.fixture
def terminating_redirect_server():
    server = HTTPServer(("127.0.0.1", 0), _TerminatingRedirectHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/"
    finally:
        server.shutdown()
        thread.join()


class _PermanentRedirectHandler(_TerminatingRedirectHandler):
    """As `_TerminatingRedirectHandler`, but answers 301 rather than 302.

    The builder writes a different bracket text per status code: `redirected
    permanently` for 301 and 308, `redirected temporarily` for 307, and
    `redirected with <reason>` for 302, 303 and unknown codes. A classifier
    matching only one of those shapes drops the rest silently, which is the
    defect this fixture exists to catch."""

    def do_GET(self) -> None:
        if self.path == "/target":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(301)
            self.send_header("Location", "/target")
            self.end_headers()


@pytest.fixture
def permanent_redirect_server():
    server = HTTPServer(("127.0.0.1", 0), _PermanentRedirectHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/"
    finally:
        server.shutdown()
        thread.join()


def _populate_from_fixture(name: str):
    """A `documented_portal` populate callback that copies a documentation
    source from tests/fixtures/<name>/ into the portal's docs/ directory."""

    def populate(docs_dir: Path) -> None:
        for item in (FIXTURES_DIR / name).iterdir():
            shutil.copy(item, docs_dir / item.name)

    return populate


def write_minimal_project(tmp_path):
    """Write the smallest project layout either command will accept."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "index.md").write_text("# Test")
    return tmp_path


class SphinxRecorder:
    """Stands in for Sphinx's entry point and records the environment it ran under.

    The settings the CLI passes to conf.py are environment variables, so the only
    place their values can be read is from inside the build itself. Pass `delegate`
    to record the environment and then run the real build anyway.
    """

    def __init__(self, delegate=None):
        self.delegate = delegate
        self.seen: dict[str, str | None] = {}

    def __call__(self, *args, **kwargs):
        self.seen.update({name: os.environ.get(name) for name in BUILD_SETTINGS})
        return 0 if self.delegate is None else self.delegate(*args, **kwargs)


class TestBuildCommand:
    def test_build_with_defaults(self, tmp_path, monkeypatch):
        # Create minimal project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        # Create a minimal index file
        (docs_dir / "index.md").write_text("# Test Docs\n\nHello world!")

        monkeypatch.chdir(tmp_path)

        # Mock sphinx.cmd.build.main to avoid actual build
        with patch("sphinx.cmd.build.main", return_value=0) as mock_build:
            runner.invoke(app, ["build"])

            # Should call sphinx_build
            assert mock_build.called

            # Check arguments passed to Sphinx
            args = mock_build.call_args[0][0]
            assert "-b" in args
            assert "html" in args
            # Check that docs path is in args (could be "docs" or absolute path)
            assert "docs" in args or str(docs_dir) in args

    def test_build_creates_output_directory(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        build_dir = tmp_path / "docs" / "_build" / "html"
        assert not build_dir.exists()

        with patch("sphinx.cmd.build.main", return_value=0):
            runner.invoke(app, ["build"])

            # Parent directory should be created
            assert build_dir.parent.exists()

    def test_build_displays_progress_messages(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            result = runner.invoke(app, ["build"])

            # Should show build start message
            assert "Building documentation" in result.stdout

            # Should show success message
            assert "Build complete" in result.stdout
            assert "✅" in result.stdout

    def test_build_exits_zero_on_success(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            result = runner.invoke(app, ["build"])

            assert result.exit_code == 0

    def test_build_error_when_no_pyproject(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["build"])

        # Should exit with error
        assert result.exit_code == 1

        # Should show clear error message (can be in stdout or stderr)
        output = result.stdout + result.stderr
        assert "No pyproject.toml found" in output
        assert "Run this command from your project root" in output

    def test_build_error_when_source_missing(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        # Don't create docs/ directory
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["build"])

        # Should exit with error
        assert result.exit_code == 1

        # Should show clear error message (can be in stdout or stderr)
        output = result.stdout + result.stderr
        assert "Source directory" in output
        assert "not found" in output
        assert "[tool.fairdm.docs]" in output

    def test_build_with_custom_source_dir(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
source_dir = "documentation"
        """)

        docs_dir = tmp_path / "documentation"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0) as mock_build:
            result = runner.invoke(app, ["build"])

            assert result.exit_code == 0

            # Should use custom source directory
            args = mock_build.call_args[0][0]
            assert "documentation" in args

    def test_build_with_custom_build_dir(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
build_dir = "build/output"
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0) as mock_build:
            result = runner.invoke(app, ["build"])

            assert result.exit_code == 0

            # Should use custom build directory
            args = mock_build.call_args[0][0]
            assert "output" in " ".join(args)

    def test_build_with_verbosity_quiet(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
verbosity = "quiet"
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0) as mock_build:
            runner.invoke(app, ["build"])

            # Should pass -q flag to Sphinx
            args = mock_build.call_args[0][0]
            assert "-q" in args

    def test_build_with_verbosity_errors_only(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
verbosity = "errors-only"
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0) as mock_build:
            runner.invoke(app, ["build"])

            # Should pass -Q flag to Sphinx
            args = mock_build.call_args[0][0]
            assert "-Q" in args

    def test_build_failure_returns_nonzero(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        # Mock Sphinx to return error code
        with patch("sphinx.cmd.build.main", return_value=2):
            result = runner.invoke(app, ["build"])

            assert result.exit_code == 2
            output = result.stdout + result.stderr
            assert "Build failed" in output

    def test_build_uses_package_conf_py(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0) as mock_build:
            runner.invoke(app, ["build"])

            # Should pass -c flag pointing to package directory
            args = mock_build.call_args[0][0]
            assert "-c" in args

            # Find the config directory argument (after -c)
            c_index = args.index("-c")
            config_dir = args[c_index + 1]

            # Should contain fairdm_docs
            assert "fairdm_docs" in config_dir

    def test_build_sets_django_env_var_false_by_default(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        sphinx = SphinxRecorder()
        with patch("sphinx.cmd.build.main", side_effect=sphinx):
            runner.invoke(app, ["build"])

            # Django env var should be false while Sphinx runs
            assert sphinx.seen["FAIRDM_DOCS_DJANGO"] == "false"

    def test_build_sets_django_env_var_true_when_enabled(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
django = true
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        sphinx = SphinxRecorder()
        with patch("sphinx.cmd.build.main", side_effect=sphinx):
            runner.invoke(app, ["build"])

            # Django env var should be true while Sphinx runs
            assert sphinx.seen["FAIRDM_DOCS_DJANGO"] == "true"


class TestBuildSettingsLifetime:
    def test_build_leaves_the_environment_as_it_found_it(self, tmp_path, monkeypatch):
        for name in BUILD_SETTINGS:
            monkeypatch.delenv(name, raising=False)
        write_minimal_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            runner.invoke(app, ["build"])

        assert [os.environ.get(name) for name in BUILD_SETTINGS] == [None, None]

    def test_check_leaves_the_environment_as_it_found_it(self, tmp_path, monkeypatch):
        for name in BUILD_SETTINGS:
            monkeypatch.delenv(name, raising=False)
        write_minimal_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            runner.invoke(app, ["check"])

        assert [os.environ.get(name) for name in BUILD_SETTINGS] == [None, None]

    def test_a_value_set_by_the_caller_survives_the_build(self, tmp_path, monkeypatch):
        monkeypatch.setenv("FAIRDM_DOCS_PROJECT_DIR", "/somewhere/the/caller/chose")
        monkeypatch.setenv("FAIRDM_DOCS_DJANGO", "true")
        write_minimal_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            runner.invoke(app, ["build"])

        assert os.environ["FAIRDM_DOCS_PROJECT_DIR"] == "/somewhere/the/caller/chose"
        assert os.environ["FAIRDM_DOCS_DJANGO"] == "true"

    def test_the_build_reads_the_directory_the_command_was_run_from(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("FAIRDM_DOCS_PROJECT_DIR", "/a/stale/directory")
        write_minimal_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        sphinx = SphinxRecorder()
        with patch("sphinx.cmd.build.main", side_effect=sphinx):
            runner.invoke(app, ["build"])

        assert sphinx.seen["FAIRDM_DOCS_PROJECT_DIR"] == str(tmp_path.resolve())


class TestBuild:
    def test_renders_a_root_page_to_html(self, documented_portal, run_fairdm_docs):
        portal_dir = documented_portal(
            "zero-config-portal", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        index_html = portal_dir / "docs" / "_build" / "html" / "index.html"
        assert index_html.exists()
        assert (
            "One page, no links, nothing else in this documentation source."
            in index_html.read_text()
        )

    def test_uses_the_portals_own_conf_py_when_present(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "uses-own-conf", "0.1.0", _populate_from_fixture("with_own_conf")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        html = (portal_dir / "docs" / "_build" / "html" / "index.html").read_text()
        # tests/fixtures/with_own_conf/conf.py hardcodes project = "with-own-conf",
        # which only reaches the output if that file, not the package's own
        # conf.py, configured the build.
        assert "with-own-conf" in html

    def test_uses_the_packages_own_conf_py_when_none_is_provided(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "no-own-conf", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        html = (portal_dir / "docs" / "_build" / "html" / "index.html").read_text()
        # The package's own conf.py selects sphinx_book_theme; a source with
        # no conf.py of its own only gets this theme's assets if that file
        # configured the build.
        assert "sphinx-book-theme.css" in html

    def test_creates_a_missing_parent_of_the_build_directory(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "missing-parent", "0.1.0", _populate_from_fixture("single_page")
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "missing-parent"\nversion = "0.1.0"\n'
            "\n"
            "[tool.fairdm.docs]\n"
            'build_dir = "output/nested/html"\n'
        )
        build_dir = portal_dir / "output" / "nested" / "html"
        assert not build_dir.parent.exists()

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert (build_dir / "index.html").exists()

    def test_reports_where_it_started_and_where_it_wrote_the_site(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "progress-messages", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert "Building documentation" in stdout
        # "Output: docs/_build/html" is the command's own message (distinct
        # from Sphinx's own "The HTML pages are in docs/_build/html.").
        assert "Output: docs/_build/html" in stdout

    def test_full_verbosity_passes_sphinxs_own_output_through(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "full-verbosity", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert "build succeeded" in stdout

    def test_sets_fairdm_docs_project_dir_to_the_portals_own_directory(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "project-dir-env-var", "0.1.0", _populate_from_fixture("single_page")
        )

        from sphinx.cmd.build import main as real_sphinx_build

        recorder = SphinxRecorder(delegate=real_sphinx_build)
        with patch("sphinx.cmd.build.main", side_effect=recorder):
            exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert recorder.seen["FAIRDM_DOCS_PROJECT_DIR"] == str(portal_dir.resolve())

    def test_the_documented_minimum_builds_and_exits_zero(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "markdown-minimum", "0.1.0", _populate_from_fixture("markdown_single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        html = (portal_dir / "docs" / "_build" / "html" / "index.html").read_text()
        assert (
            "One Markdown page, no links, nothing else in this documentation source."
            in html
        )
        output = stdout + stderr
        assert "autodoc2" not in output
        assert "Extension error" not in output


class TestConfigurationValidationErrors:
    def test_invalid_port_shows_clear_error(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
port = 100000
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["build"])

        # Should exit with error
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "port" in output.lower()
        assert "100000" in output or "invalid" in output.lower()

    def test_invalid_verbosity_shows_clear_error(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
verbosity = "invalid"
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["build"])

        # Should exit with error
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "verbosity" in output.lower()
        assert "invalid" in output or "full" in output or "quiet" in output

    def test_config_validation_error_message_format(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
port = -1
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["build"])

        # Should exit with error
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        # Error should contain the invalid value and guidance
        assert (
            "-1" in output or "negative" in output.lower() or "port" in output.lower()
        )


class TestConfigurationFailures:
    def test_metadata_failure_reported_as_message_not_traceback(
        self, tmp_path, monkeypatch
    ):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.poetry]\nname = 'test'\n")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        def build_reads_project_metadata(*args, **kwargs):
            ProjectMetadata.from_file()
            return 0

        with patch("sphinx.cmd.build.main", side_effect=build_reads_project_metadata):
            result = runner.invoke(app, ["build"])

        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Traceback" not in output
        assert "PEP 621" in output

    def test_malformed_toml_reported_as_message_not_traceback(
        self, tmp_path, monkeypatch
    ):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project\nname = probe\n")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["build"])

        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Traceback" not in output
        assert str(pyproject) in output
        assert "not valid TOML" in output


class TestCheckCommand:
    def test_check_passes_with_no_errors(self, tmp_path, monkeypatch):
        # Create minimal project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text(
            "# Test Docs\n\nValid link: [Python](https://python.org)"
        )

        monkeypatch.chdir(tmp_path)

        # Mock sphinx.cmd.build.main for linkcheck
        with patch("sphinx.cmd.build.main", return_value=0) as mock_build:
            result = runner.invoke(app, ["check"])

            # Should call sphinx_build with linkcheck builder
            assert mock_build.called
            args = mock_build.call_args[0][0]
            assert "-b" in args
            assert "linkcheck" in args

            # Should exit successfully
            assert result.exit_code == 0
            assert (
                "Link check complete" in result.stdout
                or "All links are valid" in result.stdout
            )

    def test_check_reports_broken_links(self, tmp_path, monkeypatch):
        # Create project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        # Create linkcheck output directory and file with broken link
        linkcheck_dir = tmp_path / "docs" / "_build" / "linkcheck"
        linkcheck_dir.mkdir(parents=True)
        output_file = linkcheck_dir / "output.txt"
        output_file.write_text(
            "index.md:5: [broken] https://example.invalid/: HTTPConnectionPool error\n"
        )

        monkeypatch.chdir(tmp_path)

        # Mock sphinx build to return success but with broken links in output
        with patch("sphinx.cmd.build.main", return_value=0):
            result = runner.invoke(app, ["check"])

            # Should exit with error
            assert result.exit_code == 1
            # Combined stdout and stderr for error messages
            output = result.stdout + result.stderr
            assert "broken link" in output.lower()

    def test_check_exits_zero_on_success(self, tmp_path, monkeypatch):
        # Create minimal project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        # Mock successful linkcheck
        with patch("sphinx.cmd.build.main", return_value=0):
            result = runner.invoke(app, ["check"])

            assert result.exit_code == 0

    def test_check_exits_one_on_errors(self, tmp_path, monkeypatch):
        # Create project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        # Create linkcheck output with broken link
        linkcheck_dir = tmp_path / "docs" / "_build" / "linkcheck"
        linkcheck_dir.mkdir(parents=True)
        output_file = linkcheck_dir / "output.txt"
        output_file.write_text("index.md:5: [broken] https://bad.link/: Error\n")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            result = runner.invoke(app, ["check"])

            assert result.exit_code == 1

    def test_check_displays_file_and_line_numbers(self, tmp_path, monkeypatch):
        # Create project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        # Create linkcheck output with specific file and line
        linkcheck_dir = tmp_path / "docs" / "_build" / "linkcheck"
        linkcheck_dir.mkdir(parents=True)
        output_file = linkcheck_dir / "output.txt"
        broken_link_line = (
            "docs/api.md:42: [broken] https://nowhere.invalid/: Connection failed"
        )
        output_file.write_text(broken_link_line + "\n")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            result = runner.invoke(app, ["check"])

            # Should display the file and line number
            output = result.stdout + result.stderr
            assert "api.md" in output
            assert "42" in output or broken_link_line in output


class TestCheck:
    def test_reports_success_when_every_address_resolves(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "check-all-resolve", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code == 0
        output = stdout + stderr
        assert "All links are valid" in output or "Link check complete" in output

    def test_names_the_address_and_file_of_a_broken_link(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "check-broken-link", "0.1.0", _populate_from_fixture("broken_link")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code != 0
        output = stdout + stderr
        assert "index.rst" in output
        assert "this-domain-does-not-exist-fairdm-docs-002.invalid" in output

    def test_reports_a_redirect_under_its_own_heading_and_exits_zero(
        self, documented_portal, run_fairdm_docs, terminating_redirect_server
    ):

        def populate(docs_dir):
            source = (FIXTURES_DIR / "redirected_link" / "index.rst").read_text()
            (docs_dir / "index.rst").write_text(
                source.replace("__REDIRECT_URL__", terminating_redirect_server)
            )

        portal_dir = documented_portal("check-redirect", "0.1.0", populate)

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code == 0
        output = stdout + stderr
        assert "broken link(s)" not in output.lower()
        assert "redirect" in output.lower()
        assert "index.rst" in output

    def test_reports_a_permanent_redirect_the_same_as_a_temporary_one(
        self, documented_portal, run_fairdm_docs, permanent_redirect_server
    ):

        def populate(docs_dir):
            source = (FIXTURES_DIR / "redirected_link" / "index.rst").read_text()
            (docs_dir / "index.rst").write_text(
                source.replace("__REDIRECT_URL__", permanent_redirect_server)
            )

        portal_dir = documented_portal("check-permanent-redirect", "0.1.0", populate)

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code == 0
        output = stdout + stderr
        assert "broken link(s)" not in output.lower()
        assert "redirect" in output.lower()
        assert "index.rst" in output

        report = (portal_dir / "docs" / "_build" / "check-report.txt").read_text()
        assert "Redirected links (1):" in report

    def test_writes_its_report_alongside_the_html_output(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "check-report-location", "0.1.0", _populate_from_fixture("broken_link")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code != 0
        report = portal_dir / "docs" / "_build" / "check-report.txt"
        assert report.exists()
        assert "this-domain-does-not-exist-fairdm-docs-002.invalid" in (
            report.read_text()
        )
        html_dir_report = portal_dir / "docs" / "_build" / "html" / "check-report.txt"
        assert not html_dir_report.exists()


class TestExitCodes:
    def test_check_exits_nonzero_when_no_pyproject(self, tmp_path, run_fairdm_docs):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        exit_code, stdout, stderr = run_fairdm_docs(tmp_path, ["check"])

        assert exit_code != 0
        output = stdout + stderr
        assert "Traceback" not in output
        assert "No pyproject.toml found" in output

    def test_check_exits_nonzero_when_toml_is_malformed(
        self, tmp_path, run_fairdm_docs
    ):
        (tmp_path / "pyproject.toml").write_text("[project\nname = probe\n")
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        exit_code, stdout, stderr = run_fairdm_docs(tmp_path, ["check"])

        assert exit_code != 0
        output = stdout + stderr
        assert "Traceback" not in output
        assert "not valid TOML" in output

    def test_check_exits_nonzero_when_source_dir_missing(
        self, tmp_path, run_fairdm_docs
    ):
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')

        exit_code, stdout, stderr = run_fairdm_docs(tmp_path, ["check"])

        assert exit_code != 0
        output = stdout + stderr
        assert "Traceback" not in output
        assert "Source directory" in output

    def test_check_exits_nonzero_when_port_out_of_range(
        self, tmp_path, run_fairdm_docs
    ):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\n\n[tool.fairdm.docs]\nport = 100000\n'
        )
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        exit_code, stdout, stderr = run_fairdm_docs(tmp_path, ["check"])

        assert exit_code != 0
        output = stdout + stderr
        assert "Traceback" not in output
        assert "port" in output.lower()

    def test_check_exits_nonzero_when_verbosity_invalid(
        self, tmp_path, run_fairdm_docs
    ):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\n\n[tool.fairdm.docs]\nverbosity = "loud"\n'
        )
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        exit_code, stdout, stderr = run_fairdm_docs(tmp_path, ["check"])

        assert exit_code != 0
        output = stdout + stderr
        assert "Traceback" not in output
        assert "verbosity" in output.lower()

    def test_check_exits_zero_on_success(self, documented_portal, run_fairdm_docs):
        portal_dir = documented_portal(
            "exit-codes-check-success", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code == 0
        output = stdout + stderr
        assert "Traceback" not in output


class TestLiveServerCommand:
    def test_build_live_starts_server(self, tmp_path, monkeypatch):
        # Create minimal project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        # Mock subprocess.run to simulate sphinx-autobuild
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            # Mock is_port_available to return True
            with patch("fairdm_docs.cli.is_port_available", return_value=True):
                result = runner.invoke(app, ["build", "--live"])

                # Should call subprocess.run
                assert mock_run.called

                # Check sphinx-autobuild was called with correct arguments
                args = mock_run.call_args[0][0]
                assert "sphinx_autobuild" in " ".join(args)
                assert "--port" in args
                assert "5000" in args  # Default port
                assert "--open-browser" in args

    def test_build_live_checks_port_availability(self, tmp_path, monkeypatch):
        # Create minimal project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        # Mock is_port_available to return True
        with patch(
            "fairdm_docs.cli.is_port_available", return_value=True
        ) as mock_check:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                result = runner.invoke(app, ["build", "--live"])

                # Port availability should be checked
                assert mock_check.called
                assert mock_check.call_args[0][0] == 5000  # Default port

    def test_build_live_error_when_port_occupied(self, tmp_path, monkeypatch):
        # Create minimal project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        # Mock is_port_available to return False (port occupied)
        with patch("fairdm_docs.cli.is_port_available", return_value=False):
            result = runner.invoke(app, ["build", "--live"])

            # Should exit with error
            assert result.exit_code == 1
            # Error messages go to stderr (typer.echo(..., err=True))
            output = result.stdout + result.stderr
            assert "Port 5000 is already in use" in output
            assert "[tool.fairdm.docs]" in output  # Config guidance

    def test_build_live_uses_custom_port_from_config(self, tmp_path, monkeypatch):
        # Create project with custom port configuration
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            "[project]\nname = 'test'\n\n[tool.fairdm.docs]\nport = 8080\n"
        )

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        # Mock subprocess.run
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            with patch("fairdm_docs.cli.is_port_available", return_value=True):
                result = runner.invoke(app, ["build", "--live"])

                # Should use custom port 8080
                args = mock_run.call_args[0][0]
                assert "--port" in args
                port_index = args.index("--port") + 1
                assert args[port_index] == "8080"

    def test_build_live_handles_missing_sphinx_autobuild(self, tmp_path, monkeypatch):
        # Create minimal project structure
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        # Mock subprocess.run to raise FileNotFoundError
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with patch("fairdm_docs.cli.is_port_available", return_value=True):
                result = runner.invoke(app, ["build", "--live"])

                # Should exit with error
                assert result.exit_code == 1
                # Error messages go to stderr
                output = result.stdout + result.stderr
                assert "sphinx-autobuild not found" in output


class TestLivePreview:
    def test_live_launches_against_every_configured_setting(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "live-all-settings", "0.1.0", lambda docs_dir: None
        )
        documentation_dir = portal_dir / "documentation"
        documentation_dir.mkdir()
        (documentation_dir / "index.rst").write_text("Portal\n======\n")

        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "live-all-settings"\nversion = "0.1.0"\n\n'
            "[tool.fairdm.docs]\n"
            'source_dir = "documentation"\n'
            'build_dir = "output/site"\n'
            "port = 8123\n"
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            with patch("fairdm_docs.cli.is_port_available", return_value=True):
                exit_code, stdout, stderr = run_fairdm_docs(
                    portal_dir, ["build", "--live"]
                )

        assert exit_code == 0
        assert mock_run.called
        args = mock_run.call_args[0][0]
        assert "documentation" in args
        assert str(Path("output/site")) in args
        assert "--port" in args
        assert args[args.index("--port") + 1] == "8123"
        assert "--open-browser" in args

    def test_live_stops_before_launching_when_the_configured_port_is_taken(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "live-port-taken", "0.1.0", _populate_from_fixture("single_page")
        )

        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.bind(("", 0))
        blocker.listen(1)
        taken_port = blocker.getsockname()[1]

        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "live-port-taken"\nversion = "0.1.0"\n\n'
            f"[tool.fairdm.docs]\nport = {taken_port}\n"
        )

        try:
            with patch("subprocess.run") as mock_run:
                exit_code, stdout, stderr = run_fairdm_docs(
                    portal_dir, ["build", "--live"]
                )
        finally:
            blocker.close()

        assert exit_code == 1
        mock_run.assert_not_called()
        output = stdout + stderr
        assert str(taken_port) in output
        assert "[tool.fairdm.docs]" in output


class TestInterrupt:
    def test_build_interrupted_exits_130(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")
        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", side_effect=KeyboardInterrupt):
            result = runner.invoke(app, ["build"])

        assert result.exit_code == 130
        output = result.stdout + result.stderr
        assert "Traceback" not in output

    def test_check_interrupted_exits_130(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")
        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", side_effect=KeyboardInterrupt):
            result = runner.invoke(app, ["check"])

        assert result.exit_code == 130
        output = result.stdout + result.stderr
        assert "Traceback" not in output

    def test_live_preview_interrupted_exits_130(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")
        monkeypatch.chdir(tmp_path)

        with patch("fairdm_docs.cli.is_port_available", return_value=True):
            with patch("subprocess.run", side_effect=KeyboardInterrupt):
                result = runner.invoke(app, ["build", "--live"])

        assert result.exit_code == 130
        output = result.stdout + result.stderr
        assert "Traceback" not in output


class TestCLIHelp:
    def test_app_help(self):
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "fairdm-docs" in result.stdout
        assert "build" in result.stdout
        assert "check" in result.stdout

    def test_build_help(self):
        result = runner.invoke(app, ["build", "--help"])

        assert result.exit_code == 0
        assert "Build Sphinx documentation" in result.stdout
        assert "--live" in result.stdout

    def test_check_help(self):
        result = runner.invoke(app, ["check", "--help"])

        assert result.exit_code == 0
        assert "Validate documentation" in result.stdout


class TestSettings:
    def test_source_dir_setting_changes_where_the_build_reads_from(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "custom-source-dir", "0.1.0", lambda docs_dir: None
        )
        documentation_dir = portal_dir / "documentation"
        documentation_dir.mkdir()
        (documentation_dir / "index.rst").write_text(
            "Portal\n======\n\nOnly the documentation directory has this line.\n"
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "custom-source-dir"\nversion = "0.1.0"\n\n'
            '[tool.fairdm.docs]\nsource_dir = "documentation"\n'
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        html = (portal_dir / "docs" / "_build" / "html" / "index.html").read_text()
        assert "Only the documentation directory has this line." in html

    def test_build_dir_setting_changes_where_the_build_writes_to(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "custom-build-dir", "0.1.0", _populate_from_fixture("single_page")
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "custom-build-dir"\nversion = "0.1.0"\n\n'
            '[tool.fairdm.docs]\nbuild_dir = "output/site"\n'
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert (portal_dir / "output" / "site" / "index.html").exists()
        assert not (portal_dir / "docs" / "_build" / "html" / "index.html").exists()

    def test_port_setting_changes_which_port_live_checks(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "custom-port", "0.1.0", _populate_from_fixture("single_page")
        )

        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(("", 0))
        free_port = probe.getsockname()[1]
        probe.close()

        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "custom-port"\nversion = "0.1.0"\n\n'
            f"[tool.fairdm.docs]\nport = {free_port}\n"
        )

        blocked = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocked.bind(("", 5000))
        blocked.listen(1)
        try:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                exit_code, stdout, stderr = run_fairdm_docs(
                    portal_dir, ["build", "--live"]
                )
        finally:
            blocked.close()

        assert exit_code == 0
        assert mock_run.called

    def test_quiet_verbosity_suppresses_informational_output(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "quiet-verbosity",
            "0.1.0",
            lambda docs_dir: (docs_dir / "index.rst").write_text(
                "Portal\n======\n\n.. toctree::\n\n   missing-page\n"
            ),
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "quiet-verbosity"\nversion = "0.1.0"\n\n'
            '[tool.fairdm.docs]\nverbosity = "quiet"\n'
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert "reading sources" not in stdout
        assert "toctree contains reference to nonexisting document" in stderr

    def test_errors_only_verbosity_suppresses_everything_but_errors(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "errors-only-verbosity",
            "0.1.0",
            lambda docs_dir: (docs_dir / "index.rst").write_text(
                "Portal\n======\n\n.. toctree::\n\n   missing-page\n"
            ),
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "errors-only-verbosity"\nversion = "0.1.0"\n\n'
            '[tool.fairdm.docs]\nverbosity = "errors-only"\n'
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert "reading sources" not in stdout
        assert "toctree contains reference to nonexisting document" not in stderr

    def test_django_true_sets_up_django_before_the_build(
        self, documented_portal, monkeypatch, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "django-setting", "0.1.0", _populate_from_fixture("single_page")
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "django-setting"\nversion = "0.1.0"\n\n'
            "[tool.fairdm.docs]\ndjango = true\n"
        )
        (portal_dir / "portal_django_settings.py").write_text(
            "SECRET_KEY = 'not-a-secret'\nINSTALLED_APPS = []\n"
        )
        monkeypatch.syspath_prepend(str(portal_dir))
        monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "portal_django_settings")

        import django
        from django.apps import apps as django_apps

        with patch("django.setup", wraps=django.setup) as mock_setup:
            exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert mock_setup.called
        assert django_apps.ready

    def test_django_false_leaves_django_untouched(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "django-untouched", "0.1.0", _populate_from_fixture("single_page")
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "django-untouched"\nversion = "0.1.0"\n\n'
            "[tool.fairdm.docs]\ndjango = false\n"
        )

        with patch("django.setup") as mock_setup:
            exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert not mock_setup.called

    def test_no_table_uses_every_documented_default(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "no-table", "0.1.0", _populate_from_fixture("single_page")
        )

        from sphinx.cmd.build import main as real_sphinx_build

        recorder = SphinxRecorder(delegate=real_sphinx_build)
        with patch("sphinx.cmd.build.main", side_effect=recorder):
            exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert (portal_dir / "docs" / "_build" / "html" / "index.html").exists()
        assert "build succeeded" in stdout
        assert recorder.seen["FAIRDM_DOCS_DJANGO"] == "false"

        from fairdm_docs.config import load_config

        config = load_config()
        assert config.port == 5000

    def test_partial_table_overrides_only_the_named_setting(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal(
            "partial-override", "0.1.0", _populate_from_fixture("single_page")
        )
        (portal_dir / "pyproject.toml").write_text(
            '[project]\nname = "partial-override"\nversion = "0.1.0"\n\n'
            "[tool.fairdm.docs]\nport = 9000\n"
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert (portal_dir / "docs" / "_build" / "html" / "index.html").exists()

        from fairdm_docs.config import load_config

        config = load_config()
        assert config.port == 9000
        assert config.source_dir == Path("docs")
        assert config.build_dir == Path("docs/_build/html")
