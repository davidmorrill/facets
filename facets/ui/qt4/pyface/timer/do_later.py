"""
Defines a DoLaterTimer class that allow functions or methods to be executed
at some later time on the GUI thread.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import QTimer, SIGNAL

#-------------------------------------------------------------------------------
#  'DoLaterTimer' class:
#-------------------------------------------------------------------------------

class DoLaterTimer ( QTimer ):

    #-- Class Variables --------------------------------------------------------

    # List of currently active timers:
    active_timers = []

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, interval, callable, args, kw_args ):
        """ Initializes the object.
        """
        QTimer.__init__( self )

        for timer in self.active_timers:
            if ((timer.callable == callable) and
                (timer.args     == args)     and
                (timer.kw_args  == kw_args)):
                timer.start( interval )
                return

        self.active_timers.append( self )
        self.callable = callable
        self.args     = args
        self.kw_args  = kw_args

        self.connect( self, SIGNAL( 'timeout()' ), self.Notify )

        self.setSingleShot( True )
        self.start( interval )


    def Notify ( self ):
        """ Handles the timer pop event.
        """
        self.active_timers.remove( self )
        self.callable( *self.args, **self.kw_args )

#-- EOF ------------------------------------------------------------------------