#import "@preview/ilm:1.2.1": *

#import "common.typ": *

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
