#import "@preview/gentle-clues:1.0.0"

#let template(
  metadata: (),
  doc,
) = {
  let title = metadata.at("title")
  let author = metadata.at("author")
  let date = metadata.at("date")

  set document(
    title: title,
    author: author,
    //date: date,
  )

  set heading(numbering: "1.")
  // show heading.where(level: 1): it => {{ pagebreak(weak: true); it }}
  show link: underline

  // Content

  align(center)[
    #block(inset: 2em)[
      #text(weight: "bold", size: 1.5em)[#title]
    ]
    #block(inset: 0.5em)[#author]
    #block(inset: 0.5em)[#date]
  ]

  outline(indent: 2em)

  doc
}

#let horizontalrule() = [
  #line(start: (25%, 0%), end: (75%, 0%))
]

// Admonitions

#let admonition = gentle-clues.clue.with(accent-color: purple)
#let attention = gentle-clues.clue.with(title: "Attention", accent-color: red)
#let caution = gentle-clues.clue.with(title: "Caution", accent-color: orange)
#let danger = gentle-clues.clue.with(title: "Danger", accent-color: red)
#let error = gentle-clues.clue.with(title: "Error", accent-color: red)
#let hint = gentle-clues.clue.with(title: "Hint", accent-color: green)
#let important = gentle-clues.clue.with(title: "Important", accent-color: orange)
#let note = gentle-clues.clue.with(title: "Note", accent-color: blue)
#let tip = gentle-clues.clue.with(title: "Tip", accent-color: green)
#let warning = gentle-clues.clue.with(title: "Warning", accent-color: orange)
#let seealso = gentle-clues.clue.with(title: "See also", accent-color: blue)
