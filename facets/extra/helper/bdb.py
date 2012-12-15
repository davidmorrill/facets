"""
Implements a subclass of the standard Python debugger interface for use with the
FBI debugger.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import os
import types

from os.path \
    import basename

from facets.core_api \
    import HasPrivateFacets, Any, File, Int, Str, Enum, Property, Bool

from facets.core.facet_base \
    import read_file

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Template for 'Log' break point code:
logger_template = """import logging
logger = logging.getLogger(__name__)
logger.debug( "%s: %%s" %% (%s) )
"""

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

BPType = Enum( 'Breakpoint', 'Temporary', 'Count', 'Trace', 'Print', 'Log',
               'Patch' )

#-------------------------------------------------------------------------------
#  'BdbQuit' class:
#-------------------------------------------------------------------------------

class BdbQuit ( Exception ):
    """Exception to give up completely"""

#-------------------------------------------------------------------------------
#  'Bdb' class:
#-------------------------------------------------------------------------------

class Bdb:
    """Generic Python debugger base class.

       This class takes care of details of the trace facility; a derived class
       should implement user interaction. The standard debugger class (pdb.Pdb)
       is an example.
    """

    def __init__ ( self ):
        self.fncache = {}


    def trace_dispatch ( self, frame, event, arg ):
        if self.quitting:
            return # None

        if event == 'line':
            return self.dispatch_line( frame )

        if event == 'call':
            return self.dispatch_call( frame, arg )

        if event == 'return':
            return self.dispatch_return( frame, arg )

        if event == 'exception':
            return self.dispatch_exception( frame, arg )

        print 'bdb.Bdb.dispatch: unknown debugging event:', `event`

        return self.trace_dispatch


    def dispatch_line ( self, frame ):
        if self.stop_here( frame ) or self.break_here( frame ):
            self.user_line( frame )
            if self.quitting:
                raise BdbQuit

        return self.trace_dispatch


    def dispatch_call ( self, frame, arg ):
        # XXX 'arg' is no longer used
        if self.botframe is None:
            # First call of dispatch since reset()
            self.botframe = frame.f_back # (CT) Note that this may also be None!

            return self.trace_dispatch

        if not (self.stop_here( frame ) or self.break_anywhere( frame )):
            # No need to trace this function
            return # None

        self.user_call( frame, arg )
        if self.quitting:
            raise BdbQuit

        return self.trace_dispatch


    def dispatch_return ( self, frame, arg ):
        if self.stop_here( frame ) or (frame == self.returnframe):
            self.user_return( frame, arg )
            if self.quitting:
                raise BdbQuit

        return self.trace_dispatch


    def dispatch_exception ( self, frame, arg ):
        if self.stop_here( frame ):
            self.user_exception( frame, arg )
            if self.quitting:
                raise BdbQuit

        return self.trace_dispatch


    def stop_here ( self, frame ):
        """ Normally derived classes don't override the following methods, but
            they may if they want to redefine the definition of stopping and
            breakpoints.
        """
        # (CT) stopframe may now also be None, see dispatch_call.
        # (CT) the former test for None is therefore removed from here.
        if frame is self.stopframe:
            return True

        while (frame is not None) and (frame is not self.stopframe):
            if frame is self.botframe:
                return True

            frame = frame.f_back

        return False


    def break_here ( self, frame ):
        line = frame.f_lineno
        bps  = Breakpoint.bp_map.get(
                   ( self.canonic( frame.f_code.co_filename ), line ) )
        if bps is None:
            return False

        return effective( bps, line, frame )


    def break_anywhere ( self, frame ):
        return ( Breakpoint.bp_list.get(
                    self.canonic( frame.f_code.co_filename ) ) is not None )

    #-- Derived classes should override the user_* methods to gain control -----

    def user_call ( self, frame, argument_list ):
        """ This method is called when there is the remote possibility that we
            ever need to stop in this function.
        """
        pass


    def user_line ( self, frame ):
        """ This method is called when we stop or break at this line.
        """
        pass


    def user_return ( self, frame, return_value ):
        """ This method is called when a return trap is set here.
        """
        pass


    def user_exception ( self, frame, ( exc_type, exc_value, exc_traceback ) ):
        """ This method is called if an exception occurs, but only if we are to
            stop at or just below this level.
        """
        pass

    #---------------------------------------------------------------------------
    #  Derived classes and clients can call the following methods to affect the
    #  stepping state:
    #---------------------------------------------------------------------------

    def reset ( self ):
        import linecache

        linecache.checkcache()
        self.botframe    = None
        self.stopframe   = None
        self.returnframe = None
        self.quitting    = 0


    def set_step ( self ):
        """ Stop after one line of code.
        """
        self.stopframe   = None
        self.returnframe = None
        self.quitting    = 0


    def set_next ( self, frame ):
        """ Stop on the next line in or below the given frame.
        """
        self.stopframe   = frame
        self.returnframe = None
        self.quitting    = 0


    def set_return ( self, frame ):
        """ Stop when returning from the given frame.
        """
        self.stopframe   = frame.f_back
        self.returnframe = frame
        self.quitting    = 0


    def set_trace ( self ):
        """ Start debugging from here.
        """
        frame = sys._getframe().f_back
        self.reset()
        while frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame         = frame.f_back

        self.set_step()
        sys.settrace( self.trace_dispatch )


    def set_continue ( self ):
        # Don't stop except at breakpoints or when finished:
        self.stopframe   = self.botframe
        self.returnframe = None
        self.quitting    = 0

        if not Breakpoint.bp_list:
            # No breakpoints; run without debugger overhead:
            sys.settrace( None )
            frame = sys._getframe().f_back
            while frame and (frame is not self.botframe):
                del frame.f_trace
                frame = frame.f_back


    def set_quit ( self ):
        self.stopframe   = self.botframe
        self.returnframe = None
        self.quitting    = 1
        sys.settrace( None )

    #---------------------------------------------------------------------------
    #  Derived classes and clients can call the following methods to manipulate
    #  breakpoints.
    #---------------------------------------------------------------------------

    def set_break ( self, file_name, line, bp_type = 'Breakpoint', code = '',
                          end_line = None ):
        return Breakpoint( file      = file_name,
                           line      = line,
                           end_line  = (end_line or line) + 1,
                           bp_type   = bp_type,
                           code      = code )


    def restore_break ( self, bp ):
        bp.restore()


    def clear_break ( self, file_name, line, type = None ):
        """ Clear all break points on a specified file line.
        """
        # Try to remove all break points on the specified line:
        result    = []
        file_name = self.canonic( file_name )
        bps       = Breakpoint.bp_start.get( ( file_name, line ), set() ).copy()
        for bp in bps:
            if (type is None) or (type == bp.bp_type):
                bp.delete_me()
                result.append( bp )

        # Return the list of break points deleted:
        return result


    def clear_all_file_breaks ( self, file_name, type = None ):
        """ Clear all break points within a specified file.
        """
        result = []
        for bp in Breakpoint.bp_list.get( self.canonic( file_name ), [ ] ):
            if (type is None) or (type == bp.bp_type):
                bp.delete_me()
                result.append( bp )

        return bps


    def clear_all_breaks ( self ):
        """ Clear all break points.
        """
        for bps in Breakpoint.bp_list.values():
            for bp in bps:
                bp.delete_me()


    def clear_bp ( self, bp ):
        bp.delete_me()


    def get_break ( self, file_name, line ):
        return ((self.canonic( file_name ), line ) in Breakpoint.bp_map)


    def get_breaks ( self, file_name, line ):
        return Breakpoint.bp_map.get( ( self.canonic( file_name ), line ),
                                      set() )


    def get_file_breaks ( self, file_name ):
        return Breakpoint.bp_list.get( self.canonic( file_name ), set() )


    def get_all_breaks ( self ):
        result = []
        for bps in Breakpoint.bp_list.values():
            result.extend( bps )

        return result

    #---------------------------------------------------------------------------
    #  The following two methods can be called by clients to use a debugger to
    #  debug a statement, given as a string:
    #---------------------------------------------------------------------------

    def run ( self, cmd, globals = None, locals = None ):
        if globals is None:
            import __main__
            globals = __main__.__dict__

        if locals is None:
            locals = globals

        self.reset()
        sys.settrace( self.trace_dispatch )
        if not isinstance( cmd, types.CodeType ):
            cmd += '\n'

        try:
            try:
                exec cmd in globals, locals
            except BdbQuit:
                pass
        finally:
            self.quitting = 1
            sys.settrace( None )


    def runeval ( self, expr, globals = None, locals = None ):
        if globals is None:
            import __main__
            globals = __main__.__dict__

        if locals is None:
            locals = globals

        self.reset()
        sys.settrace( self.trace_dispatch )
        if not isinstance( expr, types.CodeType ):
            expr += '\n'

        try:
            try:
                return eval( expr, globals, locals )
            except BdbQuit:
                pass
        finally:
            self.quitting = 1
            sys.settrace( None )


    def runctx ( self, cmd, globals, locals ):
        # B/W compatibility
        self.run( cmd, globals, locals )


    # This method is more useful to debug a single function call:
    def runcall ( self, func, *args ):
        self.reset()
        sys.settrace( self.trace_dispatch )
        res = None
        try:
            try:
                res = func( *args )
            except BdbQuit:
                pass
        finally:
            self.quitting = 1
            sys.settrace( None )

        return res


    def canonic ( self, file_name ):
        if file_name == ("<" + file_name[1:-1] + ">"):
            return file_name

        canonic = self.fncache.get( file_name )
        if not canonic:
            canonic = os.path.abspath( file_name )
            canonic = os.path.normcase( canonic )
            self.fncache[ file_name ] = canonic

        return canonic


def set_trace ( ):
    Bdb().set_trace()

#-------------------------------------------------------------------------------
#  'Breakpoint' class:
#-------------------------------------------------------------------------------

class Breakpoint ( HasPrivateFacets ):

    #-- Class Constants --------------------------------------------------------

    # Indexed by file name:
    bp_list  = {}

    # Indexed by ( file_name, line_number ) tuple:
    bp_start = {}
    bp_map   = {}

    #-- Facet Definitions ------------------------------------------------------

    # The owner of this break point:
    owner = Any

    # The fully qualified name of the file the break point is in:
    file = File

    # The module name:
    module = Str

    # The source file path:
    path = Str

    # The line number the break point is on:
    line = Int

    # The ending line number the break point is on (used by 'Trace'):
    end_line = Int

    # Break point type:
    bp_type = BPType

    # Is the break point enabled:
    enabled = Bool( True )

    # Optional code associated with the break point:
    code = Str

    # The number of times the break point should be ignored before tripping:
    ignore = Int

    # The number of times the break point has been hit:
    hits = Int

    # The number of times this breakpoint has been counted:
    count = Int

    # Source line:
    source = Property

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object.
        """
        super( Breakpoint, self ).__init__( **facets )
        self.register()


    def register ( self ):
        """ Registers a break point.
        """
        Breakpoint.bp_list.setdefault( self.file, set() ).add( self )
        Breakpoint.bp_start.setdefault( ( self.file, self.line ),
                                        set() ).add( self )
        for i in xrange( self.line, self.end_line ):
            Breakpoint.bp_map.setdefault( ( self.file, i ), set() ).add( self )


    def source_for ( self, line ):
        """ Returns a specified source file line.
        """
        if self._source_file is None:
            try:
                self._source_file = read_file( self.file ).split( '\n' )
            except:
                self._source_file = []

        try:
            return self._source_file[ line - 1 ].strip()
        except:
            return '???'


    def __getstate__ ( self ):
        """ Returns the persistent state of a break point.
        """
        return self.get( 'file', 'line', 'bp_type', 'enabled', 'code',
                         'source', 'end_line' )

    #-- Property Implementations -----------------------------------------------

    def _get_source ( self ):
        if self._source is None:
            try:
                self._source = read_file( self.file ).split( '\n'
                                                 )[ self.line - 1 ].strip()
            except:
                self._source = '???'
        return self._source

    def _set_source ( self, source ):
        self._source = source

    #-- Facet Event Handlers ---------------------------------------------------

    def _anyfacet_set ( self, facet ):
        """ Handles any facet on the break point being changed.
        """
        if ((self.owner is not None ) and
            (facet in ( 'bp_type', 'enabled', 'code', 'ignore' ))):
            self.owner.modified = True


    def _file_set ( self ):
        """ Handles the 'file' facet being changed.
        """
        self.path, module = os.path.split( self.file )
        self.module       = os.path.splitext( module )[ 0 ]


    def _code_set ( self ):
        """ Handles the 'code' facet being changed.
        """
        self._code = None


    def _bp_type_set ( self ):
        """ Handles the 'bp_type' facet being changed.
        """
        self._code = None

    #-- Public Methods ---------------------------------------------------------

    def restore ( self ):
        """ Restores the correct line value based on current source file
            contents.
        """
        self._file_set()
        try:
            lines = read_file( self.file ).split( '\n' )
        except:
            return False

        n      = len( lines )
        line   = self.line - 1
        delta  = self.end_line - self.line
        source = self.source

        # Search outward from the last known location of the source for a
        # match:
        for i in range( 100 ):
            if ((line - i) < 0) and ((line + i) >= n):
                break

            j = line + i
            if (j < n) and (source == lines[j].strip()):
                self.line     = j + 1
                self.end_line = delta + j + 1
                self.register()

                return True

            j = line - i
            if (j >= 0) and (source == lines[j].strip()):
                self.line     = j + 1
                self.end_line = delta + j + 1
                self.register()

                return True

        # Indicate source line could not be found:
        self.line = 0

        return False


    def delete_me ( self ):
        """ Deletes the breakpoint.
        """
        value = Breakpoint.bp_list[ self.file ]
        value.remove( self )
        if not value:
            del Breakpoint.bp_list[ self.file ]

        index = ( self.file, self.line )
        value = Breakpoint.bp_start[ index ]
        value.remove( self )
        if not value:
            del Breakpoint.bp_start[ index ]

        bp_map = Breakpoint.bp_map
        for i in xrange( self.line, self.end_line ):
            index = ( self.file, i )
            value = bp_map[ index ]
            value.remove( self )
            if not value:
                del bp_map[ index ]

#-------------------------------------------------------------------------------
#  Returns whether there is an effective (active) breakpoint at this line of
#  code.
#-------------------------------------------------------------------------------

# Break points which perform an action but do not stop execution:
action_bp_types = ( 'Trace', 'Print', 'Log', 'Patch' )

last_file   = ''
last_line   = -1
last_locals = {}


def effective ( bps, line, frame ):
    """ Returns whether there is an effective (active) breakpoint at this line
        of code.
    """
    global last_file, last_line, last_locals

    result = False
    for bp in bps:
        if not bp.enabled:
            continue

        # Count every hit when bp is enabled:
        bp.hits += 1

        code    = bp.code.strip()
        bp_type = bp.bp_type
        if bp_type in action_bp_types:
            if bp_type == 'Trace':
                if bp.ignore <= 0:
                    if last_file != bp.file:
                        last_file   = bp.file
                        last_locals = {}
                        blank_line  = False
                        print '\n==== %s ====' % basename( last_file )
                    else:
                        blank_line = ( line != ( last_line + 1 ) )

                    locals = format_locals( frame.f_locals, last_locals )
                    if locals != '':
                        print locals

                    if blank_line:
                        print

                    print '[%s/%s] %s' % ( line, bp.hits,
                                           bp.source_for( line ).strip() )

                    last_locals = frame.f_locals.copy()
                    last_line   = line
                else:
                    bp.ignore -= 1
            else:
                last_file = ''
                if bp._code is None:
                    if code == '':
                        continue

                    if bp_type == 'Print':
                        code = "print %s, %s" % ( repr( code + ':' ), code )
                    elif bp_type == 'Log':
                        code = logger_template % ( code, code )

                    try:
                        bp._code = compile( code, '<string>', 'exec' )
                    except:
                        continue

                if bp.ignore <= 0:
                    try:
                        exec bp._code in frame.f_globals, frame.f_locals
                    except:
                        print ( 'Error executing break point code on line %d '
                               'in %s' % ( bp.line, bp.file ) )
                else:
                    bp.ignore -= 1

            continue

        if code == '':
            # If unconditional, and ignoring, go on to next, else break:
            if bp.ignore > 0:
                bp.ignore -= 1
                continue

            # If this is a counter, count it and continue:
            if bp_type == 'Count':
                bp.count += 1
                continue

            # Breakpoint and marker that's ok to delete if temporary:
            result = True
            continue

        # Conditional bp.
        # Ignore count applies only to those bpt hits where the condition
        # evaluates to true.
        if bp._code is None:
            try:
                bp._code = compile( code, '<string>', 'eval' )
            except:
                result = True
                continue

        try:
            val = eval( bp._code, frame.f_globals, frame.f_locals )
            if val:
                if bp.ignore <= 0:

                    # If this is a counter, count it and continue:
                    if bp_type == 'Count':
                        bp.count += 1
                        continue

                    result = True
                    continue

                bp.ignore -= 1
        except:
            # If eval fails, most conservative thing is to stop on breakpoint
            # regardless of ignore count.
            result = True

    return result

#-------------------------------------------------------------------------------
#  Formats a 'locals' dictionary for printing:
#-------------------------------------------------------------------------------

class NoMatch ( object ): pass
NoMatch = NoMatch()

def format_locals ( new_locals, old_locals ):
    show_locals = {}
    for name, value in new_locals.items():
        if value != old_locals.get( name, NoMatch ):
            show_locals[ name ] = value

    if len( show_locals ) == 0:
        return ''

    result = []
    names  = show_locals.keys()
    names.sort()
    max_len   = max( [ len( name ) for name in names ] ) + 2
    max_value = 72 - max_len
    for name in names:
        value = repr( show_locals[ name ] )
        if len( value ) > max_value:
            value = '%s...%s' % ( value[ : ( max_value + 1 ) / 2 ],
                                  value[ -( max_value / 2 ): ] )
        result.append( '    %s%s' % ( ( name + ':' ).ljust( max_len ), value ) )

    return '\n'.join( result )

#-- EOF ------------------------------------------------------------------------