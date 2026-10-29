"""Tests for the values fairdm_docs.conf assigns from the portal's declared identity."""

import io
import os
import sys

import pytest
from sphinx.application import Sphinx
from sphinx.errors import ConfigError as SphinxConfigError
from sphinx.errors import ThemeError


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

        assert [link["url"] for link in conf.html_theme_options["icon_links"]] == [
            "https://github.com/example/sample-portal"
        ]

    def test_a_declared_title_names_the_site(self, portal):
        portal_dir = portal(
            """
[project]
name = "django-literature"

[tool.fairdm.docs]
title = "Django Literature"
"""
        )

        conf = load_site_config(portal_dir)

        assert conf.project == "Django Literature"
        assert conf.html_title == "Django Literature"

    def test_without_a_title_the_site_is_named_by_the_distribution(self, portal):
        portal_dir = portal(
            """
[project]
name = "django-literature"
"""
        )

        conf = load_site_config(portal_dir)

        assert conf.project == "django-literature"


class TestRenderedSite:
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
        # The API-documentation extension has nothing to document until R4
        # wires package discovery, so it stays out of the build rather than
        # warning about a setting the developer has no way to fill in.
        assert "autodoc2" not in output

    def test_no_repository_address_renders_no_repository_furniture(self, built_portal):
        html, output = built_portal(
            """
[project]
name = "sample-portal"
"""
        )

        assert "repository" not in html.lower()
        assert "issue" not in html.lower()
        assert "Extension error" not in output

    def test_a_declared_repository_address_renders_repository_furniture(
        self, built_portal
    ):
        html, _ = built_portal(
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

        assert 'href="https://github.com/example/sample-portal"' in html


def start_building(docs_dir, outdir, warning=None):
    """Construct a real Sphinx application against docs_dir, as a build would."""
    sys.modules.pop("fairdm_docs.conf", None)
    return Sphinx(
        srcdir=str(docs_dir),
        confdir=str(docs_dir),
        outdir=str(outdir / "html"),
        doctreedir=str(outdir / "doctrees"),
        buildername="html",
        status=io.StringIO(),
        warning=warning if warning is not None else io.StringIO(),
    )


class TestConfigurationFailures:
    def test_invalid_toml_is_reported_without_a_traceback(self, portal):
        portal_dir = portal("[project\nname = 'broken'")

        with pytest.raises(SphinxConfigError) as exc_info:
            start_building(portal_dir / "docs", portal_dir / "_build")

        message = str(exc_info.value)
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



REPOSITORY = "https://github.com/example/sample-portal"


def declaration(docs_table: str = "", repository: str = REPOSITORY) -> str:
    """A portal declaring a repository address, with an optional [tool.fairdm.docs] body."""
    urls = f'\n[project.urls]\nRepository = "{repository}"\n' if repository else ""
    docs = f"\n[tool.fairdm.docs]\n{docs_table}" if docs_table else ""
    return f'[project]\nname = "sample-portal"\n{urls}{docs}'


class TestThemeSelection:
    def test_the_default_theme_is_pydata(self, portal):
        conf = load_site_config(portal(declaration()))

        assert conf.html_theme == "pydata_sphinx_theme"

    def test_a_declared_theme_is_used_as_written(self, built_portal):
        html, _ = built_portal(declaration('theme = "alabaster"\n'))

        assert "alabaster.css" in html

    def test_a_theme_that_is_not_installed_fails_with_sphinxs_own_error(
        self, portal
    ):
        portal_dir = portal(declaration('theme = "no_such_theme"\n'))

        with pytest.raises(ThemeError):
            start_building(portal_dir / "docs", portal_dir / "_build")

    def test_another_theme_gets_no_settings_of_this_packages_own(self, portal):
        conf = load_site_config(portal(declaration('theme = "alabaster"\n')))

        assert conf.html_theme_options == {}
        assert conf.html_css_files == []


class TestThemeOptionsTable:
    def test_declared_options_replace_only_the_keys_they_name(self, portal):
        defaults = dict(load_site_config(portal(declaration())).html_theme_options)

        conf = load_site_config(
            portal(
                declaration(
                    "\n[tool.fairdm.docs.theme_options]\n"
                    "header_links_before_dropdown = 8\n"
                )
            )
        )

        assert conf.html_theme_options == {
            **defaults,
            "header_links_before_dropdown": 8,
        }

    def test_declared_options_apply_under_another_theme(self, portal):
        conf = load_site_config(
            portal(
                declaration(
                    'theme = "alabaster"\n'
                    "\n[tool.fairdm.docs.theme_options]\n"
                    'description = "A portal"\n'
                )
            )
        )

        assert conf.html_theme_options == {"description": "A portal"}

    def test_options_that_are_not_a_table_are_reported_without_a_traceback(
        self, portal
    ):
        portal_dir = portal(declaration("theme_options = 8\n"))

        with pytest.raises(SphinxConfigError) as exc_info:
            start_building(portal_dir / "docs", portal_dir / "_build")

        assert "theme_options" in str(exc_info.value)
        assert "Traceback" not in str(exc_info.value)


class TestUnknownSettings:
    def test_an_unknown_key_is_reported_in_the_build_output(self, built_portal):
        _, output = built_portal(declaration('colour_scheme = "dark"\n'))

        assert "colour_scheme" in output

    def test_the_commands_own_keys_are_not_reported(self, built_portal):
        _, output = built_portal(
            declaration(
                'source_dir = "docs"\nbuild_dir = "docs/_build/html"\n'
                'verbosity = "quiet"\n'
            )
        )

        assert "source_dir" not in output
        assert "build_dir" not in output
        assert "verbosity" not in output


class TestPyDataNavbar:
    def test_the_repository_gets_one_github_icon(self, built_portal):
        html, _ = built_portal(declaration())

        # The theme draws the navbar a second time in the narrow-screen sidebar.
        header = html[html.index("<header") : html.index("</header>")]
        assert header.count("fa-brands fa-github") == 1

    def test_a_changelog_is_linked_from_the_navbar(self, tmp_path, built_portal):
        (tmp_path / "CHANGELOG.md").write_text("# Changelog\n")

        html, _ = built_portal(declaration())

        assert f'href="{REPOSITORY}/blob/main/CHANGELOG.md"' in html

    def test_no_changelog_file_means_no_changelog_link(self, portal):
        conf = load_site_config(portal(declaration()))

        assert "external_links" not in conf.html_theme_options

    def test_no_repository_address_means_no_changelog_link(self, tmp_path, portal):
        (tmp_path / "CHANGELOG.md").write_text("# Changelog\n")

        conf = load_site_config(portal(declaration(repository="")))

        assert "external_links" not in conf.html_theme_options

    def test_the_current_page_stylesheet_is_shipped_and_linked(
        self, tmp_path, portal, built_portal
    ):
        stylesheet = load_site_config(portal(declaration())).NAVBAR_STYLESHEET

        html, _ = built_portal(declaration())

        assert (tmp_path / "_build" / "html" / "_static" / stylesheet).exists()
        assert f"_static/{stylesheet}" in html


class TestHeadingAnchors:
    def test_a_link_to_a_section_of_another_page_resolves(self, portal):
        portal_dir = portal(declaration())
        docs_dir = portal_dir / "docs"
        (docs_dir / "index.rst").unlink()
        (docs_dir / "index.md").write_text(
            "# Portal\n\n[Install](installation.md#install-the-front-end)\n\n"
            "```{toctree}\ninstallation\n```\n"
        )
        (docs_dir / "installation.md").write_text(
            "# Installation\n\n## Install the front end\n\nText.\n"
        )

        warnings = io.StringIO()
        start_building(docs_dir, portal_dir / "_build", warnings).build()

        assert "install-the-front-end" not in warnings.getvalue()
