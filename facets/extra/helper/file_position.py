"""
Defines the FilePosition class, which represents a full or partial reference to
a text file. A partial reference can specify a starting line and column within
the file as well as an optional range of lines and an arbitrary associated data
object.

It is intended to be used as a common tool interchange data format.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import basename

from facets.core_api \
    import HasPrivateFacets, Any, File, Int, Property

#-------------------------------------------------------------------------------
#  'FilePosition' class:
#-------------------------------------------------------------------------------

class FilePosition ( HasPrivateFacets ):
    """ Defines the FilePosition class, which represents a full or partial
        reference to a text file. A partial reference can specify a starting
        line and column within the file as well as an optional range of lines
        and an arbitrary associated data object.

        It is intended to be used as a common tol interchange data format.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The logical name of the file fragment:
    name = Property

    # The name of the file:
    file_name = File

    # The line number within the file:
    line = Int

    # The number of lines within the file (starting at 'line').
    # A value of -1 means the entire file:
    lines = Int( -1 )

    # The column number within the line:
    column = Int

    # An object associated with this file:
    object = Any

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        if self._name is not None:
            return self._name

        return basename( self.file_name )

    def _set_name ( self, name ):
        self._name = name

#-- EOF ------------------------------------------------------------------------