"""
Defines a ConfirmationDialog class which defines a modal dialog for prompting a
user with a question whose response can be Yes, No or Cancel.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtGui \
    import QMessageBox

from facets.api \
    import Bool, Enum, implements, Unicode, Image

from facets.ui.pyface.i_confirmation_dialog \
    import IConfirmationDialog, MConfirmationDialog

from facets.ui.pyface.constant \
    import CANCEL, YES, NO

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

    #-- 'IConfirmationDialog' interface ----------------------------------------

    cancel    = Bool( False )
    default   = Enum( NO, YES, CANCEL )
    image     = Image
    message   = Unicode
    no_label  = Unicode
    yes_label = Unicode

    #-- Protected 'IDialog' Interface ------------------------------------------

    def _create_contents ( self, parent ):
        # In PyQt this is a canned dialog.
        pass

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create_control ( self, parent ):
        dlg = QMessageBox( parent )

        dlg.setWindowTitle( self.title )
        dlg.setText( self.message )

        if self.image is None:
            dlg.setIcon( QMessageBox.Warning )
        else:
            dlg.setIconPixmap( self.image.create_image() )

        # The 'Yes' button:
        if self.yes_label:
            btn = dlg.addButton( self.yes_label, QMessageBox.YesRole )
        else:
            btn = dlg.addButton( QMessageBox.Yes )

        if self.default == YES:
            dlg.setDefaultButton( btn )

        # The 'No' button:
        if self.no_label:
            btn = dlg.addButton( self.no_label, QMessageBox.NoRole )
        else:
            btn = dlg.addButton( QMessageBox.No )

        if self.default == NO:
            dlg.setDefaultButton( btn )

        # The 'Cancel' button:
        if self.cancel:
            if self.cancel_label:
                btn = dlg.addButton( self.cancel_label,
                                     QMessageBox.RejectRole )
            else:
                btn = dlg.addButton( QMessageBox.Cancel )

            if self.default == CANCEL:
                dlg.setDefaultButton( btn )

        return dlg

#-- EOF ------------------------------------------------------------------------