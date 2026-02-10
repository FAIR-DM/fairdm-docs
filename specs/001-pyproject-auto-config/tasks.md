# Tasks: PEP 621 pyproject.toml Auto-Configuration

**Feature**: 001-pyproject-auto-config  
**Input**: Design documents from `/specs/001-pyproject-auto-config/`  
**Prerequisites**: plan.md, spec.md, data-model.md, quickstart.md

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create test fixtures and prepare project structure

- [X] T001 Create fixtures directory at `specs/001-pyproject-auto-config/fixtures/`
- [X] T002 [P] Create minimal test fixture `specs/001-pyproject-auto-config/fixtures/minimal_pyproject.toml` with only [project].name
- [X] T003 [P] Create full test fixture `specs/001-pyproject-auto-config/fixtures/full_pyproject.toml` with all PEP 621 fields and case variations (Homepage/homepage)
- [X] T004 [P] Create legacy test fixture `specs/001-pyproject-auto-config/fixtures/legacy_pyproject.toml` with only [tool.poetry] section
- [X] T005 [P] Create no_project test fixture `specs/001-pyproject-auto-config/fixtures/no_project_pyproject.toml` missing [project] section
- [X] T006 [P] Create fairdm_config test fixture `specs/001-pyproject-auto-config/fixtures/fairdm_config_pyproject.toml` with [tool.fairdm.docs] section

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create backup of existing `fairdm_docs/conf.py` as `fairdm_docs/conf.py.bak`
- [X] T008 Add tomllib/tomli import handling in `fairdm_docs/conf.py` (try tomllib for Python 3.11+, fallback to tomli)
- [X] T009 [P] Create helper function `_normalize_key(key: str) -> str` in `fairdm_docs/conf.py` for case-insensitive lookups
- [X] T010 [P] Create helper function `_load_pyproject() -> dict` in `fairdm_docs/conf.py` with error handling for missing file and TOML syntax errors
- [X] T011 Create data classes or TypedDict definitions for ProjectMetadata, FairDMDocsConfig, BrandingAssets in `fairdm_docs/conf.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Zero-Config Documentation Setup (Priority: P1) 🎯 MVP

**Goal**: Enable developers to create functional documentation with only `from fairdm_docs.conf import *` - automatic extraction of project name, version, authors, and copyright from minimal PEP 621 pyproject.toml

**Independent Test**: Create docs/conf.py with single import line, minimal pyproject.toml with only [project].name, run sphinx-build, verify HTML contains project name and sensible defaults

### Implementation for User Story 1

- [X] T012 [US1] Implement `_extract_project_metadata(data: dict) -> dict` in `fairdm_docs/conf.py` to extract [project].name with case-insensitive key lookup
- [X] T013 [US1] Add project.name validation to `_extract_project_metadata()` - raise ConfigurationError if missing with message: "Missing required 'project.name' in pyproject.toml. Add [project]\nname = 'your-project-name'"
- [X] T014 [US1] Extend `_extract_project_metadata()` to extract [project].version with default "0.0.0"
- [X] T015 [US1] Extend `_extract_project_metadata()` to extract [project].authors with default ["Unknown"], parse "Name <email>" format
- [X] T016 [US1] Add copyright generation logic in `fairdm_docs/conf.py` using current year + extracted author names
- [X] T017 [US1] Add warning logs for missing optional fields (version, authors, description) using sphinx.util.logging
- [X] T018 [US1] Update main config section in `fairdm_docs/conf.py` to use extracted metadata for project, version, release, copyright variables
- [X] T019 [US1] Test with minimal fixture: verify defaults applied, warnings logged, build succeeds

**Checkpoint**: User Story 1 complete - zero-config docs build successfully with minimal pyproject.toml

---

## Phase 4: User Story 2 - PEP 621 Standard Compliance (Priority: P2)

**Goal**: Full PEP 621 field extraction (description, urls.homepage, urls.repository) with strict validation - reject legacy [tool.poetry] format

**Independent Test**: Create full_pyproject.toml with all PEP 621 fields including case variations, verify all metadata extracted correctly; test legacy fixture raises ConfigurationError

### Implementation for User Story 2

- [X] T020 [US2] Extend `_extract_project_metadata()` in `fairdm_docs/conf.py` to extract [project].description with default ""
- [X] T021 [US2] Extend `_extract_project_metadata()` to extract [project.urls] with case-insensitive lookups (Homepage/homepage, Repository/repository)
- [X] T022 [US2] Add validation in `_load_pyproject()` to detect missing [project] section and raise ConfigurationError: "PEP 621 [project] section required. Legacy [tool.poetry] format is not supported. Please migrate: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/"
- [X] T023 [US2] Add TOML syntax error handling in `_load_pyproject()` with ConfigurationError: "Invalid TOML syntax in pyproject.toml: {error_details}"
- [X] T024 [US2] Add file not found error handling in `_load_pyproject()` with ConfigurationError: "pyproject.toml not found at {expected_path}. Ensure it exists at repository root."
- [X] T025 [US2] Update config section in `fairdm_docs/conf.py` to populate html_theme_options['repository_url'] from extracted urls.repository
- [X] T026 [US2] Test with full fixture: verify all fields extracted with correct case handling
- [X] T027 [US2] Test with legacy fixture: verify ConfigurationError raised with migration message
- [X] T028 [US2] Test with no_project fixture: verify ConfigurationError raised requesting [project] section

**Checkpoint**: User Story 2 complete - full PEP 621 compliance with strict validation

---

## Phase 5: User Story 3 - Theme Selection and Configuration (Priority: P3)

**Goal**: Support both sphinx-book-theme (default) and pydata-sphinx-theme with automatic theme-specific option configuration

**Independent Test**: Create two test projects - one with default theme, one with pydata theme override in conf.py; verify theme-specific options correctly applied

### Implementation for User Story 3

- [X] T029 [P] [US3] Implement `_apply_theme_config(theme: str, metadata: dict) -> dict` in `fairdm_docs/conf.py` for sphinx_book_theme options
- [X] T030 [P] [US3] Extend `_apply_theme_config()` to handle pydata_sphinx_theme options (github_url, navbar_end, icon_links)
- [X] T031 [US3] Implement `_resolve_branding_assets() -> dict` in `fairdm_docs/conf.py` to check docs/_static/brand/ for logo.svg and icon.svg
- [X] T032 [US3] Add fallback logic in `_resolve_branding_assets()` to use fairdm_docs/_static/ defaults if project assets not found
- [X] T033 [US3] Update config section in `fairdm_docs/conf.py` to call `_apply_theme_config()` and populate html_theme_options
- [X] T034 [US3] Update config section to set html_logo and html_favicon from `_resolve_branding_assets()` results
- [X] T035 [US3] Configure utterances comments in html_theme_options using repository URL from metadata
- [X] T036 [US3] Test default theme: verify sphinx_book_theme options populated (repository buttons, edit page buttons)
- [X] T037 [US3] Test pydata theme: manually override html_theme in conf.py, verify pydata options applied

**Checkpoint**: User Story 3 complete - both themes work with correct options

---

## Phase 6: User Story 4 - Simple Configuration in pyproject.toml (Priority: P4)

**Goal**: Allow theme selection via [tool.fairdm.docs] section in pyproject.toml - declarative configuration without Python code

**Independent Test**: Create fairdm_config fixture with [tool.fairdm.docs].theme = "pydata_sphinx_theme", import conf without overrides, verify PyData theme used

### Implementation for User Story 4

- [X] T038 [US4] Implement `_extract_fairdm_config(data: dict) -> dict` in `fairdm_docs/conf.py` to read [tool.fairdm.docs] section
- [X] T039 [US4] Extract theme setting from [tool.fairdm.docs].theme with None default if section missing
- [X] T040 [US4] Add theme validation in `_extract_fairdm_config()` to check against known themes (sphinx_book_theme, pydata_sphinx_theme)
- [X] T041 [US4] Add warning log for invalid theme: "Unknown theme '{theme}' in [tool.fairdm.docs], using default sphinx_book_theme"
- [X] T042 [US4] Add debug log for unknown keys in [tool.fairdm.docs] section
- [X] T043 [US4] Implement configuration precedence logic: conf.py overrides > [tool.fairdm.docs] > defaults
- [X] T044 [US4] Update main config section to apply [tool.fairdm.docs].theme before user conf.py can override
- [X] T045 [US4] Test with fairdm_config fixture: verify pydata theme applied from TOML
- [X] T046 [US4] Test precedence: set theme in TOML and override in conf.py, verify conf.py wins

**Checkpoint**: User Story 4 complete - TOML-based configuration working with proper precedence

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, examples, validation, and cleanup

- [X] T047 [P] Update `README.md` with PEP 621 auto-configuration section and examples
- [X] T048 [P] Update `examples/basic_conf.md` to show minimal PEP 621 setup
- [X] T049 [P] Update `examples/custom_theme_conf.md` to show [tool.fairdm.docs] usage
- [X] T050 [P] Create example in `examples/fairdm_portal_conf.md` showing full metadata extraction
- [X] T051 [P] Update `CHANGELOG.md` with migration guide from [tool.poetry] to PEP 621
- [X] T052 [P] Validate quickstart.md instructions with actual build test
- [X] T053 Remove backup file `fairdm_docs/conf.py.bak` after validation
- [X] T054 Add docstrings to all helper functions in `fairdm_docs/conf.py` with type hints
- [X] T055 [P] Test case-insensitive key handling with uppercase/mixed case pyproject.toml
- [X] T056 Test branding asset detection with custom brand assets in docs/_static/brand/
- [X] T057 Manual regression test: ensure Django integration (django.setup()) still works in fairdm_docs/conf.py (deferred to end-user projects - see T057_django_integration_test.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (US1 - Zero-Config)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (US2 - PEP 621 Compliance)**: Builds on US1 implementation (extends metadata extraction) - Start after US1 complete
- **User Story 3 (US3 - Theme Selection)**: Can start after US1 complete, uses metadata from US1/US2
- **User Story 4 (US4 - TOML Config)**: Depends on US3 (theme configuration) - Start after US3 complete

**Recommended Order**: US1 → US2 → US3 → US4 (sequential due to implementation dependencies)

### Within Each User Story

1. Setup helper functions/data structures first
2. Implement extraction logic
3. Add validation and error handling
4. Update main config section
5. Test with fixtures
6. Verify story independently works

### Parallel Opportunities

**Setup Phase**:
- T002, T003, T004, T005, T006 (all fixture creation)

**Foundational Phase**:
- T009, T010 (helper functions)

**User Story 3**:
- T029, T030 (theme config functions)

**Polish Phase**:
- T047, T048, T049, T050, T051, T052 (documentation tasks)

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes:

# Sequential execution (single developer):
Task T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019

# If team: Phase 3 can proceed while Phase 4 waits
# But within US1, tasks must be sequential (all modify same function)
```

---

## Parallel Example: Polish Phase

```bash
# All documentation tasks can run in parallel:
Task T047: Update README.md
Task T048: Update examples/basic_conf.md
Task T049: Update examples/custom_theme_conf.md
Task T050: Update examples/fairdm_portal_conf.md
Task T051: Update CHANGELOG.md
Task T052: Validate quickstart.md
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (fixtures)
2. Complete Phase 2: Foundational (helper functions, data structures)
3. Complete Phase 3: User Story 1 (zero-config metadata extraction)
4. **STOP and VALIDATE**: Test US1 with minimal fixture independently
5. If validation passes, basic MVP is ready

**MVP Deliverable**: Developers can create docs with one-line conf.py and minimal pyproject.toml

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP COMPLETE** ✅
3. Add User Story 2 → Test independently → **Full PEP 621 Support** ✅
4. Add User Story 3 → Test independently → **Theme Flexibility** ✅
5. Add User Story 4 → Test independently → **TOML Configuration** ✅
6. Polish Phase → **Production Ready** ✅

### Testing Cadence

- After each user story: Run story-specific fixture tests
- After US2 complete: Run full test matrix (all 5 fixtures)
- After US4 complete: Full regression test with all fixtures + manual theme tests
- During Polish: Validate quickstart.md with fresh project

### Parallel Team Strategy (If Multiple Developers)

With 2 developers:
1. Both complete Setup + Foundational together
2. Once Foundational done:
   - Developer A: US1 → US2 (sequential, extend same code)
   - Developer B: Create documentation (US4 spec examples)
3. After US2 complete:
   - Developer A: US3 (theme config)
   - Developer B: US4 (TOML config)
4. Both: Polish phase in parallel

---

## Validation Checklist

After all phases complete, verify:

- [ ] All 19 functional requirements (FR-001 to FR-019) implemented
- [ ] All 4 user stories demonstrable with test fixtures
- [ ] All 7 success criteria met:
  - [ ] SC-001: One-line conf.py works (<1 minute setup)
  - [ ] SC-002: All Sphinx variables auto-populated
  - [ ] SC-003: Missing optional fields don't block builds
  - [ ] SC-004: Missing critical fields show clear errors
  - [ ] SC-005: Theme switching works without errors
  - [ ] SC-006: No Sphinx knowledge required
  - [ ] SC-007: TOML configuration works
- [ ] Case-insensitive key handling tested (Homepage vs homepage)
- [ ] Branding asset fallback chain tested
- [ ] Legacy format rejection tested with clear migration message
- [ ] Documentation updated (README, CHANGELOG, examples)
- [ ] quickstart.md validated with actual build

---

## Estimated Effort

**Total**: ~10-14 hours development + 2-3 hours testing

| Phase | Tasks | Est. Time |
|-------|-------|-----------|
| Setup (Phase 1) | T001-T006 | 30 min |
| Foundational (Phase 2) | T007-T011 | 1 hour |
| US1 - Zero-Config (Phase 3) | T012-T019 | 2-3 hours |
| US2 - PEP 621 (Phase 4) | T020-T028 | 2-3 hours |
| US3 - Themes (Phase 5) | T029-T037 | 2-3 hours |
| US4 - TOML Config (Phase 6) | T038-T046 | 1-2 hours |
| Polish (Phase 7) | T047-T057 | 2-3 hours |

---

## Notes

- **[P] tasks**: Different files or independent operations, can run in parallel
- **[Story] labels**: Map task to user story for traceability and independent testing
- **Sequential dependencies**: US2 extends US1, US4 depends on US3 - follow priority order
- **Test early**: Use fixtures after each user story to catch issues early
- **Commit frequently**: After each task or logical task group
- **Django compatibility**: Maintain existing django.setup() calls in conf.py
- **Version bump**: This is breaking change requiring MINOR version bump (0.1.0 → 0.2.0)
