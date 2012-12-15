"""
Facets pyface package component
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.core_api \
    import Bool, implements, Unicode

from facets.ui.pyface.i_directory_dialog \
    import IDirectoryDialog, MDirectoryDialog

from dialog \
    import Dialog

#-------------------------------------------------------------------------------
#  'DirectoryDialog' class:
#-------------------------------------------------------------------------------

class DirectoryDialog ( MDirectoryDialog, Dialog ):
    """ The toolkit specific implementation of a DirectoryDialog.  See the
        IDirectoryDialog interface for the API documentation.
    """

    implements( IDirectoryDialog )

    #-- 'IDirectoryDialog' interface -------------------------------------------

    default_path = Unicode

    message = Unicode

    new_directory = Bool( True )

    path = Unicode

    #-- Protected 'IDialog' Interface ------------------------------------------

    def _create_contents ( self, parent ):
        # In wx this is a canned dialog:
        pass

    #-- 'IWindow' Interface ----------------------------------------------------

    def close ( self ):
        # Get the path of the chosen directory:
        self.path = unicode( self.control.GetPath() )

        # Let the window close as normal:
        super( DirectoryDialog, self ).close()

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create_control ( self, parent ):
        # The default style:
        style = wx.OPEN | wx.HIDE_READONLY

        # Create the wx style depending on which buttons are required etc:
        if self.new_directory:
            style = style | wx.DD_NEW_DIR_BUTTON

        if self.message:
            message = self.message
        else:
            message = "Choose a directory"

        # Create the actual dialog:
        return wx.DirDialog( parent, message = message,
                defaultPath = self.default_path, style = style )

#-- EOF ------------------------------------------------------------------------