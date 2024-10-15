#import "@preview/gentle-clues:1.0.0"
#import "@preview/linguify:0.4.1"
#import "@preview/charged-ieee:0.1.2": ieee

#let _translations = json("lang.json")
#let _t(content) = {
  linguify.linguify(content, from: _translations)
}

#let template(
  metadata: (),
  doc,
) = {
  let title = metadata.at("title")
  let author = metadata.at("author")
  let date = metadata.at("date")
  let language = metadata.at("language")

  set text(lang: language)

  show: ieee.with(
    title: title,
    authors: ((name: author),),
  )

  doc
}

#let horizontalrule() = [
  #line(start: (25%, 0%), end: (75%, 0%))
]

// Admonitions

#let admonition = gentle-clues.clue.with(accent-color: purple)
#let attention = gentle-clues.clue.with(
  title: _t("Attention"),
  accent-color: red,
)
#let caution = gentle-clues.clue.with(
  title: _t("Caution"),
  accent-color: orange,
)
#let danger = gentle-clues.clue.with(title: _t("Danger"), accent-color: red)
#let error = gentle-clues.clue.with(title: _t("Error"), accent-color: red)
#let hint = gentle-clues.clue.with(title: _t("Hint"), accent-color: green)
#let important = gentle-clues.clue.with(
  title: _t("Important"),
  accent-color: orange,
)
#let note = gentle-clues.clue.with(title: _t("Note"), accent-color: blue)
#let tip = gentle-clues.clue.with(title: _t("Tip"), accent-color: green)
#let warning = gentle-clues.clue.with(
  title: _t("Warning"),
  accent-color: orange,
)
#let seealso = gentle-clues.clue.with(title: _t("See also"), accent-color: blue)

// Signatures

#let _code_font = text.with(font: "DejaVu Sans Mono", size: 0.85em)
#let _punct_font = _code_font.with(fill: luma(100))

#let desc = block.with(inset: 1em)
#let desc_name = _code_font.with(fill: rgb("#4b69c6"))
#let desc_addname = _code_font.with(fill: rgb("#4b69c6").lighten(20%))

#let desc_returns = _code_font

#let desc_annotation = _code_font.with(fill: rgb("#40a02b"))
#let desc_content = block.with(inset: (x: 2em))

#let desc_parameterlist(
  open_paren: "(",
  close_paren: ")",
  child_text_separator: ", ",
  ..elements,
) = {
  _punct_font(open_paren)
  _code_font(elements.pos().join(child_text_separator))
  _code_font(close_paren, fill: luma(100))
}

#let desc_parameter(body) = body

#let desc_sig_name(body) = body
