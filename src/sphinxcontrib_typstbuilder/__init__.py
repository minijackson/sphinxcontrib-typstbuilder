"""A Sphinx extension providing a builder with Typst."""

from __future__ import annotations

import importlib.metadata
from datetime import date
from os import path
from typing import TYPE_CHECKING

from ._builder import TypstBuilder

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.util.typing import ExtensionMetadata


def setup(app: Sphinx) -> ExtensionMetadata:
    """Set up the Typst builder extension."""
    app.require_sphinx("1.4")
    app.add_builder(TypstBuilder)

    app.add_config_value("typst_template", "default", "", str)
    app.add_config_value(
        "typst_templates_path",
        [path.join(p, "typst") for p in app.config.templates_path],  # noqa: PTH118
        "",
        list[str],
    )
    app.add_config_value("typst_date", date.today(), "", date)
    app.add_config_value(
        "typst_documents",
        [
            {
                "startdocname": "index",
                "targetname": "main",
                "title": app.config.project,
            },
        ],
        "",
        list[dict[str, str]],
    )
    app.add_config_value("typst_ignore_outside_references", True, "", bool)

    return {
        "version": importlib.metadata.version("sphinxcontrib-typstbuilder"),
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
