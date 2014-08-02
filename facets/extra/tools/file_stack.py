"""
A feature-enabled tool for selecting files using the FileStackEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import File, View, UItem, FileStackEditor

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'FileStack' class:
#-------------------------------------------------------------------------------

class FileStack ( Tool ):
    """ Allows a user to select files using a FileStackEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'File Stack'

    # The currently selected file:
    file_name = File( '/', connect = 'both', save_state = True )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'file_name', editor = FileStackEditor() ),
        id = 'facets.extra.tools.file_stack.FileStack'
    )

#-- EOF ------------------------------------------------------------------------
