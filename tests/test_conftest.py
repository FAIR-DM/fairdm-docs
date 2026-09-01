"""Tests for the shared test infrastructure in conftest.py.

These prove the fixtures other stories build their own tests on behave as
their given/when/then contracts require, since nothing else exercises them
directly.
"""

from pathlib import Path


class TestDocumentedPortal:
    """`documented_portal` writes a temporary portal from a name, a version and a
    documentation-source callback."""

    def test_pyproject_declares_the_given_name_and_version(self, documented_portal):
        portal_dir = documented_portal("acme-docs", "1.2.3", lambda docs_dir: None)

        pyproject = (portal_dir / "pyproject.toml").read_text()

        assert 'name = "acme-docs"' in pyproject
        assert 'version = "1.2.3"' in pyproject

    def test_docs_directory_is_populated_by_the_caller(self, documented_portal):
        def populate(docs_dir: Path) -> None:
            (docs_dir / "index.rst").write_text("Portal\n======\n")

        portal_dir = documented_portal("acme-docs", "1.2.3", populate)

        assert (portal_dir / "docs" / "index.rst").read_text() == "Portal\n======\n"


def _populate_minimal_docs(docs_dir: Path) -> None:
    """A documentation source with its own conf.py, avoiding the package's
    default Sphinx theme so a real build needs no branding assets."""
    (docs_dir / "conf.py").write_text('project = "test"\n')
    (docs_dir / "index.rst").write_text("Portal\n======\n")


class TestRunFairdmDocs:
    """`run_fairdm_docs` invokes the CLI for real: sets sys.argv, calls
    `fairdm_docs.cli.main()`, and catches the `SystemExit` it raises."""

    def test_build_runs_for_real_and_reports_success(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal("acme-docs", "1.0.0", _populate_minimal_docs)

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["build"])

        assert exit_code == 0
        assert "Build complete" in stdout
        assert (portal_dir / "docs" / "_build" / "html" / "index.html").exists()

    def test_check_runs_for_real_and_reports_success(
        self, documented_portal, run_fairdm_docs
    ):
        portal_dir = documented_portal("acme-docs", "1.0.0", _populate_minimal_docs)

        exit_code, stdout, stderr = run_fairdm_docs(portal_dir, ["check"])

        assert exit_code == 0
        assert "valid" in stdout.lower()
