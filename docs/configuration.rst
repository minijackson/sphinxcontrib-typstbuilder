Configuration
=============

.. role:: py(code)
   :language: python


.. confval:: typst_documents

   :type: :py:`list[dict[str, Any]]`
   :default:
      .. code-block:: python

         [
             {
                 "startdocname": "index",
                 "targetname": "main",
                 "title": project,
             },
         ]

   A list of documents to generate.
   By default, it generates a document :file:`main/main.typ`
   from the :file:`index` document.

   Each document is represented as a dictionnary
   which have these attributes:

   :py:`"startdocname"`
      *Needed.*
      The root document name.
      For example :file:`my/file`.
   :py:`"targetname"`
      *Needed.*
      The name of the generated file.
      The generated file will be under :file:`_build/typst/{targetname}/{targetname}.typ`.
   :py:`"title"`
      *Needed.*
      The main title of the document.
      Used for the title page.
   :py:`"template"`
      *Optional.*
      The document template to use.
      See :confval:`typst_template` for more information.

      Defaults to the value of :confval:`typst_template`.
   :py:`"appendices"`
      *Optional.*
      A list of document names to add at the end of the document.

      Defaults to :py:`[]`
   :py:`"metadata"`
      *Optional.*
      A dictionary of extra metadata to pass to the Typst template.
      See :doc:`writing-templates` for more information.

      Defaults to :py:`{}`


.. confval:: typst_template

   :type: :py:`str`
   :default: :py:`"default"`

   The Typst template to use.

   Available templates:

   :py:`"default"`
       A simple template that uses mostly default values from the Typst project

   :py:`"charged-ieee"`
       A simple template that uses mostly default values from the Typst project

   :py:`"ilm"`
       A simple template that uses mostly default values from the Typst project
