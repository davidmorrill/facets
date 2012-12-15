"""
Provides a simple function for scheduling some code to run at some time in
    the future (assumes application is wxPython based).
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

#-------------------------------------------------------------------------------
#  'DoLaterTimer' class:
#-------------------------------------------------------------------------------

class DoLaterTimer ( wx.Timer ):

    #-- Class Constants --------------------------------------------------------

    # List of currently active timers:
    active_timers = []

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, interval, callable, args, kw_args ):
        """ Initializes the object.
        """
        global active_timers

        wx.Timer.__init__( self )
        for timer in self.active_timers:
            if ( ( timer.callable == callable ) and
                ( timer.args     == args )     and
                ( timer.kw_args  == kw_args ) ):
                timer.Start( interval, True )
                return

        self.active_timers.append( self )
        self.callable = callable
        self.args     = args
        self.kw_args  = kw_args
        self.Start( interval, True )


    def Notify ( self ):
        """ Handles the timer pop event.
        """
        global active_timers

        self.active_timers.remove( self )
        self.callable( * self.args, **self.kw_args )

#-- EOF ------------------------------------------------------------------------