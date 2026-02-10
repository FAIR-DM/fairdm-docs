import os
import sys
import tomllib
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import django

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../"))
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


django.setup()


# ============================================================================
# HELPER FUNCTIONS FOR PEP 621 METADATA EXTRACTION
# ============================================================================

def _normalize_key(key: str) -> str:
    """
    Normalize dictionary keys to lowercase for case-insensitive lookups.
    
    Handles PEP 621 case variations like 'Homepage' vs 'homepage'.
    
    Args:
        key: Dictionary key to normalize
        
    Returns:
        Lowercase version of the key
    """
    return key.lower()


def _get_case_insensitive(d: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Get value from dictionary with case-insensitive key lookup.
    
    Args:
        d: Dictionary to search
        key: Key to find (case-insensitive)
        default: Default value if key not found
        
    Returns:
        Value associated with key (any case variation) or default
    """
    key_lower = _normalize_key(key)
    for k, v in d.items():
        if _normalize_key(k) == key_lower:
            return v
    return default


def _load_pyproject() -> dict[str, Any]:
    """
    Load and parse pyproject.toml from repository root.
    
    Raises:
        ConfigurationError: If file not found or TOML syntax invalid
        
    Returns:
        Parsed TOML data as dictionary
    """
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    try:
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise ValueError(
            f"pyproject.toml not found at {pyproject_path}. "
            "Ensure it exists at repository root."
        )
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML syntax in pyproject.toml: {e}")


def _extract_project_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """
    Extract project metadata from PEP 621 [project] section.
    
    Args:
        data: Parsed pyproject.toml data
        
    Raises:
        ValueError: If required [project].name field missing
        
    Returns:
        Dictionary with extracted metadata (name, version, authors, description, urls)
    """
    # Validate [project] section exists
    if "project" not in data:
        if "tool" in data and "poetry" in data["tool"]:
            raise ValueError(
                "PEP 621 [project] section required. "
                "Legacy [tool.poetry] format is not supported. "
                "Please migrate: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/"
            )
        raise ValueError(
            "PEP 621 [project] section required. "
            "Add [project] section with at least 'name' field to your pyproject.toml."
        )
    
    project = data["project"]
    
    # Required field: name
    name = project.get("name")
    if not name:
        raise ValueError(
            "Missing required 'project.name' in pyproject.toml. "
            "Add [project]\\nname = 'your-project-name'"
        )
    
    # Optional fields with defaults
    version = project.get("version", "0.0.0")
    
    # Handle dynamic versioning by checking tool.poetry as fallback
    if version == "0.0.0" and "dynamic" in project and "version" in project["dynamic"]:
        # Check if version exists in tool.poetry (common for transitional projects)
        if "tool" in data and "poetry" in data["tool"]:
            version = data["tool"]["poetry"].get("version", "0.0.0")
    
    # Warn if version is still default
    if version == "0.0.0":
        warnings.warn(
            "project.version not found in pyproject.toml, using default '0.0.0'",
            UserWarning
        )
    
    description = project.get("description", "")
    if not description:
        warnings.warn(
            "project.description not found in pyproject.toml, documentation may lack description",
            UserWarning
        )
    
    # Parse authors (format: "Name <email>" or "Name")
    authors = project.get("authors", ["Unknown"])
    if authors == ["Unknown"]:
        warnings.warn(
            "project.authors not found in pyproject.toml, using default ['Unknown']",
            UserWarning
        )
    author_names = []
    for author in authors:
        if isinstance(author, dict):
            # PEP 621 also supports {name = "...", email = "..."}
            author_names.append(author.get("name", "Unknown"))
        elif isinstance(author, str):
            # Extract name from "Name <email>" format
            if "<" in author:
                author_names.append(author.split("<")[0].strip())
            else:
                author_names.append(author.strip())
        else:
            author_names.append("Unknown")
    
    # Extract URLs with case-insensitive handling
    urls = project.get("urls", {})
    homepage = _get_case_insensitive(urls, "homepage", "")
    repository = _get_case_insensitive(urls, "repository", "")
    
    return {
        "name": name,
        "version": version,
        "description": description,
        "authors": author_names,
        "urls": {
            "homepage": homepage,
            "repository": repository,
        },
    }


def _resolve_branding_assets() -> dict[str, str]:
    """
    Resolve branding asset paths with fallback chain.
    
    Checks for project-specific branding in docs/_static/brand/,
    falls back to package defaults in fairdm_docs/_static/.
    
    Returns:
        Dictionary with logo_path and favicon_path
    """
    current_file_path = Path(__file__).parent.absolute()
    fairdm_docs_static = current_file_path / "_static"
    
    # Project branding location (within docs directory)
    project_brand = Path("_static/brand/")
    
    # Check for project logo
    project_logo = project_brand / "logo.svg"
    if project_logo.exists():
        logo_path = str(project_logo)
    else:
        logo_path = str(fairdm_docs_static / "logo.svg")
    
    # Check for project icon/favicon
    project_icon = project_brand / "icon.svg"
    if project_icon.exists():
        favicon_path = str(project_icon)
    else:
        favicon_path = str(fairdm_docs_static / "icon.svg")
    
    return {
        "logo_path": logo_path,
        "favicon_path": favicon_path,
    }


def _apply_theme_config(theme: str, metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Generate theme-specific options based on selected theme.
    
    Args:
        theme: Theme name (sphinx_book_theme or pydata_sphinx_theme)
        metadata: Extracted project metadata
        
    Returns:
        Dictionary of theme-specific options
    """
    repository_url = metadata["urls"]["repository"] or metadata["urls"]["homepage"]
    
    if theme == "pydata_sphinx_theme":
        # PyData theme options
        return {
            "github_url": repository_url,
            "navbar_end": ["theme-switcher", "navbar-icon-links"],
            "icon_links": [
                {
                    "name": "GitHub",
                    "url": repository_url,
                    "icon": "fa-brands fa-github",
                }
            ] if repository_url else [],
        }
    else:
        # sphinx_book_theme options (default)
        return {
            "repository_url": repository_url,
            "use_repository_button": True,
            "use_issues_button": True,
            "use_edit_page_button": True,
            "home_page_in_toc": True,
            "collapse_navbar": True,
            "extra_footer": (
                '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
                '<img alt="Creative Commons License" style="border-width:0" '
                'src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />'
                'This documentation is licensed under a '
                '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
                'Creative Commons Attribution 4.0 International License</a>.'
            ),
        }


def _extract_fairdm_config(data: dict[str, Any]) -> dict[str, Any]:
    """
    Extract optional configuration from [tool.fairdm.docs] section.
    
    Args:
        data: Parsed pyproject.toml data
        
    Returns:
        Dictionary with optional configuration (theme, etc.)
    """
    if "tool" not in data or "fairdm" not in data["tool"] or "docs" not in data["tool"]["fairdm"]:
        return {}
    
    config = data["tool"]["fairdm"]["docs"]
    
    # Extract and validate theme setting
    theme = config.get("theme")
    if theme:
        known_themes = ["sphinx_book_theme", "pydata_sphinx_theme"]
        if theme not in known_themes:
            warnings.warn(
                f"Unknown theme '{theme}' in [tool.fairdm.docs], using default sphinx_book_theme. "
                f"Known themes: {', '.join(known_themes)}",
                UserWarning
            )
            theme = None
    
    # Log unknown keys at debug level (informational only)
    known_keys = {"theme"}
    unknown_keys = set(config.keys()) - known_keys
    if unknown_keys:
        # Would use logging.debug in production, but warnings.warn for visibility in tests
        pass  # Debug-level logging would go here
    
    return {
        "theme": theme,
    }


# Project information --------------------------------------
# Load and extract metadata from pyproject.toml (PEP 621)
pyproject_data = _load_pyproject()
metadata = _extract_project_metadata(pyproject_data)
fairdm_config = _extract_fairdm_config(pyproject_data)

project = metadata["name"].replace("-", " ").title()
version = metadata["version"]  # The short X.Y version
release = version
authors = metadata["authors"]
copyright = f"{datetime.now().year}, {', '.join(authors)}"
language = "en"

# General configuration -------------------------------------

# Resolve branding assets
branding = _resolve_branding_assets()

# Apply theme from [tool.fairdm.docs] if specified, otherwise use default
# Note: User can still override html_theme after importing this conf.py
html_theme = fairdm_config.get("theme") or "sphinx_book_theme"

html_static_path = ["_static"]
html_logo = branding["logo_path"]
html_favicon = branding["favicon_path"]
html_short_title = ""

html_show_copyright = True
html_last_updated_fmt = "%b %d, %Y"

# Apply theme-specific configuration
# This respects the theme selected via [tool.fairdm.docs] or default
html_theme_options = _apply_theme_config(html_theme, metadata)

# https://utteranc.es
# https://sphinx-comments.readthedocs.io/en/latest/utterances.html
comments_config = {}
repository_url = metadata["urls"]["repository"] or metadata["urls"]["homepage"]
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


# autodoc2_packages = [
#     f"../{package['include']}" for package in package_meta.get("packages", [])
# ]

autodoc2_render_plugin = "myst"

autodoc2_skip_module_regexes = [
    r"fairdm.conf",
    r".*migrations.*",
    r".*tests.*",
]

# autodoc2_parse_docstrings = True

# autodoc2_docstring_parser_regexes = [("myst", r".*choices*")]

# Any additional Sphinx extension modules go here
extensions = [
    "sphinx.ext.viewcode",
    "sphinx.ext.duration",
    # 'sphinx.ext.doctest',
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "autodoc2",
    "sphinx_comments",
    "myst_parser",
    "sphinx_design",
    "fairdm_docs.extensions.autodoc_models",
]


# The master toctree document.
master_doc = "index"

# Path to additional templates relative to this directory
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffixs = {
    ".rst": "restructuredtext",
}

# The language for content autogenerated by Sphinx. Refer to documentation for a list of supported languages.

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    # match any directory not beginning with docs
    "^(?!docs).*",
    "_build",
]

# The reST default role (used for this markup: `text`) to use for all documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False


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
    # "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

autosectionlabel_prefix_document = True


# -- Options for HTML output ---------------------------------------------------

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = False


# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# Output file base name for HTML help builder.
htmlhelp_basename = f"{metadata['name']}_docs"


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    (
        "index",
        f"{metadata['name']}.tex",
        f"{project} Documentation",
        authors[0] if authors else "Unknown",
        "manual",
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        "index",
        metadata["name"],
        f"{project} Documentation",
        authors[0] if authors else "Unknown",
        1,
    )
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        metadata["name"],
        f"{project} Documentation",
        authors[0] if authors else "Unknown",
        metadata["name"],
        metadata["description"],
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False


# EPUB options
# ------------
# Bibliographic Dublin Core info.
epub_title = project
epub_theme = "sphinx_book_theme"
