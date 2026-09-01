"""
Tests for CLI commands.

Tests the build and check commands using Typer's CliRunner
for isolated testing.
"""

import os
import shutil
import socket
import sys
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fairdm_docs.cli import app
from fairdm_docs.metadata import ProjectMetadata

runner = CliRunner()

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _populate_from_fixture(name: str):
    """A `documented_portal` populate callback that copies a documentation
    source from tests/fixtures/<name>/ into the portal's docs/ directory."""

    def populate(docs_dir: Path) -> None:
        for item in (FIXTURES_DIR / name).iterdir():
            shutil.copy(item, docs_dir / item.name)

    return populate


class TestBuildCommand:
    """Test the build command functionality."""

    def test_build_with_defaults(self, tmp_path, monkeypatch):
        """Test building documentation with default configuration."""
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
        """Test that build creates output directory if it doesn't exist."""
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
        """Test that build shows progress messages to user."""
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
        """Test that successful build exits with code 0."""
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
        """Test that build errors when pyproject.toml not found."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["build"])

        # Should exit with error
        assert result.exit_code == 1

        # Should show clear error message (can be in stdout or stderr)
        output = result.stdout + result.stderr
        assert "No pyproject.toml found" in output
        assert "Run this command from your project root" in output

    def test_build_error_when_source_missing(self, tmp_path, monkeypatch):
        """Test that build errors when source directory doesn't exist."""
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
        """Test building with custom source directory from config (T067)."""
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
        """Test building with custom build directory from config (T066)."""
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
        """Test build with quiet verbosity setting."""
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
        """Test build with errors-only verbosity setting."""
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
        """Test that Sphinx build failure returns non-zero exit code."""
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
        """Test that build uses package's built-in conf.py."""
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
        """Test that Django environment variable is set to false by default."""
        import os

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Test")

        monkeypatch.chdir(tmp_path)

        with patch("sphinx.cmd.build.main", return_value=0):
            runner.invoke(app, ["build"])

            # Django env var should be set to false
            assert os.environ.get("FAIRDM_DOCS_DJANGO") == "false"

    def test_build_sets_django_env_var_true_when_enabled(self, tmp_path, monkeypatch):
        """Test that Django environment variable is set to true when enabled in config."""
        import os

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

        with patch("sphinx.cmd.build.main", return_value=0):
            runner.invoke(app, ["build"])

            # Django env var should be set to true
            assert os.environ.get("FAIRDM_DOCS_DJANGO") == "true"


class TestBuild:
    """Real, end-to-end `fairdm-docs build` runs, via `run_fairdm_docs` rather
    than a mocked `sphinx.cmd.build.main` (constitution Article IV).
    `TestBuildCommand` above proves the argv Sphinx is handed; this class
    proves the build itself works."""

    def test_renders_a_root_page_to_html(self, documented_portal, run_fairdm_docs):
        """T004: a documentation source with a root page and zero
        configuration renders a site whose HTML carries the page's own
        content."""
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
        """T005: a documentation source with its own docs/conf.py is built
        with that configuration, not the package's."""
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
        """T006: a documentation source with no conf.py of its own still
        builds, using the package's own fairdm_docs/conf.py."""
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
        """T007: the build directory's parent is created if it does not
        already exist, without the test pre-creating it."""
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
        """T008: the command's own output names the build as started and, on
        success, names where the site was written."""
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
        """T009: the default (full) verbosity does not suppress Sphinx's own
        build output, unlike the existing mocked quiet/errors-only tests,
        which only prove the -q/-Q flags are passed."""
        portal_dir = documented_portal(
            "full-verbosity", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert "build succeeded" in stdout

    def test_sets_fairdm_docs_project_dir_to_the_portals_own_directory(
        self, documented_portal, run_fairdm_docs
    ):
        """T010 (S3R SPEC-001): FAIRDM_DOCS_PROJECT_DIR, the mechanism FR-004
        names, is set to the invoking portal's own directory during a real
        build, not the package's, not something else."""
        portal_dir = documented_portal(
            "project-dir-env-var", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert os.environ["FAIRDM_DOCS_PROJECT_DIR"] == str(portal_dir.resolve())


class TestConfigurationValidationErrors:
    """Test configuration validation error messages."""

    def test_invalid_port_shows_clear_error(self, tmp_path, monkeypatch):
        """Test that invalid port triggers clear error message (T072)."""
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
        """Test that invalid verbosity triggers clear error message (T073)."""
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
        """Test that config validation errors have clear format (T071)."""
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
    """A project-metadata failure is reported as a message, not a traceback (T026)."""

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
        """T012: a pyproject.toml that isn't valid TOML stops the command
        with a message naming the file as unreadable, never a traceback."""
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
    """Test the check command functionality."""

    def test_check_passes_with_no_errors(self, tmp_path, monkeypatch):
        """Test check command with valid links (T061)."""
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
        """Test check command detects broken links (T062)."""
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
        """Test check command exits with code 0 when no errors (T063)."""
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
        """Test check command exits with code 1 when errors found (T064)."""
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
        """Test check command displays file locations for broken links (T065)."""
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


class TestExitCodes:
    """T017: every configuration failure (T011-T015) exits non-zero through
    `check`, not just `build` — the existing coverage in TestBuildCommand,
    TestConfigurationValidationErrors and TestConfigurationFailures only
    invokes `build` (S3R REC-001). Runs through the real `run_fairdm_docs`
    fixture rather than a mocked Sphinx, per constitution Article IV."""

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
        """A successful `build` exiting 0 is already proven exhaustively by
        TestBuild (US1); `check` has no equivalent real-invocation coverage
        yet, only the mocked-Sphinx one in TestCheckCommand."""
        portal_dir = documented_portal(
            "exit-codes-check-success", "0.1.0", _populate_from_fixture("single_page")
        )

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code == 0
        output = stdout + stderr
        assert "Traceback" not in output


class TestLiveServerCommand:
    """Test the build --live command functionality."""

    def test_build_live_starts_server(self, tmp_path, monkeypatch):
        """Test that --live flag starts sphinx-autobuild server (T048)."""
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
        """Test that live server checks port availability before starting (T049)."""
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
        """Test error handling when port is already in use (T050)."""
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
        """Test that live server uses custom port from config (T051)."""
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
        """Test error handling when sphinx-autobuild is not installed."""
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


class TestInterrupt:
    """T018: an interrupt during an ordinary build, a live preview, or a
    check stops the command without a traceback and exits 130 in every
    mode (D6). Each mocks the narrowest point that can raise
    KeyboardInterrupt (`sphinx.cmd.build.main` or `subprocess.run`), per
    constitution Article IV."""

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
        """Currently fails: the live-mode handler at cli.py's ~line 147
        exits 0 today, which is the D6 defect T019 fixes."""
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
    """Test CLI help output."""

    def test_app_help(self):
        """Test main app help message."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "fairdm-docs" in result.stdout
        assert "build" in result.stdout
        assert "check" in result.stdout

    def test_build_help(self):
        """Test build command help message."""
        result = runner.invoke(app, ["build", "--help"])

        assert result.exit_code == 0
        assert "Build Sphinx documentation" in result.stdout
        assert "--live" in result.stdout

    def test_check_help(self):
        """Test check command help message."""
        result = runner.invoke(app, ["check", "--help"])

        assert result.exit_code == 0
        assert "Validate documentation" in result.stdout


class TestSettings:
    """Real, end-to-end proof that each `[tool.fairdm.docs]` setting changes
    build behaviour, and that a setting a portal does not name keeps its
    documented default (FR-015 through FR-019, SC-003). `TestBuildCommand`
    above proves the argv Sphinx is handed for these settings; this class
    proves the settings actually change what the build does."""

    def test_source_dir_setting_changes_where_the_build_reads_from(
        self, documented_portal, run_fairdm_docs
    ):
        """T020: source_dir named in the table is read from instead of the
        default docs/ — proven by content that exists only there, not just
        that the build succeeded."""
        portal_dir = documented_portal("custom-source-dir", "0.1.0", lambda docs_dir: None)
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
