"""Tests for fairdm_docs.utils.

The search runs upward from the current working directory, which is why every
test here changes into a directory it has just built. Sphinx executes conf.py
with the working directory set to the configuration directory, so this is the
real condition the code meets.
"""

import pytest

from fairdm_docs.utils import find_pyproject_toml, load_pyproject_toml


class TestFindPyprojectToml:
    """Locating a project's pyproject.toml from somewhere inside it."""

    def test_finds_it_from_the_docs_directory(self, tmp_path, monkeypatch):
        """Searches upward from the documentation source directory."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test-project"\nversion = "0.1.0"\n')

        monkeypatch.chdir(docs_dir)
        result = find_pyproject_toml()

        assert result is not None
        assert result.exists()
        assert result.name == "pyproject.toml"
        assert result.parent == tmp_path

    def test_finds_it_from_a_deeply_nested_directory(self, tmp_path, monkeypatch):
        """Searches more than one level upward."""
        nested_dir = tmp_path / "docs" / "_build" / "html"
        nested_dir.mkdir(parents=True)

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test-project"\n')

        monkeypatch.chdir(nested_dir)
        result = find_pyproject_toml()

        assert result is not None
        assert result.parent == tmp_path

    def test_returns_none_when_there_is_none(self, tmp_path, monkeypatch):
        """Returns None rather than raising when the search reaches the root."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        monkeypatch.chdir(empty_dir)

        assert find_pyproject_toml() is None


class TestLoadPyprojectToml:
    """Reading a located pyproject.toml."""

    def test_raises_when_there_is_none(self, tmp_path, monkeypatch):
        """Loading is the strict counterpart of finding: absence is an error."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        monkeypatch.chdir(empty_dir)

        with pytest.raises(FileNotFoundError, match=r"pyproject\.toml not found"):
            load_pyproject_toml()
