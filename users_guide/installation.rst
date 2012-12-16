Getting Facets
==============

Facets is a Python package that works with Python 2.6.x or Python 2.7.x. It does
not currently work with Python 3.x.x. Before proceeding you should make sure
that your system has one of the supported versions of Python installed.

In order to use Facets you'll need to:

* Download the current Facets source code.
* Install Facets by building the C extension modules and setting up your
  PYTHONPATH.
* Download and install additional Python packages used by Facets.

Downloading Facets
------------------

The Facets source code can be downloaded from:

* https://github.com/davidmorrill/facets

If you are working from a command shell and have git installed, you can use the
following command to create a local copy of the Facets source code repository
on your system::

    git clone https://github.com/davidmorrill/facets.git

.. _installing_facets:

Installing Facets
-----------------

.. note::

   This section covers the installation procedure for the *alpha* version of
   Facets and will be replaced with updated documentation once the *beta* stage
   is reached.

Since this is *alpha* level software and subject to frequent update and change,
it is **not** recommended that Facets be installed into your Python
*site_packages* folder. You should use the following procedure instead:

* Download the Facets source code and make the top-level Facets directory (i.e.
  the one containing the *setup.py* file) your current working directory::

      cd facets

* Run the following command to build the two Facets C extension modules::

      python setup.py build_ext --inplace

  This command compiles the extension modules directly into the Facets source
  code tree.

  If you get an error message under Windows, you may have to add an option like
  ``--compiler=msvc`` to specify the correct compiler for building the extension
  modules::

      python setup.py build_ext --inplace --compiler=msvc

* Finally, add the top-level Facets directory (i.e. the one containing the
  *setup.py* file) to your **PYTHONPATH** environment variable.

Updating Facets
---------------

If you update the Facets source code from the GitHub repository, simply re-run
the Python set-up command described in the :ref:`installing_facets` section to
re-build the Facets C extension modules.

In practice, the source code for these modules does not change very often, so it
is usually not necessary run the set-up procedure each time you update the
Facets source. If you do decide to skip this step however, and get unexpected
results when running any Facets-based code, try running the set-up procedure
again before doing any further investigation into the problem.

Facets Prerequisites
--------------------

Before you can use Facets, you must also install the following additional Python
packages:

**numpy**
    Numeric Python (http://numpy.scipy.org/). For Windows binaries, also see:
    http://www.lfd.uci.edu/~gohlke/pythonlibs/.

**PyQt4**
    Python bindings for the Qt GUI toolkit
    (http://www.riverbankcomputing.co.uk/software/pyqt/download). For Windows
    binaries, also see: http://www.lfd.uci.edu/~gohlke/pythonlibs/.

    This package is needed for creating graphical user interfaces (GUI's) using
    Facets.

.. note::

   Facets uses a user interface abstraction layer that allows it to be used with
   other cross platform GUI toolkits. However, the *alpha* level code has only
   been extensively tested using the PyQt4 toolkit. It is anticipated that the
   *beta* version will support the following additional GUI toolkits:

   **wxPython**
       Python bindings for the wxWindows GUI toolkit.

   **PySide**
       An alternative set of Python bindings for the Qt GUI toolkit released
       under a more liberal license than PyQt4.
