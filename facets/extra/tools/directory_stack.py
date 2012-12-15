"""
A feature-enabled tool for selecting directories using the FileStackEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Directory, View, UItem, FileStackEditor

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'DirectoryStack' class:
#-------------------------------------------------------------------------------

class DirectoryStack ( Tool ):
    """ Allows a user to select directories using a FileStackEditor.
    """

    #-- Facet Definitions ----------------------------------------------------------

    # The name of the tool:
    name = 'Directory Stack'

    # The currently selected directory:
    directory_name = Directory( '/', connect = 'both', save_state = True )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'directory_name', editor = FileStackEditor( type = 'path' ) )
    )

#-- EOF ------------------------------------------------------------------------
