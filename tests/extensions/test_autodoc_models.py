"""Tests for fairdm_docs.extensions.autodoc_models.

The FairDM registry now yields the model classes it holds directly, not the
mapping-style config objects this extension used to consume: reproduces the
`generate_model_docs` failure reported against a real portal, where
`registry.samples` and `registry.measurements` are lists of model classes.
"""

from pathlib import Path
from types import SimpleNamespace

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
        DATABASES={},
        USE_TZ=True,
    )
    django.setup()

from django.db import models

from fairdm_docs.extensions import autodoc_models


class HeatFlowSite(models.Model):
    """Stand-in for a registered Sample model, as the real registry yields."""

    class Meta:
        app_label = "heat_flow"
        verbose_name = "Heat Flow Site"


class Conductivity(models.Model):
    """Stand-in for a registered Measurement model."""

    class Meta:
        app_label = "heat_flow"
        verbose_name = "Thermal Conductivity"


class TestGenerateModelDocs:
    """Building data_models/samples.md and measurements.md from the registry."""

    def test_writes_sample_and_measurement_pages_from_model_classes(
        self, tmp_path, monkeypatch
    ):
        """The registry yields model classes; the extension must read them as such."""
        fake_registry = SimpleNamespace(
            samples=[HeatFlowSite], measurements=[Conductivity]
        )
        monkeypatch.setattr(autodoc_models, "registry", fake_registry)

        app = SimpleNamespace(srcdir=str(tmp_path))
        autodoc_models.generate_model_docs(app)

        samples = (Path(tmp_path) / "data_models" / "samples.md").read_text()
        measurements = (Path(tmp_path) / "data_models" / "measurements.md").read_text()

        assert "Heat Flow Site" in samples
        assert "{autodoc-model} heat_flow.HeatFlowSite" in samples
        assert "Thermal Conductivity" in measurements
        assert "{autodoc-model} heat_flow.Conductivity" in measurements

    def test_skips_generation_when_registry_unavailable(self, tmp_path, monkeypatch):
        """No FairDM install: the extension warns and writes nothing, per its own contract."""
        monkeypatch.setattr(autodoc_models, "registry", None)

        app = SimpleNamespace(srcdir=str(tmp_path))
        autodoc_models.generate_model_docs(app)

        assert not (Path(tmp_path) / "data_models").exists()
