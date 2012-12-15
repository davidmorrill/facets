"""
Defines a Breakpoints tool for creating and managing program breakpoints used
while debugging an application.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import join

from facets.api \
    import SingletonHasPrivateFacets, Any, List, Str, Instance, Bool, Event, \
           Color, View, Item, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.features.api \
    import CustomFeature

from facets.extra.helper.file_position \
    import FilePosition

from facets.extra.helper.bdb \
    import Breakpoint

#-------------------------------------------------------------------------------
#  'BreakpointsGridAdapter' class:
#-------------------------------------------------------------------------------

class BreakpointsGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping breakpoints tool data to the GridEditor.
    """

    columns = [
        ( 'Module',    'module'   ),
        ( 'Line',      'line'     ),
        ( 'BP Type',   'bp_type'  ),
        ( 'Condition', 'code'     ),
        ( 'Enabled',   'enabled'  ),
        ( 'Hits',      'hits'     ),
        ( 'Count',     'count'    ),
        ( 'Ignore',    'ignore'   ),
        ( 'Source',    'source'   ),
#       ( 'File',      'file'     ),
#       ( 'Path',      'path'     ),
#       ( 'End Line',  'end_line' ),
    ]

    # Define selection colors:
    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    # Define editable columns:
    can_edit         = Bool( False )
    bp_type_can_edit = Bool( True )
    code_can_edit    = Bool( True )
    ignore_edit      = Bool( True )

    # Define column alignments:
    line_alignment    = Str( 'center' )
    bp_type_alignment = Str( 'center' )
    enabled_alignment = Str( 'center' )
    hits_alignment    = Str( 'center' )
    count_alignment   = Str( 'center' )
    ignore_alignment  = Str( 'center' )


bp_grid_editor = GridEditor(
    adapter    = BreakpointsGridAdapter,
    operations = [ 'edit', 'delete', 'sort' ],
    selected   = 'selected'
)

#-------------------------------------------------------------------------------
#  'Breakpoints' class:
#-------------------------------------------------------------------------------

class Breakpoints ( SingletonHasPrivateFacets ):

    #-- Public Facet Definitions -----------------------------------------------

    # The name of the tool:
    name = Str( 'Breakpoints' )

    # Reference to the FBI debugger context:
    fbi = Any # Constant( FBI() )

    # The list of currently defined break points:
    break_points = List( Breakpoint )

    # The currently selected break points:
    selected = Instance( Breakpoint )

    # Fired when user wants to restore all saved break points:
    restore_bp = CustomFeature(
        image   = '@facets:fbi_restore_bp',
        click   = 'restore',
        tooltip = 'Click to restore all saved break points.'
    )

    # Clear all current break points:
    clear_bp = CustomFeature(
        image   = '@facets:fbi_clear_bp',
        enabled = False,
        click   = 'clear',
        tooltip = 'Click to clear all break points.'
    )

    # Have break points been restored yet?
    restored = Bool( False )

    # Fired when a break point has been modified:
    modified = Event

    # The file position of the currently selected break point:
    file_position = Instance( FilePosition,
                    connect   = 'from:file position',
                    draggable = "Drag the current break point's file position" )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        Item( 'break_points',
              show_label = False,
              editor     = bp_grid_editor
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def clear ( self ):
        """ Handles the user requesting that all break points be cleared.
        """
        del self.break_points[:]


    def restore ( self ):
        """ Restores all previously saved break points.
        """
        if not self.restored:
            self.restored           = True
            self.restore_bp.enabled = False
            bps = [ bp for bp in self.facet_db_get(
                       'facets.extra.tools.breakpoints.state', [] )
                    if bp.restore() ]
            self._no_save = True
            self.break_points.extend( bps )
            self._no_save = False

            fbi = self.fbi
            bdb = fbi.bdb
            for bp in bps:
                bdb.restore_break( bp )
                fbi.mark_bp_at( bp )


    def save ( self ):
        """ Persists all of the current break points.
        """
        # Merge in any previously saved break points (if necessary):
        self.restore()

        # Now save out all current break points:
        self.facet_db_set( 'facets.extra.tools.breakpoints.state',
                           self.break_points[:] )


    def add ( self, *bps ):
        """ Adds a list of break points.
        """
        self.break_points.extend( bps )


    def remove ( self, *bps ):
        """ Removes a list of break points.
        """
        break_points = self.break_points[:]
        for bp in bps:
            break_points.remove( bp )

        self.break_points = break_points


    def remove_temporaries_for ( self, frame ):
        """ Removes any temporary break points for the specified frame.
        """
        bps    = self.get_break_points_for( frame, frame.line )
        delete = [ i for i, bp in bps if bp.bp_type == 'Temporary' ]
        if len( delete ) > 0:
            delete.sort( lambda l, r: cmp( r, l ) )
            for i in delete:
                del self.break_points[ i ]


    def get_break_points_for ( self, frame, line ):
        """ Returns the break point (if any) at a specified frame line.
        """
        file   = self.fbi.canonic( join( frame.file_path, frame.file_name ) )
        result = []
        for i, bp in enumerate( self.break_points ):
            if (file == bp.file) and (line == bp.line):
                result.append( ( i, bp ) )

        return result


    def check_bps ( self ):
        """ Check the status of any features.
        """
        self.clear_bp.enabled = (len( self.break_points ) > 0)
        do_later( self.save )

    #-- Facet View Definitions -------------------------------------------------

    def _fbi_default ( self ):
        from facets.extra.helper.fbi import FBI

        return FBI()

    #-- Facet Event Handlers ---------------------------------------------------

    def _break_points_set ( self, bps ):
        """ Handles the 'break_points' facet being changed.
        """
        for bp in bps:
            bp.owner = self

        self.check_bps()


    def _break_points_items_set ( self, event ):
        """ Handles the 'break_points' facet being changed.
        """
        for bp in event.added:
            bp.owner = self

        fbi = self.fbi
        bdb = fbi.bdb
        for bp in event.removed:
            bdb.clear_bp( bp )
            if len( bdb.get_breaks( bp.file, bp.line ) ) == 0:
                fbi.get_module( bp.file ).bp_lines.remove( bp.line )

        self.check_bps()


    def _modified_set ( self ):
        """ Handles the 'modified' facet being changed.
        """
        self.check_bps()


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if selected is not None:
            self.file_position = FilePosition( file_name = selected.file,
                                               line      = selected.line )

#-- EOF ------------------------------------------------------------------------