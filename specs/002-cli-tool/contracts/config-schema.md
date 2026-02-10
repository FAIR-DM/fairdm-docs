# Configuration Schema Examples

## Minimal Configuration (Zero-Config)

No configuration required - just works with defaults:

```toml
# pyproject.toml
[tool.poetry]
name = "my-fairdm-project"
version = "0.1.0"

# NO [tool.fairdm.docs] section needed!
# CLI uses these defaults:
#   source_dir = "docs"
#   build_dir = "docs/_build/html"
#   port = 5000
#   verbosity = "full"
```

Usage:
```bash
fairdm-docs build         # Works with defaults
fairdm-docs build --live  # Live server on port 5000
fairdm-docs check         # Link validation
```

---

## Custom Source and Build Directories

Override default directory locations:

```toml
# pyproject.toml
[tool.fairdm.docs]
source_dir = "documentation"
build_dir = "build/html"
```

Project structure:
```
my-project/
├── pyproject.toml
├── documentation/          # Custom source location
│   ├── index.md
│   └── guides/
└── build/                  # Custom build location
    └── html/
```

---

## Custom Port for Live Server

Avoid port conflicts with other services:

```toml
# pyproject.toml
[tool.fairdm.docs]
port = 5001  # Or any available port 1024-65535
```

Useful when:
- Port 5000 is used by Flask/Django development server
- Running multiple live documentation servers
- Corporate firewall restrictions

---

## Quiet Build Output

Reduce console output noise:

```toml
# pyproject.toml
[tool.fairdm.docs]
verbosity = "quiet"
```

Output levels:
- `"full"` (default): All Sphinx output including warnings
- `"quiet"`: Only errors and final status
- `"errors-only"`: Only errors, suppress warnings

Useful for:
- CI/CD pipelines (cleaner logs)
- Automated builds
- Experienced users who don't need detailed output

---

## Complete Custom Configuration

All options customized:

```toml
# pyproject.toml
[tool.fairdm.docs]
source_dir = "docs"
build_dir = "public/documentation"
port = 8080
verbosity = "quiet"
```

---

## Real-World Example: FairDM Portal

Typical configuration for a FairDM research data portal:

```toml
# pyproject.toml
[tool.poetry]
name = "my-research-portal"
version = "1.0.0"
description = "Research data portal for XYZ project"

[tool.poetry.dependencies]
python = "^3.11"
django = "^4.2"
fairdm = "^0.5.0"

[tool.poetry.group.dev.dependencies]
fairdm-docs = {git = "https://github.com/FAIR-DM/fairdm-docs.git"}

[tool.fairdm.docs]
# Documentation in standard location
source_dir = "docs"

# Build to separate directory for deployment
build_dir = "docs/_build/html"

# Use port 5001 to avoid Django dev server (port 8000)
port = 5001

# Full output for development
verbosity = "full"
```

Commands:
```bash
# Development
poetry run fairdm-docs build --live  # Live preview on :5001

# CI/CD
poetry run fairdm-docs check         # Validate before deploy
poetry run fairdm-docs build         # Production build
```

---

## Schema Reference

| Field | Type | Default | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| `source_dir` | string (path) | `"docs"` | Any valid directory path | Documentation source directory |
| `build_dir` | string (path) | `"docs/_build/html"` | Any valid directory path | Build output directory |
| `port` | integer | `5000` | `1024-65535` | Port for live preview server |
| `verbosity` | string | `"full"` | `"full"`, `"quiet"`, `"errors-only"` | Console output level |

---

## Validation Rules

### source_dir

- **Must exist** when command is run
- **Must be readable**
- Error message includes configuration guidance if missing

Example error:
```
❌ Error: Source directory 'documentation' not found.
   Specify source directory in pyproject.toml:

   [tool.fairdm.docs]
   source_dir = "path/to/docs"
```

### build_dir

- **Created automatically** if doesn't exist
- **Must be writable** if exists
- Parent directory must exist

### port

- **Must be integer** between 1024-65535
- **Must be available** when starting live server
- Error message suggests alternative port if conflict

Example error:
```
❌ Error: Port 5000 is already in use.
   Configure a different port in pyproject.toml:

   [tool.fairdm.docs]
   port = 5001
```

### verbosity

- **Must be one of**: `"full"`, `"quiet"`, `"errors-only"`
- Case-sensitive
- Invalid value causes clear error message

---

## Migration Guide

### From manual sphinx-build

Before:
```bash
sphinx-build -b html docs docs/_build/html
sphinx-autobuild docs docs/_build/html --port 8000
```

After:
```bash
fairdm-docs build
fairdm-docs build --live
```

No configuration needed if using standard structure!

### From custom Makefile

Before (Makefile):
```makefile
SOURCEDIR     = documentation
BUILDDIR      = build
PORT          = 5001

html:
	sphinx-build -b html $(SOURCEDIR) $(BUILDDIR)/html

livehtml:
	sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html --port $(PORT)
```

After (pyproject.toml):
```toml
[tool.fairdm.docs]
source_dir = "documentation"
build_dir = "build/html"
port = 5001
```

Commands:
```bash
fairdm-docs build         # Replaces: make html
fairdm-docs build --live  # Replaces: make livehtml
```

---

## Future Extensions (Planned)

These configuration options are planned for future releases:

```toml
[tool.fairdm.docs]
# Current options (available now)
source_dir = "docs"
build_dir = "docs/_build/html"
port = 5000
verbosity = "full"

# Future options (not yet implemented)
# check_external_links = true      # Enable/disable external link checking
# max_link_timeout = 30            # Timeout for external link checks (seconds)
# parallel_build = true            # Use Sphinx parallel build (-j auto)
# watch_exclude = ["_build", ".git"]  # Patterns to exclude from live reload
```

All future options will be:
- **Optional** (backward compatible)
- **Documented** with examples
- **Validated** with clear error messages
