Writing custom templates
========================

sphinxcontrib-typstbuilder comes with a set a Typst templates ready to use,
but gives you the option to define your own.

To do so,
the simplest way to start is to copy the :file:`default.typ` template,
from the :file:`src/sphinxcontrib_typstbuilder/templates/` directory
of the sphinxcontrib-typstbuilder source code.

Needed functions
----------------

The generated Typst code use some functions that aren't defined
in the Typst standard library,
so you must define them in the template.

You can use the default implementations by adding at the top of your template:

.. code-block:: typst

   #import "common.typ": *

See the documented functions in :file:`src/sphinxcontrib_typstbuilder/templates/common.typ`.
