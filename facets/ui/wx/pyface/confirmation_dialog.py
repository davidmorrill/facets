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

from facets.api \
    import Bool, Enum, Image, Unicode, implements

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

    def _create_buttons ( self, parent ):
        sizer = wx.BoxSizer( wx.HORIZONTAL )

        # 'YES' button:
        if self.yes_label:
            label = self.yes_label
        else:
            label = "Yes"

        self._yes = yes = wx.Button( parent, wx.ID_YES, label )
        if self.default == YES:
            yes.SetDefault()

        wx.EVT_BUTTON( parent, wx.ID_YES, self._on_yes )
        sizer.Add( yes )

        # 'NO' button:
        if self.no_label:
            label = self.no_label
        else:
            label = "No"

        self._no = no = wx.Button( parent, wx.ID_NO, label )
        if self.default == NO:
            no.SetDefault()

        wx.EVT_BUTTON( parent, wx.ID_NO, self._on_no )
        sizer.Add( no, 0, wx.LEFT, 10 )

        if self.cancel:
            # 'Cancel' button.
            if self.no_label:
                label = self.cancel_label
            else:
                label = "Cancel"

            self._cancel = cancel = wx.Button( parent, wx.ID_CANCEL, label )
            if self.default == CANCEL:
                cancel.SetDefault()

            wx.EVT_BUTTON( parent, wx.ID_CANCEL, self._wx_on_cancel )
            sizer.Add( cancel, 0, wx.LEFT, 10 )

        return sizer


    def _create_dialog_area ( self, parent ):
        panel = wx.Panel( parent, -1 )
        sizer = wx.BoxSizer( wx.HORIZONTAL )
        panel.SetSizer( sizer )
        panel.SetAutoLayout( True )

        # The image:
        if self.image is None:
            image_rc = '@facets:warning'
        else:
            image_rc = self.image

        image = wx.StaticBitmap( panel, -1, image_rc.create_bitmap() )
        sizer.Add( image, 0, wx.EXPAND | wx.ALL, 10 )

        # The message:
        message = wx.StaticText( panel, -1, self.message )
        sizer.Add( message, 1, wx.EXPAND | wx.TOP, 15 )

        # Resize the panel to match the sizer:
        sizer.Fit( panel )

        return panel

    #-- wx Event Handlers ------------------------------------------------------

    def _on_yes ( self, event ):
        """ Called when the 'Yes' button is pressed.
        """
        self.control.EndModal( wx.ID_YES )


    def _on_no ( self, event ):
        """ Called when the 'No' button is pressed.
        """
        self.control.EndModal( wx.ID_NO )

#-- EOF ------------------------------------------------------------------------