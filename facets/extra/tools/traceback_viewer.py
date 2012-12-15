"""
Views the contents of a Python traceback.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re
import sys

from os.path \
    import basename, dirname, exists, join, split, normpath, isdir, isfile

from facets.api \
    import HasPrivateFacets, File, Int, List, Code, Instance, Str, Any, \
           Property, View, Item, GridEditor, toolkit, on_facet_set

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.features.api \
    import CustomFeature

from facets.extra.api \
    import FilePosition

from facets.extra.helper.themes \
    import TTitle

from facets.ui.pyface.timer.api \
    import do_later

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

file_pat       = re.compile( r'^\s*File "(.*?)", line\s*(\d*),\s*in\s*(.*)' )
file_begin_pat = re.compile( r'^\s*File "' )

#-------------------------------------------------------------------------------
#  'TracebackEntry' class:
#-------------------------------------------------------------------------------

class TracebackEntry ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The file associated with the traceback entry:
    file_name = File

    # The base file name (minus path):
    base_name = Property

    # The file name path:
    path_name = Property

    # The line number within the file:
    line = Int

    # The source code line:
    source = Code

    # The function/method name:
    name = Str

    #-- Property Implementations -----------------------------------------------

    def _get_base_name ( self ):
        return basename( self.file_name )


    def _get_path_name ( self ):
        return dirname( self.file_name )

#-------------------------------------------------------------------------------
#  'TracebackGridAdapter' class:
#-------------------------------------------------------------------------------

class TracebackGridAdapter ( GridAdapter ):
    """ Grid adapter for the Traceback tool.
    """

    columns = [
        ( 'Caller', 'name' ),
        ( 'Source', 'source' ),
        ( 'Line',   'line' ),
        ( 'File',   'base_name' ),
        ( 'Path',   'path_name' ),
    ]

    # Column alignments:
    line_alignment = Str( 'center' )


traceback_grid_editor = GridEditor(
    adapter    = TracebackGridAdapter,
    selected   = 'selected',
    operations = []
)

#-------------------------------------------------------------------------------
#  'TracebackViewer' class:
#-------------------------------------------------------------------------------

class TracebackViewer ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Traceback Viewer' )

    feature = CustomFeature(
        image   = '@facets:clipboard',
        click   = 'paste_traceback',
        tooltip = 'Click to paste traceback'
    )

    # Connectable form of traceback information:
    buffer = Str( connect = 'to: traceback text' )

    # The exception that occurred:
    exception = Str

    # The current traceback being processed:
    traceback = List( TracebackEntry )

    # The currently selected traceback item:
    selected = Instance( TracebackEntry, allow_none = False )

    # The file position within the currently selected traceback file:
    file_position = Instance( FilePosition,
                        connect   = 'from: file position',
                        draggable = 'Drag current traceback file position.' )

    # The original value of sys.stderr:
    stderr = Any

    #-- Private Facets ---------------------------------------------------------

    # The buffer used to accumulate 'stderr' text into:
    error_buffer = Str

    # The list of all valid sys.path entries:
    sys_path = Any

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        TTitle( 'exception' ),
        Item( 'traceback',
              id         = 'traceback',
              show_label = False,
              editor     = traceback_grid_editor
        ),
        id = 'facets.extra.tools.traceback_viewer'
    )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object.
        """
        super( TracebackViewer, self ).__init__( **facets )

        self.stderr, sys.stderr = sys.stderr, self


    def write ( self, buffer ):
        """ Handles 'write' calls to stderr.
        """
        self.stderr.write( buffer )
        self.error_buffer += buffer


    def flush ( self ):
        """ Handles 'flush' calls to stderr.
        """
        self.stderr.flush()


    def paste_traceback ( self, buffer = None ):
        """ Handles the 'paste_traceback' event being fired.
        """
        if buffer is None:
            buffer = toolkit().clipboard().text

        lines = buffer.replace( '\r\n', '\n' ).replace(
                                '\r', '\n' ).split( '\n' )
        hits  = [ i for i, line in enumerate( lines )
                    if file_begin_pat.match( line ) is not None ]

        n = len( lines )
        if (n > 0) and (len( lines[-1] ) > 0) and (lines[-1][:1] != ' ' ):
            hits.append( n - 1 )

        for i in range( len( hits ) - 1 ):
            h1, h2 = hits[ i: i + 2 ]
            for j in range( h1 + 1, h2 - 1 ):
                lines[ h1 ] += lines[ j ]
                lines[ j ]   = ''

        lines = [ line for line in lines if line != '' ]

        got_match = False
        i         = 0
        n         = len( lines )
        entries   = []
        exception = 'Unknown Exception'
        while i < n:
            match = file_pat.match( lines[ i ] )
            if match is not None:
                got_match = True
                entries.append( TracebackEntry(
                    file_name = self._check_file( match.group( 1 ) ),
                    line      = int( match.group( 2 ) ),
                    name      = match.group( 3 ),
                    source    = lines[ i + 1 ].strip()
                ) )
                i += 2
            elif got_match:
                exception = lines[ i ].strip()
                break
            else:
                i += 1

        self.exception = exception
        self.traceback = entries

    #-- Private Methods --------------------------------------------------------

    def _process_error_buffer ( self ):
        """ Process all data written to 'stderr' that has been accumulated in
            the 'error_buffer'.
        """
        if len( self.error_buffer ) > 0:
            header = 'Traceback (most recent call last):'
            chunks = self.error_buffer.split( header )
            self.error_buffer = ''
            if len( chunks ) >= 2:
                self.paste_traceback( header + chunks[1] )


    def _check_file ( self, file_name ):
        """ Returns the 'checked' version of the specified file name. In the
            case of a traceback that has been pasted into the tool, that data
            may have originated on another system with a different pythonpath,
            so the file may not exist locally. This method attempts to adjust
            such a file, if possible. If the specified file cannot be found
            locally, the original file name is returned.
        """
        if not exists( file_name ):
            fn, base_name = split( normpath( file_name ) )
            paths         = [ '' ]
            while True:
                fn, path = split( fn )
                if path == '':
                    break

                paths.insert( 0, join( path, paths[0] ) )

            for sys_path in self.sys_path:
                for path in paths:
                    fn = join( sys_path, path, base_name )
                    if (isfile( fn ) and ((path == '') or
                        (isfile( join( sys_path, path, '__init__.py' ) )))):
                        return fn

        return file_name

    #-- Facets Default Values --------------------------------------------------

    def _sys_path_default ( self ):
        return [ path for path in sys.path if isdir( path ) ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _buffer_set ( self, buffer ):
        """ Handles the 'buffer' facet being changed.
        """
        self.paste_traceback( buffer )


    def _selected_set ( self, entry ):
        """ Handles a new traceback entry being selected.
        """
        self.file_position = FilePosition( file_name = entry.file_name,
                                           line      = entry.line )


    @on_facet_set( 'error_buffer', dispatch = 'ui' )
    def _error_buffer_modified ( self ):
        """ Handles new data being written to 'stderr' by making sure that it
            gets processed in the future by the UI thread. We don't process it
            now because the data for a traceback tends to get written in small
            chunks. Deferring it should allow for all of the data to be
            accumulated in the 'error_buffer' before being processed'
        """
        do_later( self._process_error_buffer )

#-- EOF ------------------------------------------------------------------------