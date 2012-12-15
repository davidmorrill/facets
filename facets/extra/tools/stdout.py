"""
Defines a tool for intercepting and displaying output sent to 'stdout'.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from facets.api \
    import HasPrivateFacets, Str, Any, Bool, Range, List, Property, Instance, \
           Button, View, VGroup, HGroup, Item, UItem, spring, GridEditor,     \
           ThemedCheckboxEditor, property_depends_on

from facets.ui.i_filter \
    import Filter

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.pyface.timer.api \
    import do_later, do_after

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The colors used to display stderr and stdout lines:
LineBGColors   = ( 0x91BFF9, 0xFFFFFF )
LineTextColors = ( 0x000000, 0x000000 )

#-------------------------------------------------------------------------------
#  'Writer' class:
#-------------------------------------------------------------------------------

class Writer ( HasPrivateFacets ):
    """ Handles output written to a file handle.
    """

    # Does this writer represent 'stdout' (True) or 'stderr' (False)?
    is_stdout = Bool

    # Reference to the owning 'Stdout' object:
    owner = Any

    # Original file handle this writer is intercepting:
    file = Any

    # The buffer used to accumulate text until complete lines are available:
    buffer = Str

    #-- File Interface ---------------------------------------------------------

    def write ( self, buffer ):
        """ Handles 'write' calls to the file.
        """
        if self.owner.passthru:
            self.file.write( buffer )

        self.buffer += buffer
        do_later( self._parse_lines )


    def flush ( self ):
        """ Handles 'flush' calls to the file.
        """
        if self.owner.passthru:
            self.file.flush()

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_set (self ):
        """ Handles the 'file' facet being changed.
        """
        self.buffer = ''

    #-- Public Methods ---------------------------------------------------------

    def _parse_lines ( self ):
        """ Attempt to parse the current buffer into one or more complete text
            lines and pass them over to the Stdout tool.
        """
        is_stdout = self.is_stdout
        lines     = self.buffer.split( '\n' )
        self.owner.add_lines( [( is_stdout, line ) for line in lines[:-1] ] )
        self.buffer = lines[-1]

#-------------------------------------------------------------------------------
#  'LinesFilter' class:
#-------------------------------------------------------------------------------

class LinesFilter ( Filter ):

    #-- Facet Definitions ------------------------------------------------------

    # String that any line must match on:
    match = Str

    # Is any case allowed in a match?
    any_case = Bool( True )

    # Event fired when the user wants to clear the match string:
    clear_match = Button( '@icons2:Delete' )

    # Is this a filter or a search?
    is_filter = Bool( True )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HGroup(
            Item( 'match',
                  show_label = False,
                  width      = 150
            ),
            UItem( 'any_case',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@icons:case_insensitive',
                       off_image   = '@icons:case_sensitive',
                       on_tooltip  = 'Use case insensitive matching',
                       off_tooltip = 'Use case sensitive matching' )
            ),
            UItem( 'clear_match',
                   tooltip = 'Clear the current match string'
            ),
        )
    )

    #-- IFilter Interface ------------------------------------------------------

    def filter ( self, line ):
        """ Returns whether a specified line object passes the filter.
        """
        match = self.match
        if match == '':
            return self.is_filter

        text = line[1]
        if self.any_case:
            return (text.lower().find( match.lower() ) >= 0)

        return (text.find( match ) >= 0)

    #-- Facet Event Handlers ---------------------------------------------------

    def _clear_match_set ( self ):
        """ Handles the 'clear_match' facet being changed.
        """
        self.match = ''

#-------------------------------------------------------------------------------
#  'LinesGridAdapter' class:
#-------------------------------------------------------------------------------

class LinesGridAdapter ( GridAdapter ):
    """ Grid adapter mapping from a list of lines to a grid editor.
    """

    columns = [ ( 'Lines', 'lines' ) ]

    grid_visible     = False
    font             = 'Courier 10'
    lines_bg_color   = Property
    lines_text_color = Property
    lines_content    = Property

    #-- Property Implementations -----------------------------------------------

    def _get_lines_bg_color ( self ):
        return LineBGColors[ self.item[0] ]


    def _get_lines_text_color ( self ):
        return LineTextColors[ self.item[0] ]


    def _get_lines_content ( self ):
        return self.item[1]


lines_grid_editor = GridEditor(
    adapter        = LinesGridAdapter,
    operations     = [],
    show_titles    = False,
    auto_scroll    = True,
    filter         = 'filter',
    search         = 'search',
    selection_mode = 'rows',
    selected       = 'selected'
)

#-------------------------------------------------------------------------------
#  'Stdout' class:
#-------------------------------------------------------------------------------

class Stdout ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Stdout'

    # The Writer objects used to handle output to stdout and stderr:
    stdout_writer = Instance( Writer )
    stderr_writer = Instance( Writer )

    # The reference to the original 'stdout' file handle:
    stdout = Any

    # The reference to the original 'stderr' file handle:
    stderr = Any

    # Are we currently intercepting output sent to 'stdout'?
    stdout_enabled = Bool( True, save_state = True )

    # Are we currently intercepting output sent to 'stderr'?
    stderr_enabled = Bool( False, save_state = True )

    # Are we passing thru all intercepted data to the original 'stdout/stderr':
    passthru = Bool( True, save_state = True )

    # Maximum number of lines to display:
    max_lines = Range( 1, 10000, 1000, save_state = True )

    # The current set of lines being displayed:
    lines = List

    # The current list of selected lines:
    selected = List

    # The current selected lines as a single string:
    selected_text = Property( connect = 'from' )

    # The filter to apply to the lines being displayed:
    filter = Instance( LinesFilter, () )

    # The search criteria to use:
    search = Instance( LinesFilter, { 'is_filter': False } )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        HGroup(
            Item( 'filter',
                  label = 'Filter',
                  style = 'custom'
            ),
            '_',
            Item( 'search',
                  label = 'Search',
                  style = 'custom'
            ),
            '_',
            spring
        ),
        Item( 'lines',
              show_label = False,
              editor     = lines_grid_editor
        )
    )

    options = View(
        VGroup(
            Item( 'stdout_enabled',
                  label   = 'Intercept stdout',
                  tooltip = 'Should output to stdout be interecepted?'
            ),
            Item( 'stderr_enabled',
                  label   = 'Intercept stderr',
                  tooltip = 'Should output to stderr be intercepted?'
            ),
            Item( 'passthru',
                  label   = 'Enable passthru',
                  tooltip = 'Should output be forwarded to the original '
                            'stdout/stderr?'
            ),
            Scrubber( 'max_lines',
                label = 'Maximum # of lines',
                width = 50
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- HasFacets Interface ----------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        # Make sure any needed standard file handle intercepters are in place:
        self._stdout_enabled_set()
        self._stderr_enabled_set()

    #-- Public Methods ---------------------------------------------------------

    def add_lines ( self, lines ):
        """ Add the specified list of lines to the view.
        """
        self.lines = (self.lines + lines)[ -self.max_lines: ]

    #-- Facets Default Values --------------------------------------------------

    def _stdout_writer_default ( self ):
        return Writer( is_stdout = True, owner = self )


    def _stderr_writer_default ( self ):
        return Writer( is_stdout = False, owner = self )

    #-- Facet Event Handlers ---------------------------------------------------

    def _stdout_enabled_set ( self ):
        """ Handles the 'stdout_enabled' facet being changed.
        """
        if self.stdout_enabled:
            self.stdout_writer.file, sys.stdout = sys.stdout, self.stdout_writer
        elif self.stdout_writer.file is not None:
            self.stdout_writer.file, sys.stdout = None, self.stdout_writer.file


    def _stderr_enabled_set ( self ):
        """ Handles the 'stderr_enabled' facet being changed.
        """
        if self.stderr_enabled:
            self.stderr_writer.file, sys.stderr = sys.stderr, self.stderr_writer
        elif self.stderr_writer.file is not None:
            self.stderr_writer.file, sys.stderr = None, self.stderr_writer.file


    def _max_lines_set ( self, max_lines ):
        """ Handles the 'max_lines' facet being changed.
        """
        do_after( 500, self._resynch_lines )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'selected' )
    def _get_selected_text ( self ):
        return '\n'.join( line[1] for line in self.selected )

    #-- Private Methods --------------------------------------------------------

    def _resynch_lines ( self ):
        """ Resets the current lines based upon the maximum number of lines
            allowed.
        """
        self.lines = self.lines[ -self.max_lines: ]

#-- EOF ------------------------------------------------------------------------