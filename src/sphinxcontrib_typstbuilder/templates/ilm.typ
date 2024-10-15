#import "@preview/gentle-clues:1.0.0"
#import "@preview/linguify:0.4.1"
#import "@preview/ilm:1.2.1": *

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

  show: ilm.with(
    title: title,
    author: author,
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
