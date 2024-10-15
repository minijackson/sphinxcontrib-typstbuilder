from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sphinx.builders import Builder
from sphinx.locale import _
from sphinx.util.console import darkgreen
from sphinx.util.display import progress_message
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

    def _assemble_doctree(self, startdocname: str) -> nodes.document:
        tree = self.env.get_doctree(startdocname)
        tree = inline_all_toctrees(
            self,
            set(),
            startdocname,
            tree,
            darkgreen,
            [startdocname],
        )
        tree["docname"] = startdocname
        self.env.resolve_references(tree, startdocname, self)
        return tree

    def write(
        self,
        _build_docnames: Iterable[str] | None,
        _updated_docnames: Sequence[str],
        _method: str = "update",
    ) -> None:
        for document in self.config.typst_documents:
            startdocname: str = document["startdocname"]
            targetname: str = document["targetname"]
            title: str = document["title"]
            template: str = document.get("template", self.config.typst_template)
            extra_metadata: str = document.get("metadata", {})

            with progress_message(f"processing {startdocname}"):
                self._write_doc(
                    startdocname,
                    targetname,
                    title,
                    template,
                    extra_metadata,
                )

    def _write_doc(
        self,
        startdocname: str,
        targetname: str,
        title: str,
        template: str,
        extra_metadata: dict[str, Any],
    ) -> None:
        outdir = Path(self.outdir) / targetname
        outdir.mkdir(exist_ok=True)

        doctree = self._assemble_doctree(startdocname)
        destination = SphinxFileOutput(
            destination_path=outdir / f"{targetname}.typ",
            encoding="utf-8",
            overwrite_if_changed=True,
        )

        docwriter = TypstWriter(self)
        docwriter.write(doctree, destination)

        self._copy_template(template, outdir)
        self._write_metadata(title, docwriter.label_aliases, extra_metadata, outdir)

    def _write_metadata(
        self,
        title: str,
        label_aliases: dict[str, str],
        extra_metadata: dict[str, Any],
        outdir: Path,
    ) -> None:
        filepath = outdir / "metadata.json"
        metadata = {
            "title": title,
            "author": self.config.author,
            "date": self.config.today,
            "language": self.config.language,
            "label_aliases": label_aliases,
        }
        metadata.update(extra_metadata)
        with filepath.open("w") as f:
            json.dump(metadata, f)

    def _copy_template(self, template_name: str, outdir: Path) -> None:
        template_file = f"{template_name}.typ"
        templates_path = outdir / "templates"

        template_dest_path = templates_path / template_file
        template_dest_path.parent.mkdir(exist_ok=True)

        template_source_path = resources.files(templates) / template_file

        template_dest_path.write_text(template_source_path.read_text())

        language = self.config.language

        translations_dest_path = templates_path / "lang.json"
        translations = {}
        for message in [
            "Attention",
            "Caution",
            "Danger",
            "Error",
            "Hint",
            "Important",
            "Note",
            "Tip",
            "Warning",
            "See also",
        ]:
            translations[message] = _(message)

        with translations_dest_path.open("w") as f:
            json.dump(
                {
                    "conf": {"default-lang": self.config.language},
                    "lang": {language: translations},
                },
                f,
            )
