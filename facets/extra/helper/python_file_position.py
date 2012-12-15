"""
Defines the PythonFilePosition class, which represents a full or partial
reference to a Python source file. It is a subclass of FilePosition which adds
additional Python specific information, such as package, module, class and
method name.

It is intended to be used as a common tool interchange data format.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.extra.helper.file_position \
    import FilePosition

from facets.core_api \
    import Str

#-------------------------------------------------------------------------------
#  'PythonFilePosition' class:
#-------------------------------------------------------------------------------

class PythonFilePosition ( FilePosition ):
    """ Defines the PythonFilePosition class, which represents a full or partial
        reference to a Python source file. It is a subclass of FilePosition
        which adds additional Python specific information, such as package,
        module, class and  method name.

        It is intended to be used as a common tool interchange data format.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The package name associated with the file position:
    package_name = Str

    # The module name associated with the file position:
    module_name = Str

    # The class name associated with the file position:
    class_name = Str

    # The method name associated with the file position:
    method_name = Str

#-- EOF ------------------------------------------------------------------------