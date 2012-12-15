"""
A `wx.Timer` subclass that invokes a specified callback periodically.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

#-------------------------------------------------------------------------------
#  'Timer' class:
#-------------------------------------------------------------------------------

class Timer ( wx.Timer ):
    """ Simple subclass of wx.Timer that allows the user to have a function
        called periodically.

        Any exceptions raised in the callable are caught. If `StopIteration`
        is raised the timer stops. If other exceptions are encountered the
        timer is stopped and the exception re-raised.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, millisecs, callable, *args, **kw_args ):
        """ Initialize instance to invoke the given `callable` with given
            arguments and keyword args after every `millisecs` (milliseconds).
        """
        wx.Timer.__init__( self, id = wx.NewId() )

        self.callable = callable
        self.args     = args
        self.kw_args  = kw_args
        self.Start( millisecs )


    def Notify ( self ):
        """ Overridden to call the given callable.  Exceptions raised in the
            callable are caught.  If `StopIteration` is raised the timer stops.
            If other exceptions are encountered the timer is stopped and the
            exception re-raised.
        """
        try:
            self.callable( *self.args, **self.kw_args )
        except StopIteration:
            self.Stop()
        except:
            self.Stop()

            raise

#-- EOF ------------------------------------------------------------------------