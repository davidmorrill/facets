"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide \
    import QtGui

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
    """ The toolkit specific implementation of a DirectoryDialog. See the
        IDirectoryDialog interface for the API documentation.
    """

    implements( IDirectoryDialog )

    #-- 'IDirectoryDialog' interface -------------------------------------------

    default_path  = Unicode
    message       = Unicode
    new_directory = Bool( True )
    path          = Unicode

    #-- Protected IDialog Interface --------------------------------------------

    def _create_contents ( self, parent ):
        # In Qt this is a canned dialog.
        pass

    #-- IWindow Interface ------------------------------------------------------

    def close ( self ):
        # Get the path of the chosen directory:
        files = self.control.selectedFiles()

        if files:
            self.path = unicode( files[ 0 ] )
        else:
            self.path = ''

        # Let the window close as normal:
        super( DirectoryDialog, self ).close()

    #-- Protected IWidget Interface --------------------------------------------

    def _create_control ( self, parent ):
        dlg = QtGui.QFileDialog( parent, self.title, self.default_path )

        dlg.setViewMode( QtGui.QFileDialog.Detail )
        dlg.setFileMode( QtGui.QFileDialog.DirectoryOnly )

        if not self.new_directory:
            dlg.setReadOnly( True )

        if self.message:
            dlg.setLabelText( QtGui.QFileDialog.LookIn, self.message )

        return dlg

#-- EOF ------------------------------------------------------------------------