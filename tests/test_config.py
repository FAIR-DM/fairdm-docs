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
    find_pyproject,
    load_config,
    load_pyproject,
    validate_config,
)


class TestConfigurationLoading:
    """Test configuration loading from pyproject.toml."""
    
    def test_build_configuration_defaults(self):
        """Test BuildConfiguration has correct default values."""
        config = BuildConfiguration()
        
        assert config.source_dir == Path("docs")
        assert config.build_dir == Path("docs/_build/html")
        assert config.port == 5000
        assert config.verbosity == "full"
        assert config.config_dir is None
        assert config.django is False  # Django should be disabled by default
    
    def test_find_pyproject_in_current_dir(self, tmp_path, monkeypatch):
        """Test finding pyproject.toml in current directory."""
        # Create a pyproject.toml in temp directory
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")
        
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        found = find_pyproject()
        assert found == pyproject
        assert found.exists()
    
    def test_find_pyproject_in_parent_dir(self, tmp_path, monkeypatch):
        """Test finding pyproject.toml in parent directory."""
        # Create pyproject.toml in parent
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")
        
        # Create subdirectory and change to it
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)
        
        found = find_pyproject()
        assert found == pyproject
    
    def test_find_pyproject_not_found(self, tmp_path, monkeypatch):
        """Test find_pyproject returns None when not found."""
        monkeypatch.chdir(tmp_path)
        
        found = find_pyproject()
        assert found is None
    
    def test_load_pyproject_success(self, tmp_path, monkeypatch):
        """Test successfully loading pyproject.toml."""
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
        """Test load_pyproject raises ConfigError when not found."""
        monkeypatch.chdir(tmp_path)
        
        with pytest.raises(ConfigError) as exc_info:
            load_pyproject()
        
        assert "No pyproject.toml found" in str(exc_info.value)
    
    def test_load_config_with_defaults(self, tmp_path, monkeypatch):
        """Test loading config with no [tool.fairdm.docs] section uses defaults."""
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
        """Test loading config with custom [tool.fairdm.docs] section."""
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
        """Test that missing source directory raises clear error."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test"
        """)
        
        # Don't create docs/ directory
        monkeypatch.chdir(tmp_path)
        
        with pytest.raises(ConfigError) as exc_info:
            load_config()
        
        error_msg = str(exc_info.value)
        assert "Source directory" in error_msg
        assert "not found" in error_msg
        assert "[tool.fairdm.docs]" in error_msg
    
    def test_load_config_validates_port_range(self, tmp_path, monkeypatch):
        """Test that invalid port number raises error."""
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
        assert "Invalid port" in error_msg
        assert "1024-65535" in error_msg
    
    def test_load_config_validates_verbosity(self, tmp_path, monkeypatch):
        """Test that invalid verbosity level raises error."""
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
        assert "Invalid verbosity" in error_msg
        assert "full, quiet, errors-only" in error_msg
    
    def test_no_pyproject_raises_error(self, tmp_path, monkeypatch):
        """Test that missing pyproject.toml raises appropriate error."""
        monkeypatch.chdir(tmp_path)
        
        with pytest.raises(ConfigError) as exc_info:
            load_config()
        
        # Should match ERROR_MESSAGES["no_pyproject"]
        error_msg = str(exc_info.value)
        assert "No pyproject.toml found" in error_msg
        assert "Run this command from your project root" in error_msg
    
    def test_user_config_overrides_defaults(self, tmp_path, monkeypatch):
        """Test that user configuration takes precedence over defaults."""
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
        """Test loading config with Django integration enabled."""
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
        """Test that Django is disabled by default when not specified."""
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
    """Test configuration validation rules."""
    
    def test_validate_config_success(self, tmp_path):
        """Test validation passes with valid configuration."""
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
        """Test validation fails when source directory doesn't exist."""
        config = BuildConfiguration(
            source_dir=Path("/nonexistent/path"),
        )
        
        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)
        
        error_msg = str(exc_info.value)
        assert "Source directory" in error_msg
        assert "not found" in error_msg
    
    def test_validate_port_too_low(self, tmp_path):
        """Test validation fails when port number is too low."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        config = BuildConfiguration(
            source_dir=docs_dir,
            port=500,  # Below minimum
        )
        
        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)
        
        assert "Invalid port" in str(exc_info.value)
    
    def test_validate_port_too_high(self, tmp_path):
        """Test validation fails when port number is too high."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        config = BuildConfiguration(
            source_dir=docs_dir,
            port=70000,  # Above maximum
        )
        
        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)
        
        assert "Invalid port" in str(exc_info.value)
    
    def test_validate_invalid_verbosity(self, tmp_path):
        """Test validation fails with invalid verbosity level."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        config = BuildConfiguration(
            source_dir=docs_dir,
            verbosity="invalid",
        )
        
        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)
        
        assert "Invalid verbosity" in str(exc_info.value)
    
    def test_validate_all_verbosity_options(self, tmp_path):
        """Test all valid verbosity options pass validation."""
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
        """Test error message templates are properly formatted."""
        # Test no_pyproject message
        msg = ERROR_MESSAGES["no_pyproject"]
        assert "No pyproject.toml found" in msg
        assert "fairdm-docs requires" in msg
        
        # Test missing_source message callable
        msg = ERROR_MESSAGES["missing_source"]("docs/")
        assert "Source directory 'docs/' not found" in msg
        assert "[tool.fairdm.docs]" in msg
        
        # Test port_conflict message callable
        msg = ERROR_MESSAGES["port_conflict"](5000)
        assert "Port 5000 is already in use" in msg
        assert "port = 5001" in msg
