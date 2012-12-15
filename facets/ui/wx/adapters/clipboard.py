"""
Defines a wxPython specific WxClipboard class that provides a concrete
implementation of the Clipboard interface.

The WxClipboard class adapts the wxPython clipboard to provide a set of toolkit
neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.adapters.clipboard \
    import Clipboard

#-------------------------------------------------------------------------------
#  'WxClipboard' class:
#-------------------------------------------------------------------------------

class WxClipboard ( Clipboard ):
    """ Defines a wxPython specific WxClipboard class that provides a concrete
        implementation of the Clipboard interface.

        The WxClipboard class adapts the wxPython clipboard to provide a set of
        toolkit neutral properties and methods.
    """

    #-- Concrete Property Implementations --------------------------------------

    def _get_text ( self ):
        text = ''
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported( wx.DF_TEXT ):
                data = wx.TextDataObject()
                wx.TheClipboard.GetData( data )
                text = data.GetText()

            wx.TheClipboardClose()

        return text

    def _set_text ( self, text ):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData( wx.TextDataObject( text ) )
            wx.TheClipboard.Close()


    def _get_image ( self ):
        # fixme: Implement this...
        raise NotImplementedError

    def _set_image ( self, image ):
        # fixme: Implement this...
        raise NotImplementedError


    def _get_object ( self ):
        # fixme: Implement this...
        raise NotImplementedError

    def _set_object ( self, image ):
        # fixme: Implement this...
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------
