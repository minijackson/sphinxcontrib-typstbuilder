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

:Ref: :ref:`reference to title`
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

.. :Abbreviation: :abbr:`LIFO (last-in, first-out)`
:Command: :command:`rm`
:Definition: :dfn:`binary mode`
:File: :file:`/usr/lib/python3.{x}/site-packages`
:GUI Label: :guilabel:`&Cancel`
:Keystrokes: :guilabel:`Control-x Control-f`
:Mail header: :mailheader:`Content-Type`
:Make variable: :makevar:`help`
.. :Man page: :manpage:`ls(1)`
:Menu selection: :menuselection:`Start --> Programs`
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

RST Admonitions
^^^^^^^^^^^^^^^

.. admonition:: title

   world

   world

.. tip::

   world
