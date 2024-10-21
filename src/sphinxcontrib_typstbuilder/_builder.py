from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sphinx.builders import Builder
from sphinx.environment.adapters.asset import ImageAdapter
from sphinx.errors import ConfigError
from sphinx.locale import _, __
from sphinx.util.console import darkgreen
from sphinx.util.display import progress_message, status_iterator
from sphinx.util.docutils import SphinxFileOutput
from sphinx.util.fileutil import copy_asset, copy_asset_file
from sphinx.util.nodes import inline_all_toctrees

from . import templates
from ._writer import TypstTranslator, TypstWriter, document_label

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from docutils import nodes


class TypstBuilder(Builder):
    name = "typst"
    format = "typst"

    # See: https://typst.app/docs/reference/visualize/image/
    supported_image_types: tuple[str] = (
        "image/svg+xml",
        "image/png",
        "image/jpeg",
        "image/gif",
    )

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

    def _assemble_doctree(
        self,
        startdocname: str,
        appendices: list[str],
    ) -> nodes.document:
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

        for docname in appendices:
            appendix = self.env.get_doctree(docname)
            appendix["docname"] = docname
            tree.append(appendix)

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
            appendices: str = document.get("appendices", [])
            extra_metadata: str = document.get("metadata", {})

            self._write_doc(
                startdocname,
                targetname,
                title,
                template,
                appendices,
                extra_metadata,
            )

    def _write_doc(
        self,
        startdocname: str,
        targetname: str,
        title: str,
        template: str,
        appendices: list[str],
        extra_metadata: dict[str, Any],
    ) -> None:
        outdir = Path(self.outdir) / targetname
        outdir.mkdir(exist_ok=True)

        with progress_message(__("processing %s") % startdocname):
            doctree = self._assemble_doctree(startdocname, appendices)
            destination = SphinxFileOutput(
                destination_path=outdir / f"{targetname}.typ",
                encoding="utf-8",
                overwrite_if_changed=True,
            )

            self.images = {}
            self.post_process_images(doctree)

            docwriter = TypstWriter(self)
            docwriter.write(doctree, destination)

        self._copy_images(outdir)
        self._copy_template(template, outdir)
        self._write_metadata(title, docwriter.label_aliases, extra_metadata, outdir)

    def _copy_images(self, outdir: Path) -> None:
        # for image in self.images:
        stringify_func = ImageAdapter(self.app.env).get_original_image_uri
        for image in status_iterator(
            self.images,
            __("copying images... "),
            "brown",
            len(self.images),
            self.app.verbosity,
            stringify_func=stringify_func,
        ):
            copy_asset_file(self.srcdir / image, outdir / self.images[image])

    @progress_message("copying template files")
    def _copy_template(self, template_name: str, outdir: Path) -> None:
        # Find which of the template dir contains the template with the given name
        templates_dest_dir = outdir / "templates"

        template_name = f"{template_name}.typ"
        templates_source_dir = resources.files(templates)
        template_file = templates_source_dir / template_name

        if not template_file.is_file():
            # Maybe a custom template
            for t in self.config.typst_templates_path:
                templates_source_dir = Path(t)
                template_file = templates_source_dir / template_name

                if template_file.is_file():
                    break
            else:
                msg = f"No built-in or custom template named {template_name!r}"
                raise ConfigError(msg)

        # Copy the whole directory,
        # since there could be assets
        with resources.as_file(templates_source_dir) as templates_source_dir:
            copy_asset(templates_source_dir, templates_dest_dir)

        language = self.config.language

        translations_dest_path = templates_dest_dir / "lang.json"
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

    @progress_message("writing metadata")
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
            "date": {
                "year": self.config.typst_date.year,
                "month": self.config.typst_date.month,
                "day": self.config.typst_date.day,
            },
            "language": self.config.language,
            "label_aliases": label_aliases,
        }
        metadata.update(extra_metadata)
        with filepath.open("w") as f:
            json.dump(metadata, f)
