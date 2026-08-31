# Tasks — 001

**Specification**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Written from the specification alone, as though the repository contained no code. Nothing was
carried over from the previous version of this file, and the reasons are in
[decisions.md](decisions.md), D10. Which of these are already satisfied is settled afterwards, in
[reconciliation.md](reconciliation.md), against the code and the test suite together.

`[P]` marks a task that touches a file no other `[P]` task in the same group touches, so it can be
worked in parallel with them.

Article I governs the order: within each story the test tasks come before the implementation task
they cover, and they are expected to fail when written.

## Phase 1 — Shared test infrastructure

- **T001** `tests/conftest.py` — a fixture that writes a temporary portal from a given declaration:
  a `pyproject.toml`, a `docs/` directory, a `docs/index.rst` and a `docs/conf.py` containing only
  `from fairdm_docs.conf import *`. The repository has no `conftest.py` today.
- **T002** `tests/conftest.py` — a fixture that builds such a portal's documentation for real and
  returns the rendered HTML together with the build output. Required by SC-006 and Article IV.
- **T003** [P] `tests/fixtures/` — the declarations these tests read: a full one, one carrying only
  `name`, one carrying only `[tool.poetry]`, one with neither table, one with `[project]` but no
  `name`, one that is not valid TOML, one declaring its version dynamic with a `[tool.poetry]`
  version behind it, one whose `[project.urls]` keys are variously capitalised, and one with both
  author forms.

## Phase 2 — US1: a portal's declared identity appears on its site (P1)

**Goal**: the rendered site carries the portal's name, version, authors and year.
**Independently testable**: build a site from a filled-in declaration and read those values back
out of the HTML.

- **T004** [P] `tests/test_metadata.py::TestProjectMetadata` — `name`, `version` and `description`
  are read from the `[project]` table of a parsed declaration. (FR-001, FR-002)
- **T005** [P] `tests/test_metadata.py::TestAuthors` — an author written as `"Name <email>"` and one
  written as `"Name"` each produce a display name. (FR-003)
- **T006** [P] `tests/test_metadata.py::TestAuthors` — an author written as a table produces the same
  display name the string form would have produced. (FR-003)
- **T007** [P] `tests/test_metadata.py::TestProjectMetadata` — the copyright is the current year
  followed by the display names. (FR-009)
- **T008** `fairdm_docs/metadata.py` — `ProjectMetadata` and `from_toml_data`, covering T004 to T007.
- **T009** [P] `tests/test_conf.py::TestSiteIdentity` — the site's project name is the declared name
  exactly as declared, including a name that is an acronym and a name containing a hyphen: no change
  of case, no substitution of characters. (FR-007, SC-002)
- **T010** [P] `tests/test_conf.py::TestSiteIdentity` — the site's version and release are the
  declared version. (FR-008)
- **T011** [P] `tests/test_conf.py::TestSiteIdentity` — the site's author and copyright are built
  from the declared authors. (FR-009, FR-010)
- **T012** `fairdm_docs/conf.py` — assign the Sphinx namespace from `ProjectMetadata`, covering T009
  to T011.
- **T013** `tests/test_conf.py::TestRenderedSite` — build a real site from a declaration carrying
  name, version, description and authors, and assert the title, the version and the copyright in the
  rendered HTML. (SC-001, SC-006)

**Checkpoint**: a portal with a filled-in declaration gets a site that is recognisably its own.

## Phase 3 — US2: a portal declaring almost nothing still builds (P2)

**Goal**: a build succeeds from one declared field, and says what it had to invent.
**Independently testable**: build from a declaration carrying only `name`.

- **T014** [P] `tests/test_metadata.py::TestDefaults` — an absent version, authors, description and
  address each take their specified default. (FR-012)
- **T015** [P] `tests/test_metadata.py::TestDefaults` — one warning is emitted per defaulted field
  and each names its field. (FR-013)
- **T016** [P] `tests/test_metadata.py::TestDefaults` — a version declared dynamic falls back to a
  version under `[tool.poetry]`. (FR-006)
- **T017** `fairdm_docs/metadata.py` — the defaults, the per-field warnings through the
  documentation build's own logger, and the dynamic-version fallback, covering T014 to T016.
  (FR-006, FR-012, FR-013, FR-014)
- **T018** `tests/test_conf.py::TestRenderedSite` — build a real site from a declaration carrying
  only `name`, assert the build succeeds, and assert the build output names each defaulted field.
  (SC-003, FR-014)

**Checkpoint**: the zero-configuration path is the tested path (Article XIII).

## Phase 4 — US3: a portal that cannot be identified is told exactly why (P3)

**Goal**: five failure conditions, each producing a message a developer can act on.
**Independently testable**: drive each condition and assert on the error type and its message.

- **T019** [P] `tests/test_metadata.py::TestFailures` — a declaration with no `[project]` table but a
  `[tool.poetry]` table fails with a message saying PEP 621 is required, that the legacy format is
  not read, and linking the migration guide. (FR-016)
- **T020** [P] `tests/test_metadata.py::TestFailures` — a declaration with neither table fails with a
  message saying what to add. (FR-016)
- **T021** [P] `tests/test_metadata.py::TestFailures` — a `[project]` table with no `name` fails with
  a message naming the field and showing where it goes, and the message renders as line breaks
  rather than showing escape characters. (FR-017)
- **T022** [P] `tests/test_metadata.py::TestFailures` — a file that is not valid TOML fails with a
  message identifying the problem as TOML syntax and carrying the parser's own description. (FR-018)
- **T023** [P] `tests/test_metadata.py::TestFailures` — an absent file fails with a message naming
  where it looked. (FR-019)
- **T024** [P] `tests/test_metadata.py::TestFailures` — every one of the five raises the single error
  type this package's command already recognises. (FR-015)
- **T025** `fairdm_docs/metadata.py` — `from_file`, and the failures throughout, covering T019 to
  T024. (FR-015 to FR-019)
- **T026** `tests/test_cli.py::TestConfigurationFailures` — the command reports one of these
  failures as a message rather than a traceback. (SC-004)

**Checkpoint**: a first-attempt mistake is a fixable message.

## Phase 5 — US4: a portal's declared addresses reach the site (P4)

**Goal**: the declared addresses are extracted and available.
**Independently testable**: declare the same address under several capitalisations.

- **T027** [P] `tests/test_metadata.py::TestAddresses` — the homepage and repository addresses are
  read from `[project.urls]`. (FR-002)
- **T028** [P] `tests/test_metadata.py::TestAddresses` — a key written `Repository`, `repository` or
  `REPOSITORY` is found in every case, while PEP 621's own field names are matched exactly as the
  standard spells them. (FR-004, SC-005)
- **T029** [P] `tests/test_metadata.py::TestAddresses` — where one address is needed and both are
  declared, the repository address is used. (FR-005)
- **T030** [P] `tests/test_metadata.py::TestAddresses` — a declaration with no `[project.urls]` table
  leaves both addresses empty and fails at nothing. (FR-012)
- **T031** `fairdm_docs/metadata.py` — address extraction, the case-insensitive lookup and the
  preference, covering T027 to T030. (FR-004, FR-005)
- **T032** `tests/test_conf.py::TestSiteIdentity` — the extracted addresses reach the site's theme
  configuration. Whether furniture is drawn from them is out of scope. (FR-011)

**Checkpoint**: every requirement in the specification has a test.

## Phase 6 — Edge cases

- **T033** [P] `tests/test_metadata.py::TestEdgeCases` — a `[project]` table present but empty; an
  `authors` list present but empty; an author string with no email; an author string that is only an
  email; an author table with an email and no name; a version declared dynamic with nothing to fall
  back on; a `[project.urls]` table declaring one address twice under two capitalisations; a declared
  name that is not a valid distribution name.

## Phase 7 — Polish

- **T034** [P] `README.md` and `CHANGELOG.md` — the site title is now the declared name rather than a
  prettied version of it, what a portal sees change, and what it does if it wanted the old title.
  (Article VI, Article XIV)
- **T035** The whole suite, the lint and type gates, and coverage. The configuration module's
  coverage is no longer zero. (SC-006)

## Dependencies

- Phase 1 blocks everything.
- T008 blocks T012; T012 blocks T013.
- T017 blocks T018. T025 blocks T026. T031 blocks T032.
- The four stories are independent of one another once Phase 1 is done, other than that they edit
  `fairdm_docs/metadata.py` in turn.
- Phase 7 comes last.
