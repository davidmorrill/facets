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

import wx

from facets.core_api \
    import Enum, Unicode, implements

from facets.ui.pyface.i_message_dialog \
    import IMessageDialog, MMessageDialog

from dialog \
    import Dialog

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Map the ETS severity to the corresponding wx standard icon.
SEVERITY_TO_ICON_MAP = {
    'information':  wx.ICON_INFORMATION,
    'warning':      wx.ICON_WARNING,
    'error':        wx.ICON_ERROR
}

#-------------------------------------------------------------------------------
#  'MessageDialog' class:
#-------------------------------------------------------------------------------

class MessageDialog ( MMessageDialog, Dialog ):
    """ The toolkit specific implementation of a MessageDialog. See the
        IMessageDialog interface for the API documentation.
    """

    implements( IMessageDialog )

    #-- 'IMessageDialog' interface ---------------------------------------------

    # The message to be displayed in the dialog:
    message = Unicode

    # The severity level of the message:
    severity = Enum( 'information', 'warning', 'error' )

    #-- Protected 'IDialog' Interface ------------------------------------------

    def _create_contents ( self, parent ):
        # In wx this is a canned dialog:
        pass

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create_control ( self, parent ):
        return wx.MessageDialog(
            parent, self.message, self.title,
            SEVERITY_TO_ICON_MAP[ self.severity ] | wx.OK | wx.STAY_ON_TOP
        )

#-- EOF ------------------------------------------------------------------------