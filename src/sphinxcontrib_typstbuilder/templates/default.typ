#import "common.typ": *

#let template(
  metadata: (),
  doc,
) = {
  let title = metadata.at("title")
  let author = metadata.at("author")
  let date = get_date(metadata.at("date", default: none))
  let language = metadata.at("language")

  set text(lang: language)

  set document(
    title: title,
    author: author,
    date: date,
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

    #if date != none {
      block(inset: 0.5em)[#date.display()]
    }
  ]

  outline(indent: 2em)

  doc
}
