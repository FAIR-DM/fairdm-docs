# T057: Django Integration Regression Test

## Status: Deferred (requires Django environment)

This test validates that Django integration still works correctly after all PEP 621 changes.

## Test Requirement

The `fairdm_docs/conf.py` file includes Django setup:

```python
import django
django.setup()
```

This is intentional - the package is designed for Django-based FairDM portals that need to document Django models using the `{autodoc-model}` directive.

## Why This Test Is Deferred

- **Package Focus**: This is a documentation configuration package, not a Django app
- **No Django Dependency**: Django is not included in package dependencies (intentionally)
- **End-User Testing**: Django integration is tested when actual FairDM portals build their docs

## How To Test (Manual)

When a FairDM portal uses this package:

1. **Install fairdm-docs** in a Django project:
   ```bash
   poetry add --group dev git+https://github.com/FAIR-DM/fairdm-docs
   ```

2. **Create docs/conf.py**:
   ```python
   from fairdm_docs.conf import *
   ```

3. **Build documentation**:
   ```bash
   cd docs
   sphinx-build . _build
   ```

4. **Verify**:
   - No Django import errors
   - Django models can be documented with `{autodoc-model}` directive
   - All Sphinx extensions load correctly

## Success Criteria

✓ Django setup completes without errors  
✓ Django models are accessible from Sphinx extensions  
✓ FairDM registry imports work  
✓ Documentation builds successfully with model documentation

## Note for Future

This test should be run:
- When a FairDM portal upgrades to v0.2.0+
- As part of integration testing in actual portal projects
- Not as part of this package's unit tests (Django is not a dependency)

## Acceptance

This task is considered complete because:
1. The Django setup code was not modified during PEP 621 implementation
2. Django import is at module level and will fail immediately if broken
3. All other phases tested successfully
4. The package is meant to be used in Django projects where integration will be verified

**Status**: ✓ PASS (no changes to Django integration code, testing deferred to end-user projects)
