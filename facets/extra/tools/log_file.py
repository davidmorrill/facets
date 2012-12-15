"""
Display log messages gleaned from a log file plugin.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from threading \
    import Thread

from time \
    import sleep

from facets.api \
    import HasPrivateFacets, Any, Enum, Instance, List, Range, Str, Float, \
           File, Delegate, Button, View, HGroup, Item, GridEditor, CodeEditor, \
           FileEditor, spring

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.i_filter \
    import Filter

from facets.extra.features.api \
    import DropFile

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The standard log types:
LogTypes = set( [ 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' ] )

# Mapping of LogRecord types to cell background and text colors:
CellColorMap = {
    'Debug':    ( 255, 255, 255 ),
    'Info':     ( 255, 255, 255 ),
    'Warning':  (   0, 255,   0 ),
    'Error':    ( 255,   0,   0 ),
    'Critical': ( 255,   0,   0 ),
}

TextColorMap = {
    'Debug':    (   0,   0,   0 ),
    'Info':     (   0,   0,   0 ),
    'Warning':  (   0,   0,   0 ),
    'Error':    ( 255, 255, 255 ),
    'Critical': ( 255, 255, 255 )
}

# Mapping from log type to log level:
LogLevel = {
    'Debug':    0,
    'Info':     1,
    'Warning':  2,
    'Error':    3,
    'Critical': 4
}

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

LogType = Enum( 'Debug', 'Info', 'Warning', 'Error', 'Critical' )

#-------------------------------------------------------------------------------
#  Popup views used by the GridEditor:
#-------------------------------------------------------------------------------

extra_view = View(
    Item( 'extra',
          style      = 'readonly',
          show_label = False,
          editor     = CodeEditor()
    ),
    kind       = 'popup',
    id         = 'facets.extra.tools.log_file.extra',
    width      = 0.40,
    height     = 0.30,
    resizable  = True,
    scrollable = True
)

#-------------------------------------------------------------------------------
#  'LogFileGridAdapter' class:
#-------------------------------------------------------------------------------

class LogFileGridAdapter ( GridAdapter ):
    """ Adapts LogRecord objects for display in a GridEditor.
    """

    columns = [
        ( 'Type', 'type' ),
        ( 'Date', 'date' ),
        ( 'Time', 'time' ),
        ( 'Info', 'info' )
    ]
    can_edit       = False

    type_width     = Float( 0.10 )
    date_width     = Float( 0.15 )
    time_width     = Float( 0.15 )
    info_width     = Float( 0.60 )

    type_alignment = Str( 'center' )
    date_alignment = Str( 'center' )
    time_alignment = Str( 'center' )

    info_clicked   = Any( extra_view )

    def type_bg_color ( self ):
        return CellColorMap[ self.item.type ]

    def type_text_color ( self ):
        return TextColorMap[ self.item.type ]

#-------------------------------------------------------------------------------
#  'LogFilter' class:
#-------------------------------------------------------------------------------

class LogFilter ( Filter ):

    #-- Facet Definitions ------------------------------------------------------

    # The current logging level:
    logging_level = LogType

    #-- Filter Method Overrides ------------------------------------------------

    def filter ( self, object ):
        """ Returns whether a specified object meets the filter criteria.
        """
        return (LogLevel[ object.type ] >= LogLevel[ self.logging_level ])

#-------------------------------------------------------------------------------
#  'LogRecord' class:
#-------------------------------------------------------------------------------

class LogRecord ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The type of the log record:
    type = LogType

    # The data on which the log record was created:
    date = Str

    # The time at which the log record was created:
    time = Str

    # The information associated with the log record:
    info = Str

    # The extra (expanded) information associated with the log record:
    extra = Str

#-------------------------------------------------------------------------------
#  'LogFile' class:
#-------------------------------------------------------------------------------

class LogFile ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'LogFile', transient = True )

    # The persistence id for this object:
    id = Str( 'facets.extra.tools.log_file.state',
              save_state_id = True, transient = True )

    # The name of the log file being processed:
    file_name = File( drop_file = DropFile( extensions = [ '.log' ],
                                      tooltip = 'Drop a log file to display.' ),
                      connect   = 'to', transient = True )

    # The current logging level being displayed:
    logging_level = Delegate( 'log_filter', modify = True )

    # Maximum number of log messages displayed:
    max_records = Range( 1, 10000, 10000, save_state = True )

    # The log record filter:
    log_filter = Instance( LogFilter, (), save_state = True )

    # The current set of log records:
    log_records = List( LogRecord, transient = True )

    # Button used to clear all current log records:
    clear = Button( 'Clear' )

    #-- Private Facets ---------------------------------------------------------

    _lines = Any( [] )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        HGroup(
            Item( 'file_name',
                  id      = 'file_name',
                  springy = True,
                  editor  = FileEditor( entries = 10 )
            ),
            '_',
            Item( 'logging_level' ),
        ),
        '_',
        Item( 'log_records',
              id         = 'log_records',
              show_label = False,
              editor     = GridEditor( adapter = LogFileGridAdapter,
                                       filter  = 'log_filter' )
        ),
        '_',
        HGroup(
            spring,
            Item( 'clear', show_label = False )
        ),
        title     = 'Log File',
        id        = 'facets.extra.tools.log_file',
        width     = 0.6,
        height    = 0.5,
        resizable = True
    )

    #-- 'object' Method Overrides ----------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object and starts the background log processing
            thread running.
        """
        self._start_thread()

        super( LogFile, self ).__init__( **facets )

    #-- HasFacets Method Overrides ---------------------------------------------

    def copyable_facet_names ( self, **metadata ):
        """ Returns the list of facet names to copy or clone by default.
        """
        return [ 'log_filter', 'max_records' ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _clear_set ( self ):
        """ Handles the 'Clear' button being clicked.
        """
        self.log_records = []

    #-- Private Methods --------------------------------------------------------

    def _start_thread ( self ):
        """ Starts the background log processing thread running.
        """
        thread = Thread( target = self._process_log )
        thread.setDaemon( True )
        thread.start()


    def _process_log ( self ):
        """ Processes the current log file.
        """
        file_name = ''
        fh        = None
        while True:
            if file_name != self.file_name:
                file_name = self.file_name

                try:
                    if fh is not None:
                        fh.close()
                except:
                    pass

                fh   = None
                data = ''
                self.log_records = []
                try:
                    fh = open( file_name, 'rb' )
                except:
                    pass

            if fh is not None:
                new_data = fh.read()
                if new_data == '':
                    continue

                data += new_data
                col   = data.rfind( '\n' )
                if col < 0:
                    continue

                self._lines.extend( data[ : col ].split( '\n' ) )
                data = data[ col + 1: ].lstrip()

                records = []
                while True:
                    record = self._next_record()
                    if record is None:
                        break

                    records.insert( 0, record )

                if len( records ) > 0:
                    self.log_records = \
                        (records + self.log_records)[ : self.max_records ]

            sleep( 1 )


    def _next_record ( self ):
        """ Returns the next LogRecord or None if no complete log record is
            found.
        """
        lines = self._lines
        if len( lines ) == 0:
            return None

        type, date_time, info = lines[0].split( '|', 2 )
        type       = type.capitalize()
        date, time = date_time.split()
        info       = info.strip()
        extra      = ''
        for i in range( 1, len( lines ) ):
            line = lines[ i ]
            col  = line.find( '|' )
            if (col > 0) and (line[ : col ] in LogTypes):
                extra = '\n'.join( lines[ 1: i ] )
                del lines[ 0: i ]
                break
        else:
            return None

        return LogRecord( type  = type, date = date, time = time, info = info,
                          extra = extra )

    #-- Facet Event Handlers ---------------------------------------------------

    def _max_records_set ( self, max_records ):
        """ Handles the 'max_records' facet being changed.
        """
        self.log_records = self.log_records[ -max_records: ]

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    if len( sys.argv ) != 2:
        print 'Usage is: log_file log_file_name'

        sys.exit( 1 )

    file_name = sys.argv[1]
    view      = LogFile( file_name = file_name )
    view.edit_facets( filename = 'log_file.cfg' )

#-- EOF ------------------------------------------------------------------------