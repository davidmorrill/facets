"""
Defines a Facets specific FBIBdb subclass of the standard Python 'bdb' debugger.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from sys \
    import settrace, _getframe

from facets.extra.helper.fbi \
    import FBI

from facets.extra.helper.bdb \
    import Bdb

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# Reference to the FBI debugger context:
fbi = FBI()

# fixme: Is this ever used in a meaningful fashion anywhere?...
# Should the next break point hit be skipped?
skip_bp = False

#-------------------------------------------------------------------------------
#  'FBIBdb' class:
#-------------------------------------------------------------------------------

class FBIBdb ( Bdb ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self ):
        Bdb.__init__( self )
        self.bp = {}


    def user_call ( self, frame, argument_list ):
        """ This method is called when there is the remote possibility
            that we ever need to stop in this function.
        """
        if self.break_here( frame ):
            fbi.bp( msg = 'Break point', offset = 3, debug_frame = frame )


    def user_line ( self, frame ):
        """ This method is called when we stop or break at this line.
        """
        global skip_bp

        if skip_bp:
            skip_bp = False
        else:
            fbi.bp( msg = 'Step', offset = 3, debug_frame = frame,
                    allow_exception = False )


    def user_return ( self, frame, return_value ):
        """ This method is called when a return trap is set here.
        """
        fbi.bp( msg = 'Return', offset = 3, debug_frame = frame,
                allow_exception = False )


    def user_exception ( self, frame, ( exc_type, exc_value, exc_traceback ) ):
        """ This method is called if an exception occurs, but only if we are
            to stop at or just below this level.
        """
        fbi.bp( offset = 3, debug_frame = frame )


    def set_trace ( self ):
        """Start debugging from here.
        """
        frame = _getframe().f_back
        code  = frame.f_code
        key   = ( code.co_filename, frame.f_lineno )
        if key in self.bp:
            return

        self.bp[ key ] = None
        self.reset()
        self.stopframe = frame = frame.f_back
        while frame:
            frame.f_trace = self.trace_dispatch
            frame         = frame.f_back

        self.botframe = -1

        settrace( self.trace_dispatch )


    def begin_trace ( self ):
        """ Start debugging from here.
        """
        settrace( None )
        frame = _getframe().f_back
        code  = frame.f_code
        frame = frame.f_back
        self.reset()
        while frame:
            frame.f_trace = self.trace_dispatch
            frame         = frame.f_back

        self.botframe = -1

        self.set_continue()
        settrace( self.trace_dispatch )

#-- EOF ------------------------------------------------------------------------