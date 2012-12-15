Introduction
------------

Facets is a Python package for model-driven reactive programming.

Prerequisites
-------------

The base Facets package should work on any platform supporting
2.4 <= Python < 3.0.

The user interface capabilities of the facets package require additional
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

Enter the following command in the top-level directory:

   python setup.py install

This will perform a normal install of the Facets package into your Python
installation. Refer to the Python 'distutils' documentation for more
installation options.

Download
--------

The Facets package is available at:

    https://github.com/davidmorrill/facets

License
-------

The Facets package is available under a BSD style license. Refer to the
LICENSE.md file for more information.

Videos
------

There are a number of Facets related videos available at:

    http://www.youtube.com/user/FacetsTV
