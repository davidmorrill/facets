"""
Facets pyface package component
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from logging \
    import DEBUG

import wx

from facets.core_api \
    import Any, Bool, implements, Instance, Int

from facets.core_api \
    import Tuple, Unicode

# FIXME v3: This should be moved out of pyface.
from facets.ui.pyface.util.font_helper \
    import new_font_like

from facets.ui.pyface.i_splash_screen \
    import ISplashScreen, MSplashScreen

from facets.ui.pyface.image_resource \
    import ImageResource

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from window \
    import Window

#-------------------------------------------------------------------------------
#  'SplashScreen' class:
#-------------------------------------------------------------------------------

class SplashScreen ( MSplashScreen, Window ):
    """ The toolkit specific implementation of a SplashScreen. See the
        ISplashScreen interface for the API documentation.
    """

    implements( ISplashScreen )

    #-- 'ISplashScreen' interface ----------------------------------------------

    image             = Instance( AnImageResource, ImageResource( 'splash' ) )
    log_level         = Int( DEBUG )
    show_log_messages = Bool( True )
    text              = Unicode
    text_color        = Any
    text_font         = Any
    text_location     = Tuple( 5, 5 )

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create_control ( self, parent ):
        # Get the splash screen image:
        image = self.image.create_image()

        splash_screen = wx.SplashScreen(
            # The bitmap to display on the splash screen:
            image.ConvertToBitmap(),

            # Splash Style:
            wx.SPLASH_NO_TIMEOUT | wx.SPLASH_CENTRE_ON_SCREEN,

            # Timeout in milliseconds (we don't currently timeout!):
            0,

            # The parent of the splash screen:
            parent,

            # wx Id:
            -1,

            # Window style:
            style = wx.SIMPLE_BORDER | wx.FRAME_NO_TASKBAR
        )

        # By default we create a font slightly bigger and slightly more italic
        # than the normal system font ;^)  The font is used inside the event
        # handler for 'EVT_PAINT'.
        self._wx_default_text_font = new_font_like(
            wx.NORMAL_FONT,
            point_size = wx.NORMAL_FONT.GetPointSize() + 1,
            style      = wx.ITALIC
        )

        # This allows us to write status text on the splash screen:
        wx.EVT_PAINT( splash_screen, self._on_paint )

        return splash_screen

    #-- Private Methods --------------------------------------------------------

    def _text_set ( self ):
        """ Called when the splash screen text has been changed.
        """
        # Passing 'False' to 'Refresh' means "do not erase the background":
        self.control.Refresh( False )
        self.control.Update()
        wx.Yield()


    def _on_paint ( self, event ):
        """ Called when the splash window is being repainted.
        """
        if self.control is not None:
            # Get the window that the splash image is drawn in:
            window = self.control.GetSplashWindow()

            dc = wx.PaintDC( window )

            if self.text_font is None:
                text_font = self._wx_default_text_font
            else:
                text_font = self.text_font

            dc.SetFont( text_font )

            if self.text_color is None:
                text_color = 'black'
            else:
                text_color = self.text_color

            dc.SetTextForeground( text_color )

            x, y = self.text_location
            dc.DrawText( self.text, x, y )

        # Let the normal wx paint handling do its stuff:
        event.Skip()

#-- EOF ------------------------------------------------------------------------