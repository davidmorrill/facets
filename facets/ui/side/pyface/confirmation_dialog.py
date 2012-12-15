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
    import Bool, Enum, implements, Instance, Unicode

from facets.ui.pyface.i_confirmation_dialog \
    import IConfirmationDialog, MConfirmationDialog

from facets.ui.pyface.constant \
    import CANCEL, YES, NO

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from dialog \
    import Dialog

#-------------------------------------------------------------------------------
#  'ConfirmationDialog' class:
#-------------------------------------------------------------------------------

class ConfirmationDialog ( MConfirmationDialog, Dialog ):
    """ The toolkit specific implementation of a ConfirmationDialog.  See the
        IConfirmationDialog interface for the API documentation.
    """

    implements( IConfirmationDialog )

    #-- IConfirmationDialog Interface ------------------------------------------

    cancel    = Bool( False )
    default   = Enum( NO, YES, CANCEL )
    image     = Instance( AnImageResource )
    message   = Unicode
    no_label  = Unicode
    yes_label = Unicode

    #-- Protected IDialog Interface --------------------------------------------

    def _create_contents ( self, parent ):
        # In Qt this is a canned dialog:
        pass

    #-- Protected IWidget Interface --------------------------------------------

    def _create_control ( self, parent ):
        dlg = QtGui.QMessageBox( parent )

        dlg.setWindowTitle( self.title )
        dlg.setText( self.message )

        if self.image is None:
            dlg.setIcon( QtGui.QMessageBox.Warning )
        else:
            dlg.setIconPixmap( self.image.create_image() )

        # The 'Yes' button:
        if self.yes_label:
            btn = dlg.addButton( self.yes_label, QtGui.QMessageBox.YesRole )
        else:
            btn = dlg.addButton( QtGui.QMessageBox.Yes )

        if self.default == YES:
            dlg.setDefaultButton( btn )

        # The 'No' button:
        if self.no_label:
            btn = dlg.addButton( self.no_label, QtGui.QMessageBox.NoRole )
        else:
            btn = dlg.addButton( QtGui.QMessageBox.No )

        if self.default == NO:
            dlg.setDefaultButton( btn )

        # The 'Cancel' button:
        if self.cancel:
            if self.cancel_label:
                btn = dlg.addButton( self.cancel_label,
                                     QtGui.QMessageBox.RejectRole )
            else:
                btn = dlg.addButton( QtGui.QMessageBox.Cancel )

            if self.default == CANCEL:
                dlg.setDefaultButton( btn )

        return dlg

#-- EOF ------------------------------------------------------------------------