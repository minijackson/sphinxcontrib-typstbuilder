#import "@preview/charged-ieee:0.1.2": ieee

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

  show: ieee.with(
    title: title,
    authors: ((name: author),),
  )

  doc
}
