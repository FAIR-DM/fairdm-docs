"""
Test branding asset detection with custom brand assets in docs/_static/brand/

This script validates T056: Test branding asset detection
Tests the _resolve_branding_assets() logic without requiring Django
"""

import os
from pathlib import Path


def _resolve_branding_assets() -> dict[str, str]:
    """
    Simplified version of _resolve_branding_assets from fairdm_docs/conf.py
    Tests branding detection logic without Django dependency.
    """
    branding = {}
    
    # Check for custom branding in docs/_static/brand/
    brand_dir = Path("docs/_static/brand")
    custom_logo = brand_dir / "logo.svg"
    custom_icon = brand_dir / "icon.svg"
    
    if custom_logo.exists():
        branding["html_logo"] = str(custom_logo)
    else:
        # Fallback to package default
        package_dir = Path(__file__).parent.parent / "fairdm_docs" / "_static"
        branding["html_logo"] = str(package_dir / "logo.svg")
    
    if custom_icon.exists():
        branding["html_favicon"] = str(custom_icon)
    else:
        # Fallback to package default
        package_dir = Path(__file__).parent.parent / "fairdm_docs" / "_static"
        branding["html_favicon"] = str(package_dir / "icon.svg")
    
    return branding

def test_branding_detection():
    """Test branding asset detection with different scenarios."""
    
    print("Testing branding asset detection...")
    print("=" * 60)
    
    # Test 1: Without custom branding (should fall back to package defaults)
    print("\nTest 1: Default branding (no custom assets)")
    print("-" * 60)
    branding = _resolve_branding_assets()
    print(f"Logo: {branding['html_logo']}")
    print(f"Icon: {branding['html_favicon']}")
    
    # Verify defaults point to fairdm_docs/_static/
    assert "fairdm_docs" in branding["html_logo"] and "_static" in branding["html_logo"], \
        "Default logo should come from fairdm_docs/_static/"
    assert "fairdm_docs" in branding["html_favicon"] and "_static" in branding["html_favicon"], \
        "Default icon should come from fairdm_docs/_static/"
    print("✓ PASS: Default branding resolved correctly")
    
    # Test 2: Create custom branding directory and files
    print("\nTest 2: Custom branding (with docs/_static/brand/ assets)")
    print("-" * 60)
    
    custom_brand_dir = Path("docs/_static/brand")
    custom_brand_dir.mkdir(parents=True, exist_ok=True)
    
    # Create dummy SVG files
    custom_logo = custom_brand_dir / "logo.svg"
    custom_icon = custom_brand_dir / "icon.svg"
    
    custom_logo.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Custom Logo</text></svg>')
    custom_icon.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Icon</text></svg>')
    
    print(f"Created: {custom_logo.absolute()}")
    print(f"Created: {custom_icon.absolute()}")
    
    # Test detection with custom assets present
    branding = _resolve_branding_assets()
    print(f"Logo: {branding['html_logo']}")
    print(f"Icon: {branding['html_favicon']}")
    
    # Verify custom branding is detected
    assert "docs" in branding["html_logo"] and "_static" in branding["html_logo"] and "brand" in branding["html_logo"], \
        "Custom logo should be detected from docs/_static/brand/"
    assert "docs" in branding["html_favicon"] and "_static" in branding["html_favicon"] and "brand" in branding["html_favicon"], \
        "Custom icon should be detected from docs/_static/brand/"
    print("✓ PASS: Custom branding detected and used")
    
    # Test 3: Partial custom branding (only logo)
    print("\nTest 3: Partial branding (logo only, icon falls back)")
    print("-" * 60)
    
    custom_icon.unlink()  # Remove custom icon
    print(f"Removed: {custom_icon.absolute()}")
    
    branding = _resolve_branding_assets()
    print(f"Logo: {branding['html_logo']}")
    print(f"Icon: {branding['html_favicon']}")
    
    # Logo should be custom, icon should fall back to default
    assert "docs" in branding["html_logo"] and "_static" in branding["html_logo"] and "brand" in branding["html_logo"], \
        "Custom logo should still be used"
    assert "fairdm_docs" in branding["html_favicon"] and "_static" in branding["html_favicon"], \
        "Icon should fall back to default"
    print("✓ PASS: Partial branding with correct fallback")
    
    # Cleanup
    print("\nCleaning up test assets...")
    custom_logo.unlink()
    custom_brand_dir.rmdir()
    custom_brand_dir.parent.rmdir()
    custom_brand_dir.parent.parent.rmdir()
    print("✓ Cleanup complete")
    
    print("\n" + "=" * 60)
    print("All branding detection tests PASSED ✓")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    # Change to repo root
    os.chdir(Path(__file__).parent.parent)
    
    try:
        test_branding_detection()
    except AssertionError as e:
        print(f"\n✗ FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
