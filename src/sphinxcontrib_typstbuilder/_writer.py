from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from textwrap import indent
from typing import TYPE_CHECKING, Any, cast

from docutils import nodes, writers
from sphinx.util.docutils import SphinxTranslator

if TYPE_CHECKING:
    from docutils.nodes import Element, Text
    from sphinx.builders.text import TextBuilder

    from ._builder import TypstBuilder


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


# class EvalMode(Enum):
#     """The syntactical mode in which the current Typst code is.
#
#     See https://typst.app/docs/reference/foundations/eval/#parameters-mode
#     """
#
#     CODE = 1
#     MARKUP = 2
#     MATH = 3


@dataclass
class Document:
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

    def to_text(self) -> str:
        named = ""
        for name, arg in self.named_params.items():
            named += f"{name}: {arg}, "

        pos = ""
        for arg in self.positional_params:
            pos += f"{arg}, "

        body = "".join(self.body).strip()
        if "\n" in body:
            body = "\n" + indent(body, "  ") + "\n"
        if body != "":
            body = f"[{body}]"

        labels = ""
        for label in self.labels:
            labels += f" <{label}>"

        return f"{self.name}({named}{pos}){body}{labels}"


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
            labels += f" <{label}>"

        return f"[{body}{labels}]"


@dataclass
class ArrayArg:
    body: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        body = ", ".join(self.body).strip()

        return f"({body})"


def document_label(docname: str) -> str:
    return "document:" + docname.replace("/", ":")


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


class TypstTranslator(SphinxTranslator):
    def __init__(self, document: nodes.document, builder: TextBuilder) -> None:
        super().__init__(document, builder)
        self.body_bak = ""

        self.sectionlevel = 0
        self.curr_elements = [Document()]

        self.this_is_the_title = True

        self.pending_labels: list[str] = []
        self.label_aliases = {}

    def curr_element(self) -> Any:
        return self.curr_elements[-1]

    def append_el(self, el: Any) -> None:
        self.curr_elements.append(el)

    def pop_el(self) -> str:
        return self.curr_elements.pop().to_text()

    def append_inline_fun(self, *args, **kwargs) -> None:
        self.append_el(InlineMarkupFunction(*args, **kwargs))

    def append_block_fun(self, *args, **kwargs) -> None:
        self.append_el(BlockMarkupFunction(*args, **kwargs))

    def append_inline_code_fun(self, *args, **kwargs) -> None:
        self.append_el(InlineCodeFunction(*args, **kwargs))

    def append_block_code_fun(self, *args, **kwargs) -> None:
        self.append_el(BlockCodeFunction(*args, **kwargs))

    def register_labels(self, labels: list[str]) -> list[str]:
        """Register a list of document labels, and return only the main one."""
        if not labels:
            return []

        main_label = labels[0]

        # TODO: handle labels, that can be duplicate across files
        for label in labels:
            self.label_aliases[label] = main_label

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
        # TODO: error management
        # main_label = self.label_aliases[label]
        # return f"label({main_label})"

        # TODO: this skips document for refs with anchors in other documents
        # this means that there can be collision if same label in multiple documents
        # if (pos := label.find("#")) != -1:
        #     label = label[pos + 1:]

        if (pos := label.find("#")) != -1:
            label = label[:pos]

        return f"label(label-aliases.at({escape_str(label)}))"

    def body(self) -> str:
        if len(self.curr_elements) != 1:
            # TODO: print warning
            pass

        content = self.curr_elements[0].to_text()

        return f"""
#import "templates/{self.config.typst_template}.typ": *

#let metadata = json("metadata.json")
#let label-aliases = metadata.at("label_aliases")

#show: template.with(metadata: metadata)

{content}
"""

    # Visitor functions
    # =================

    # Containers

    def visit_document(self, node: Element) -> None:
        self.pending_labels.append(document_label(node["docname"]))

    def depart_document(self, node: Element) -> None:
        pass

    def visit_start_of_file(self, node: Element) -> None:
        self.pending_labels.append(document_label(node["docname"]))

    def depart_start_of_file(self, node: Element) -> None:
        pass

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
            self.append_block_fun(name="figure")

    def depart_container(self, node: Element) -> None:
        if "literal-block-wrapper" in node["classes"]:
            self.absorb_fun_in_body()

    # Inline markup

    def visit_emphasis(self, _node: Element) -> None:
        self.append_inline_fun(name="emph")

    def depart_emphasis(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_strong(self, _node: Element) -> None:
        self.append_inline_fun(name="strong")

    def depart_strong(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_title_reference(self, _node: Element) -> None:
        self.append_inline_fun(name="emph")

    def depart_title_reference(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_literal(self, node: Element) -> None:
        lang = node.get("language", None)

        if "code" not in node["classes"] or not lang:
            self.append_inline_fun("literal")
            return

        named_params = {}
        if lang:
            named_params["lang"] = escape_str(lang)
        self.append_inline_fun(
            name="raw",
            named_params=named_params,
            positional_params=[escape_raw_str(node.astext())],
        )
        self.absorb_fun_in_body()
        raise nodes.SkipNode

    def depart_literal(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_inline(self, node: Element) -> None:
        # TODO: check for classes, e.g. "menuselection", "guilabel"
        pass

    def depart_inline(self, _node: Element) -> None:
        pass

    # Links

    def visit_reference(self, node: Element) -> None:
        # TODO: use different functions depending on internal or not,
        # in order to be able to style.
        self.append_inline_fun(name="link")

        internal = node.get("internal", False)

        if "refuri" in node and not internal:
            self.curr_element().positional_params.append(escape_str(node["refuri"]))
        elif "refuri" in node and internal:
            self.curr_element().positional_params.append(self.label_ref(node["refuri"]))
        else:
            self.curr_element().positional_params.append(self.label_ref(node["refid"]))

    def depart_reference(self, _node: Element) -> None:
        self.absorb_fun_in_body()
        pass

    def visit_target(self, node: Element) -> None:
        pass

    def depart_target(self, _node: Element) -> None:
        pass

    # ...

    def visit_title(self, node: Element) -> None:
        if isinstance(node.parent, nodes.Admonition):
            self.append_el(MarkupArg())
            return

        if self.this_is_the_title:
            self.this_is_the_title = False
            raise nodes.SkipNode

        self.append_block_fun(name="heading", named_params={"level": self.sectionlevel})

    def depart_title(self, node: Element) -> None:
        if isinstance(node.parent, nodes.Admonition):
            el = self.pop_el()
            self.curr_element().named_params["title"] = el
            return

        self.absorb_fun_in_body()

    def visit_paragraph(self, _node: Element) -> None:
        # self.curr_element().body.append("\n")
        self.append_block_fun(name="par")

    def depart_paragraph(self, _node: Element) -> None:
        # self.curr_element().body.append("\n")
        self.absorb_fun_in_body()

    # Lists

    def visit_bullet_list(self, _node: Element) -> None:
        self.append_block_fun(name="list")

    def depart_bullet_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_enumerated_list(self, _node: Element) -> None:
        self.append_block_fun(name="enum")

    def depart_enumerated_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_list_item(self, _node: Element) -> None:
        self.append_el(MarkupArg())

    def depart_list_item(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # Definition lists

    def visit_definition_list(self, _node: Element) -> None:
        self.append_block_fun(name="terms")

    def depart_definition_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    # TODO: this doesn't support for ex.:
    #
    # Term 1
    # Term 2
    #     Definition for both
    def visit_definition_list_item(self, node: Element) -> None:
        self.append_block_code_fun(name="terms.item")

    def depart_definition_list_item(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_term(self, node: Element) -> None:
        self.append_el(MarkupArg(labels=self.register_labels(node["ids"])))

    def depart_term(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_definition(self, node: Element) -> None:
        self.append_el(MarkupArg())

    def depart_definition(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # Field lists

    def visit_field_list(self, _node: Element) -> None:
        # TODO: style it differently?
        self.append_block_fun(name="terms")

    def depart_field_list(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_field(self, node: Element) -> None:
        self.append_block_code_fun(name="terms.item")

    def depart_field(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_field_name(self, node: Element) -> None:
        self.append_el(MarkupArg(labels=self.register_labels(node["ids"])))

    def depart_field_name(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_field_body(self, node: Element) -> None:
        self.append_el(MarkupArg())

    def depart_field_body(self, _node: Element) -> None:
        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    # Figures / Images / Code blocks

    def visit_figure(self, node: Element) -> None:
        self.append_block_fun(name="figure")

    def depart_figure(self, node: Element) -> None:
        self.absorb_fun_in_body()

    # TODO: visit_legend
    def visit_caption(self, node: Element) -> None:
        self.append_el(MarkupArg())

    def depart_caption(self, node: Element) -> None:
        el = self.pop_el()
        self.curr_element().named_params["caption"] = el

    def visit_image(self, node: Element) -> None:
        image = self.builder.images[node["uri"]]
        self.append_inline_fun(name="image", positional_params=[escape_raw_str(image)])

    def depart_image(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_literal_block(self, node: Element) -> None:
        self.append_block_fun(
            name="raw",
            named_params={"block": "true", "lang": escape_str(node["language"])},
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_literal_block(self, node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_block_quote(self, _node: Element) -> None:
        self.append_block_fun(name="quote", named_params={"block": "true"})

    def depart_block_quote(self, node: Element) -> None:
        self.absorb_fun_in_body()

    # Glossary / Indices

    def visit_glossary(self, node: Element) -> None:
        pass

    def depart_glossary(self, node: Element) -> None:
        pass

    def visit_index(self, _node: Element) -> None:
        # TODO
        raise nodes.SkipNode

    # Admonitions

    def visit_admonition(self, _node: Element) -> None:
        self.append_block_fun(name="admonition")

    def depart_admonition(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def _visit_named_admonition(self, node: Element) -> None:
        self.append_block_fun(name=node.tagname)

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

    # Signatures / objects

    def visit_desc(self, _node: Element) -> None:
        self.append_block_fun(name="desc")

    def depart_desc(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_signature(self, node: Element) -> None:
        if "ids" in node:
            self.pending_labels += node["ids"]

    def depart_desc_signature(self, _node: Element) -> None:
        pass

    def visit_desc_name(self, node: Element) -> None:
        self.append_inline_fun(
            name="desc_name",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_name(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_addname(self, node: Element) -> None:
        self.append_inline_fun(
            name="desc_addname",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_addname(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_returns(self, node: Element) -> None:
        self.append_inline_fun(
            name="desc_returns",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_returns(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_annotation(self, node: Element) -> None:
        self.append_inline_fun(
            name="desc_annotation",
            positional_params=[escape_raw_str(node.astext())],
        )

    def depart_desc_annotation(self, _node: Element) -> None:
        self.curr_element().body = []
        self.absorb_fun_in_body()

    def visit_desc_content(self, _node: Element) -> None:
        self.append_block_fun(name="desc_content")

    def depart_desc_content(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_parameterlist(self, node: Element) -> None:
        self.append_block_fun(
            name="desc_parameterlist",
            named_params={
                "open_paren": '"("',
                "close_paren": '")"',
                "child_text_separator": '"' + node.child_text_separator + '"',
            },
        )

    def depart_desc_parameterlist(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_desc_parameter(self, _node: Element) -> None:
        self.append_el(MarkupArg())
        self.append_inline_fun(name="desc_parameter")

    def depart_desc_parameter(self, _node: Element) -> None:
        self.absorb_fun_in_body()
        if self.pending_labels:
            self.curr_element().labels = self.register_labels(self.pending_labels)
            self.pending_labels = []

        el = self.pop_el()
        self.curr_element().positional_params.append(el)

    def visit_desc_sig_name(self, _node: Element) -> None:
        self.append_inline_fun(name="desc_sig_name")

    def depart_desc_sig_name(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    # Others

    def visit_transition(self, _node: Element) -> None:
        self.append_block_fun(name="horizontalrule")

    def depart_transition(self, _node: Element) -> None:
        self.absorb_fun_in_body()

    def visit_problematic(self, node: Element) -> None:
        self.append_inline_fun(
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

    def visit_raw(self, _node: Element) -> None:
        # TODO
        raise nodes.SkipNode

    def visit_comment(self, _node: Element) -> None:
        raise nodes.SkipNode
