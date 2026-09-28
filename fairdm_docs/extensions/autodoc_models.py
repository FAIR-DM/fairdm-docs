"""The `autodoc-model` Sphinx directive, which documents a Django model from a template."""

from pathlib import Path
from typing import Any

import django
from django.apps import apps
from django.db.models import Model
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
    """Sphinx directive for auto-documenting Django models.

    Usage:
        .. autodoc-model:: myapp.MyModel
    """

    required_arguments = 1
    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        """Render the named model through the model template."""
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

        template_env = self._get_template_env()
        context = self._prepare_context(model)
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
        """Wrap a message in an error node.

        Args:
            message: The error to show in the rendered page.

        Returns:
            An error node holding the message.
        """
        error = nodes.error("", nodes.paragraph("", message))
        return error

    def _get_template_env(self) -> Environment:
        """Build the Jinja2 environment that loads the model template.

        Returns:
            The template environment.

        Raises:
            FileNotFoundError: The package's templates directory is missing.
        """
        # Templates live in the parent package, not this subpackage.
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

        env.filters["title"] = lambda s: s.title() if s else s

        return env

    def _prepare_context(self, model: type[Model]) -> dict[str, Any]:
        """Build the template context for a model.

        Args:
            model: The Django model class to document.

        Returns:
            The context, holding the model class.
        """
        return {"model": model}


def generate_model_docs(app: Sphinx) -> None:
    """Write a page per registered model type into the data_models directory.

    Args:
        app: The Sphinx application whose source directory receives the pages.
    """
    if not registry:
        logger.warning("FairDM registry not available, skipping auto-generation")
        return

    docs_dir = Path(app.srcdir)
    out_dir = docs_dir / "data_models"
    out_dir.mkdir(exist_ok=True)

    index_path = out_dir / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Data Models\n\n")
        f.write("```{toctree}\n")
        f.write(":maxdepth: 2\n\n")
        f.write("samples\n")
        f.write("measurements\n")
        f.write("```\n")

    samples_path = out_dir / "samples.md"
    with open(samples_path, "w", encoding="utf-8") as f:
        f.write("# Sample Types\n\n")
        for model in registry.samples:
            model_path = f"{model._meta.app_label}.{model.__name__}"
            f.write(f"## {model._meta.verbose_name}\n\n")
            f.write(f"```{{autodoc-model}} {model_path}\n```\n\n")

    measurements_path = out_dir / "measurements.md"
    with open(measurements_path, "w", encoding="utf-8") as f:
        f.write("# Measurement Types\n\n")
        for model in registry.measurements:
            model_path = f"{model._meta.app_label}.{model.__name__}"
            f.write(f"## {model._meta.verbose_name}\n\n")
            f.write(f"```{{autodoc-model}} {model_path}\n```\n\n")


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the autodoc-model directive and the model page generator."""
    app.add_directive("autodoc-model", AutoDocModelDirective)
    app.connect("builder-inited", generate_model_docs)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
