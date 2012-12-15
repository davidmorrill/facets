"""
A log handler that emits records to a splash screen.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from logging \
    import Handler

#-------------------------------------------------------------------------------
#  'SplashScreenLogHandler' class:
#-------------------------------------------------------------------------------

class SplashScreenLogHandler ( Handler ):
    """ A log handler that displays log messages on a splash screen.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, splash_screen ):
        """ Creates a new handler for a splash screen.
        """
        # Base class constructor:
        Handler.__init__( self )

        # The splash screen that we will display log messages on:
        self._splash_screen = splash_screen


    def emit ( self, record ):
        """ Emits the log record.
        """
        self._splash_screen.text = str( record.getMessage() ) + '...'

#-- EOF ------------------------------------------------------------------------