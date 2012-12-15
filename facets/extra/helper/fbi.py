"""
Defines the FBI, an object for maintaining the current debugger state of a
Facets-based application. Many of the debugger related tools use the debugger's
state information for their display.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from os.path \
    import split, join, abspath, normcase

from inspect \
    import stack, getinnerframes

from facets.api \
    import HasFacets, HasPrivateFacets, SingletonHasPrivateFacets, Str, Int, \
           Instance, List, Dict, Any, Constant, PythonValue, Bool, Code, \
           toolkit, push_exception_handler

from facets.core.facets_env \
    import facets_env

from facets.extra.tools.tools \
    import Tools

from facets.extra.tools.breakpoints \
    import Breakpoints

from facets.extra.services.file_watch \
    import file_watch

#-------------------------------------------------------------------------------
#  'FBIValue' class:
#-------------------------------------------------------------------------------

class FBIValue ( HasPrivateFacets ):

    #-- Public Facet Definitions -----------------------------------------------

    # Name of the python value:
    name = Str

    # Type of python value:
    type = Str

    # The actual value:
    value = Any

    # String represention of the value:
    str_value = Str

#-------------------------------------------------------------------------------
#  'FBIModule' class:
#-------------------------------------------------------------------------------

class FBIModule ( HasPrivateFacets ):

    #-- Public Facet Definitions -----------------------------------------------

    # File defining the module:
    file_name = Str

    # List of the line numbers of the active break points in the module:
    bp_lines = List( Int )

#-------------------------------------------------------------------------------
#  'StackFrame' class:
#-------------------------------------------------------------------------------

class StackFrame ( HasPrivateFacets ):

    #-- Public Facet Definitions -----------------------------------------------

    # File name:
    file_name = Str

    # File path:
    file_path = Str

    # Function name:
    function_name = Str

    # Line number:
    line = Int

    # Source code line being executed:
    source = Str

    # Module source code:
    module_source = Code

    # List of local variables (including the arguments):
    local_variables = List( FBIValue )

    # Frame local values:
    frame_locals = PythonValue

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, stack_frame ):
        """ Initializes the object.
        """
        frame, file_name, line, self.function_name, lines, index = stack_frame
        self.file_path, self.file_name = split( file_name )

        # Create the list of local variables:
        locals  = self.frame_locals = frame.f_locals
        nlocals = frame.f_code.co_nlocals
        args    = frame.f_code.co_argcount
        names   = frame.f_code.co_varnames
        if (args < nlocals) and (names[0] == 'self'):
            args += 1
        variables = []
        for i in range( nlocals ):
            try:
                # The following statement could fail if the local has not been
                # initialized yet:
                name  = names[ i ]
                value = locals[ name ]
                type  = 'local'
                if i < args:
                    type = 'argument'
                variables.append( FBIValue( name      = name,
                                            type      = type,
                                            value     = value,
                                            str_value = repr( value ) ) )
            except:
                pass

        self.local_variables = variables

        # Read the module source code:
        self.module_source = self.text_file( file_name )

        # Get the source code line being executed:
        try:
            self.source = lines[ index ].strip()
        except:
            self.source = '???'

        # Set the current source code line number being executed:
        self.line = line


    def text_file ( self, file_name ):
        """ Returns the contents of a text file.
        """
        fh = None
        try:
            fh     = open( file_name, 'rb' )
            result = fh.read()
        except:
            result = ''

        if fh is not None:
            fh.close()

        return result

#-------------------------------------------------------------------------------
#  'FBI' class:
#-------------------------------------------------------------------------------

class FBI ( SingletonHasPrivateFacets ):
    """ Model for maintaining important debugger state information.
    """

    #-- Public Facet Definitions -----------------------------------------------

    # Optional 'application' object passed to the tools window when it is
    # initialized:
    object = Instance( HasFacets )

    # Has the debugging environment been initialized yet?
    initialized = Bool( False )

    # Is the debugger enabled for use?
    enabled = Bool

    # Is the debugger active (i.e. is the application suspended)?
    active = Bool( False )

    # Has the user 'quit' the debugger?
    has_quit = Bool( False )

    # Reference to the low-level 'bdb' base debugger:
    bdb = Any # Constant( FBIBdb() )

    # Message to display to the user:
    msg = Str

    # The list of stack frames currently being inspected:
    frames = List( StackFrame )

    # Current frame being inspected:
    frame = Instance( StackFrame )

    # The currently defined break points:
    break_points = Constant( Breakpoints() )

    # The persistent break points manager:
    saved_break_points = Any # Instance( SavedBreakpoints )

    # The set of modules containing break point information:
    modules = Dict( Str, Instance( FBIModule ) )

    # List of local variables (including the arguments) for the current frame:
    local_variables = List( FBIValue )

    # Current selected frame's locals:
    frame_locals = PythonValue

    # Is the FBI being run under an app that has a UI:
    has_ui = Bool( True )

    # Is the FBI being run modally:
    is_modal = Bool( True )

    # Frame information received from the debugger:
    debug_frame = Any

    # The application development/debugger tool suite being used:
    tools = Instance( Tools )

    #-- Public Methods ---------------------------------------------------------

    def start ( self ):
        """ Start the FBI debugging environment.
        """
        self.enabled = True
        self.bdb.begin_trace()


    def step ( self ):
        """ Runs the application program until it reaches the next statement
            (even in a nested function).
        """
        self.bdb.set_step()
        self.exit_ui()


    def next ( self ):
        """ Runs the application program up to the next statement in the
            current function.
        """
        self.bdb.set_next( self.debug_frame )
        self.exit_ui()


    def return_ ( self ):
        """ Runs the application program until the current function returns.
        """
        self.bdb.set_return( self.debug_frame )
        self.exit_ui()


    def go ( self ):
        """ Allows the application program to resume execution.
        """
        self.bdb.set_continue()
        self.exit_ui()


    def quit ( self ):
        """ Shuts down the debugging environment.
        """
        self.bdb.set_quit()
        self.debug_frame = None
        self.has_quit    = True
        self.exit_ui()


    def exit_ui ( self ):
        """ Exits the user interface.
        """
        # Release no longer needed data being held by the debugger:
        self.debug_frame     = None
        self.frames          = []
        self.local_variables = []
        self.frame_locals    = {}

        # Terminate the debugger's event loop and allow the program to resume
        # execution:
        toolkit().event_loop( 0 )


    def add_break_point ( self, file_name, line, bp_type = 'Breakpoint',
                                code = '', end_line = None ):
        """ Adds (or replaces) a break point.
        """
        file_name = self.canonic( file_name )
        bp = self.bdb.set_break( file_name, line, bp_type, code, end_line )
        self.break_points.add( bp )
        self.mark_bp_at( bp )

        self.bdb.begin_trace()


    def mark_bp_at ( self, bp ):
        """ Ensures we have a specified file line marked as having a break
            point.
        """
        bp_lines = self.get_module( bp.file ).bp_lines
        for line in xrange( bp.line, bp.end_line ):
            if line not in bp_lines:
                bp_lines.append( line )


    def remove_break_point ( self, file_name, line = None, type = None ):
        """ Removes all break points on a specified file or single line within
            the file.
        """
        bdb       = self.bdb
        file_name = self.canonic( file_name )

        if line is None:
            bps = bdb.clear_all_file_breaks( file_name, type = type )
        else:
            bps = bdb.clear_break( file_name, line, type = type )

        if len( bps ) > 0:
            self.break_points.remove( *bps )
            lines = set()
            for bp in bps:
                lines.update( xrange( bp.line, bp.end_line ) )

            bp_lines = self.get_module( file_name ).bp_lines
            for line in lines:
                if not bdb.get_break( file_name, line ):
                    bp_lines.remove( line )


    def break_point_lines ( self, file_name ):
        """ Returns the list of lines containing breakpoints for a specified
            file.
        """
        return self.get_module( file_name ).bp_lines[ : ]


    def get_module_for ( self, frame ):
        """ Gets the FBIModule corresponding to a specified frame.
        """
        return self.get_module( join( frame.file_path, frame.file_name ) )


    def get_module ( self, file_name ):
        """ Returns the FBIModule corresponding to a specified file path and
            name.
        """
        file_name = self.canonic( file_name )
        module    = self.modules.get( file_name )
        if module is not None:
            return module

        self.modules[ file_name ] = module = FBIModule( file_name = file_name )

        return module


    def canonic ( self, file_name ):
        """ Returns the canonical form of a specified file name.
        """
        return normcase( abspath( file_name ) )


    def bp ( self, msg = '', offset = 0, debug_frame = None,
                   allow_exception = True ):
        """ Handles an execution break point.
        """
        if allow_exception:
            args = sys.exc_info()
        else:
            args = ( None, None, None )

        self.exception( msg         = msg,
                        offset      = offset,
                        debug_frame = debug_frame,
                        *args )


    def exception ( self, type, value, traceback,
                    msg = '', offset = 0, debug_frame = None ):
        """ Handles a program exception or break point.
        """
        # Get the correct status message and execution frames:
        if value is None:
            msg    = msg or 'Called the FBI'
            frames = [ StackFrame( frame )
                       for frame in stack( 15 )[ offset + 2: ] ]
        else:
            msg    = 'Exception: %s' % str( value )
            frames = [ StackFrame( frame )
                       for frame in getinnerframes( traceback, 15 ) ]
            frames.reverse()
            frames.extend( [ StackFrame( frame )
                             for frame in stack( 15 )[3:] ] )

        # Make sure we don't handle and more exceptions for the moment:
        self.enabled = False

        # Set the new debugging context data:
        self.msg         = msg
        self.frames      = frames
        self.debug_frame = debug_frame

        # Activate the user interface containing all of the debugger tools:
        self.tools.activate()

        # Stop execution here until the developer resumes execution:
        self.active = True
        toolkit().event_loop()
        self.active = False

        # Resume execution and re-enable the debugger:
        self.enabled = (not self.has_quit)

    #-- Facets Default Values --------------------------------------------------

    def _bdb_default ( self ):
        from facets.extra.helper.fbi_bdb import FBIBdb

        return FBIBdb()


    def _enabled_default ( self ):
        enabled = (facets_env.fbi != 0)
        if enabled:
            self._enabled_set( enabled )

        return enabled


    def _saved_break_points_default ( self ):
        from facets.extra.helper.ex_fbi import SavedBreakpoints

        return SavedBreakpoints()


    def _tools_default ( self ):
        from facets.extra.tools.tools import tools, Toolbox

        result = tools(
            application = 'FBI',
            tools       = [ 'FBI Buttons', 'FBI Viewer', 'Stack Frames',
                            'Local Variables' ],
            toolbox     = Toolbox( file_name = 'fbi.box' ),
            object      = self.object,
            show        = False
        )
        result.on_close = self._on_close

        return result

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self, enabled ):
        """ Handles the 'enabled' facet being changed.
        """
        if enabled:
            sys.excepthook, self._excepthook = self.exception, sys.excepthook

            if not self.initialized:
                self.initialized = True

                # Modify the Facets event exception handler so we can handle
                # exceptions:
                try:
                    push_exception_handler(
                        handler            = lambda a, b, c, d: None,
                        reraise_exceptions = True,
                        main               = True,
                        locked             = True
                    )
                except:
                    print 'Could not set Facets notification exception handler'

                # Restore any persistent break points:
                file_name = self.saved_break_points.file_name
                self._bp_watch( file_name )
                self.break_points.restore()

                # Set up a file watch on the persistent break points file:
                file_watch.watch( self._bp_watch, file_name )
        else:
            sys.excepthook = self._excepthook


    def _frames_set ( self, frames ):
        """ Handles the 'frames' facet being changed.
        """
        if len( frames ) > 0:
            self.frame = frame = frames[0]
            self.break_points.remove_temporaries_for( frame )


    def _frame_set ( self, frame ):
        """ Handles the user selecting a new stack frame.
        """
        self.frame_locals    = frame.frame_locals
        self.local_variables = frame.local_variables

    #-- Private Methods --------------------------------------------------------

    def _bp_watch ( self, file_name ):
        """ Restores the set of saved break points when the persistence file
            changes.
        """
        self.saved_break_points.restore()


    def _on_close ( self ):
        """ Returns whether the tools window can be closed now or not.
        """
        return (not self.active)

#-------------------------------------------------------------------------------
#  Debugging Helper Functions:
#-------------------------------------------------------------------------------

# Insert a call to this function into your program to invoke the debugger:
def bp ( condition = True, object = None ):
    """ Sets a breakpoint (conditionally).
    """
    fbi = FBI()

    # Allow setting the 'application' object being debugged (if specified):
    if isinstance( object, HasFacets ):
        fbi.object = object

    if condition is None:
        if facets_env.fbi != 0:
            fbi.tools.activate()
    elif fbi.enabled:
        if condition:
            fbi.bdb.set_trace()
        else:
            fbi.bdb.begin_trace()

#-- EOF ------------------------------------------------------------------------