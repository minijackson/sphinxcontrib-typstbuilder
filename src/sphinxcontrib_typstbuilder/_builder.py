from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

from sphinx.builders import Builder
from sphinx.util.console import darkgreen
from sphinx.util.docutils import SphinxFileOutput
from sphinx.util.nodes import inline_all_toctrees

from . import templates
from ._writer import TypstTranslator, TypstWriter, document_label

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from docutils import nodes


class TypstBuilder(Builder):
    name = "typst"
    format = "typst"

    # supported_image_types: list[str] = []
    default_translator_class = TypstTranslator

    def init(self) -> None:
        print("init!")

    def get_outdated_docs(self) -> str | Iterable[str]:
        return "all documents"

    def get_target_uri(self, docname: str, _typ: str | None = None) -> str:
        return document_label(docname)

    def get_relative_uri(self, _from: str, to: str, typ: str | None = None) -> str:
        # ignore source path, it's a single document
        return self.get_target_uri(to, typ)

    def assemble_doctree(self) -> nodes.document:
        # TODO(minijackson): make that configurable, like latex
        root = self.config.root_doc
        tree = self.env.get_doctree(root)
        tree = inline_all_toctrees(self, set(), root, tree, darkgreen, [root])
        tree["docname"] = root
        self.env.resolve_references(tree, root, self)
        return tree

    def write(
        self,
        _build_docnames: Iterable[str] | None,
        _updated_docnames: Sequence[str],
        _method: str = "update",
    ) -> None:
        targetname: str = "main.typ"

        doctree = self.assemble_doctree()
        destination = SphinxFileOutput(
            destination_path=Path(self.outdir) / targetname,
            encoding="utf-8",
            overwrite_if_changed=True,
        )

        docwriter = TypstWriter(self)
        docwriter.write(doctree, destination)

        self._copy_template(self.config.typst_template)
        self._write_metadata(docwriter.label_aliases)

    def _write_metadata(self, label_aliases: dict[str, str]) -> None:
        filepath = Path(self.outdir) / "metadata.json"
        with filepath.open("w") as f:
            json.dump(
                {
                    "title": self.config.project,
                    "author": self.config.author,
                    "date": self.config.today,
                    "label_aliases": label_aliases,
                },
                f,
            )

    def _copy_template(self, template_name: str) -> None:
        template_file = f"{template_name}.typ"

        template_dest_path = Path(self.outdir) / "templates" / template_file
        template_dest_path.parent.mkdir(exist_ok=True)

        template_source_path = resources.files(templates) / template_file

        template_dest_path.write_text(template_source_path.read_text())
