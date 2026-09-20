"""Tests for generating a front page when a documentation source has none."""

from pathlib import Path

import pytest

from fairdm_docs.frontpage import GeneratedFrontPage
from fairdm_docs.metadata import ProjectMetadata


def _metadata(**overrides) -> ProjectMetadata:
    fields = {
        "name": "acme-portal",
        "version": "1.0.0",
        "description": "A portal for testing.",
        "authors": ["Ada"],
        "homepage": "",
        "repository": "",
    }
    fields.update(overrides)
    return ProjectMetadata(**fields)


class TestHasRootDocument:
    def test_true_for_an_rst_root_document(self, tmp_path: Path):
        (tmp_path / "index.rst").write_text("Portal\n======\n")
        assert GeneratedFrontPage(tmp_path, _metadata()).has_root_document() is True

    def test_true_for_a_markdown_root_document(self, tmp_path: Path):
        (tmp_path / "index.md").write_text("# Portal\n")
        assert GeneratedFrontPage(tmp_path, _metadata()).has_root_document() is True

    def test_false_with_no_root_document(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        assert GeneratedFrontPage(tmp_path, _metadata()).has_root_document() is False


class TestDiscoverDocnames:
    def test_finds_pages_at_the_top_level(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        (tmp_path / "reference.rst").write_text("Reference\n=========\n")
        page = GeneratedFrontPage(tmp_path, _metadata())
        assert page.discover_docnames() == ["guide", "reference"]

    def test_finds_pages_in_subdirectories(self, tmp_path: Path):
        (tmp_path / "howto").mkdir()
        (tmp_path / "howto" / "install.md").write_text("# Install\n")
        page = GeneratedFrontPage(tmp_path, _metadata())
        assert page.discover_docnames() == ["howto/install"]

    def test_excludes_the_root_document_itself(self, tmp_path: Path):
        (tmp_path / "index.md").write_text("# Portal\n")
        (tmp_path / "guide.md").write_text("# Guide\n")
        page = GeneratedFrontPage(tmp_path, _metadata())
        assert page.discover_docnames() == ["guide"]

    def test_excludes_static_and_template_and_build_directories(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        (tmp_path / "_static").mkdir()
        (tmp_path / "_static" / "custom.md").write_text("not a page\n")
        (tmp_path / "_templates").mkdir()
        (tmp_path / "_templates" / "layout.md").write_text("not a page\n")
        (tmp_path / "_build").mkdir()
        (tmp_path / "_build" / "html.md").write_text("not a page\n")
        page = GeneratedFrontPage(tmp_path, _metadata())
        assert page.discover_docnames() == ["guide"]

    def test_excludes_hidden_directories(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        (tmp_path / ".hidden").mkdir()
        (tmp_path / ".hidden" / "secret.md").write_text("not a page\n")
        page = GeneratedFrontPage(tmp_path, _metadata())
        assert page.discover_docnames() == ["guide"]

    def test_ignores_files_that_are_not_documentation_pages(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        (tmp_path / "conf.py").write_text("project = 'x'\n")
        (tmp_path / "logo.svg").write_text("<svg></svg>\n")
        page = GeneratedFrontPage(tmp_path, _metadata())
        assert page.discover_docnames() == ["guide"]

    def test_empty_source_returns_no_docnames(self, tmp_path: Path):
        page = GeneratedFrontPage(tmp_path, _metadata())
        assert page.discover_docnames() == []


class TestRender:
    def test_carries_the_name_and_description(self, tmp_path: Path):
        rendered = GeneratedFrontPage(tmp_path, _metadata()).render()
        assert "acme-portal" in rendered
        assert "A portal for testing." in rendered

    def test_links_every_discovered_page(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        (tmp_path / "howto").mkdir()
        (tmp_path / "howto" / "install.md").write_text("# Install\n")
        rendered = GeneratedFrontPage(tmp_path, _metadata()).render()
        assert "guide" in rendered
        assert "howto/install" in rendered
        assert "{toctree}" in rendered

    def test_omits_the_toctree_when_there_are_no_other_pages(self, tmp_path: Path):
        rendered = GeneratedFrontPage(tmp_path, _metadata()).render()
        assert "{toctree}" not in rendered

    def test_omits_a_blank_description_line_when_none_is_declared(self, tmp_path: Path):
        rendered = GeneratedFrontPage(tmp_path, _metadata(description="")).render()
        lines = [line for line in rendered.splitlines() if line.strip()]
        assert lines == ["# acme-portal"]


class TestGeneratedFrontPageAsAContextManager:
    def test_generates_an_index_when_none_exists(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        with GeneratedFrontPage(tmp_path, _metadata()):
            generated = (tmp_path / "index.md").read_text()
            assert "acme-portal" in generated
            assert "guide" in generated

    def test_removes_the_generated_index_after_the_build(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        with GeneratedFrontPage(tmp_path, _metadata()):
            pass
        assert not (tmp_path / "index.md").exists()

    def test_removes_the_generated_index_even_if_the_build_raises(self, tmp_path: Path):
        (tmp_path / "guide.md").write_text("# Guide\n")
        with pytest.raises(RuntimeError):
            with GeneratedFrontPage(tmp_path, _metadata()):
                raise RuntimeError("build failed")
        assert not (tmp_path / "index.md").exists()

    def test_leaves_a_developers_own_rst_root_document_untouched(self, tmp_path: Path):
        (tmp_path / "index.rst").write_text("Portal\n======\n\nMine.\n")
        with GeneratedFrontPage(tmp_path, _metadata()):
            assert (tmp_path / "index.rst").read_text() == "Portal\n======\n\nMine.\n"
        assert (tmp_path / "index.rst").read_text() == "Portal\n======\n\nMine.\n"

    def test_never_writes_or_removes_a_developers_own_markdown_root_document(
        self, tmp_path: Path
    ):
        (tmp_path / "index.md").write_text("# Mine\n")
        with GeneratedFrontPage(tmp_path, _metadata()):
            assert (tmp_path / "index.md").read_text() == "# Mine\n"
        # A developer's own index.md survives exit exactly as it did entry —
        # the page this context manager did not generate is never its to
        # remove.
        assert (tmp_path / "index.md").read_text() == "# Mine\n"
