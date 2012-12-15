"""
The toolkit specific implementation of a MessageDialog. See the IMessageDialog
interface for the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 \
    import QtGui

from facets.core_api \
    import Enum, implements, Unicode

from facets.ui.pyface.i_message_dialog \
    import IMessageDialog, MMessageDialog

from dialog \
    import Dialog

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Map the ETS severity to the corresponding PyQt standard icon:
_SEVERITY_TO_ICON_MAP = {
    'information':  QtGui.QMessageBox.Information,
    'warning':      QtGui.QMessageBox.Warning,
    'error':        QtGui.QMessageBox.Critical
}

#-------------------------------------------------------------------------------
#  'MessageDialog' class:
#-------------------------------------------------------------------------------

class MessageDialog ( MMessageDialog, Dialog ):
    """ The toolkit specific implementation of a MessageDialog.  See the
        IMessageDialog interface for the API documentation.
    """

    implements( IMessageDialog )

    #-- 'IMessageDialog' interface ---------------------------------------------

    message = Unicode

    severity = Enum( 'information', 'warning', 'error' )

    #-- Protected IDialog Interface --------------------------------------------

    def _create_contents ( self, parent ):
        # In PyQt this is a canned dialog:
        pass

    #-- Protected IWidget Interface --------------------------------------------

    def _create_control ( self, parent ):
        return QtGui.QMessageBox(
            _SEVERITY_TO_ICON_MAP[ self.severity ],
            self.title, self.message, QtGui.QMessageBox.Ok, parent
        )

#-- EOF ------------------------------------------------------------------------