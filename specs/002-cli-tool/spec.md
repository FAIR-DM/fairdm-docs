# Feature Specification: One command builds a portal's documentation

**Feature Branch**: `002-cli-tool`
**Created**: 2026-02-10
**Rewritten**: 2026-09-01
**Status**: Specified
**Roadmap item**: R1 — *A command that builds a portal's documentation*
**Goals served**: G1 — *A portal builds a complete documentation site with no configuration file
of its own in its documentation source*

A developer with a directory of documentation and a portal to describe should not have to learn
Sphinx's command line to see a rendered page. This feature is the command they type instead:
`fairdm-docs build` renders the site, `fairdm-docs build --live` serves it and rebuilds while they
write, and `fairdm-docs check` resolves the addresses the documentation links to before anyone
publishes it. A handful of settings in the portal's `pyproject.toml` move the source directory,
the output directory, the preview port and how much the build says as it runs.

This specification covers the commands and stops where the builder starts. What the builder is
configured to do, where it finds a portal's inputs and what the rendered page looks like belong to
other roadmap items, listed in [decisions.md](decisions.md).

**Prior version:** this specification was rewritten on 2026-09-01. What changed, and why, is in
[decisions.md](decisions.md).

## Clarifications

### Session 2026-02-10

- Q: What happens when the command runs outside a Python project? → A: It stops immediately and
  says a `pyproject.toml` is required.
- Q: What happens when the preview port is already in use? → A: The default is 5000, because
  Django already uses 8000. A taken port stops the command with a message saying how to change it.
- Q: What happens when the documentation source is not at `docs/`? → A: The developer names its
  location in the settings table.
- Q: How do build errors reach the developer? → A: In full, exactly as the builder emitted them,
  with verbosity adjustable in the settings table.
- Q: When the settings table and the package's defaults disagree, which wins? → A: The settings
  table.

### Session 2026-09-01

- Q: Must the build always use the package's own Sphinx configuration? → A: No. A portal that has
  written its own `docs/conf.py` gets that file used instead, whole. This is ADR 0002's third
  layer and it postdates the original answer.
- Q: Does `check` validate internal cross-references? → A: No. It resolves external addresses.
  Unresolvable cross-references are already reported by the build as warnings, and deciding
  whether warnings fail a build is R7's.
- Q: Should `check` be built so further validators can be added to it? → A: No. There is one
  validator, and structure invented for a second one that nobody has specified would be designed
  again the moment that second one arrived.
- Q: Is an address that redirects a broken link? → A: No. It is reported as a redirect and does
  not fail the check.
- Q: What does the command exit with when the developer interrupts it? → A: 130, in every mode.
- Q: What happens when a portal's `pyproject.toml` is not valid TOML? → A: The same as every other
  way a declaration can fail to be read: one readable message, per ADR 0008.
- Q: Does this feature prove the live server rebuilds and reloads? → A: No. Those are the
  upstream server's behaviours. What is proven is that the server is launched correctly and that a
  taken port stops the command first.
- Q: Does this feature decide which Django settings module a build loads? → A: No. It records that
  a setting switches Django on. Nominating the module is R6's, under ADR 0003.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A portal's documentation renders from one command (Priority: P1)

A developer has a portal with a documentation source and no Sphinx knowledge. They run
`fairdm-docs build` and get a rendered HTML site, in a directory they can open, with no arguments
and no configuration file of their own.

**Why this priority**: this is the command the package exists to provide, and every other story
here is a variation on it.

**Independent Test**: run `fairdm-docs build` against a project with a documentation source
containing a root page, and read the rendered HTML back off disk.

**Acceptance Scenarios**:

1. **Given** a project with a documentation source containing a root page, **When** the developer
   runs `fairdm-docs build`, **Then** rendered HTML appears in the output directory and the
   command exits 0.
2. **Given** a project whose documentation source contains its own `conf.py`, **When** the
   developer runs `fairdm-docs build`, **Then** that file configures the build and the package's
   own configuration is not consulted.
3. **Given** a project whose documentation source contains no `conf.py`, **When** the developer
   runs `fairdm-docs build`, **Then** the package's configuration is used.
4. **Given** an output directory whose parent does not exist, **When** the developer runs
   `fairdm-docs build`, **Then** the directory is created and the build succeeds.

---

### User Story 2 — Writing with a live preview (Priority: P2)

A developer editing documentation runs `fairdm-docs build --live`, gets the site in their browser,
and keeps writing while the page keeps up.

**Why this priority**: the difference between reading documentation you have written and reading
documentation you are writing. Valuable, and useless without the build itself.

**Independent Test**: run the command with the flag and assert the preview server is started
against the configured source, output directory, port and configuration; separately, occupy the
port and assert the command stops before starting anything.

**Acceptance Scenarios**:

1. **Given** a project with a documentation source, **When** the developer runs `fairdm-docs build
   --live`, **Then** a preview server is started against that source and the configured output
   directory, on the configured port, and is asked to open a browser.
2. **Given** a configured port that another process is already listening on, **When** the
   developer runs `fairdm-docs build --live`, **Then** the command stops with a message naming the
   port and the setting that changes it, and no server is started.
3. **Given** a running preview, **When** the developer interrupts it, **Then** the command stops
   without a traceback and exits 130.

---

### User Story 3 — Broken addresses are found before publication (Priority: P3)

A maintainer about to publish runs `fairdm-docs check` and learns which of the addresses their
documentation links to no longer resolve, and where each one is written.

**Why this priority**: documentation rots outward — the pages stay put and the world they link to
moves. Worth catching, and only worth catching once there is a site to publish.

**Independent Test**: run the command against a documentation source containing one address that
does not resolve and one that redirects, and read the exit code and the report.

**Acceptance Scenarios**:

1. **Given** documentation whose external addresses all resolve, **When** the developer runs
   `fairdm-docs check`, **Then** the command reports success and exits 0.
2. **Given** documentation containing an address that does not resolve, **When** the developer
   runs `fairdm-docs check`, **Then** the command names that address and the file it appears in,
   and exits non-zero.
3. **Given** documentation containing an address that redirects, **When** the developer runs
   `fairdm-docs check`, **Then** the command reports the redirect separately from any failure and
   exits 0 if nothing else failed.
4. **Given** any run of the command, **When** it finishes, **Then** its report has been written
   alongside the HTML output rather than inside it.

---

### User Story 4 — The command bends to the portal that runs it (Priority: P4)

A developer whose documentation does not live in `docs/`, or who wants the site built elsewhere,
or who runs something else on port 5000, writes a line in their `pyproject.toml` and the command
obeys it.

**Why this priority**: most portals need none of this, which is the point. It exists so that the
ones that do are not forced off the command entirely.

**Independent Test**: set each setting in turn, run the command, and assert the build changed in
the way the setting describes.

**Acceptance Scenarios**:

1. **Given** a `[tool.fairdm.docs]` table naming a source directory, an output directory, a port
   and a verbosity, **When** the developer runs the command, **Then** each of those values is used
   in place of the corresponding default.
2. **Given** a project with no `[tool.fairdm.docs]` table at all, **When** the developer runs the
   command, **Then** every default applies and the build succeeds.
3. **Given** a table setting `django` to true, **When** the developer runs the command, **Then**
   Django is set up before the build runs.
4. **Given** a table setting only one key, **When** the developer runs the command, **Then** that
   key is used and every other setting keeps its default.

---

### User Story 5 — Every failure arrives as a message a developer can act on (Priority: P2)

A developer who has mistyped a bracket, pointed at a directory that does not exist, or asked for a
port outside the usable range gets one line telling them what is wrong and what to write instead.
They never get a stack trace.

**Why this priority**: the package's promise is that a developer does not have to understand
Sphinx. A traceback out of a TOML parser breaks that promise at the exact moment they are least
equipped to read it, and this is the story that carries the standing decision the code currently
violates.

**Independent Test**: produce each failure in turn and assert both the message and the absence of
a traceback.

**Acceptance Scenarios**:

1. **Given** a directory with no `pyproject.toml` anywhere above it, **When** the developer runs
   either command, **Then** it stops with a message saying a Python project is required, and exits
   non-zero.
2. **Given** a `pyproject.toml` that is not valid TOML, **When** the developer runs either
   command, **Then** it stops with a message naming the file as unreadable, with no traceback.
3. **Given** a configured source directory that does not exist, **When** the developer runs either
   command, **Then** it stops with a message naming the directory and the setting that changes it.
4. **Given** a configured port outside 1024–65535, or a verbosity that is not one of the three
   accepted values, **When** the developer runs either command, **Then** it stops with a message
   naming the value and what is accepted.
5. **Given** any of the above, **When** the command stops, **Then** the exit code is non-zero.

---

### Edge Cases

- A documentation source that exists but contains no root page is the builder's error to report,
  and reaches the developer through the builder's own output.
- Two preview servers on one port cannot both run; the second stops at the port check.
- Running `check` before anything has been built is supported — the check builds what it needs.
- An external address that times out counts as one that does not resolve, and the builder's own
  timeout governs.

## Requirements *(mandatory)*

### Functional Requirements

**The command itself**

- **FR-001**: Installing the package MUST make a `fairdm-docs` command available.
- **FR-002**: `fairdm-docs build` MUST render the portal's documentation source to HTML with no
  argument beyond the command, using defaults that suit a portal that has configured nothing.
- **FR-003**: The build MUST use the portal's own `docs/conf.py` when the documentation source
  contains one, and the package's own configuration when it does not. The two are never combined.
- **FR-004**: The build MUST make the directory the command was run from available to the
  configuration it runs, so that configuration can still find the portal after the builder changes
  directory.
- **FR-005**: The command MUST tell the developer that a build has started and, on success, where
  the site was written.
- **FR-006**: The command MUST pass the builder's own output to the developer unaltered unless a
  verbosity setting says otherwise.
- **FR-007**: The command MUST create the output directory's parent when it does not exist.

**Live preview**

- **FR-008**: `fairdm-docs build --live` MUST start a preview server against the configured source
  directory, output directory, port and configuration, which rebuilds the site when a source file
  changes.
- **FR-009**: `--live` MUST ask the preview server to open the site in the developer's browser.
- **FR-010**: `--live` MUST establish that the configured port is free before starting anything,
  and when it is not, MUST stop with a message naming the port and the setting that changes it.

**Checking**

- **FR-011**: `fairdm-docs check` MUST attempt to resolve every external address the documentation
  links to, and MUST report each one that does not resolve together with the file it is written
  in.
- **FR-012**: `check` MUST exit non-zero when at least one address does not resolve, and 0
  otherwise.
- **FR-013**: An address that resolves by redirection MUST be reported as a redirect, separately
  from addresses that failed, and MUST NOT by itself cause a non-zero exit.
- **FR-014**: `check` MUST write its report alongside the HTML output rather than inside it.

**Settings**

- **FR-015**: Both commands MUST read the `[tool.fairdm.docs]` table from the portal's
  `pyproject.toml`, and MUST apply their own default for every setting the table does not name.
- **FR-016**: The table MUST accept these settings, with these defaults:

  | Setting | Default | Effect |
  |---|---|---|
  | `source_dir` | `docs` | Where the documentation source is read from |
  | `build_dir` | `docs/_build/html` | Where the rendered site is written |
  | `port` | `5000` | The port the preview server listens on |
  | `verbosity` | `full` | How much of the builder's output reaches the developer |
  | `django` | `false` | Whether Django is set up before the build runs |

- **FR-017**: `verbosity` MUST accept `full`, which passes the builder's output through; `quiet`,
  which suppresses informational output; and `errors-only`, which suppresses everything the
  builder does not report as an error.
- **FR-018**: When `django` is true, the command MUST arrange for Django to be set up before the
  build runs. Which settings module is loaded is not decided here.
- **FR-019**: A value in the table MUST override the corresponding default.

**Failing**

- **FR-020**: Every way the portal's declaration can fail to be read MUST reach the developer as a
  single message naming what is wrong and what to write instead, never as a traceback. This covers
  at least: no `pyproject.toml` found, a `pyproject.toml` that is not valid TOML, a source
  directory that does not exist, a port outside 1024–65535, and a verbosity that is not one of the
  three accepted values.
- **FR-021**: Both commands MUST exit 0 on success and non-zero on any failure.
- **FR-022**: An interrupt MUST stop either command without a traceback and MUST exit 130, in
  every mode including live preview.

### Key Entities

- **The command**: `fairdm-docs`, with the subcommands `build` and `check`.
- **The settings**: the `[tool.fairdm.docs]` table, merged over the package's defaults.
- **The builder**: Sphinx, invoked by the command and responsible for everything downstream of it.
- **The preview server**: the upstream auto-rebuilding server the `--live` flag launches.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A project declaring a name and holding a documentation source with a root page
  builds through `fairdm-docs build` to rendered HTML on disk, and the criterion is decided by
  reading that HTML rather than by inspecting the arguments the builder was handed.
- **SC-002**: Both branches of FR-003 are decided by a build whose output differs according to
  which configuration was used.
- **SC-003**: Each of the five settings in FR-016 is set on its own and changes the build in the
  way the table describes.
- **SC-004**: Each failure enumerated in FR-020 produces a message naming the problem, and no
  output from any of them contains a traceback.
- **SC-005**: An interrupt in each of the three modes — build, live preview, check — exits 130.
- **SC-006**: A documentation source containing one address that does not resolve exits non-zero
  and names that address; the same source with that address replaced by one that redirects exits
  0 and reports the redirect.
- **SC-007**: No requirement above is decided solely by asserting on arguments handed to a stand-in
  for Sphinx, with the single exception of FR-008 and FR-009, whose behaviour belongs to the
  upstream server.

## Assumptions

- The package is installed in the environment the command runs in.
- The documentation source follows Sphinx's conventions, because Sphinx builds it.
- A portal being documented is a Python project, so it has a `pyproject.toml`.
- The developer runs the command from the portal's root directory.
- Whether a build succeeds once the builder has started is the builder's business and the business
  of the roadmap items that configure it.

## Out of Scope

- Output formats other than HTML. Sphinx builds them and a developer who needs one can call it.
- Publishing anywhere, which is R7.
- Making the zero-configuration Markdown path succeed, which is R3.
- Where a portal's branding, static files and bibliography are found, which are R4 and R8.
- Which Django settings module a build loads, which is R6.
- A single definition of the settings table shared by everything that reads it, which is R10.
- Validators beyond the resolution of external addresses.
- Configuration through environment variables or command-line flags beyond `--live`.
- More than one preview server at a time.
