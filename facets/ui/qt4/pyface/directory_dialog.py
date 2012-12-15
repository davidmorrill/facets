"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Major package imports:
from PyQt4 \
    import QtGui

# Facets library imports:
from facets.core_api \
    import Bool, implements, Unicode

# Local imports:
from facets.ui.pyface.i_directory_dialog \
    import IDirectoryDialog, MDirectoryDialog

from dialog \
    import Dialog


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

    #---------------------------------------------------------------------------
    # Protected 'IDialog' interface.
    #---------------------------------------------------------------------------

    def _create_contents ( self, parent ):
        # In PyQt this is a canned dialog.
        pass

    #---------------------------------------------------------------------------
    # 'IWindow' interface.
    #---------------------------------------------------------------------------

    def close ( self ):
        # Get the path of the chosen directory.
        files = self.control.selectedFiles()

        if files:
            self.path = unicode( files[ 0 ] )
        else:
            self.path = ''

        # Let the window close as normal.
        super( DirectoryDialog, self ).close()

    #---------------------------------------------------------------------------
    # Protected 'IWidget' interface.
    #---------------------------------------------------------------------------

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