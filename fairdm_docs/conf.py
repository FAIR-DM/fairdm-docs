"""The Sphinx configuration a portal's documentation is built with."""

import os
import sys
import warnings
from dataclasses import fields
from pathlib import Path
from typing import Any

from sphinx.errors import ConfigError as SphinxConfigError
from sphinx.util.logging import getLogger

from fairdm_docs.config import BuildConfiguration, ConfigError
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


PYDATA_THEME = "pydata_sphinx_theme"

# Shipped in this package's _static. It styles the navbar entry for the current
# page as PyData styles the current section's, so the homepage's own entry is
# highlighted on the homepage, which belongs to no section.
NAVBAR_STYLESHEET = "fairdm-docs-navbar.css"

# The keys [tool.fairdm.docs] accepts: the command's build settings, and the ones
# this module reads.
DECLARATIVE_KEYS = {setting.name for setting in fields(BuildConfiguration)} | {
    "theme",
    "title",
    "theme_options",
}


def pydata_theme_options(
    metadata: ProjectMetadata, project_root: Path
) -> dict[str, Any]:
    """Return this package's own PyData theme options for a portal.

    Args:
        metadata: The portal's declared identity, whose address the navbar links to
        project_root: The directory holding the portal's pyproject.toml

    Returns:
        Dictionary of PyData theme options
    """
    address = metadata.address
    options: dict[str, Any] = {
        "navbar_align": "left",
        "header_links_before_dropdown": 6,
        "navbar_end": ["theme-switcher", "navbar-icon-links"],
        "icon_links": [
            {
                "name": "GitHub",
                "url": address,
                "icon": "fa-brands fa-github",
            }
        ]
        if address
        else [],
    }
    # The changelog is linked where it lives, never copied into the site.
    if address and (project_root / "CHANGELOG.md").exists():
        options["external_links"] = [
            {
                "name": "Changelog",
                "url": f"{address.rstrip('/')}/blob/main/CHANGELOG.md",
            }
        ]
    return options


def extract_fairdm_config(data: dict[str, Any]) -> dict[str, Any]:
    """Return the [tool.fairdm.docs] table, warning about any key it does not accept.

    Args:
        data: Parsed pyproject.toml data

    Returns:
        The table, or an empty one when the portal declares none

    Raises:
        SphinxConfigError: theme_options is not a table.
    """
    config = data.get("tool", {}).get("fairdm", {}).get("docs", {})

    logger = getLogger(__name__)
    for key in sorted(config.keys() - DECLARATIVE_KEYS):
        logger.warning(
            f"Unknown key {key!r} in [tool.fairdm.docs] is ignored. "
            f"Known keys: {', '.join(sorted(DECLARATIVE_KEYS))}."
        )

    if not isinstance(config.get("theme_options", {}), dict):
        raise SphinxConfigError(
            "theme_options in [tool.fairdm.docs] must be a table, such as "
            "[tool.fairdm.docs.theme_options]."
        )

    return config


def read_declaration() -> tuple[ProjectMetadata, dict[str, Any], Path]:
    """Read the portal's declaration once, for the identity and the options.

    Search from cwd first. FAIRDM_DOCS_PROJECT_DIR, set by the command, is only
    consulted when that fails, e.g. because Sphinx changed cwd to the conf.py
    location (#12). Every return value comes from the same file, so the optional
    configuration cannot be read from one pyproject.toml while the identity comes
    from another.

    Returns:
        The portal's declared identity, its [tool.fairdm.docs] configuration, and
        the directory holding its pyproject.toml

    Raises:
        SphinxConfigError: The declaration is missing, unreadable or incomplete.
    """
    path = find_pyproject_toml(start_dir=None)
    if path is None:
        path = find_pyproject_toml(use_env_var=True)

    # Sphinx prints its own ConfigError as a message. Anything else it re-wraps
    # with a traceback embedded (#12).
    if path is None:
        raise SphinxConfigError(f"No pyproject.toml found. Searched from: {Path.cwd()}")
    try:
        metadata = ProjectMetadata.from_file(path.parent)
    except ConfigError as exc:
        raise SphinxConfigError(str(exc)) from exc

    return metadata, extract_fairdm_config(load_pyproject_toml(path)), path.parent


metadata, fairdm_config, project_root = read_declaration()

# Used exactly as declared (docs/adr/0007-a-declaration-is-used-exactly-as-written.md).
project = fairdm_config.get("title") or metadata.name
if "title" in fairdm_config:
    html_title = project
version = metadata.version
release = version
author = ", ".join(metadata.authors)
copyright = metadata.copyright
language = "en"

branding = _resolve_branding_assets()

# Any installed theme, named as Sphinx names it. A project's own conf.py can still
# override html_theme after importing this one.
html_theme = fairdm_config.get("theme") or PYDATA_THEME

html_static_path = ["_static"]
html_css_files: list[str] = []
html_logo = branding["logo_path"]
html_favicon = branding["favicon_path"]
html_short_title = ""

html_show_copyright = True
html_last_updated_fmt = "%b %d, %Y"

# This package's own theme options are written for PyData. Under any other theme
# the portal's declared options are all there is.
html_theme_options: dict[str, Any] = {}
if html_theme == PYDATA_THEME:
    html_theme_options = pydata_theme_options(metadata, project_root)
    # Listed first, so a file of the same name in the portal's own _static wins.
    html_static_path.insert(0, str(Path(__file__).parent / "_static"))
    html_css_files.append(NAVBAR_STYLESHEET)
html_theme_options.update(fairdm_config.get("theme_options", {}))

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

# Section links such as installation.md#install-the-front-end resolve to headings.
myst_heading_anchors = 3

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
