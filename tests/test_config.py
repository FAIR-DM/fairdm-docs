"""
Tests for configuration loading and validation.

Tests the BuildConfiguration dataclass, pyproject.toml parsing,
configuration merging, and validation rules.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fairdm_docs.config import (
    ERROR_MESSAGES,
    BuildConfiguration,
    ConfigError,
    load_config,
    load_pyproject,
    validate_config,
)
from fairdm_docs.utils import find_pyproject_toml


class TestConfigurationLoading:
    def test_build_configuration_defaults(self):
        config = BuildConfiguration()

        assert config.source_dir == Path("docs")
        assert config.build_dir == Path("docs/_build/html")
        assert config.port == 5000
        assert config.verbosity == "full"
        assert config.django is False  # Django should be disabled by default

    def test_find_pyproject_in_current_dir(self, tmp_path, monkeypatch):
        # Create a pyproject.toml in temp directory
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        found = find_pyproject_toml()
        assert found == pyproject
        assert found.exists()

    def test_find_pyproject_in_parent_dir(self, tmp_path, monkeypatch):
        # Create pyproject.toml in parent
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        # Create subdirectory and change to it
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        found = find_pyproject_toml()
        assert found == pyproject

    def test_find_pyproject_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        found = find_pyproject_toml()
        assert found is None

    def test_load_pyproject_success(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test-project"
version = "1.0.0"
        """)

        monkeypatch.chdir(tmp_path)

        data = load_pyproject()
        assert data["project"]["name"] == "test-project"
        assert data["project"]["version"] == "1.0.0"

    def test_load_pyproject_raises_when_missing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ConfigError):
            load_pyproject()

    def test_load_config_with_defaults(self, tmp_path, monkeypatch):
        # Create minimal pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"
        """)

        # Create expected source directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        config = load_config()

        # Should have default values
        assert config.source_dir == Path("docs")
        assert config.build_dir == Path("docs/_build/html")
        assert config.port == 5000
        assert config.verbosity == "full"

    def test_load_config_with_custom_values(self, tmp_path, monkeypatch):
        # Create pyproject.toml with custom config
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
source_dir = "documentation"
build_dir = "build/html"
port = 8080
verbosity = "quiet"
        """)

        # Create custom source directory
        docs_dir = tmp_path / "documentation"
        docs_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        config = load_config()

        # Should have custom values
        assert config.source_dir == Path("documentation")
        assert config.build_dir == Path("build/html")
        assert config.port == 8080
        assert config.verbosity == "quiet"

    def test_load_config_validates_source_dir(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"
        """)

        # Don't create docs/ directory
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ConfigError):
            load_config()

    def test_load_config_validates_port_range(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
port = 99999
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        error_msg = str(exc_info.value)
        assert "99999" in error_msg

    def test_load_config_validates_verbosity(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
verbosity = "invalid-level"
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        error_msg = str(exc_info.value)
        assert "invalid-level" in error_msg

    def test_no_pyproject_raises_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ConfigError):
            load_config()

    def test_user_config_overrides_defaults(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
port = 7000
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        config = load_config()

        # User-specified port should override default
        assert config.port == 7000
        # Other values should remain default
        assert config.source_dir == Path("docs")
        assert config.verbosity == "full"

    def test_load_config_with_django_enabled(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"

[tool.fairdm.docs]
django = true
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        config = load_config()

        # Django should be enabled
        assert config.django is True

    def test_load_config_django_disabled_by_default(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"
        """)

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        config = load_config()

        # Django should be disabled by default
        assert config.django is False


class TestConfigurationValidation:
    def test_validate_config_success(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        config = BuildConfiguration(
            source_dir=docs_dir,
            build_dir=tmp_path / "build",
            port=5000,
            verbosity="full",
        )

        # Should not raise
        validate_config(config)

    def test_validate_missing_source_dir(self):
        config = BuildConfiguration(
            source_dir=Path("/nonexistent/path"),
        )

        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)

        error_msg = str(exc_info.value)
        assert "/nonexistent/path" in error_msg

    def test_validate_port_too_low(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        config = BuildConfiguration(
            source_dir=docs_dir,
            port=500,  # Below minimum
        )

        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)

        assert "500" in str(exc_info.value)

    def test_validate_port_too_high(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        config = BuildConfiguration(
            source_dir=docs_dir,
            port=70000,  # Above maximum
        )

        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)

        assert "70000" in str(exc_info.value)

    def test_validate_invalid_verbosity(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        config = BuildConfiguration(
            source_dir=docs_dir,
            verbosity="invalid",
        )

        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)

        assert "invalid" in str(exc_info.value)

    def test_validate_all_verbosity_options(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        valid_options = ["full", "quiet", "errors-only"]

        for verbosity in valid_options:
            config = BuildConfiguration(
                source_dir=docs_dir,
                verbosity=verbosity,
            )
            # Should not raise
            validate_config(config)

    def test_error_message_templates(self):
        # Test missing_source message callable
        msg = ERROR_MESSAGES["missing_source"]("docs/")
        assert "docs/" in msg

        # Test port_conflict message callable
        msg = ERROR_MESSAGES["port_conflict"](5000)
        assert "5000" in msg
        assert "port = 5001" in msg
