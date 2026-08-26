"""
Sphinx extension for auto-documenting Django models using Jinja2 templates.

This extension provides the `autodoc-model` directive that automatically
generates documentation for Django models using configurable Jinja2 templates.
"""

from pathlib import Path
from typing import Any

import django
from django.apps import apps
from docutils import nodes
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger

try:
    from fairdm.registry import registry
except ImportError:
    registry = None

logger = getLogger(__name__)


class AutoDocModelDirective(SphinxDirective):
    """
    Sphinx directive for auto-documenting Django models.

    Usage:
        .. autodoc-model:: myapp.MyModel
    """

    required_arguments = 1
    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        """Execute the directive."""
        if not apps.ready:
            django.setup()

        model_path = self.arguments[0]

        try:
            app_label, model_name = model_path.rsplit(".", 1)
        except ValueError:
            return [self._error_node(f"Invalid model path: '{model_path}'")]

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return [self._error_node(f"Could not load model: '{model_path}'")]

        if model is None:
            return [self._error_node(f"Model not found: '{model_path}'")]

        # Get the template environment
        template_env = self._get_template_env()

        # Prepare context for template
        context = self._prepare_context(model)

        # Render the template
        try:
            template = template_env.get_template("model.md.jinja")
            rendered_content = template.render(**context)
        except Exception as e:
            return [self._error_node(f"Template rendering failed: {e}")]

        # Parse the rendered markdown as RST
        from docutils.frontend import OptionParser
        from docutils.parsers.rst import Parser
        from docutils.utils import new_document

        parser = Parser()
        settings = OptionParser(components=(Parser,)).get_default_values()
        document = new_document("<rst-doc>", settings=settings)

        try:
            parser.parse(rendered_content, document)
        except Exception as e:
            return [self._error_node(f"Markdown parsing failed: {e}")]

        return list(document.children)

    def _error_node(self, message: str) -> nodes.Node:
        """Create an error node."""
        error = nodes.error("", nodes.paragraph("", message))
        return error

    def _get_template_env(self) -> Environment:
        """Get the Jinja2 template environment."""
        # Find the templates directory (in the parent package, not extensions subpackage)
        current_dir = Path(__file__).parent.parent
        templates_dir = current_dir / "_templates"

        if not templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")

        loader = FileSystemLoader(templates_dir)
        env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        env.filters["title"] = lambda s: s.title() if s else s

        return env

    def _prepare_context(self, model) -> dict[str, Any]:
        """Prepare the context dictionary for template rendering."""
        # Just pass the model class - template handles everything else
        return {"model": model}


def generate_model_docs(app: Sphinx) -> None:
    """
    Generate model documentation files at build time.

    This function creates individual markdown files for all registered models
    in the data_models directory.
    """
    if not registry:
        logger.warning("FairDM registry not available, skipping auto-generation")
        return

    docs_dir = Path(app.srcdir)
    out_dir = docs_dir / "data_models"
    out_dir.mkdir(exist_ok=True)

    # Create index file
    index_path = out_dir / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Data Models\n\n")
        f.write("```{toctree}\n")
        f.write(":maxdepth: 2\n\n")
        f.write("samples\n")
        f.write("measurements\n")
        f.write("```\n")

    # Create samples index
    samples_path = out_dir / "samples.md"
    with open(samples_path, "w", encoding="utf-8") as f:
        f.write("# Sample Types\n\n")
        for config in registry.samples:
            model_path = config["full_name"]
            f.write(f"## {config['verbose_name']}\n\n")
            f.write(f"```{{autodoc-model}} {model_path}\n```\n\n")

    # Create measurements index
    measurements_path = out_dir / "measurements.md"
    with open(measurements_path, "w", encoding="utf-8") as f:
        f.write("# Measurement Types\n\n")
        for config in registry.measurements:
            model_path = config["full_name"]
            f.write(f"## {config['verbose_name']}\n\n")
            f.write(f"```{{autodoc-model}} {model_path}\n```\n\n")


def setup(app: Sphinx) -> dict[str, Any]:
    """
    Setup the autodoc-models extension.
    """
    app.add_directive("autodoc-model", AutoDocModelDirective)
    app.connect("builder-inited", generate_model_docs)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
