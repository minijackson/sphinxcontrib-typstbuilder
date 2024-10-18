#import "@preview/gentle-clues:1.0.0"
#import "@preview/linguify:0.4.1"

// Utilities

#let _translations = json("lang.json")
#let _t(content) = {
  linguify.linguify(content, from: _translations)
}

// Given a dictionnary of year, month, date,
// return a datetime object
#let get_date(date) = {
  if date != none {
    datetime(
      year: date.at("year"),
      month: date.at("month"),
      day: date.at("day"),
    )
  }
}

// Functions from RST

#let horizontalrule() = [
  #line(start: (25%, 0%), end: (75%, 0%))
]

// Roles

#let literal = text.with(font: "DejaVu Sans Mono", size: 9pt)

// inspired by the acrostiche package
#let abbreviation(explanation: none, abbr) = {
  let state-key = "abbreviation-state-" + abbr
  let displayed = state(state-key, false)
  context {
    smallcaps(abbr)
    if not displayed.get() {
      displayed.update(true)
      [ (#explanation)]
    }
  }
}

// inspired by keyle
#let kbd(sequences) = {
  let _kbd_sym = box.with(
    inset: (x: 5pt),
    outset: (x: -2pt, y: 3pt),
    radius: 2pt,
    stroke: 1pt,
  )
  let _kbd(..keys) = keys.pos().map(_kbd_sym).join("-")

  sequences
    .split()
    .map(sequence => {
        let keys = sequence.split(regex("[+-]"))
        _kbd(..keys)
      })
    .join(" ")
}

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

// Inline

#show raw.where(lang: "samp"): it => {
  // Find blocks like {this}
  show regex("\{.+\}"): it => {
    // Remove start and ending braces
    show regex("(^\{)|(\}$)"): it => []
    // And print it emphasized
    emph(it)
  }
  it
}
