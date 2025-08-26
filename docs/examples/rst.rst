reStructured text
=================

RST Markup
----------

Inline markup
^^^^^^^^^^^^^

*emphasis*,
**strong emphasis**,
`interpreted text`,
``inline literal``,
`reference to link`_,
`reference to title`_,
`problematic phrase reference`_

.. _reference to link: https://example.com/

.. _reference to title:

Substitution with |substitution|.

.. |substitution| replace:: replacement *text*

Lists
^^^^^

- hello 1,
  hello 1.5

  hello 1.75
- hello 2
- hello 3

  - hello 4

    - hello 5

#. hello 4
#. hello 5
#. hello 6

Line blocks
^^^^^^^^^^^

Take it away, Eric the Orchestra Leader!

| A one, two, a one two three four
|
| Half a bee, philosophically,
|     must, *ipso facto*, half not be.
| But half the bee has got to be,
|     *vis a vis* its entity.  D'you see?
|
| But can a bee be said to be
|     or not to be an entire bee,
|         when half the bee is not a bee,
|             due to some ancient injury?
|
| Singing...

Footnotes
^^^^^^^^^

Lorem ipsum [#f1]_ dolor sit amet ... [#f2]_

.. [#f1] Text of the first footnote.
.. [#f2] Text of the second footnote.

Citations
^^^^^^^^^

Here is a citation reference: [CIT2002]_.

.. [CIT2002] This is the citation.  It's just like a footnote,
   except the label is textual.
.. [CIT2003] This is the citation.  It's just like a footnote,
   except the label is textual.
.. [CIT2004] This is the citation.  It's just like a footnote,
   except the label is textual.

RST Roles
---------

Cross-references
^^^^^^^^^^^^^^^^

:Ref:
    - To a title: :ref:`reference to title`
    - To a figure: :ref:`Drawing`
    - To a table: :ref:`Table`
:Doc: :doc:`md`
:Doc: :doc:`With custom title <md>`
:Term: See :term:`source directory`

Inline code highlighting
^^^^^^^^^^^^^^^^^^^^^^^^

.. role:: python(code)
   :language: python

:Code: :code:`1 + 2`
:Python code: :python:`print(1 + 2)`

Math
^^^^

.. :Math: :math:`a^2 + b^2 = c^2`
.. :Eq: :eq:`a^2 + b^2 = c^2`

Other semantic markup
^^^^^^^^^^^^^^^^^^^^^

:Abbreviation:
    - First call: :abbr:`Lifo (last-in, first-out)`
    - Following calls: :abbr:`Lifo (last-in, first-out)`
:Command: :command:`rm`
:Definition: :dfn:`binary mode`
:File: :file:`/usr/lib/python3.{x}/site-packages`
:GUI Label: :guilabel:`&Cancel`
:Keystrokes: :kbd:`Control-x Control-f`
:Mail header: :mailheader:`Content-Type`
:Make variable: :makevar:`help`
.. :Man page: :manpage:`ls(1)`
:Menu selection: :menuselection:`&Start --> P&rograms`
:MIME type: :mimetype:`text/plain`
:Newsgroup: :newsgroup:`comp.lang.python`
:Program: :program:`curl`
:Regular expression: :regexp:`([abc])+`
:Samp: :samp:`print(1+{variable})`
.. :CVE: :cve:`2020-10735`
.. :CWE: :cwe:`787`
:PEP: :pep:`8`
:RFC: :rfc:`2324`

RST Directives
--------------

Images
^^^^^^

Inline image:

.. image:: drawing.svg

.. figure:: drawing.svg
   :alt: Figure
   :name: Drawing
   :width: 100%

   This is a figure

Tables
^^^^^^

.. table:: The table
   :name: Table

   +------------------------+------------+----------+----------+
   | Header row, column 1   | Header 2   | Header 3 | Header 4 |
   | (header rows optional) |            |          |          |
   +========================+============+==========+==========+
   | body row 1, column 1   | column 2   | column 3 | column 4 |
   +------------------------+------------+----------+----------+
   | body row 2             | Cells may span columns.          |
   +------------------------+------------+---------------------+
   | body row 3             | Cells may  | - Table cells       |
   +------------------------+ span rows. | - contain           |
   | body row 4             |            | - body elements.    |
   +------------------------+------------+---------------------+

.. csv-table:: Frozen Delights!
   :header: "Treat", "Quantity", "Description"
   :widths: 15, 10, 30

   "Albatross", 2.99, "On a stick!"
   "Crunchy Frog", 1.49, "If we took the bones out,
   it wouldn't be crunchy, now would it?"
   "Gannet Ripple", 1.99, "On a stick!"

RST Admonitions
^^^^^^^^^^^^^^^

.. admonition:: Generic admonition

   one

   two

.. attention::

   one

.. caution::

   one

.. danger::

   one

.. error::

   one

.. hint::

   one

.. important::

   one

.. note::

   one

.. tip::

   one

.. warning::

   one

.. seealso::

   one

Glossary
^^^^^^^^

.. glossary::

   environment
      A structure where information about all documents under the root is
      saved, and used for cross-referencing.  The environment is pickled
      after the parsing stage, so that successive runs only need to read
      and parse new and changed documents.

   source directory
      The directory which, including its subdirectories, contains all
      source files for one Sphinx project.

Other directives
^^^^^^^^^^^^^^^^

.. rubric:: Rubric
