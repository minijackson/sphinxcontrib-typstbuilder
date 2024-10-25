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

RST Admonitions
^^^^^^^^^^^^^^^

.. admonition:: title

   world

   world

.. tip::

   world
