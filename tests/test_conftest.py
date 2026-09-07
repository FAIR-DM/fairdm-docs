"""Tests for the shared test infrastructure in conftest.py.

These prove the fixtures other stories build their own tests on behave as
their given/when/then contracts require, since nothing else exercises them
directly.
"""

from http.client import HTTPConnection
from pathlib import Path
from urllib.parse import urlsplit


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


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestDocumentationSourceFixtures:
    """The shared documentation sources under tests/fixtures/, used by the
    stories that build on this one to prove US1, US3 and US5's scenarios."""

    def test_single_page_has_only_a_root_index(self):
        source = FIXTURES_DIR / "single_page"

        assert [p.name for p in source.iterdir()] == ["index.rst"]

    def test_broken_link_points_at_a_domain_that_will_not_resolve(self):
        content = (FIXTURES_DIR / "broken_link" / "index.rst").read_text()

        assert "this-domain-does-not-exist-fairdm-docs-002.invalid" in content

    def test_redirected_link_has_a_placeholder_for_the_test_server_url(self):
        content = (FIXTURES_DIR / "redirected_link" / "index.rst").read_text()

        assert "__REDIRECT_URL__" in content

    def test_with_own_conf_ships_its_own_conf_py(self):
        source = FIXTURES_DIR / "with_own_conf"

        assert (source / "conf.py").exists()
        assert (source / "index.rst").exists()


class TestRedirectServer:
    """The tiny http.server-based fixture that serves a redirect for the
    `redirected_link` source, with no new dependency."""

    def test_responds_with_a_302_redirect(self, redirect_server):
        parts = urlsplit(redirect_server)
        connection = HTTPConnection(parts.hostname, parts.port)

        connection.request("GET", parts.path or "/")
        response = connection.getresponse()

        assert response.status == 302
        assert response.getheader("Location")
