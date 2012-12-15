"""
The interface for a splash screen.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import logging

from facets.api \
    import Any, Bool, Image, Int, Tuple, Unicode

from splash_screen_log_handler \
    import SplashScreenLogHandler

from i_window \
    import IWindow

#-------------------------------------------------------------------------------
#  'ISplashScreen' class:
#-------------------------------------------------------------------------------

class ISplashScreen ( IWindow ):
    """ The interface for a splash screen.
    """

    #-- 'ISplashScreen' Interface ----------------------------------------------

    # The image to display on the splash screen:
    image = Image

    # If log messages are to be displayed then this is the logging level. See
    # the Python documentation for the 'logging' module for more details:
    log_level = Int( logging.DEBUG )

    # Should the splash screen display log messages in the splash text?
    show_log_messages = Bool( True )

    # Optional text to display on top of the splash image:
    text = Unicode

    # The text color:
    # FIXME v3: When FacetsUI supports PyQt then change this to 'Color',
    # (unless that needs the toolkit to be selected too soon, in which case it
    # may need to stay as Any - or Str?)
    #text_color = WxColor('black')
    text_color = Any

    # The text font:
    # FIXME v3: When FacetsUI supports PyQt then change this back to
    # 'Font(None)' with the actual default being toolkit specific.
    #text_font = Font(None)
    text_font = Any

    # The x, y location where the text will be drawn:
    # FIXME v3: Remove this.
    text_location  = Tuple( 5, 5 )

    #-- Facet Default Values ---------------------------------------------------

    def _image_default ( self ):
        from facets.ui.ui_facets import image_for

        return image_for( '@facets:pyface.jpg' )

#-------------------------------------------------------------------------------
#  'MSplashScreen' class:
#-------------------------------------------------------------------------------

class MSplashScreen ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the ISplashScreen interface.

        Reimplements: open(), close()
    """

    #-- 'IWindow' Interface ----------------------------------------------------

    def open ( self ):
        """ Creates the toolkit-specific control for the widget.
        """
        super( MSplashScreen, self ).open()

        if self.show_log_messages:
            self._log_handler = SplashScreenLogHandler( self )
            self._log_handler.setLevel( self.log_level )

            # Get the root logger.
            logger = logging.getLogger()
            logger.addHandler( self._log_handler )


    def close ( self ):
        """ Close the window.
        """
        if self.show_log_messages:
            # Get the root logger.
            logger = logging.getLogger()
            logger.removeHandler( self._log_handler )

        super( MSplashScreen, self ).close()

#-- EOF ------------------------------------------------------------------------