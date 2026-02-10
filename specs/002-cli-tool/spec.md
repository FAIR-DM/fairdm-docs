# Feature Specification: FairDM-Docs CLI Tool

**Feature Branch**: `002-cli-tool`  
**Created**: February 10, 2026  
**Status**: Draft  
**Input**: User description: "I would like to create and ship a simple cli with the package. The cli should be called fairdm-docs. It should have 1 main function that wraps sphinx-build. The difference? We will provide default args to the sphinx-build directive directly (taking away complexity from end users). For advanced users, we will accept some configuration via [tools.fairdm.docs]. e.g. build directory, etc. ADDITIONALLY, we will allow a single argument to the `fairdm-docs build` command -- `--live`. If this argument is provided, we will deploy docs to a live server using 'sphinx-autobuild'."

## Clarifications

### Session 2026-02-10

- Q: When the CLI runs outside a Python project (no `pyproject.toml`), what should happen? → A: Error immediately and refuse to run, requiring pyproject.toml
- Q: When the live server port (default 8000) is already in use, what should happen? → A: Default port is 5000 (Django uses 8000). Error when port occupied, inform user to adjust via [tool.fairdm.docs]
- Q: When the Sphinx source directory is not in the expected location (`docs/`), what should happen? → A: Require users to specify source directory in [tool.fairdm.docs] configuration if not using docs/
- Q: How should build errors from Sphinx be communicated to the user? → A: Show full Sphinx error output including all warnings and errors, with option to configure verbosity in pyproject.toml
- Q: When configuration in `pyproject.toml` conflicts with package defaults, how should conflicts be resolved? → A: User configuration in pyproject.toml always overrides package defaults

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Documentation Build (Priority: P1)

A documentation contributor wants to build their Sphinx documentation with zero configuration. They simply run a single command and get their documentation built in a standard output directory.

**Why this priority**: This is the core MVP - users need a simple way to build docs without complex Sphinx command-line arguments. This eliminates the primary barrier to entry for new users.

**Independent Test**: Can be fully tested by running the CLI command in a project with Sphinx docs and verifying HTML output is generated in the expected directory.

**Acceptance Scenarios**:

1. **Given** a FairDM project with documentation source files, **When** user runs `fairdm-docs build`, **Then** documentation is built to the default output directory with HTML format
2. **Given** a project without any prior Sphinx configuration, **When** user runs `fairdm-docs build`, **Then** the command uses sensible defaults from the package's base configuration
3. **Given** an empty or invalid documentation source, **When** user runs `fairdm-docs build`, **Then** the command displays clear error messages indicating what's missing

---

### User Story 2 - Live Preview Server (Priority: P2)

A documentation author wants to preview their changes in real-time without manually rebuilding. They add a single flag to the build command and get a live-reloading preview server.

**Why this priority**: Live preview dramatically improves documentation authoring workflow by providing immediate feedback. This is a key differentiator from standard Sphinx builds but is secondary to basic build capability.

**Independent Test**: Can be fully tested by running the CLI with the live flag, making a documentation change, and verifying the browser auto-refreshes with the updated content.

**Acceptance Scenarios**:

1. **Given** a FairDM project with documentation, **When** user runs `fairdm-docs build --live`, **Then** a local web server starts and opens the documentation in a browser
2. **Given** the live server is running, **When** user modifies a documentation source file, **Then** the documentation rebuilds automatically and the browser refreshes to show changes
3. **Given** the live server is running, **When** user stops the server (Ctrl+C), **Then** the server shuts down gracefully and releases the port

---

### User Story 3 - Documentation Validation (Priority: P3)

A documentation maintainer wants to validate their documentation for broken links and other quality issues before publishing. They run a single check command that reports any problems found.

**Why this priority**: Documentation quality is important for user experience, but validation is typically done before publishing rather than during active authoring. This is valuable but not required for basic documentation building workflows.

**Independent Test**: Can be fully tested by running the check command on documentation with known broken links and verifying the issues are reported correctly.

**Acceptance Scenarios**:

1. **Given** a FairDM project with documentation, **When** user runs `fairdm-docs check`, **Then** the system validates all links in the documentation and reports any broken links
2. **Given** documentation with broken external links, **When** user runs `fairdm-docs check`, **Then** the command displays clear error messages identifying each broken link with its location
3. **Given** documentation with all valid links, **When** user runs `fairdm-docs check`, **Then** the command reports success with a summary of checks performed
4. **Given** a user needs to add more validation checks in the future, **When** the check command is extended, **Then** new validators can be added without breaking existing functionality

---

### User Story 4 - Advanced Configuration (Priority: P4)

An advanced user needs to customize build behavior (e.g., different output directory, custom build options). They configure these settings in their project's `pyproject.toml` file under a dedicated section.

**Why this priority**: This enables power users to customize behavior without blocking basic functionality. Most users will be satisfied with defaults, making this a lower priority enhancement.

**Independent Test**: Can be fully tested by adding configuration to `pyproject.toml`, running the build command, and verifying the custom settings are applied (e.g., output appears in custom directory).

**Acceptance Scenarios**:

1. **Given** a project with `[tool.fairdm.docs]` configuration specifying a custom build directory, **When** user runs `fairdm-docs build`, **Then** documentation is built to the specified custom directory
2. **Given** a project with multiple configuration options in `pyproject.toml`, **When** user runs the CLI, **Then** all specified options are applied correctly
3. **Given** invalid configuration in `pyproject.toml`, **When** user runs the CLI, **Then** a clear validation error is displayed with guidance on correct format

---

### Edge Cases

- CLI MUST error immediately when run outside a Python project (no `pyproject.toml` found), displaying a clear message that a Python project with pyproject.toml is required
- When the live server port (default 5000) is already in use, CLI MUST error with a clear message informing the user they can adjust the port via `[tool.fairdm.docs]` configuration
- If Sphinx source directory is not found at default location `docs/`, CLI MUST error with a clear message that the source directory must be specified in `[tool.fairdm.docs]` configuration
- Build errors from Sphinx MUST be displayed in full (including all warnings and errors) by default, with option to configure verbosity level in `[tool.fairdm.docs]`
- User configuration in `[tool.fairdm.docs]` always takes precedence over package defaults when conflicts occur
- How does the check command handle timeouts when checking external links?
- What happens when check is run but documentation hasn't been built yet?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI MUST provide a command named `fairdm-docs` accessible after package installation
- **FR-002**: CLI MUST provide a `build` subcommand that builds Sphinx documentation
- **FR-003**: `fairdm-docs build` MUST invoke the documentation build process with default arguments that work for standard FairDM projects
- **FR-004**: CLI MUST use the package's existing `fairdm_docs.conf` as the base configuration for builds
- **FR-005**: `fairdm-docs build` MUST accept a `--live` flag that starts a live-reloading preview server
- **FR-006**: When `--live` flag is provided, CLI MUST use auto-rebuild functionality to detect file changes
- **FR-007**: When `--live` flag is provided, CLI MUST open the documentation in the user's default web browser
- **FR-008**: CLI MUST read configuration from `[tool.fairdm.docs]` section in `pyproject.toml` when present
- **FR-009**: Configuration MUST support customizing the build output directory
- **FR-010**: Configuration MUST support customizing the source directory location; if source directory is not at default `docs/` location, users MUST specify it in configuration
- **FR-010a**: Configuration MUST support customizing the live server port number
- **FR-010b**: Configuration MUST support customizing the build output verbosity level
- **FR-011**: CLI MUST display full Sphinx error output by default, including all warnings and errors; verbosity level MUST be configurable via `[tool.fairdm.docs]`
- **FR-012**: CLI MUST display build progress information to the user (e.g., "Building documentation...", "Build complete")
- **FR-013**: CLI MUST exit with appropriate status codes (0 for success, non-zero for failures)
- **FR-014**: When live server is running, CLI MUST handle shutdown gracefully on interrupt signals (Ctrl+C)
- **FR-015**: CLI MUST validate configuration values from `pyproject.toml` and report errors for invalid settings
- **FR-015a**: User configuration specified in `[tool.fairdm.docs]` MUST always take precedence over package defaults
- **FR-016**: CLI MUST provide a `check` subcommand that validates documentation quality
- **FR-017**: `fairdm-docs check` MUST run link validation to detect broken internal and external links
- **FR-018**: Check command MUST report validation results with clear identification of issues found (file location, link URL, error type)
- **FR-019**: Check command MUST exit with non-zero status code when validation issues are found
- **FR-020**: Check command implementation MUST be extensible to support additional validators in the future beyond link checking
- **FR-021**: CLI MUST require a `pyproject.toml` file to be present and error immediately with a clear message if not found
- **FR-022**: When live server port is already in use, CLI MUST error with a clear message indicating the port conflict and instructing the user how to configure a custom port via `[tool.fairdm.docs]`
- **FR-023**: CLI MUST default to `docs/` as the source directory; if not found, CLI MUST error with a clear message instructing the user to specify the source directory in `[tool.fairdm.docs]` configuration

### Key Entities

- **CLI Command**: The entry point `fairdm-docs` that users invoke from the terminal
- **Build Configuration**: Settings that control how documentation is built, sourced from package defaults and user overrides
- **Build Process**: The operation that transforms source files into HTML documentation
- **Live Server**: A local web server that serves documentation and auto-reloads on changes
- **Validation Process**: The operation that checks documentation for quality issues (broken links, etc.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can build documentation with a single command (`fairdm-docs build`) in under 30 seconds for a typical small project (< 50 pages)
- **SC-002**: Live preview server starts and displays documentation in browser within 5 seconds of running `fairdm-docs build --live`
- **SC-003**: File changes are detected and rebuilt within 2 seconds of saving when using live preview
- **SC-004**: 100% of required configuration is handled automatically through defaults - no mandatory user configuration needed
- **SC-005**: Custom configuration options work correctly in 100% of test cases when specified in `pyproject.toml`
- **SC-006**: Error messages clearly identify the problem in 100% of common failure scenarios (missing source, invalid config, build errors)
- **SC-007**: Check command validates all links in documentation and reports results within 60 seconds for typical projects (< 100 pages)
- **SC-008**: Check command correctly identifies 100% of broken links in test scenarios
- **SC-009**: Validation errors include precise location information (file path and line number when available) in 100% of cases

## Assumptions

- Users have Python and Poetry installed (or pip for non-Poetry users)
- Users have basic familiarity with command-line tools
- The package is installed in the user's Python environment
- Documentation source files follow standard Sphinx conventions
- Default build output directory will be `docs/_build/html` (standard Sphinx convention)
- Default source directory will be `docs/` (standard location)
- Live preview server will use default port 5000 (avoiding conflict with Django's default port 8000) unless configured otherwise
- Configuration validation will check for common errors (invalid paths, wrong types) but won't exhaustively validate all possible Sphinx options

## Out of Scope

- Support for other documentation formats (PDF, ePub) - users can still use Sphinx directly for these
- Integration with external deployment services (ReadTheDocs, GitHub Pages) - this is a local build tool
- GUI interface - CLI only
- Configuration through environment variables or command-line flags beyond `--live` - configuration should be in `pyproject.toml`
- Support for multiple simultaneous live servers
- Custom Sphinx extension management through CLI - users should configure extensions in their project's `conf.py` or `pyproject.toml`
- Advanced validation checks beyond link checking in initial version (spell checking, accessibility audits, etc.) - these may be added in future iterations
- Custom validation rules or plugins - initial version provides built-in checks only
