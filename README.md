Introduction
------------

The 'docs' branch of the Facets repository is an *orphan* branch containing just
the source files for the Facets documentation. The documentation files generated
from this branch can be viewed at: <http://davidmorrill.github.com/facets>.

Installing
----------

If you want to have your own local copy of the Facets documentation, you can
simply check-out the 'gh-pages' branch, which contains all of the documentation
files generated from the 'docs' branch. These are the same files you see when
browsing <http://davidmorrill.github.com/facets>.

If you want to generate your own copy of the documentation from the 'docs'
source files, you will need to have Sphinx installed (<http://sphinx-doc.org/>).

Assuming that you have Sphinx installed and have checked out the 'docs' branch
of Facets, you can generate the documentation by:

  1. Changing to the *users_guide* dicrectory.
  2. Running the command *make html*

This creates a *_build* directory under the *users_guide* directory which
contains all of the files generated by Sphinx. The *_build/html/index.html*
file is the main page for the Facets documentation.

