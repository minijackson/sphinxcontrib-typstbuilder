# Markdown

## Footnotes

- This is a manually-numbered footnote reference.[^3]
- This is an auto-numbered footnote reference.[^myref]

[^myref]: This is an auto-numbered footnote definition.
[^3]: This is a manually-numbered footnote definition.

## Admonitions

```{admonition} title
world
```

```{tip}
world
```

## Md Links

### Md Autolinks

:External URL: <https://example.com>
:Internal target reference: <project:#md-autolinks>
:Internal file reference: <project:index.rst>
:Internal file reference: <project:md.md#md-links>
<!-- :Internal file -> heading reference: <project:../intro.md#-get-started> -->
<!-- :Downloadable file: <path:example.txt> -->
<!-- :Intersphinx reference: <inv:sphinx:std#index> -->

## Escape sequences

These characters should be properly escaped:

In \* ad \$ officiis # et \_ quos \ doloribus \` recusandae.
Molestias " error	quia ea corporis corrupti aut.

https://ddg.gg

<https://ddg.gg>

## Tables

| foo | bar |
| --- | --- |
| baz | bim |

| left | center | right |
| :--- | :----: | ----: |
| a    | b      | c     |

:::{table} Table caption
:widths: 1, 2, 1
:align: center

| foo | bar | baz |
| --- | --: | --- |
| bim | bam |     |
:::
