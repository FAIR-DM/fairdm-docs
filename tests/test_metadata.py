"""Tests for fairdm_docs.metadata.ProjectMetadata."""

from datetime import datetime

import pytest

from fairdm_docs.config import ConfigError
from fairdm_docs.metadata import ProjectMetadata


class TestProjectMetadata:
    """ProjectMetadata built from a parsed [project] table."""

    def test_name_version_and_description_are_the_declared_values(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "version": "1.2.3",
                    "description": "A sample research data portal",
                    "authors": ["Jane Doe <jane@example.com>"],
                }
            }
        )

        assert metadata.name == "sample-portal"
        assert metadata.version == "1.2.3"
        assert metadata.description == "A sample research data portal"

    def test_copyright_is_the_current_year_and_the_display_names(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "version": "1.2.3",
                    "description": "A sample research data portal",
                    "authors": [
                        "Jane Doe <jane@example.com>",
                        "John Smith",
                    ],
                }
            }
        )

        assert metadata.copyright == f"{datetime.now().year}, Jane Doe, John Smith"


class TestAuthors:
    """Display names built from PEP 621's author forms."""

    def test_author_string_with_email_produces_a_display_name(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "version": "1.2.3",
                    "description": "",
                    "authors": ["Jane Doe <jane@example.com>"],
                }
            }
        )

        assert metadata.authors == ["Jane Doe"]

    def test_author_string_without_email_produces_a_display_name(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "version": "1.2.3",
                    "description": "",
                    "authors": ["Jane Doe"],
                }
            }
        )

        assert metadata.authors == ["Jane Doe"]

    def test_author_table_produces_the_same_display_name_as_the_string_form(self):
        string_form = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "version": "1.2.3",
                    "description": "",
                    "authors": ["Jane Doe <jane@example.com>"],
                }
            }
        )
        table_form = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "version": "1.2.3",
                    "description": "",
                    "authors": [{"name": "Jane Doe", "email": "jane@example.com"}],
                }
            }
        )

        assert table_form.authors == string_form.authors


class TestDefaults:
    """Optional fields default when a declaration omits them."""

    def test_absent_optional_fields_take_their_defaults(self):
        metadata = ProjectMetadata.from_toml_data(
            {"project": {"name": "sample-portal"}}
        )

        assert metadata.version == "0.0.0"
        assert metadata.authors == ["Unknown"]
        assert metadata.description == ""

    def test_one_warning_is_emitted_per_defaulted_field(self, caplog):
        with caplog.at_level("WARNING"):
            ProjectMetadata.from_toml_data({"project": {"name": "sample-portal"}})

        messages = [record.message for record in caplog.records]

        assert len(messages) == 3
        assert any("version" in message for message in messages)
        assert any("authors" in message for message in messages)
        assert any("description" in message for message in messages)

    def test_dynamic_version_falls_back_to_tool_poetry(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "description": "A sample research data portal",
                    "authors": ["Jane Doe"],
                    "dynamic": ["version"],
                },
                "tool": {"poetry": {"version": "2.5.0"}},
            }
        )

        assert metadata.version == "2.5.0"


class TestAddresses:
    """The declared homepage and repository addresses (FR-002, FR-004, FR-005, FR-012)."""

    def test_homepage_and_repository_are_read_from_project_urls(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "urls": {
                        "Homepage": "https://example.org",
                        "Repository": "https://github.com/example/sample-portal",
                    },
                }
            }
        )

        assert metadata.homepage == "https://example.org"
        assert metadata.repository == "https://github.com/example/sample-portal"

    @pytest.mark.parametrize("key", ["Repository", "repository", "REPOSITORY"])
    def test_repository_key_is_matched_regardless_of_case(self, key):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "urls": {key: "https://github.com/example/sample-portal"},
                }
            }
        )

        assert metadata.repository == "https://github.com/example/sample-portal"

    def test_pep_621_field_names_are_not_matched_case_insensitively(self):
        """D6: case-insensitivity is narrowed to [project.urls]; PEP 621's own
        field names elsewhere are matched exactly."""
        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_toml_data({"project": {"Name": "sample-portal"}})

        assert "name" in str(exc_info.value)

    def test_repository_is_preferred_when_both_addresses_are_declared(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "urls": {
                        "Homepage": "https://example.org",
                        "Repository": "https://github.com/example/sample-portal",
                    },
                }
            }
        )

        assert metadata.address == "https://github.com/example/sample-portal"

    def test_no_urls_table_leaves_both_addresses_empty(self):
        metadata = ProjectMetadata.from_toml_data(
            {"project": {"name": "sample-portal"}}
        )

        assert metadata.homepage == ""
        assert metadata.repository == ""
        assert metadata.address == ""


class TestFailures:
    """Each of the five ways a declaration cannot be read raises ConfigError with an actionable message."""

    def test_poetry_only_table_fails_requiring_pep_621(self):
        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_toml_data(
                {"tool": {"poetry": {"name": "sample-portal", "version": "1.2.3"}}}
            )

        message = str(exc_info.value)
        assert "PEP 621" in message
        assert "not read" in message
        assert (
            "https://github.com/FAIR-DM/fairdm-docs#migration-from-toolpoetry"
            in message
        )

    def test_neither_table_fails_saying_what_to_add(self):
        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_toml_data({})

        message = str(exc_info.value)
        assert "[project]" in message
        assert "name" in message

    def test_project_with_no_name_fails_naming_the_field(self):
        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_toml_data({"project": {"version": "1.2.3"}})

        message = str(exc_info.value)
        assert "name" in message
        assert "[project]" in message
        # Rendered as readable lines, not a literal backslash-n.
        assert "\n" in message
        assert "\\n" not in message

    def test_invalid_toml_fails_identifying_the_syntax_problem(self, tmp_path):
        import tomllib

        bad_toml = "[project\nname = 'broken'"
        (tmp_path / "pyproject.toml").write_text(bad_toml)

        try:
            tomllib.loads(bad_toml)
        except tomllib.TOMLDecodeError as exc:
            parser_description = str(exc)

        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_file(tmp_path)

        message = str(exc_info.value)
        assert "TOML" in message
        assert "syntax" in message.lower()
        assert parser_description in message

    def test_missing_pyproject_fails_naming_where_it_looked(self, tmp_path):
        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_file(tmp_path)

        message = str(exc_info.value)
        assert str(tmp_path) in message

    def test_every_failure_raises_the_single_config_error_type(self, tmp_path):
        calls = [
            lambda: ProjectMetadata.from_toml_data(
                {"tool": {"poetry": {"name": "sample-portal"}}}
            ),
            lambda: ProjectMetadata.from_toml_data({}),
            lambda: ProjectMetadata.from_toml_data({"project": {}}),
            lambda: ProjectMetadata.from_file(tmp_path),
        ]

        for call in calls:
            with pytest.raises(ConfigError) as exc_info:
                call()
            assert type(exc_info.value) is ConfigError

        bad_toml_dir = tmp_path / "bad-toml"
        bad_toml_dir.mkdir()
        (bad_toml_dir / "pyproject.toml").write_text("[project\nbroken")
        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_file(bad_toml_dir)
        assert type(exc_info.value) is ConfigError


class TestEdgeCases:
    """Less common declarations from Phase 6, pinning the code's actual behaviour."""

    def test_empty_project_table_fails_the_same_way_as_no_name(self):
        with pytest.raises(ConfigError) as exc_info:
            ProjectMetadata.from_toml_data({"project": {}})

        message = str(exc_info.value)
        assert "name" in message
        assert "[project]" in message

    def test_empty_authors_list_is_present_not_defaulted(self, caplog):
        """D16: defaulting checks key presence, not truthiness. A declared-but-empty
        authors list is not "not found", so it is kept as an empty list and no
        warning is emitted for it."""
        with caplog.at_level("WARNING"):
            metadata = ProjectMetadata.from_toml_data(
                {"project": {"name": "sample-portal", "authors": []}}
            )

        assert metadata.authors == []
        assert not any("authors" in record.message for record in caplog.records)

    def test_author_string_with_no_email_produces_that_string_as_the_display_name(self):
        metadata = ProjectMetadata.from_toml_data(
            {"project": {"name": "sample-portal", "authors": ["Jane Doe"]}}
        )

        assert metadata.authors == ["Jane Doe"]

    def test_author_string_that_is_only_an_email_produces_an_empty_display_name(self):
        """display_name splits on "<" and keeps what comes before it; an
        email-only string has nothing before the "<" (fairdm_docs/metadata.py:42)."""
        metadata = ProjectMetadata.from_toml_data(
            {"project": {"name": "sample-portal", "authors": ["<jane@example.com>"]}}
        )

        assert metadata.authors == [""]

    def test_author_table_with_email_and_no_name_produces_an_empty_display_name(self):
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "authors": [{"email": "jane@example.com"}],
                }
            }
        )

        assert metadata.authors == [""]

    def test_dynamic_version_without_a_poetry_fallback_defaults_and_warns(self, caplog):
        with caplog.at_level("WARNING"):
            metadata = ProjectMetadata.from_toml_data(
                {"project": {"name": "sample-portal", "dynamic": ["version"]}}
            )

        assert metadata.version == "0.0.0"
        assert any("version" in record.message for record in caplog.records)

    def test_repository_declared_twice_under_different_capitalisation_first_wins(self):
        """TOML preserves declaration order, and resolve_address returns on the
        first case-insensitive match it finds — so whichever spelling is written
        first in the file wins, not "repository" specifically."""
        metadata = ProjectMetadata.from_toml_data(
            {
                "project": {
                    "name": "sample-portal",
                    "urls": {
                        "Repository": "https://github.com/example/first",
                        "repository": "https://github.com/example/second",
                    },
                }
            }
        )

        assert metadata.repository == "https://github.com/example/first"

    def test_invalid_distribution_name_is_used_verbatim(self):
        """FR-007: the name is used as declared; nothing in this feature validates it."""
        metadata = ProjectMetadata.from_toml_data(
            {"project": {"name": "Not A Valid Name!"}}
        )

        assert metadata.name == "Not A Valid Name!"
