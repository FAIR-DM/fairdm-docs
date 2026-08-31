"""Tests for fairdm_docs.metadata.ProjectMetadata."""

from datetime import datetime

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
