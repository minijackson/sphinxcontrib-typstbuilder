from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import indent
from typing import TYPE_CHECKING, Any, cast

import sphinx.addnodes
from docutils import nodes, writers
from sphinx.util import logging
from sphinx.util.docutils import SphinxTranslator

if TYPE_CHECKING:
    from docutils.nodes import Element, Text
    from sphinx.builders.text import TextBuilder

    from ._builder import TypstBuilder

logger = logging.getLogger(__name__)


class TypstWriter(writers.Writer):
    supported = ("typst",)
    settings_spec = ("No options here.", "", ())
    settings_defaults: dict[str, Any] = {}

    output: str

    def __init__(self, builder: TypstBuilder) -> None:
        super().__init__()
        self.builder = builder

    def translate(self) -> None:
        visitor = self.builder.create_translator(self.document, self.builder)
        self.document.walkabout(visitor)
        translator = cast(TypstTranslator, visitor)
        self.output = translator.body()
        self.label_aliases = translator.label_aliases


@dataclass
class Unprocessed:
    body: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        return "".join(self.body)


@dataclass
class CodeFunction:
    """A function in code mode."""

    name: str
    named_params: dict[str, str] = field(default_factory=dict)
    positional_params: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    force_body: bool = False

    def to_text(self) -> str:
        named = ", ".join(
            f"{name}: {arg}"
            for name, arg in self.named_params.items()
            if arg is not None
        )

        pos = ", ".join(self.positional_params)

        body = "".join(self.body).strip()
        if "\n" in body:
            body = "\n" + indent(body, "  ") + "\n"
        if body != "":
            body = f"[{body}]"
        elif self.force_body:
            body = "[]"

        labels = ""
        for label in self.labels:
            labels += f" #label({escape_str(label)})"

        args_sep = ", " if named and pos else ""
        args = f"({named}{args_sep}{pos})"
        if args == "()" and body:
            args = ""

        return f"{self.name}{args}{body}{labels}"


class BlockCodeFunction(CodeFunction):
    def to_text(self) -> str:
        return super().to_text() + "\n"


class InlineCodeFunction(CodeFunction):
    pass


class MarkupFunction(CodeFunction):
    """A function in markup mode."""

    def to_text(self) -> str:
        return "#" + super().to_text()


class BlockMarkupFunction(MarkupFunction):
    def to_text(self) -> str:
        return super().to_text() + "\n"


class InlineMarkupFunction(MarkupFunction):
    pass


class Table(BlockMarkupFunction):
    def __init__(self, node: Element) -> None:
        self.colwidths: list[int] = []
        self.classes: list[str] = node.get("classes", [])
        self.colwidths_given: bool = "colwidths-given" in self.classes
        self.cells: list[str] = []

        super().__init__(name="figure")

    def to_text(self) -> str:
        columns = str(len(self.colwidths))
        if self.colwidths_given:
            columns = ", ".join(f"{x}fr" for x in self.colwidths)
            columns = f"({columns})"

        self.body.append(
            BlockMarkupFunction(
                name="table",
                named_params={
                    "align": "left",
                    "columns": columns,
                },
                positional_params=self.cells,
            ).to_text()
        )

        return super().to_text()


@dataclass
class MarkupArg:
    body: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        body = "".join(self.body).strip()
        if "\n" in body:
            body = "\n" + indent(body, "  ") + "\n"

        labels = ""
        for label in self.labels:
            labels += f" #label({escape_str(label)})"

        return f"[{body}{labels}]"


@dataclass
class ArrayArg:
    body: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        body = ", ".join(self.body).strip()

        return f"({body})"


@dataclass
class Math:
    block: bool = False
    body: str = ""
    labels: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        ws = " " if self.block else ""
        body = self.body.strip()

        labels = ""
        for label in self.labels:
            labels += f" #label({escape_str(label)})"

        return f"${ws}{body}{ws}${labels}"


# Label format (inspired from the LaTeX writer):
#
#     %path/to/document
# Or:
#     %path/to/document#fragment


def document_label(docname: str) -> str:
    return "%" + docname


def escape_str(s: str) -> str:
    """Convert a string to a Typst string.

    Since this function is used for Text,
    it replaces line returns with a space.

    See: <https://typst.app/docs/reference/foundations/str/#escapes>
    """
    return (
        '"'
        + s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
        + '"'
    )


def escape_raw_str(s: str) -> str:
    """Convert a string used in ``raw()`` to a Typst string.

    See: <https://typst.app/docs/reference/foundations/str/#escapes>
    """
    return (
        '"'
        + s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
        + '"'
    )


def escape_markup(s: str) -> str:
    """Escape special Typst characters in markup mode.

    See: <https://typst.app/docs/reference/syntax/#markup>
    """
    return (
        s.replace("\\", "\\\\")
        .replace("*", "\\*")
        .replace("_", "\\_")
        .replace("`", "\\`")
        .replace("$", "\\$")
        .replace("#", "\\#")
    )


def to_str_list(l: list[str]) -> str:
    inside = ",".join(escape_str(el) for el in l)
    return f"({inside})"


class TypstTranslator(SphinxTranslator):
    def __init__(self, document: nodes.document, builder: TextBuilder) -> None:
        super().__init__(document, builder)

        self.template = document["template"]

        self.body_bak = ""

        self.sectionlevel = 0
        self.curr_elements = [Unprocessed()]
        self.curr_files = []
        self.attached_files = set()

        self.this_is_the_title = True

        self.pending_labels: list[str] = []
        self.label_aliases = {}

    def curr_element(self) -> Any:
        return self.curr_elements[-1]

    def append_el(self, el: Any) -> None:
        self.curr_elements.append(el)

    def pop_el(self) -> str:
        return self.curr_elements.pop().to_text()

    def append_inline_fun(self, node: Element | None, *args, **kwargs) -> None:
        el = InlineMarkupFunction(*args, **kwargs)
        if node is not None:
            el.labels = self.register_labels(node["ids"])
        self.append_el(el)

    def append_block_fun(self, node: Element | None, *args, **kwargs) -> None:
        el = BlockMarkupFunction(*args, **kwargs)
        if node is not None:
            el.labels = self.register_labels(node["ids"])
        self.append_el(el)

    def append_inline_code_fun(self, node: Element | None, *args, **kwargs) -> None:
        el = InlineCodeFunction(*args, **kwargs)
        if node is not None:
            el.labels = self.register_labels(node["ids"])
        self.append_el(el)

    def append_block_code_fun(self, node: Element | None, *args, **kwargs) -> None:
        el = BlockCodeFunction(*args, **kwargs)
        if node is not None:
            el.labels = self.register_labels(node["ids"])
        self.append_el(el)

    def append_unprocessed(self, node: Element | None, *args, **kwargs) -> None:
        el = Unprocessed(*args, **kwargs)
        if node is not None:
            self.pending_labels += node["ids"]
        self.append_el(el)

    def append_markup_arg(self, node: Element | None, *args, **kwargs) -> None:
        el = MarkupArg(*args, **kwargs)
        if node is not None:
            el.labels = self.register_labels(node["ids"])
        self.append_el(el)

    def register_labels(self, labels: list[str]) -> list[str]:
        """Register a list of document labels, and return only the main one."""
        if not labels:
            return []

        main_label = self.label_ref(labels[0])

        for label in labels:
            self.label_aliases[self.label_ref(label)] = main_label

        return [main_label]

    def absorb_fun_in_body(self) -> str:
        if self.pending_labels:
            self.curr_element().labels = self.register_labels(self.pending_labels)
            self.pending_labels = []

        # self.curr_element().labels = self.pending_labels
        # self.pending_labels = []
        el = self.pop_el()
        self.curr_element().body.append(el)

    def label_ref(self, label: str) -> str:
        if not label.startswith("%"):
            label = "%" + self.curr_files[-1] + "#" + label

        return label

    def body(self) -> str:
        if len(self.curr_elements) != 1:
            # TODO: print warning
            pass

        content = self.curr_elements[0].to_text()

        return f"""
#import "templates/{self.template}.typ": *

#let metadata = json("metadata.json")
#let label-aliases = metadata.at("label_aliases")

#let internal-link(dest, body) = {{
  let l = label-aliases.at(dest, default: none)
  if l == none {{
    missing_link(dest, body)
  }} else {{
	link(label(l), body)
  }}
}}

#let footnote-content(id) = context state("footnote-" + id).final()

#show: template.with(metadata: metadata)

{content}
"""

    # Visitor functions
    # =================

    # Containers

    def visit_document(self, node: Element) -> None:
        self.curr_files.append(node["docname"])
        self.pending_labels.append(document_label(node["docname"]))

    def depart_document(self, _node: Element) -> None:
        self.curr_files.pop()

    def visit_start_of_file(self, node: Element) -> None:
        self.curr_files.append(node["docname"])
        self.pending_labels.append(document_label(node["docname"]))

    def depart_start_of_file(self, _node: Element) -> None:
        self.curr_files.pop()

    def visit_compound(self, node: Element) -> None:
        pass

    def depart_compound(self, node: Element) -> None:
        pass

    def visit_section(self, node: Element) -> None:
        if not self.this_is_the_title:
            self.sectionlevel += 1

        if "ids" in node:
            self.pending_labels += node["ids"]

    def depart_section(self, _node: Element) -> None:
        self.sectionlevel = max(0, self.sectionlevel - 1)
        self.body_bak += "\n"

    def visit_container(self, node: Element) -> None:
        if "literal-block-wrapper" in node["classes"]:
            self.append_block_fun(node, name="figure")

    def depart_container(self, node: Element) -> None:
        if "literal-block-wrapper" in node["classes"]:
            self.absorb_fun_in_body()

    # Inline markup

    def visit_emphasis(self, node: Element) -> None:
        self.append_inline_fun(node, name="emph")

    def depart_emphasis(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_strong(self, node: Element) -> None:
        self.append_inline_fun(node, name="strong")

    def depart_strong(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_subscript(self, node: Element) -> None:
        self.append_inline_fun(node, name="sub")

    def depart_subscript(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_superscript(self, node: Element) -> None:
        self.append_inline_fun(node, name="super")

    def depart_superscript(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_literal_emphasis(self, node: Element) -> None:
        self.append_inline_fun(node, name="literal_emphasis")

    def depart_literal_emphasis(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_literal_strong(self, node: Element) -> None:
        self.append_inline_fun(node, name="literal_strong")

    def depart_literal_strong(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_title_reference(self, node: Element) -> None:
        self.append_inline_fun(node, name="emph")

    def depart_title_reference(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    # Roles

    def visit_literal(self, node: Element) -> None:
        if "kbd" in node["classes"]:
            self.append_inline_fun(
                node,
                name="kbd",
                positional_params=[escape_str(node.astext())],
            )
            self.absorb_fun_in_body()
            raise nodes.SkipNode

        lang = node.get("language", None)

        if lang is None and "regexp" in node["classes"]:
            lang = "regexp"
        elif "code" not in node["classes"] or not lang:
            self.append_inline_fun(node, "literal")
            return

        named_params = {}
        if lang:
            named_params["lang"] = escape_str(lang)
        self.append_inline_fun(
            node,
            name="raw",
            named_params=named_params,
            positional_params=[escape_raw_str(node.astext())],
        )
        self.absorb_fun_in_body()
        raise nodes.SkipNode

    def depart_literal(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_inline(self, node: Element) -> None:
        if "accelerator" in node["classes"]:
            self.append_inline_fun(node, name="accelerator")
            return

        if "menuselection" in node["classes"]:
            self.append_inline_fun(node, name="menuselection")
            return

        if "guilabel" in node["classes"]:
            self.append_inline_fun(node, name="guilabel")
            return

        if "versionmodified" in node["classes"]:
            self.append_inline_fun(node, name="versionmodified")
            return

        self.append_inline_fun(
            node,
            name="inline",
            named_params={"classes": to_str_list(node["classes"])},
            force_body=True,
        )

    def depart_inline(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_abbreviation(self, node: Element) -> None:
        named_params = {}
        if node.hasattr("explanation"):
            named_params["explanation"] = escape_str(node["explanation"])

        self.append_inline_fun(
            node,
            name="abbreviation",
            named_params=named_params,
            positional_params=[escape_str(node.astext())],
        )
        self.absorb_fun_in_body()
        raise nodes.SkipNode

    def visit_manpage(self, node: Element) -> None:
        return self.visit_literal_emphasis(node)

    def depart_manpage(self, node: Element) -> None:
        return self.depart_literal_emphasis(node)

    # Links

    def visit_reference(self, node: Element) -> None:
        internal = node.get("internal", False) or "refid" in node

        if internal:
            self.append_inline_fun(node, name="internal-link")
        else:
            self.append_inline_fun(node, name="link")

        if "refuri" in node and not internal:
            self.curr_element().positional_params.append(escape_str(node["refuri"]))
        elif "refuri" in node and internal:
            self.curr_element().positional_params.append(
                escape_str(self.label_ref(node["refuri"])),
            )
        else:
            self.curr_element().positional_params.append(
                escape_str(self.label_ref(node["refid"])),
            )

    def depart_reference(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_download_reference(self, node: Element) -> None:
        # There doesn't seem to be a way of creating a link to an attachment
        if node["filename"] in self.attached_files:
            return

        self.attached_files.add(node["filename"])
        self.append_inline_fun(
            node,
            name="pdf.attach",
            positional_params=[escape_str(node["filename"])],
            named_params={"description": escape_str(node["reftarget"])},
        )
        self.absorb_fun_in_body()

    def depart_download_reference(self, _node: Element) -> None:
        pass

    def visit_target(self, node: Element) -> None:
        pass

    def depart_target(self, _node: Element) -> None:
        pass

    # Footnotes and citations

    def visit_footnote_reference(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="footnote",
            positional_params=[f"footnote-content({escape_str(node['refid'])})"],
        )
        self.absorb_fun_in_body()
        raise nodes.SkipNode

    def visit_footnote(self, node: Element) -> None:
        self.append_block_fun(
            node,
            name="register_footnote",
            positional_params=[escape_str(node["ids"][0])],
        )

    def depart_footnote(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_citation(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="citation",
        )

    def depart_citation(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_label(self, node: Element) -> None:
        if isinstance(node.parent, nodes.footnote):
            raise nodes.SkipNode

        self.append_inline_code_fun(node, name="reference_label")

    def depart_label(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # ...

    def visit_title(self, node: Element) -> None:
        if isinstance(
            node.parent,
            (nodes.Admonition, nodes.topic, nodes.sidebar, nodes.table),
        ):
            self.append_markup_arg(node)
            return

        if self.this_is_the_title:
            self.this_is_the_title = False
            raise nodes.SkipNode

        self.append_block_fun(
            node,
            name="heading",
            named_params={"level": self.sectionlevel},
        )

    def depart_title(self, node: Element) -> None:
        if isinstance(node.parent, (nodes.Admonition, nodes.topic, nodes.sidebar)):
            el = self.pop_el()
            self.curr_element().named_params["title"] = el
            return

        if isinstance(node.parent, nodes.table):
            el = self.pop_el()
            self.curr_element().named_params["caption"] = el
            return

        self.absorb_fun_in_body()

    def visit_subtitle(self, node: Element) -> None:
        if isinstance(node.parent, nodes.sidebar):
            self.append_markup_arg(node)

    def depart_subtitle(self, node: Element) -> None:
        if isinstance(node.parent, nodes.sidebar):
            el = self.pop_el()
            self.curr_element().named_params["subtitle"] = el

    def visit_paragraph(self, node: Element) -> None:
        # Don't call "#par()" when not needed,
        # i.e. when it's the first child of a block item
        if (
            isinstance(
                node.parent,
                (
                    nodes.admonition,
                    nodes.citation,
                    nodes.description,
                    nodes.entry,
                    nodes.field_body,
                    nodes.footnote,
                    nodes.list_item,
                    nodes.topic,
                    sphinx.addnodes.desc_content,
                    sphinx.addnodes.versionmodified,
                ),
            )
            and not self.curr_element().body
        ):
            self.append_unprocessed(node)
            return

        # self.curr_element().body.append("\n")
        self.append_block_fun(node, name="par", force_body=True)

    def depart_paragraph(self, _node: Element) -> None:
        # self.curr_element().body.append("\n")
        self.absorb_fun_in_body()

    # Lists

    def visit_bullet_list(self, node: Element) -> None:
        self.append_block_fun(
            node,
            name="list",
            named_params={"tight": "false"},
        )

    def depart_bullet_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_enumerated_list(self, node: Element) -> None:
        self.append_block_fun(node, name="enum")

    def depart_enumerated_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_list_item(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_list_item(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # Definition lists

    def visit_definition_list(self, node: Element) -> None:
        self.append_block_fun(
            node,
            name="terms",
            named_params={"tight": "false"},
        )

    def depart_definition_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    # TODO: this doesn't support for ex.:
    #
    # Term 1
    # Term 2
    #     Definition for both
    def visit_definition_list_item(self, node: Element) -> None:
        self.append_block_code_fun(node, name="terms.item")

    def depart_definition_list_item(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_term(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_term(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_definition(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_definition(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # Field lists

    def visit_field_list(self, node: Element) -> None:
        self.append_block_fun(node, name="field_list")

    def depart_field_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_field(self, node: Element) -> None:
        self.append_block_code_fun(node, name="field_item")

    def depart_field(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_field_name(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_field_name(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_field_body(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_field_body(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # Figures / Images / Code blocks

    def visit_figure(self, node: Element) -> None:
        self.append_block_fun(node, name="figure")

    def depart_figure(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_caption(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_caption(self, node: Element) -> None:
        el = self.pop_el()
        self.curr_element().named_params["caption"] = el

    def visit_legend(self, node: Element) -> None:
        self.append_unprocessed(node)

    def depart_legend(self, node: Element) -> None:
        el = self.pop_el()
        caption = self.curr_element().named_params["caption"]
        # HACK: this assumes a caption was already added,
        # and is a MarkupArg, so is of the form `[thing]`
        new_caption = caption[:-1] + el + caption[-1]
        self.curr_element().named_params["caption"] = new_caption

    def visit_image(self, node: Element) -> None:
        if node["uri"] in self.builder.images:
            image = self.builder.images[node["uri"]]
        else:
            logger.warning("missing image %s", node["uri"])
            image = node["uri"]
        self.append_inline_fun(
            node,
            name="image",
            positional_params=[escape_raw_str(image)],
        )

        width = node.get("width")
        if width is None:
            if isinstance(node.parent, nodes.figure) and "width" in node.parent:
                width = node.parent["width"]
            elif (
                isinstance(node.parent, nodes.reference)
                and isinstance(node.parent.parent, nodes.figure)
                and "width" in node.parent.parent
            ):
                width = node.parent.parent["width"]

        if width is not None:
            if width.endswith(("pt", "mm", "cm", "in", "em", "%")):
                self.curr_element().named_params["width"] = width
            else:
                logger.warning("unsupported width length unit for %s, ignoring", width)

    def depart_image(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_literal_block(self, node: Element) -> None:
        self.append_block_fun(
            node,
            name="raw",
            named_params={"block": "true", "lang": escape_str(node["language"])},
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_literal_block(self, node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_block_quote(self, node: Element) -> None:
        self.append_block_fun(node, name="quote", named_params={"block": "true"})

    def depart_block_quote(self, node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_attribution(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_attribution(self, node: Element) -> None:
        el = self.pop_el()
        self.curr_element().named_params["attribution"] = el

    # Tables

    def visit_table(self, node: Element) -> None:
        table = Table(node)
        table.labels = self.register_labels(node["ids"])
        self.append_el(table)

    def depart_table(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_tgroup(self, _node: Element) -> None:
        pass

    def depart_tgroup(self, _node: Element) -> None:
        pass

    def visit_colspec(self, node: Element) -> None:
        # TODO: see https://www.oasis-open.org/specs/tm9901.html#AEN446
        self.curr_element().colwidths.append(node["colwidth"])
        raise nodes.SkipNode

    def visit_tabular_col_spec(self, node: Element) -> None:
        # This is LaTeX-specific tabular specification
        raise nodes.SkipNode

    def depart_colspec(self, node: Element) -> None:
        pass

    def visit_thead(self, node: Element) -> None:
        self.append_inline_code_fun(node, name="table.header")

    def depart_thead(self, node: Element) -> None:
        el = self.pop_el()
        self.curr_element().cells.append(el)

    def visit_tbody(self, node: Element) -> None:
        pass

    def depart_tbody(self, node: Element) -> None:
        pass

    def visit_row(self, node: Element) -> None:
        pass

    def depart_row(self, node: Element) -> None:
        pass

    def visit_entry(self, node: Element) -> None:
        align = None

        classes = node.get("classes", [])
        if "text-left" in classes:
            align = "left"
        elif "text-center" in classes:
            align = "center"
        elif "text-right" in classes:
            align = "right"

        colspan = 1 + node.get("morecols", 0)
        rowspan = 1 + node.get("morerows", 0)
        self.append_inline_code_fun(
            node,
            "table.cell",
            named_params={
                "colspan": colspan,
                "rowspan": rowspan,
                "align": align,
            },
            force_body=True,
        )

    def depart_entry(self, node: Element) -> None:
        el = self.pop_el()

        if isinstance(node.parent.parent, nodes.thead):
            self.curr_element().positional_params.append(el)
            return

        self.curr_element().cells.append(el)

    # Line blocks

    def visit_line_block(self, node: Element) -> None:
        self.append_block_fun(node, name="line_block")

    def depart_line_block(self, node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_line(self, node: Element) -> None:
        self.append_inline_fun(node, name="line_block_line")

    def depart_line(self, node: Element) -> None:
        self.absorb_fun_in_body()

    # Other directives

    def visit_rubric(self, node: Element) -> None:
        self.append_inline_fun(node, name="rubric")

    def depart_rubric(self, node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_topic(self, node: Element) -> None:
        self.append_block_fun(node, name="topic")

    def depart_topic(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_sidebar(self, node: Element) -> None:
        self.append_block_fun(node, name="sidebar")

    def depart_sidebar(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_hlist(self, node: Element) -> None:
        self.append_block_fun(
            node,
            name="columns",
            positional_params=[node["ncolumns"]],
        )

    def depart_hlist(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_hlistcol(self, _node: Element) -> None:
        pass

    def depart_hlistcol(self, _node: Element) -> None:
        self.curr_element().body.append("#colbreak()\n")

    def visit_centered(self, node: Element) -> None:
        self.append_block_fun(node, name="align", positional_params=["center"])

    def depart_centered(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    # TODO: as comma-separated list?
    def visit_acks(self, _node: Element) -> None:
        pass

    def depart_acks(self, _node: Element) -> None:
        pass

    visit_productionlist = visit_literal
    depart_productionlist = depart_literal

    def visit_production(self, _node: Element) -> None:
        pass

    def depart_production(self, _node: Element) -> None:
        self.curr_element().body.append(" \\\n")

    # Glossary / Indices

    def visit_glossary(self, node: Element) -> None:
        pass

    def depart_glossary(self, node: Element) -> None:
        pass

    def visit_index(self, _node: Element) -> None:
        # TODO
        raise nodes.SkipNode

    # Admonitions

    def visit_admonition(self, node: Element) -> None:
        self.append_block_fun(node, name="admonition")

    def depart_admonition(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def _visit_named_admonition(self, node: Element) -> None:
        self.append_block_fun(node, name=node.tagname)

    def _depart_named_admonition(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    visit_attention = _visit_named_admonition
    depart_attention = _depart_named_admonition
    visit_caution = _visit_named_admonition
    depart_caution = _depart_named_admonition
    visit_danger = _visit_named_admonition
    depart_danger = _depart_named_admonition
    visit_error = _visit_named_admonition
    depart_error = _depart_named_admonition
    visit_hint = _visit_named_admonition
    depart_hint = _depart_named_admonition
    visit_important = _visit_named_admonition
    depart_important = _depart_named_admonition
    visit_note = _visit_named_admonition
    depart_note = _depart_named_admonition
    visit_tip = _visit_named_admonition
    depart_tip = _depart_named_admonition
    visit_warning = _visit_named_admonition
    depart_warning = _depart_named_admonition
    visit_seealso = _visit_named_admonition
    depart_seealso = _depart_named_admonition

    def visit_versionmodified(self, node: Element) -> None:
        self.append_block_fun(node, name=node["type"])

    def depart_versionmodified(self, node: Element) -> None:
        self.absorb_fun_in_body()

    # Signatures / objects

    def visit_desc(self, node: Element) -> None:
        self.append_block_fun(node, name="desc")

    def depart_desc(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_signature(self, node: Element) -> None:
        self.append_block_fun(node, name="desc_signature")

    def depart_desc_signature(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_signature_line(self, node: Element) -> None:
        if self.curr_element().body:
            self.curr_element().body.append("#linebreak()")

    def depart_desc_signature_line(self, _node: Element) -> None:
        pass

    def visit_desc_name(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="desc_name",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_name(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_addname(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="desc_addname",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_addname(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_type(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_type")

    def depart_desc_type(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_type_parameter(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_desc_type_parameter(self, node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_desc_type_parameter_list(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_type_parameter_list")

    def depart_desc_type_parameter_list(self, node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_returns(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="desc_returns",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_returns(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_annotation(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="desc_annotation",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_annotation(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_content(self, node: Element) -> None:
        self.append_block_fun(node, name="desc_content")

    def depart_desc_content(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_inline(self, node: Element) -> None:
        self.append_inline_fun(node, name="literal")

    def depart_desc_inline(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_parameterlist(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="desc_parameterlist",
            named_params={
                "open_paren": '"("',
                "close_paren": '")"',
                "child_text_separator": '"' + node.child_text_separator + '"',
            },
        )

    def depart_desc_parameterlist(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_parameter(self, node: Element) -> None:
        self.append_markup_arg(node)
        self.append_inline_fun(None, name="desc_parameter")

    def depart_desc_parameter(self, _node: Element) -> None:
        self.absorb_fun_in_body()
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_desc_sig_name(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_sig_name")

    def depart_desc_sig_name(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_optional(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_optional")

    def depart_desc_optional(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_sig_punctuation(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_sig_punctuation")

    def depart_desc_sig_punctuation(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_sig_space(self, _node: Element) -> None:
        pass

    def depart_desc_sig_space(self, _node: Element) -> None:
        pass

    def visit_desc_sig_keyword(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_sig_keyword")

    def depart_desc_sig_keyword(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_sig_keyword_type(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_sig_keyword_type")

    def depart_desc_sig_keyword_type(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_sig_literal_string(self, node: Element) -> None:
        self.append_inline_fun(node, name="desc_sig_literal_string")

    def depart_desc_sig_literal_string(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    # Options

    def visit_option_list(self, node: Element) -> None:
        # Format:
        #
        # #option_list(
        #   option_group(option["-h"], option["--help"]), [something],
        #   option_group(option(argument: ["file"], delimiter: "=")["--one"]), [something],
        # )
        self.append_block_fun(node, name="option_list")

    def depart_option_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_option_list_item(self, _node: Element) -> None:
        pass

    def depart_option_list_item(self, _node: Element) -> None:
        pass

    def visit_option_group(self, node: Element) -> None:
        self.append_block_code_fun(node, name="option_group")

    def depart_option_group(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_option(self, node: Element) -> None:
        self.append_inline_code_fun(node, name="option")

    def depart_option(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_option_string(self, node: Element) -> None:
        self.append_unprocessed(node)

    def depart_option_string(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_option_argument(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_option_argument(self, node: Element) -> None:
        el = self.pop_el()
        self.curr_element().named_params["argument"] = el
        if "delimiter" in node:
            self.curr_element().named_params["delimiter"] = escape_str(
                node["delimiter"]
            )

    def visit_description(self, node: Element) -> None:
        self.append_markup_arg(node)

    def depart_description(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # Others

    def visit_transition(self, node: Element) -> None:
        self.append_block_fun(node, name="horizontalrule")

    def depart_transition(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_problematic(self, node: Element) -> None:
        self.append_inline_fun(
            node,
            name="text",
            named_params={"fill": "red"},
            positional_params=[escape_str(node.astext())],
        )

    def depart_problematic(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_Text(self, node: Text) -> None:  # noqa: N802
        self.curr_element().body += ["#" + escape_str(node.astext())]

    def depart_Text(self, node: Text) -> None:  # noqa: N802
        pass

    def visit_raw(self, node: Element) -> None:
        if "typst" in node.get("format", "").split():
            self.append_unprocessed(node, body=[node.astext(), "\n"])
            self.absorb_fun_in_body()
        raise nodes.SkipNode

    def visit_substitution_definition(self, _node: Element) -> None:
        raise nodes.SkipNode

    def visit_math(self, node: Element) -> None:
        self.append_el(
            Math(
                block=False,
                body=node.astext(),
                labels=self.register_labels(node["ids"]),
            ),
        )
        self.absorb_fun_in_body()
        raise nodes.SkipNode

    def visit_math_block(self, node: Element) -> None:
        self.append_el(
            Math(
                block=True,
                body=node.astext(),
                labels=self.register_labels(node["ids"]),
            ),
        )
        self.absorb_fun_in_body()
        raise nodes.SkipNode

    def visit_comment(self, _node: Element) -> None:
        raise nodes.SkipNode
