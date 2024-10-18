#import "@preview/ilm:1.2.1": *

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

  show: ilm.with(
    title: title,
    author: author,
	date: date,
  )

  doc
}

#let literal(body) = {
  // Same as upstream's raw
  set text(font: "DejaVu Sans Mono", size: 9pt)

  // Same as upstream's raw.where(block: false)
  box(
    fill: fill-color.darken(2%),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 2pt,
    body,
  )
}

// Switch back to "DejaVu Sans Mono" because Fira Code doesn't have italics
#show raw: set text(font: "DejaVu Sans Mono")
