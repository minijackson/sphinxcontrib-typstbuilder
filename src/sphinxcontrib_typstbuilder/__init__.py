"""A Sphinx extension providing a builder with Typst."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._builder import TypstBuilder

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.util.typing import ExtensionMetadata


def setup(app: Sphinx) -> ExtensionMetadata:
    """Set up the Typst builder extension."""
    app.require_sphinx("1.4")
    app.add_builder(TypstBuilder)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }