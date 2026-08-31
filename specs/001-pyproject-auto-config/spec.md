# Feature Specification: The portal's metadata becomes the site's identity

**Feature Branch**: `001-pyproject-auto-config`
**Created**: 2026-02-10
**Rewritten**: 2026-08-31
**Status**: Specified
**Roadmap item**: R2 — *The portal's own metadata becomes the site's identity*
**Goals served**: G4 — *The rendered site carries the portal's own name, description and branding
rather than the framework's*

A portal has already declared what it is called, what version it is, who wrote it and where it
lives. It declared all of that for packaging, in `pyproject.toml`, in the format Python standardised
in PEP 621. This feature reads that declaration and turns it into the identity of the rendered
documentation site, so that a portal which has stated a fact once is never asked to state it again.

A fact that is missing and optional produces a warning and a sensible default. A fact that is
missing and required stops the build with a message naming what to add and where.

**Prior version:** this specification was rewritten on 2026-08-31. What changed, and why, is in
[decisions.md](decisions.md).

## Clarifications

### Session 2026-02-10

- Q: Legacy format support strategy → A: PEP 621 only. A file carrying only `[tool.poetry]` is an
  error, with a link to the migration guide.

### Session 2026-08-31

- Q: Does this feature decide *which* `pyproject.toml` is read? → A: No. Locating the portal being
  documented is R4. This feature begins once a parsed file is in hand, and its requirements hold
  whichever file that turns out to be.
- Q: Does this feature draw the repository and edit buttons on the page? → A: No. It extracts the
  addresses and makes them available. Whether furniture appears, and what happens when there is no
  address to draw it from, is R3.
- Q: Does this feature read the `[tool.fairdm.docs]` settings table? → A: No. That table is R10,
  which covers all of it rather than the one key this specification previously mentioned.
- Q: When the declared name and the site title disagree, which is right? → A: The declared name.
  The title is the portal's name, not a prettied version of it. A portal that wants a different
  display title is asking for a setting, and settings are R10.
- Q: Should key lookups be case-insensitive everywhere? → A: Only under `[project.urls]`, whose key
  names are chosen by whoever wrote the file. PEP 621's own field names are matched as the standard
  spells them.
- Q: Where should a warning about a defaulted field appear? → A: In the build output, where the
  developer is already reading. A warning delivered anywhere else has not been delivered.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A portal's declared identity appears on its site (Priority: P1)

A developer has a portal with a filled-in `[project]` table. They build the documentation and the
rendered site carries their portal's name in the title, their version in the version line, and their
authors and the current year in the copyright. They wrote nothing down twice.

**Why this priority**: this is the whole of G4 and the reason the feature exists. Without it the
site advertises the framework instead of the portal.

**Independent Test**: build a site from a project declaring name, version, description and authors,
and read those values back out of the rendered HTML.

**Acceptance Scenarios**:

1. **Given** a project declaring `name`, `version`, `description` and `authors`, **When** the
   documentation is built, **Then** the site's title is the declared name, the version line is the
   declared version, and the copyright names the declared authors and the current year.
2. **Given** a project whose declared name contains capitals or is an acronym, such as `GHFDB`,
   **When** the documentation is built, **Then** the site's title is that name exactly as declared,
   with no change of case and no substitution of characters.
3. **Given** a project declaring authors as PEP 621 tables rather than strings, **When** the
   documentation is built, **Then** the copyright names the same people it would have named had they
   been written as strings.

---

### User Story 2 — A portal declaring almost nothing still builds (Priority: P2)

A developer has a new portal whose `pyproject.toml` carries a name and little else. They build the
documentation and get a site. Every fact the build had to invent is named in the build output, so
they can see what to fill in next, and nothing stops them.

**Why this priority**: the package's first promise is a site from nearly nothing. A build that
refuses until the packaging metadata is complete breaks that promise for exactly the projects most
likely to be trying the package for the first time.

**Independent Test**: build a site from a project declaring only `project.name` and assert both that
it succeeds and that the build output names each defaulted field.

**Acceptance Scenarios**:

1. **Given** a project declaring only `project.name`, **When** the documentation is built, **Then**
   the build succeeds.
2. **Given** that same project, **When** the documentation is built, **Then** the build output names
   each field that was defaulted, one message per field.
3. **Given** a project declaring its version as dynamic while carrying a version under
   `[tool.poetry]`, **When** the documentation is built, **Then** that version is used rather than
   the placeholder.

---

### User Story 3 — A portal that cannot be identified is told exactly why (Priority: P3)

A developer's `pyproject.toml` is missing, unparseable, written in a format this package does not
read, or missing the one field that has no sensible default. The build stops and says which of those
happened, names the file or field at fault, and does so as a message rather than a stack trace
pointing into somebody else's package.

**Why this priority**: these are the failures a developer meets on their first attempt, and a
traceback at that moment is the difference between a fixable mistake and an abandoned tool.

**Independent Test**: drive each failure condition and assert on the error type and the text of its
message.

**Acceptance Scenarios**:

1. **Given** a `pyproject.toml` with no `[project]` table but a `[tool.poetry]` table, **When** the
   documentation is built, **Then** the build stops with a message saying PEP 621 is required and
   linking the migration guide.
2. **Given** a `pyproject.toml` with neither table, **When** the documentation is built, **Then** the
   build stops with a message saying what to add.
3. **Given** a `[project]` table with no `name`, **When** the documentation is built, **Then** the
   build stops with a message naming the field and showing where it goes, rendered as readable
   lines.
4. **Given** a `pyproject.toml` that is not valid TOML, **When** the documentation is built, **Then**
   the build stops with a message identifying it as a syntax problem and quoting the parser's own
   description of it.
5. **Given** no `pyproject.toml` at all, **When** the documentation is built, **Then** the build
   stops with a message naming where it looked.
6. **Given** any of the above, **When** the failure is raised, **Then** it is the one error type this
   package's command already recognises, so the developer sees the message and not a traceback.

---

### User Story 4 — A portal's declared addresses reach the site (Priority: P4)

A developer has declared a repository address under `[project.urls]`. The rendered site's
integrations use it, and it is found whether they capitalised the key or not.

**Why this priority**: the addresses are part of the declared identity, but what is built on top of
them is scheduled elsewhere, so this story delivers the value and stops at the boundary.

**Independent Test**: declare the same address under several capitalisations and assert it is
extracted each time.

**Acceptance Scenarios**:

1. **Given** `[project.urls]` declaring a repository address, **When** metadata is extracted,
   **Then** that address is available to the site's configuration.
2. **Given** the key written as `Repository`, `repository` or `REPOSITORY`, **When** metadata is
   extracted, **Then** the address is found in every case.
3. **Given** both a homepage and a repository address, **When** one address is needed, **Then** the
   repository address is the one used.
4. **Given** no `[project.urls]` table, **When** metadata is extracted, **Then** both addresses are
   empty and nothing fails.

---

### Edge Cases

- A `[project]` table present but empty.
- `authors` present but an empty list.
- An author string with no email, an author string that is only an email, and an author table with
  an email but no name.
- A version declared dynamic with no `[tool.poetry]` version to fall back on.
- A `[project.urls]` table declaring the same address twice under two capitalisations.
- A declared name that is not a valid Python distribution name.

## Requirements *(mandatory)*

### Functional Requirements

**Reading the declaration**

- **FR-001**: System MUST read project metadata from the PEP 621 `[project]` table of a parsed
  `pyproject.toml`. Which file that is, and how it is located, is out of scope (R4).
- **FR-002**: System MUST extract `name`, `version`, `description`, `authors` and the `[project.urls]`
  table.
- **FR-003**: System MUST accept both PEP 621 author forms — a string of the form `"Name <email>"` or
  `"Name"`, and a table of the form `{name = "...", email = "..."}` — and MUST produce a display name
  from each.
- **FR-004**: System MUST match key names under `[project.urls]` without regard to case. System MUST
  match PEP 621's own field names exactly as the standard spells them.
- **FR-005**: System MUST prefer the repository address over the homepage address wherever a single
  address is required.
- **FR-006**: System MUST fall back to a version declared under `[tool.poetry]` when `[project]`
  declares its version dynamic and supplies none.

**Becoming the site's identity**

- **FR-007**: System MUST set the site's project name to the declared name exactly as declared,
  applying no change of case and no substitution of characters.
- **FR-008**: System MUST set the site's version and release from the declared version.
- **FR-009**: System MUST set the site's copyright from the current year and the display names of
  the declared authors.
- **FR-010**: System MUST set the site's author from the display names of the declared authors.
- **FR-011**: System MUST make the extracted repository and homepage addresses available to the
  site's theme configuration. Whether page furniture is drawn from them is out of scope (R3).

**Missing optional facts**

- **FR-012**: System MUST supply defaults for optional fields it does not find: version `0.0.0`,
  authors `["Unknown"]`, description empty, and both addresses empty.
- **FR-013**: System MUST emit one warning per optional field it defaults, naming the field.
- **FR-014**: System MUST emit those warnings into the documentation build's own output, so that a
  developer reading the build sees them without configuring anything to make them visible.

**Failures**

- **FR-015**: System MUST raise a single error type for every failure in this specification, and it
  MUST be the type this package's command already recognises and reports as a message rather than a
  traceback.
- **FR-016**: System MUST fail when no `[project]` table is present. Where a `[tool.poetry]` table is
  present instead, the message MUST say that PEP 621 is required, that the legacy format is not
  supported, and MUST link the migration guide. Where neither is present, the message MUST say what
  to add.
- **FR-017**: System MUST fail when `[project]` declares no `name`, with a message naming the field
  and showing where it goes. The message MUST render as readable lines rather than showing escape
  characters to the developer.
- **FR-018**: System MUST fail on a `pyproject.toml` that is not valid TOML, with a message
  identifying the problem as TOML syntax and including the parser's own description of it.
- **FR-019**: System MUST fail when no `pyproject.toml` is found, with a message naming where it
  looked.

### Key Entities

- **Project Metadata** — what a portal declared about itself for packaging: its name, version,
  description, the display names of its authors, and its homepage and repository addresses. It is
  read once and every value below is derived from it.

## Success Criteria *(mandatory)*

- **SC-001**: A portal declaring name, version, description, authors and a repository address builds
  a site whose title, version line and copyright carry that portal's own values, with no
  documentation configuration written by the developer.
- **SC-002**: A declared name containing capitals or an acronym appears on the built site exactly as
  declared.
- **SC-003**: A portal declaring only a name builds successfully, and the build output names every
  field that was defaulted.
- **SC-004**: Each of the five failure conditions produces the package's own error type, carrying a
  message that names the field or file at fault, and the command reports it without a traceback.
- **SC-005**: A repository address is found whatever the capitalisation of its key.
- **SC-006**: Every requirement above is covered by a test, and the identity requirements are
  covered at least once by a test that reads a rendered site rather than only the values extracted
  on the way to it.

## Risks *(mandatory)*

- **Risk**: using the declared name verbatim changes the title of sites that build today, from
  "Fairdm Docs" to "fairdm-docs".
  **Mitigation**: accepted, and it is the point. The declared name is the portal's own and the
  transformed one is not. A portal wanting a different display title is asking for a setting, which
  R10 covers. No consumer has pinned a release of this package, so no published site changes without
  a deliberate update.

- **Risk**: this feature's requirements are stated against a parsed file, while the file itself is
  located by code that R4 is scheduled to change.
  **Mitigation**: the requirements are written so that none of them depends on how the file was
  found. R4 may change the answer without changing anything specified here.

- **Risk**: a project declaring only `[tool.poetry]` cannot build its documentation at all.
  **Mitigation**: unchanged from the original decision, taken 2026-02-10, and PEP 621 has been the
  standard since 2021. The message links the migration guide.

- **Risk**: sending warnings into the build's own output makes them subject to whatever the build
  does with warnings, including failing on them.
  **Mitigation**: intended. R7 asks for a build that can be made to fail on warnings so a broken
  site is caught before publication, and a defaulted field is exactly the kind of thing a portal
  should be able to decide to treat as an error.

## Out of scope

Each of these was covered by the original version of this specification and now belongs elsewhere.
None is dropped.

| Subject | Owner |
|---|---|
| Which `pyproject.toml` is read, and from where | R4 |
| Where branding assets are found | R4 |
| Repository, issue and edit buttons, and the comment system | R3 |
| The extension list and its defaults | R3, R8 |
| The `[tool.fairdm.docs]` settings table, theme selection, precedence, unknown keys | R10 |
| End-to-end build tests, model documentation coverage, dependency bounds | R11 |
