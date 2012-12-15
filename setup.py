"""
The Facets toolset for reactive programming.

Facets allows Python programmers to use a special kind of type definition
called a *facet*, which gives object attributes some additional characteristics:

- **Initialization**: A facet has a *default value*, which is
  automatically set as the initial value of an attribute before its
  first use in a program.
- **Validation**: A facet attribute's type is *explicitly declared*. The
  type is evident in the code, and only values that meet a
  programmer-specified set of criteria (i.e., the facet definition) can
  be assigned to that attribute.
- **Delegation**: The value of a facet attribute can be contained either
  in the defining object or in another object *delegated* to by the
  facet.
- **Notification**: Setting the value of a facet attribute can *notify*
  other parts of the program that the value has changed.
- **Visualization**: User interfaces that allow a user to *interactively
  modify* the value of a facet attribute can be automatically
  constructed using the facet's definition. (This feature requires that
  a supported GUI toolkit be installed. If this feature is not used, the
  Facets project does not otherwise require GUI support.)

A class can freely mix facet-based attributes with normal Python attributes,
or can opt to allow the use of only a fixed or open set of facet attributes
within the class. Facet attributes defined by a class are automatically
inherited by any subclass derived from the class.

Prerequisites
-------------
You must have the following libraries installed before building or installing
Facets:

* `Numpy <http://pypi.python.org/pypi/numpy/1.1.1>`_ to support the facet types
  for arrays. Version 1.1.0 or later is preferred. Version 1.0.4 will work, but
  some tests may fail.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from os \
    import walk, sep

from os.path \
    import dirname, join, abspath

from distutils.core \
    import setup, Extension

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

# The root path to this file:
root_path = abspath( dirname( sys.argv[0] ) )

def find_packages ( root_package ):
    """ Returns all of the packages of the specified root package.
    """
    packages     = []
    package_data = {}
    n            = len( root_path ) + 1

    for path, dirs, files in walk( join( root_path, root_package ) ):
        if '__init__.py' in files:
            package = path[ n: ].replace( sep, '.' )
            packages.append( package )
            for name in ( 'images', 'library', 'themes' ):
                if name in dirs:
                    items = package_data.setdefault( package, [] )
                    if name == 'library':
                        items.extend( [ name + '/*.zip', name + '/*.txt' ] )
                    elif name == 'themes':
                        items.extend( [ name + '/*.theme' ] )
                    else:
                        items.append( name + '/*' )
                        
                    dirs.remove( name )
        else:
            del dirs[:]

    return ( packages, package_data )


def get_version ( ):
    """ Returns the current Facets version information.
    """
    file_name = join( root_path, 'facets', 'core', 'facets_version.py' )
    version   = '4.0.0'
    fh        = None
    try:
        fh = open( file_name, 'rb' )
        for line in fh.readlines():
            if line.find( '__version__' ) >= 0:
                version = line.split( '=', 1 )[1].strip().strip( "'" )
                break
    finally:
        if fh is not None:
            fh.close()

    return version

#-------------------------------------------------------------------------------
#  Setup the package:
#-------------------------------------------------------------------------------

# Define the packages and package data to include:
packages, package_data = find_packages( 'facets' )

# Define the C level extension modules:
ext_modules = [
    Extension(
        'facets.core.cfacets',
        sources            = [ 'facets/core/cfacets.c' ],
        extra_compile_args = [ '-DNDEBUG=1', '-O3' ],
    ),
    Extension(
        'facets.core.protocols._speedups',
        # fixme: Use the generated sources until Pyrex 0.9.6 and setuptools can
        # work with each other.
        sources            = [ 'facets/core/protocols/_speedups.c' ],
        extra_compile_args = [ '-DNDEBUG=1', '-O3' ],
    )
]

# Define the package classifiers:
classifiers = [
    c.strip() for c in """
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: End Users/Desktop
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: C
        Programming Language :: Python
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        Topic :: Software Development :: Graphical User Interfaces
        Topic :: Software Development :: MVC Programming
        """.splitlines()
    if len( c.strip() ) > 0
]

# Invoke the distutils 'setup' function to perform the specified installation
# request:
setup(
    name             = 'Facets',
    version          = get_version(),
    description      = 'The Facets toolset for reactive programming',
    long_description = __doc__,
    classifiers      = classifiers,

    url              = 'http://dmorrill.com',
    download_url     = 'http://dmorrill.com',

    author           = 'David C. Morrill',
    author_email     = 'david.morrill@gmail.com',
    maintainer       = 'David C. Morrill',
    maintainer_email = 'david.morrill@gmail.com',

    ext_modules      = ext_modules,
    packages         = packages,
    package_data     = package_data
)

#-- EOF ------------------------------------------------------------------------