Introduction
------------

Facets is a Python package for model-driven reactive programming.

License
-------

The Facets package is available under a BSD style license. Refer to the
LICENSE.md file for more information.

Download
--------

The Facets package is available at: <https://github.com/davidmorrill/facets>

Prerequisites
-------------

The base Facets package should work on any platform supporting
2.4 <= Python < 3.0.

Some portions of Facets depend on the Numerical Python (numpy) package, which is
available at: http://www.scipy.org/Download

The user interface capabilities of the facets package also require additional
Python packages to be installed.

Facets has a GUI-toolkit neutral design which can support different GUI
toolkits. At this time however, the only backend that is actively being
maintained is:

  - Qt4, consisting of:
    - PyQt4 (available from
             http://www.riverbankcomputing.co.uk/software/pyqt/intro)
    - Qt4 (available from http://qt.nokia.com/products/)

Before attempting to use Facets UI, please be sure to install a recent version
of the PyQt toolkit on your system first. Facets will automatically detect that
the toolkit is installed and use it.

Installation
------------

The Facets package is installed using the standard Python 'distutils' package.
Enter the following command while in the top-level Facets source directory:

    python setup.py install

This will perform a normal install of the Facets package into your Python
installation.

You can also try out Facets without adding it permanently to your Python
installation using the command:

    python setup.py build_ext --inplace

If you do this, be sure to add the directory containing the setup.py file to
your PYTHONPATH before attempting to use Facets.

You can also refer to the Python 'distutils' documentation for more
installation options.

Getting Started
---------------

Facets comes with a large number of demonstrations of its user interface,
animation and reactive programming capabilities. Once you have finished
installing Facets, you can try these by running:

    python -m facets.extra.demo.ui.demo

Click on any item in the **Demos** section to run the corresponding demo and to
view/edit/re-run its source code.

Videos
------

There are a number of Facets related videos available at:
<http://www.youtube.com/user/FacetsTV>
