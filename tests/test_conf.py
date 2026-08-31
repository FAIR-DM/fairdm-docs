"""Tests for the values fairdm_docs.conf assigns from the portal's declared identity."""

import os
import sys

import pytest


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
