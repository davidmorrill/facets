"""
Defines the FBIViewer tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Any, Int, Str, Code, List, Range, Button, \
           Instance, Bool, Constant, View, VGroup, HToolbar, Item,     \
           NotebookEditor, CodeEditor

from facets.core.facet_base \
    import read_file

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.features.api \
    import DropFile

from facets.extra.api \
    import FilePosition

from facets.extra.helper.fbi \
    import FBI

from facets.extra.helper.themes \
    import TTitle, TButton

from facets.extra.helper.bdb \
    import BPType

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Editor selection color:
SelectionColor = 0xFBD391

#-------------------------------------------------------------------------------
#  'FBIViewer' class:
#-------------------------------------------------------------------------------

class FBIViewer ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'FBI Viewer'

    # Maximum number of open viewers allowed:
    max_viewers = Range( 1, 50, 3, mode = 'spinner', save_state = True )

    # The current item being inspected:
    file_position = Instance( FilePosition,
                     drop_file  = DropFile(
                     extensions = [ '.py' ],
                     tooltip    = 'Drop a Python file or file position here.' ),
                     connect    = 'to:file position' )

    # Current list of source files being viewed:
    viewers = List

    # The currently selected viewer:
    selected = Any # Instance( AnFBIViewer )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'viewers@',
              show_label = False,
              editor     = NotebookEditor( deletable  = True,
                                           page_name  = '.name',
                                           export     = 'DockWindowShell',
                                           selected   = 'selected',
                                           dock_style = 'auto' )
        )
    )

    options = View(
        VGroup(
            Scrubber( 'max_viewers', label = 'Maximum number of open viewers' ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _max_viewers_set ( self, max_viewers ):
        """ Handles the 'max_viewers' facet being changed.
        """
        delta = len( self.viewers ) - max_viewers
        if delta > 0:
            del self.viewers[ : delta ]


    def _file_position_set ( self, file_position ):
        """ Handles the 'file_position' facet being changed.
        """
        if file_position is not None:
            # Reset the current file position to None, so we are ready for a
            # new one:
            do_later( self.set, file_position = None )

            viewers = self.viewers
            for i, viewer in enumerate( viewers ):
                if ((file_position.name      == viewer.name)      and
                    (file_position.file_name == viewer.file_name) and
                    (file_position.lines     == viewer.lines)     and
                    (file_position.object    == viewer.object)):

                    viewer.selected_line = file_position.line
                    self.selected        = viewer

                    return

            # Create the viewer:
            viewer = AnFBIViewer(
                         **file_position.get( 'name', 'file_name', 'line',
                                              'lines', 'object' ) )

            # Make sure the # of viewers doesn't exceed the maximum allowed:
            if len( viewers ) >= self.max_viewers:
                del viewers[0]

            # Add the new viewer to the list of viewers (which will cause it to
            # appear as a new notebook page):
            viewers.append( viewer )

#-------------------------------------------------------------------------------
#  'AnFBIViewer' class:
#-------------------------------------------------------------------------------

class AnFBIViewer ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # Reference to the FBI debugger context:
    fbi = Constant( FBI() )

    # The viewer page name:
    name = Str

    # The name of the file being viewed:
    file_name = Str( draggable = 'Drag the file name.' )

    # The starting line number:
    line = Int

    # The number of lines (start at 'line'):
    lines = Int( -1 )

    # The number of lines of text in the view:
    nlines = Int

    # The object associated with this view:
    object = Any

    # The title of this view:
    title = Str

    # Should the break point trigger only for the specified object:
    object_only = Bool( False )

    # Type of breakpoint to set:
    bp_type = BPType

    # The condition the break point should trigger on:
    condition = Str

    # The currently selected line:
    selected_line = Int

    # The current cursor position:
    cursor = Int( -1 )

    # The list of lines with break points:
    bp_lines = List( Int )

    # The logical starting line (used to adjust lines passed to the FBI):
    starting_line = Int

    # Fired when a breakpoint is to be set:
    bp_set = Button( 'Set' )

    # Fired when a breakpoint is to be reset:
    bp_reset = Button( 'Reset' )

    # Does the current line have any breakpoints set on it:
    has_bp = Bool( False )

    # The source code being viewed:
    source = Code

    # The FBI module this file corresponds to:
    module = Any

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            TTitle( 'title' ),
            HToolbar(
                Item( 'object_only',
                      label        = 'This object only',
                      enabled_when = 'object.object is not None'
                ),
                Item( 'bp_type',   label = 'Type' ),
                Item( 'condition', width = 100, springy = True ),
                TButton( 'bp_set',
                         label        = 'Set',
                         enabled_when = "(bp_type != 'Trace') or "
                                        "(condition.strip() != '')"
                ),
                TButton( 'bp_reset',
                         label        = 'Reset',
                         enabled_when = 'has_bp'
                ),
                id = 'toolbar'
            ),
            Item( 'source',
                  editor = CodeEditor( selected_line = 'selected_line',
                                       line          = 'cursor',
                                       mark_lines    = 'bp_lines',
                                       mark_color    = SelectionColor,
                                       auto_scroll   = False )
            ),
            show_labels = False
        ),
        id = 'facets.extra.tools.fbi_viewer.AnFBIViewer'
    )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, **facets ):
        """ Initializes the object.
        """
        super( AnFBIViewer, self ).__init__( **facets )

        source = read_file( self.file_name )
        if source is not None:
            text   = source.split( '\n' )
            nlines = self.lines
            if nlines >= 0:
                self.nlines = nlines
                line        = self.line - 1
                source      = '\n'.join( text[ line: line + nlines ] )
                self.line   = 1
                self.starting_line = line
            else:
                self.nlines = len( text )

            self.selected_line = self.cursor = self.line
            self.source        = source

            self.module = self.fbi.get_module( self.file_name )
            self.module.on_facet_set( self.update_viewer, 'bp_lines[]' )

            title  = self.file_name
            object = self.object
            if object is not None:
                title += '     Object: %s(0x%08X)' % (
                         object.__class__.__name__, id( object ) )
            self.title = title

            self.update_viewer()


    def update_viewer ( self ):
        """ Updates the viewer when the current set of breakpoint lines changes.
        """
        n        = self.nlines
        sline    = self.starting_line
        bp_lines = [ i - sline
                     for i in self.fbi.break_point_lines( self.file_name ) ]
        self.bp_lines = [ i for i in bp_lines if 0 <= i <= n ]
        self._cursor_set()

    #-- Facet Event Handlers ---------------------------------------------------

    def _cursor_set ( self ):
        """ Handles the user selecting a new line.
        """
        self.has_bp = (self.cursor in self.bp_lines)
        self.selected_line = self.cursor


    def _bp_set_set ( self ):
        """ Handles the 'Set' breakpoint button being clicked.
        """
        condition = self.condition.strip()
        if self.object_only:
            self_check = ('id(self) == %d' % id( self.object ))
            if condition != '':
                condition = '(%s) and (%s)' % ( condition, self_check )
            else:
                condition = self_check

        self.fbi.add_break_point(
            self.file_name, self.cursor + self.starting_line, self.bp_type,
            condition )


    def _bp_reset_set ( self ):
        """ Handles the 'Reset' breakpoint button being clicked.
        """
        self.fbi.remove_break_point( self.file_name,
                                     self.cursor + self.starting_line )

#-- EOF ------------------------------------------------------------------------