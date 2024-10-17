#import "@preview/charged-ieee:0.1.2": ieee

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
