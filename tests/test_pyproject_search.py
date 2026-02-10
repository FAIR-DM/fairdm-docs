"""
Tests for pyproject.toml search functionality in conf.py.

Verifies that _find_pyproject() correctly searches upward from
the documentation directory to find the project's pyproject.toml.
"""

import sys
import tempfile
from pathlib import Path

import pytest


def test_find_pyproject_from_docs_dir():
    """Test that _find_pyproject searches upward from docs directory."""
    # Create temporary project structure
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        docs_dir = project_root / "docs"
        docs_dir.mkdir()
        
        # Create pyproject.toml in project root
        pyproject = project_root / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test-project"
version = "0.1.0"
""")
        
        # Import the conf module and test _find_pyproject
        # We need to simulate being in the docs directory
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(docs_dir)
            
            # Import after changing directory
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from fairdm_docs.utils import find_pyproject_toml
            
            result = find_pyproject_toml()
            
            assert result is not None
            assert result.exists()
            assert result.name == "pyproject.toml"
            assert result.parent == project_root
            
        finally:
            os.chdir(original_cwd)
            if str(Path(__file__).parent.parent) in sys.path:
                sys.path.remove(str(Path(__file__).parent.parent))


def test_find_pyproject_from_nested_dir():
    """Test that _find_pyproject searches multiple levels upward."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        nested_dir = project_root / "docs" / "_build" / "html"
        nested_dir.mkdir(parents=True)
        
        # Create pyproject.toml in project root
        pyproject = project_root / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test-project"
""")
        
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(nested_dir)
            
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from fairdm_docs.utils import find_pyproject_toml
            
            result = find_pyproject_toml()
            
            assert result is not None
            assert result.parent == project_root
            
        finally:
            os.chdir(original_cwd)
            if str(Path(__file__).parent.parent) in sys.path:
                sys.path.remove(str(Path(__file__).parent.parent))


def test_find_pyproject_not_found():
    """Test that _find_pyproject returns None when file not found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_dir = Path(tmpdir) / "empty"
        empty_dir.mkdir()
        
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(empty_dir)
            
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from fairdm_docs.utils import find_pyproject_toml
            
            result = find_pyproject_toml()
            
            assert result is None
            
        finally:
            os.chdir(original_cwd)
            if str(Path(__file__).parent.parent) in sys.path:
                sys.path.remove(str(Path(__file__).parent.parent))


def test_load_pyproject_raises_when_not_found():
    """Test that _load_pyproject raises ValueError when file not found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_dir = Path(tmpdir) / "empty"
        empty_dir.mkdir()
        
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(empty_dir)
            
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from fairdm_docs.utils import load_pyproject_toml
            
            with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):
                load_pyproject_toml()
            
        finally:
            os.chdir(original_cwd)
            if str(Path(__file__).parent.parent) in sys.path:
                sys.path.remove(str(Path(__file__).parent.parent))
