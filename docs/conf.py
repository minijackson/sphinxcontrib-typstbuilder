# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import date

sys.path.append(os.path.abspath("../src"))  # noqa: PTH100

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sphinxcontrib-typstbuilder"
copyright = "Minijackson"
author = "Minijackson"
release = "0.1.0"

source_repository = "https://github.com/minijackson/sphinxcontrib-typstbuilder"

today: str

if date_s := os.environ.get("LAST_MODIFIED"):
    today = f"{date_s[:4]}-{date_s[4:6]}-{date_s[6:8]}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxcontrib_typstbuilder",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for Typst output ------------------------------------------------
# https://minijackson.github.io/sphinxcontrib-typstbuilder/configuration.html

typst_template = "ilm"
typst_date: date

if date_s := os.environ.get("LAST_MODIFIED"):
    typst_date = date(
        year=int(date_s[:4]),
        month=int(date_s[4:6]),
        day=int(date_s[6:8]),
    )

typst_documents = [
    {
        "startdocname": "index",
        "targetname": "main",
        "title": project,
    },
    {
        "startdocname": "examples/index",
        "targetname": "examples",
        "title": f"{project} examples",
        "metadata": {
            "hello": "world!",
        },
    },
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_theme_options = {
    "source_repository": source_repository,
    "source_branch": "main",
    "source_directory": "docs/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": source_repository,
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

# -- Options for MyST --------------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html

myst_heading_anchors = 3

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    # "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# By default, MyST generates a vertical line
# at the end of each document that has footnotes.
# This is useful for HTML, but annoying for PDFs,
# which handle footnotes by themselves,
# so we disable it
myst_footnote_transition = False

def setup(app):
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )
