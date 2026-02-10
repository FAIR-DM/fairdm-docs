# Implementation Plan: FairDM-Docs CLI Tool

**Branch**: `002-cli-tool` | **Date**: February 10, 2026 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-cli-tool/spec.md`

## Summary

Create a command-line interface tool (`fairdm-docs`) that wraps Sphinx documentation builds with simplified defaults. The CLI provides two primary commands: `build` (with optional `--live` flag for live preview) and `check` (for link validation). Configuration is read from `[tool.fairdm.docs]` section in `pyproject.toml`, with sensible defaults requiring zero configuration for standard FairDM projects. The CLI uses **Typer** (modern Python CLI framework with type hints) for clean, testable code with rich console output.

## Technical Context

**Language/Version**: Python 3.10+ (supporting 3.10, 3.11, 3.12)  
**Primary Dependencies**: Typer (^0.12.0), Sphinx (>=8.1), sphinx-autobuild (>=2024.10), tomli/tomllib (stdlib in 3.11+)  
**Storage**: Configuration from pyproject.toml (TOML parsing)  
**Testing**: pytest with Typer's CliRunner for isolated CLI testing  
**Target Platform**: Cross-platform CLI (Windows, Linux, macOS) via Python entry points  
**Project Type**: Single Python package with CLI entry point  
**Performance Goals**: Build completes in <30s for small projects (<50 pages), live server starts in <5s, file change detection within 2s  
**Constraints**: Must work without pyproject.toml present (error with clear message), port 5000 must be available or error with config guidance  
**Scale/Scope**: Small CLI tool (2 commands, ~5 configuration options), integrates with existing fairdm_docs package

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Convention Over Configuration
✅ **PASS** - CLI provides working defaults (port 5000, docs/ source, docs/_build output) without requiring configuration
✅ **PASS** - Reads configuration from existing pyproject.toml, no new config files required

### Principle II: Zero-Config Philosophy
✅ **PASS** - Users can run `fairdm-docs build` without any configuration
✅ **PASS** - CLI wraps complexity of sphinx-build and sphinx-autobuild commands

### Principle III: Backward Compatibility
✅ **PASS** - New feature, no breaking changes to existing functionality
✅ **PASS** - Configuration keys follow `fairdm_*` naming convention
⚠️ **NOTE** - This is a new CLI entry point; will require pyproject.toml update for `[tool.poetry.scripts]`

### Principle IV: Documentation-First
✅ **PASS** - Will include README examples, quickstart guide, and configuration reference
✅ **PASS** - Will add examples/ directory with sample configurations

### Principle V: Extensibility with Sensible Defaults
✅ **PASS** - All defaults can be overridden via [tool.fairdm.docs] configuration
✅ **PASS** - Check command designed for future extensibility (additional validators)

**GATE RESULT**: ✅ **APPROVED** - No constitutional violations

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-tool/
├── plan.md              # This file
├── research.md          # Phase 0: CLI framework research (Typer vs Click vs argparse)
├── data-model.md        # Phase 1: Configuration schema and CLI structure
├── quickstart.md        # Phase 1: User guide for CLI usage
├── contracts/           # Phase 1: Configuration examples
│   ├── config-schema.toml   # Sample [tool.fairdm.docs] configurations
│   └── cli-interface.md     # Command signatures and outputs
└── tasks.md             # Phase 2: Implementation task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
fairdm_docs/
├── __init__.py          # Existing package root
├── conf.py              # Existing Sphinx configuration
├── cli.py               # NEW: Typer CLI application
├── config.py            # NEW: Configuration loader from pyproject.toml
├── _static/             # Existing assets
├── _templates/          # Existing templates
└── extensions/          # Existing Sphinx extensions

tests/
├── test_cli.py          # NEW: CLI command tests
├── test_config.py       # NEW: Configuration loading tests
└── fixtures/            # Test pyproject.toml files
    ├── minimal.toml
    ├── custom_config.toml
    └── invalid_config.toml

pyproject.toml           # Updated with CLI dependencies and entry point
README.md                # Updated with CLI usage documentation
```

**Structure Decision**: Single Python package structure. CLI module (`cli.py`) added to existing `fairdm_docs/` package. Configuration loader (`config.py`) separates concerns of reading pyproject.toml from CLI logic. Tests added for both CLI commands and configuration parsing.

## Complexity Tracking

**No constitutional violations** - This feature aligns with all core principles without requiring exceptions.
