"""
Defines some useful functions for scheduling work to be done on the UI thread
at some later point in time, either as soon as the UI has processed all other
events (do_later) or after some specified amount of time has elapsed (do_after).
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.pyface.toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  Defines the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

DoLaterTimer = toolkit_object( 'timer.do_later:DoLaterTimer' )

#-------------------------------------------------------------------------------
#  Function Definitions:
#-------------------------------------------------------------------------------

def do_later ( callable, *args, **kw_args ):
    """ Does something 50 milliseconds from now.
    """
    DoLaterTimer( 50, callable, args, kw_args )


def do_after ( interval, callable, *args, **kw_args ):
    """ Does something after some specified time interval.
    """
    DoLaterTimer( interval, callable, args, kw_args )

#-- EOF ------------------------------------------------------------------------