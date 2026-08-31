"""Tests for the values fairdm_docs.conf assigns from the portal's declared identity."""

import io
import os
import sys

import pytest
from sphinx.application import Sphinx
from sphinx.errors import ConfigError as SphinxConfigError


def load_site_config(portal_dir):
    """Import fairdm_docs.conf fresh, as Sphinx would, with cwd set to the portal's docs directory."""
    sys.modules.pop("fairdm_docs.conf", None)
    docs_dir = portal_dir / "docs"
    previous_cwd = os.getcwd()
    os.chdir(docs_dir)
    try:
        import fairdm_docs.conf as conf

        return conf
    finally:
        os.chdir(previous_cwd)


class TestSiteIdentity:
    """The Sphinx namespace fairdm_docs.conf assigns from ProjectMetadata."""

    @pytest.mark.parametrize("name", ["GHFDB", "sample-portal"])
    def test_project_is_the_declared_name_verbatim(self, portal, name):
        portal_dir = portal(
            {
                "project": {
                    "name": name,
                    "version": "1.0.0",
                    "description": "",
                    "authors": ["Jane Doe"],
                }
            }
        )

        conf = load_site_config(portal_dir)

        assert conf.project == name

    def test_version_and_release_are_the_declared_version(self, portal):
        portal_dir = portal(
            """
[project]
name = "sample-portal"
version = "3.1.4"
description = ""
authors = ["Jane Doe"]
"""
        )

        conf = load_site_config(portal_dir)

        assert conf.version == "3.1.4"
        assert conf.release == "3.1.4"

    def test_author_and_copyright_are_built_from_the_declared_authors(self, portal):
        portal_dir = portal(
            """
[project]
name = "sample-portal"
version = "1.0.0"
description = ""
authors = ["Jane Doe <jane@example.com>", "John Smith"]
"""
        )

        conf = load_site_config(portal_dir)

        assert conf.author == "Jane Doe, John Smith"
        assert "Jane Doe, John Smith" in conf.copyright

    def test_repository_address_reaches_the_theme_configuration(self, portal):
        portal_dir = portal(
            {
                "project": {
                    "name": "sample-portal",
                    "version": "1.0.0",
                    "description": "",
                    "authors": ["Jane Doe"],
                    "urls": {"Repository": "https://github.com/example/sample-portal"},
                }
            }
        )

        conf = load_site_config(portal_dir)

        assert (
            conf.html_theme_options["repository_url"]
            == "https://github.com/example/sample-portal"
        )


class TestRenderedSite:
    """A real build of a portal whose identity is fully declared."""

    def test_title_version_and_copyright_reach_the_rendered_html(self, built_portal):
        html, _ = built_portal(
            """
[project]
name = "sample-portal"
version = "1.2.3"
description = "A sample research data portal"
authors = ["Jane Doe <jane@example.com>"]
"""
        )

        assert "sample-portal" in html
        assert "1.2.3" in html
        assert "Jane Doe" in html

    def test_a_declaration_with_only_a_name_still_builds(self, built_portal):
        _, output = built_portal(
            """
[project]
name = "sample-portal"
"""
        )

        assert "version" in output
        assert "authors" in output
        assert "description" in output


def start_building(docs_dir, outdir):
    """Construct a real Sphinx application against docs_dir, as a build would."""
    sys.modules.pop("fairdm_docs.conf", None)
    return Sphinx(
        srcdir=str(docs_dir),
        confdir=str(docs_dir),
        outdir=str(outdir / "html"),
        doctreedir=str(outdir / "doctrees"),
        buildername="html",
        status=io.StringIO(),
        warning=io.StringIO(),
    )


class TestConfigurationFailures:
    """A real build reports a project-metadata failure as a message, not a traceback (T032a)."""

    def test_invalid_toml_is_reported_without_a_traceback(self, portal):
        portal_dir = portal("[project\nname = 'broken'")

        with pytest.raises(SphinxConfigError) as exc_info:
            start_building(portal_dir / "docs", portal_dir / "_build")

        message = str(exc_info.value)
        assert "TOML" in message
        assert "syntax" in message.lower()
        assert "Traceback" not in message

    def test_missing_pyproject_is_reported_without_a_traceback(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.rst").write_text("Portal\n======\n")
        (docs_dir / "conf.py").write_text("from fairdm_docs.conf import *\n")

        with pytest.raises(SphinxConfigError) as exc_info:
            start_building(docs_dir, tmp_path / "_build")

        message = str(exc_info.value)
        assert "Traceback" not in message
