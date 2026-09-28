"""The Sphinx configuration a portal's documentation is built with."""

import os
import sys
import warnings
from pathlib import Path
from typing import Any

from sphinx.errors import ConfigError as SphinxConfigError

from fairdm_docs.config import ConfigError
from fairdm_docs.metadata import ProjectMetadata
from fairdm_docs.utils import find_pyproject_toml, load_pyproject_toml

sys.path.insert(0, os.path.abspath("../"))
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)

if os.environ.get("FAIRDM_DOCS_DJANGO", "false").lower() == "true":
    try:
        import django

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        django.setup()
    except ImportError:
        warnings.warn(
            "Django integration enabled but Django is not installed. "
            "Install Django or set django=false in [tool.fairdm.docs]",
            stacklevel=2,
        )


def _resolve_branding_assets() -> dict[str, str]:
    """Resolve branding asset paths with fallback chain.

    Checks for project-specific branding in docs/_static/brand/,
    falls back to package defaults in fairdm_docs/_static/.

    Returns:
        Dictionary with logo_path and favicon_path
    """
    current_file_path = Path(__file__).parent.absolute()
    fairdm_docs_static = current_file_path / "_static"

    project_brand = Path("_static/brand/")

    project_logo = project_brand / "logo.svg"
    logo_path = (
        str(project_logo)
        if project_logo.exists()
        else str(fairdm_docs_static / "logo.svg")
    )

    project_icon = project_brand / "icon.svg"
    favicon_path = (
        str(project_icon)
        if project_icon.exists()
        else str(fairdm_docs_static / "icon.svg")
    )

    return {
        "logo_path": logo_path,
        "favicon_path": favicon_path,
    }


def _apply_theme_config(theme: str, metadata: ProjectMetadata) -> dict[str, Any]:
    """Generate theme-specific options based on selected theme.

    Args:
        theme: Theme name (sphinx_book_theme or pydata_sphinx_theme)
        metadata: The portal's declared identity, whose address the theme links to

    Returns:
        Dictionary of theme-specific options
    """
    repository_url = metadata.address

    if theme == "pydata_sphinx_theme":
        return {
            "github_url": repository_url,
            "navbar_end": ["theme-switcher", "navbar-icon-links"],
            "icon_links": [
                {
                    "name": "GitHub",
                    "url": repository_url,
                    "icon": "fa-brands fa-github",
                }
            ]
            if repository_url
            else [],
        }
    else:
        # The repository, issue and edit buttons all read the same address. A
        # portal that has declared none gets none of them, rather than buttons
        # the theme cannot resolve.
        has_repository = bool(repository_url)
        return {
            "repository_url": repository_url,
            "use_repository_button": has_repository,
            "use_issues_button": has_repository,
            "use_edit_page_button": has_repository,
            "home_page_in_toc": True,
            "collapse_navbar": True,
            "extra_footer": (
                '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
                '<img alt="Creative Commons License" style="border-width:0" '
                'src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />'
                "This documentation is licensed under a "
                '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
                "Creative Commons Attribution 4.0 International License</a>."
            ),
        }


def _extract_fairdm_config(data: dict[str, Any]) -> dict[str, Any]:
    """Extract optional configuration from [tool.fairdm.docs] section.

    Args:
        data: Parsed pyproject.toml data

    Returns:
        Dictionary with optional configuration (theme, etc.)
    """
    if (
        "tool" not in data
        or "fairdm" not in data["tool"]
        or "docs" not in data["tool"]["fairdm"]
    ):
        return {}

    config = data["tool"]["fairdm"]["docs"]

    theme = config.get("theme")
    if theme:
        theme = theme.replace("-", "_")
        known_themes = ["sphinx_book_theme", "pydata_sphinx_theme"]
        if theme not in known_themes:
            warnings.warn(
                f"Unknown theme '{theme}' in [tool.fairdm.docs], using default sphinx_book_theme. "
                f"Known themes: {', '.join(known_themes)}",
                UserWarning,
                stacklevel=2,
            )
            theme = None

    return {
        "theme": theme,
    }


def _read_declaration() -> tuple[ProjectMetadata, dict[str, Any]]:
    """Read the portal's declaration once, for both the identity and the options.

    Search from cwd first. FAIRDM_DOCS_PROJECT_DIR, set by the command, is only
    consulted when that fails, e.g. because Sphinx changed cwd to the conf.py
    location (#12). Both return values come from the same file, so the optional
    configuration cannot be read from one pyproject.toml while the identity comes
    from another.

    Returns:
        The portal's declared identity, and its [tool.fairdm.docs] configuration

    Raises:
        SphinxConfigError: The declaration is missing, unreadable or incomplete.
    """
    path = find_pyproject_toml(start_dir=None)
    if path is None:
        path = find_pyproject_toml(use_env_var=True)

    try:
        metadata = ProjectMetadata.from_file(path.parent if path is not None else None)
    except ConfigError as exc:
        # Sphinx prints its own ConfigError as a message. Anything else it re-wraps
        # with a traceback embedded (#12).
        raise SphinxConfigError(str(exc)) from exc

    return metadata, _extract_fairdm_config(load_pyproject_toml(path))


metadata, fairdm_config = _read_declaration()

# Used exactly as declared (docs/adr/0007-a-declaration-is-used-exactly-as-written.md).
project = metadata.name
version = metadata.version
release = version
author = ", ".join(metadata.authors)
copyright = metadata.copyright
language = "en"

branding = _resolve_branding_assets()

# A project's own conf.py can still override html_theme after importing this one.
html_theme = fairdm_config.get("theme") or "sphinx_book_theme"

html_static_path = ["_static"]
html_logo = branding["logo_path"]
html_favicon = branding["favicon_path"]
html_short_title = ""

html_show_copyright = True
html_last_updated_fmt = "%b %d, %Y"

html_theme_options = _apply_theme_config(html_theme, metadata)

comments_config = {}
repository_url = metadata.address
if repository_url:
    repo_parts = repository_url.rstrip("/").split("/")[-2:]
    if len(repo_parts) == 2:
        comments_config = {
            "utterances": {
                "repo": "/".join(repo_parts),
                "issue-term": "pathname",
                "theme": "preferred-color-scheme",
                "label": "documentation",
                "crossorigin": "anonymous",
            }
        }


# autodoc2 stays out until the build reads a portal's package list (docs/ROADMAP.md
# R4). With nothing to document it warns in a way the developer cannot act on.
extensions = [
    "sphinx.ext.viewcode",
    "sphinx.ext.duration",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "sphinx_comments",
    "myst_parser",
    "sphinx_design",
]

# The model-documentation extension is not registered yet (#31).

master_doc = "index"

templates_path = ["_templates"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns = [
    "_build",
]

add_module_names = False

pygments_style = "sphinx"

autodoc_default_options = {
    "exclude-members": "__weakref__",
}

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

autosectionlabel_prefix_document = True

htmlhelp_basename = f"{metadata.name}_docs"

latex_elements: dict[str, str] = {}

latex_documents = [
    (
        "index",
        f"{metadata.name}.tex",
        f"{project} Documentation",
        metadata.authors[0] if metadata.authors else "Unknown",
        "manual",
    ),
]

man_pages = [
    (
        "index",
        metadata.name,
        f"{project} Documentation",
        metadata.authors[0] if metadata.authors else "Unknown",
        1,
    )
]

texinfo_documents = [
    (
        "index",
        metadata.name,
        f"{project} Documentation",
        metadata.authors[0] if metadata.authors else "Unknown",
        metadata.name,
        metadata.description,
        "Miscellaneous",
    ),
]

epub_title = project
epub_theme = "sphinx_book_theme"
