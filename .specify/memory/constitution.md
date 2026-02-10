<!--
═══════════════════════════════════════════════════════════════════════════════
SYNC IMPACT REPORT
═══════════════════════════════════════════════════════════════════════════════
Version Change: [TEMPLATE] → 1.0.0
Modified Principles:
  - [PRINCIPLE_1_NAME] → Convention Over Configuration
  - [PRINCIPLE_2_NAME] → Zero-Config Philosophy
  - [PRINCIPLE_3_NAME] → Backward Compatibility (NON-NEGOTIABLE)
  - [PRINCIPLE_4_NAME] → Documentation-First
  - [PRINCIPLE_5_NAME] → Extensibility with Sensible Defaults
Added Sections:
  - Technology Stack
  - Development Workflow
Removed Sections: None
Templates Requiring Updates:
  ✅ constitution.md - Updated
  ⚠ plan-template.md - Review for alignment with constitution principles
  ⚠ spec-template.md - Review for documentation requirements
  ⚠ tasks-template.md - Review for task categorization (breaking changes, docs)
  ⚠ commands/*.md - Review for agent guidance consistency
Follow-up TODOs:
  - Validate all dependent template files against new principles
  - Ensure CONTRIBUTING.md aligns with Development Workflow section
═══════════════════════════════════════════════════════════════════════════════
-->

# FairDM-Docs Constitution

## Core Principles

### I. Convention Over Configuration

**MUST**: Provide working defaults for all settings without requiring user configuration.

**MUST**: Automatically extract project metadata from `pyproject.toml` (project name, version, authors, homepage).

**MUST**: Detect and use project branding assets when present, fallback to package defaults when absent.

**Rationale**: Documentation should work out-of-the-box. Developers should focus on content, not configuration management. Every setting that requires manual input is a barrier to adoption and consistency across FairDM portals.

### II. Zero-Config Philosophy

**MUST**: Users should be able to create docs with only `from fairdm_docs.conf import *` in their `conf.py`.

**MUST**: Never require users to manage complex Sphinx configuration, Makefiles, or build tooling directly.

**MUST**: Abstract away third-party tool complexities (Sphinx, MyST, themes, extensions).

**Rationale**: The primary goal is to eliminate the cognitive overhead of documentation infrastructure. Portal developers should not need to become Sphinx experts. This package handles all tooling decisions and configurations.

### III. Backward Compatibility (NON-NEGOTIABLE)

**MUST**: Semantic versioning strictly enforced:

- **MAJOR**: Breaking changes to configuration API or removed functionality
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, documentation, non-semantic refinements

**MUST**: Configuration changes require deprecation warnings for at least one minor version before removal.

**MUST**: Breaking changes documented in CHANGELOG.md with migration guide.

**MUST NOT**: Change import paths, configuration variable names, or directive interfaces without major version bump.

**Rationale**: FairDM portals depend on stable documentation tooling. Breaking changes disrupt multiple projects simultaneously. Stability enables confidence in upgrades and long-term maintenance.

### IV. Documentation-First

**MUST**: Every feature documented with usage examples before merging.

**MUST**: README.md contains comprehensive quick start, feature list, and customization guide.

**MUST**: Configuration examples provided in `examples/` directory for common use cases.

**MUST**: Public functions and classes have complete docstrings with parameters, returns, exceptions, and examples.

**Rationale**: This package exists to improve documentation. It must exemplify documentation quality. Users learn primarily from examples, not abstract descriptions.

### V. Extensibility with Sensible Defaults

**MUST**: All default settings can be overridden in user's `conf.py`.

**MUST**: Support multiple themes (Sphinx Book Theme, PyData Sphinx Theme) via optional dependencies.

**MUST**: Custom Sphinx extensions provided for FairDM-specific needs (Django model documentation).

**SHOULD**: New features added as opt-in extensions or optional dependencies when possible.

**Rationale**: While zero-config is the goal, diverse projects have diverse needs. The package must balance "it just works" with "I can customize it". Power users should have full control without breaking simplicity for basic users.

## Technology Stack

**Package Manager**: Poetry (>=2.0)

**Python Versions**: 3.10, 3.11, 3.12 (support for actively maintained versions)

**Core Dependencies**:

- Sphinx (>=8.1) - Documentation engine
- MyST-Parser (>=4.0) - Markdown support
- Sphinx Book Theme (>1.1) - Default theme
- Django integration for model documentation

**Code Quality**:

- Black (120 character line length)
- Pre-commit hooks for automated formatting
- Type hints encouraged where appropriate

**Distribution**: Git-based installation (`poetry add --group dev git+https://github.com/FAIR-DM/fairdm-docs`)

**Rationale**: Technology choices prioritize stability, maintainability, and integration with the broader FairDM ecosystem. Poetry provides reproducible builds. Sphinx is the de facto Python documentation standard.

## Development Workflow

**Branch Strategy**: Feature branches from main (`feature/description`, `fix/description`)

**Code Style**: PEP 8 compliance enforced via Black formatter

**Testing Requirements**:

- Test changes against real FairDM portal projects before merging
- Verify builds succeed with both minimal and complex configurations
- Validate branding detection and metadata extraction

**Pull Request Requirements**:

- Update README.md if adding features or changing behavior
- Add examples to `examples/` directory for significant features
- Update CHANGELOG.md following Keep a Changelog format
- Run Black formatter before committing
- Ensure pre-commit hooks pass

**Review Criteria**:

- Does it work with zero configuration?
- Does it break backward compatibility? (If yes, must be justified and documented)
- Is it documented with examples?
- Does it follow established naming conventions (`fairdm_*` prefix)?

**Rationale**: Consistent process ensures quality and maintainability. Testing against real projects catches integration issues. Documentation requirements prevent incomplete features from merging.

## Governance

**Constitutional Authority**: This constitution supersedes conflicting guidance in any other project documentation.

**Amendment Process**:

1. Proposed changes discussed via GitHub issue
2. If consensus reached, update constitution with rationale
3. Increment version according to semantic rules
4. Update dependent documentation/templates
5. Document in CHANGELOG.md

**Compliance**: All pull requests and code reviews must verify adherence to Core Principles.

**Complexity Justification**: Any configuration complexity must be justified against Zero-Config Philosophy. Default to simpler solutions.

**Runtime Guidance**: For AI coding agents, reference `.github/instructions/copilot.instructions.md` for development patterns and conventions.

**Version**: 1.0.0 | **Ratified**: 2026-02-10 | **Last Amended**: 2026-02-10
