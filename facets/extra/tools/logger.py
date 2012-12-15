"""
Defines the Logger tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import logging

from facets.api \
    import HasPrivateFacets, Any, Enum, Instance, List, Range, Str, Color, \
           Property, View, VGroup, Item, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.api \
    import FilePosition

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from our Enum values to the logging module values:
LevelMap = {
    'Debug':    logging.DEBUG,
    'Info':     logging.INFO,
    'Warning':  logging.WARNING,
    'Error':    logging.ERROR,
    'Critical': logging.CRITICAL
}

# Formatters for formatting the various log record fields:
Formatters = {
    'name':       logging.Formatter( '%(name)s' ),
    'level_no':   logging.Formatter( '%(levelno)s' ),
    'level_name': logging.Formatter( '%(levelname)s' ),
    'path_name':  logging.Formatter( '%(pathname)s' ),
    'file_name':  logging.Formatter( '%(filename)s' ),
    'module':     logging.Formatter( '%(module)s' ),
    'line_no':    logging.Formatter( '%(lineno)s' ),
    'created':    logging.Formatter( '%(created)s' ),
    'asctime':    logging.Formatter( '%(asctime)s' ),
    'msecs':      logging.Formatter( '%(msecs)s' ),
    'thread':     logging.Formatter( '%(thread)s' ),
    'process':    logging.Formatter( '%(process)s' ),
    'message':    logging.Formatter( '%(message)s' )
}

#-------------------------------------------------------------------------------
#  'LogHandler' class:
#-------------------------------------------------------------------------------

class LogHandler ( logging.Handler ):

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, owner ):
        logging.Handler.__init__( self )
        self.owner = owner


    def emit ( self, record ):
        self.owner.emit( record )

#-------------------------------------------------------------------------------
#  Define the LRProperty facets:
#-------------------------------------------------------------------------------

def get_lr_field ( log_record, name ):
    return Formatters[ name ].format( log_record.log_record
           ).split( '\n' )[0].strip()

LRProperty = Property( get_lr_field )

#-------------------------------------------------------------------------------
#  'LogRecord' class:
#-------------------------------------------------------------------------------

class LogRecord ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The associated logging log record:
    log_record = Any

    # The name of the logger:
    name = LRProperty

    # Numeric logging level for the message
    level_no = LRProperty

    # Text logging level for the message
    level_name = LRProperty

    # Full path name of the source file where the logging call was issued:
    path_name = LRProperty

    # File name portion of path name:
    file_name = LRProperty

    # Module (name portion of the file name):
    module = LRProperty

    # Source line number where the logging call was issued:
    line_no = LRProperty

    # Time when the LogRecord was created (as returned by time.time()):
    created = LRProperty

    # Human-readable time when the LogRecord was created:
    asctime = LRProperty

    # Millisecond portion of the time when the LogRecord was created:
    msecs = LRProperty

    # Thread ID:
    thread = LRProperty

    # Process ID:
    process = LRProperty

    # The logged message, computed as msg % args:
    message = LRProperty

#-------------------------------------------------------------------------------
#  'LoggerGridAdapter' class:
#-------------------------------------------------------------------------------

class LoggerGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping logger data to a GridEditor.
    """

    columns = [
        ( 'Level',            'level_name' ),
        ( 'Logger Name',      'name'       ),
        ( 'Message',          'message'    ),
       #( 'Level #',          'level_no'   ),
       #( 'Path Name',        'path_name'  ),
       #( 'File Name',        'file_name'  ),
       #( 'Module',           'module'     ),
       #( 'Line #',           'line_no'    ),
       #( 'Raw Time Created', 'created'    ),
       #( 'Time Created',     'asctime'    ),
       #( 'Milliseconds',     'msecs'      ),
       #( 'Thread Id',        'thread'     ),
       #( 'Process Id',       'process'    ),
    ]

    # Selection Colors:
    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    # Column alignments:
    level_alignment    = Str( 'center' )
    level_no_alignment = Str( 'center' )
    line_no_alignment  = Str( 'center' )


logger_grid_editor = GridEditor(
    adapter    = LoggerGridAdapter,
    operations = [],
    selected   = 'selected'
)

#-------------------------------------------------------------------------------
#  'Logger' class:
#-------------------------------------------------------------------------------

class Logger ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Logger'

    # Maximum number of log messages displayed:
    max_records = Range( 1, 10000, 100, save_state = True )

    # Current logging level:
    logging_level = Enum( 'Debug', 'Info', 'Warning', 'Error', 'Critical',
                          save_state = True )

    # Log handler:
    log_handler = Instance( LogHandler )

    # Log record formatter:
    formatter = Instance( logging.Formatter, ( '%(levelname)s: %(message)s', ) )

    # Current selected log record:
    selected = Instance( LogRecord, allow_none = False )

    # The current set of log records:
    log_records = List( LogRecord )

    # Currently selected entries file position information:
    file_position = Instance( FilePosition,
                              draggable = 'Drag file position information',
                              connect   = 'from: file position' )

    # Currently selected entries associated traceback information:
    traceback = Str( connect = 'from: traceback text' )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'log_records',
              id         = 'log_records',
              show_label = False,
              editor     = logger_grid_editor
        ),
        id = 'facets.extra.tools.logger'
    )

    options = View(
        VGroup(
            Item( 'logging_level',
                  width = 100
            ),
            Item( 'max_records',
                  label = 'Max # log messages'
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the logger tool.
        """
        self.log_handler = LogHandler( self )
        self.log_handler.setLevel( LevelMap[ self.logging_level ] )
        root_logger = logging.getLogger()
        root_logger.addHandler( self.log_handler )

    #-- Facet Event Handlers ---------------------------------------------------

    def _logging_level_set ( self, logging_level ):
        """ Handles the 'logging_level' facet being changed.
        """
        self.log_handler.setLevel( LevelMap[ logging_level ] )


    def _max_records_set ( self, max_records ):
        """ Handles the 'max_records' facet being changed.
        """
        self.log_records = self.log_records[ -max_records: ]


    def _selected_set ( self, record ):
        """ Handles a new log record being selected.
        """
        log_record         = record.log_record
        self.file_position = FilePosition( file_name = log_record.pathname,
                                           line      = log_record.lineno )
        msg = self.formatter.format( log_record )
        col = msg.find( '\n' )
        if col >= 0:
            self.traceback = msg[ col + 1: ]


    def emit ( self, log_record ):
        """ Handles a log record being emitted.
        """
        if len( self.log_records ) >= self.max_records:
            del self.log_records[0]

        self.log_records.append( LogRecord( log_record = log_record ) )

#-- EOF ------------------------------------------------------------------------