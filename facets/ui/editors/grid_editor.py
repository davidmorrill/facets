"""
A facets UI editor for editing gridable data (arrays, list of tuples, lists
of objects, etc).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Int, Enum, List, Bool, Instance, Any, Tuple, Dict, Callable,  \
           Either, Property, Event, Editor, BasicEditorFactory, on_facet_set, \
           property_depends_on

from facets.ui.i_filter \
    import IFilter

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.constants \
    import LEFT, CENTER, RIGHT

from facets.ui.pen \
    import Pen

from facets.ui.pyface.timer.api \
    import do_later, do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Selection modes that imply multiple items can be selected:
MultipleModes = ( 'rows', 'columns', 'cells' )
RowModes      = ( 'row', 'rows' )

# Spacing used between text, images and cell edges:
Spacing = 4

# Image alignment is relative to the cell (otherwise relative to the text):
CELL = 0x80

# Mapping from grid adapter horizontal alignment values to bit mask values:
AlignmentMap = {
    'default':     LEFT,
    'left':        LEFT,
    'right':       RIGHT,
    'center':      CENTER,
    'text left':   LEFT,
    'text right':  RIGHT,
    'cell left':   CELL | LEFT,
    'cell right':  CELL | RIGHT,
    'cell center': CELL | CENTER
}

#-------------------------------------------------------------------------------
#  '_GridEditor' class:
#-------------------------------------------------------------------------------

class _GridEditor ( Editor ):
    """ A facets UI editor for editing gridable data (arrays, list of tuples,
        lists of objects, etc).
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the grid editor scrollable? This value overrides the default.
    scrollable = True

    # Is the value of the editor a list whose content changes should be handled
    # by the 'update_editor' method?
    is_list = True

    # The current set of selected items:
    #selected = Any/List

    # The current set of selected item indices:
    #selected_indices = Any/List

    # The (optional) IFilter object used to filter the data:
    filter = Instance( IFilter )

    # The item index to use when invoking the filter:
    filter_index = Int( 1 )

    # The (optional) IFilter object used to search for user-specified items in
    # the data:
    search = Instance( IFilter )

    # The item index to use when invoking the search filter:
    search_index = Int( 1 )

    # The adapter from facet values to editor values:
    grid_adapter = Instance( GridAdapter )

    # Event fired when the editor data has been modified in a way that affects
    # the operation of the editor:
    changed = Event

    # The sorting function to use for sorting (a value of None means the data is
    # not being sorted):
    sorter = Callable

    # Is the data being sorted in ascending order (if 'sorter' is not None)?
    sort_ascending = Bool( True )

    # Are screen space rows being mapped into data space rows?
    mapping = Property

    # The mapping from screen space rows to data space rows:
    mapped_rows = Property

    # The mapping from data space rows to screen rows:
    screen_rows = Property

    # The current number of (screen space) rows:
    rows = Property

    # The maximum row height requested:
    height = Int

    # Number of active in-cell editing operations:
    editing = Int

    # Is there an editor update pending?
    update_pending = Bool( False )

    # The set of supported grid editing operations:
    operations = Any # Set

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory         = self.factory
        selection_mode  = factory.selection_mode
        self._themes    = set()
        self.operations = set( factory.operations )

        # Define the selection facets based upon the specified selection mode:
        is_list = (selection_mode in MultipleModes)
        if is_list:
            self.add_facet( 'selected',         List )
            self.add_facet( 'selected_indices', List )
        else:
            self.add_facet( 'selected',         Any )
            self.add_facet( 'selected_indices', Any )

        # Set up the adapter to use:
        adapter = factory.adapter
        if not isinstance( adapter, GridAdapter ):
            adapter = adapter(
                grid_editor = self,
                object      = self.object,
                name        = self.name
            )
        else:
            adapter.set(
                grid_editor = self,
                object      = self.object,
                name        = self.name
            )

        self.grid_adapter = adapter

        # Create and initialize the control:
        self.gui_create_control( parent )

        # Set up the control's toolkit neutral event handlers:
        self.adapter.set_event_handler(
            size         = self._size_modified,
            key_press    = self._key_pressed,
            left_down    = self._left_down,
            left_up      = self._left_up,
            left_dclick  = self._left_dclick,
            right_down   = self._right_down,
            right_up     = self._right_up,
            right_dclick = self._right_dclick,
            motion       = self._motion
        )

        # Set up the selection listeners (if necessary):
        self.sync_value( factory.selected, 'selected', 'both',
                         is_list = is_list )
        self.sync_value( factory.selected_indices, 'selected_indices', 'both',
                         is_list = is_list )

        # Set up the data and search filters:
        self.sync_value( factory.filter, 'filter', 'from' )
        self.sync_value( factory.search, 'search', 'from' )

        # If there is no specified filter, use the adapter's filter GridFilter
        # object as the filter:
        if factory.filter == '':
            self.filter       = adapter.grid_filter
            self.filter_index = 0

        # If there is no specified search, use the adapter's search GridFilter
        # object as the search filter:
        if factory.search == '':
            self.facet_setq( search = adapter.grid_search )
            self.search_index = 0

        # Set up the requested items monitors:
        self._item_monitors()

        # Make sure the grid view gets initialized:
        self.gui_rebuild()

        # Set the list control's tooltip:
        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        # Remove the requested items monitors:
        self._item_monitors( remove = True )

        # Remove the control's toolkit neutral event handlers:
        self.adapter.unset_event_handler(
            size         = self._size_modified,
            key_press    = self._key_pressed,
            left_down    = self._left_down,
            left_up      = self._left_up,
            left_dclick  = self._left_dclick,
            right_down   = self._right_down,
            right_up     = self._right_up,
            right_dclick = self._right_dclick,
            motion       = self._motion
        )

        # Handle any GUI toolkit specific dispose logic:
        self.gui_dispose()

        super( _GridEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.do_update_editor()

        search = self.search
        if (search is not None) and search.active:
            self.update_search()


    @on_facet_set( 'grid_adapter:changed, filter.changed, sorter, sort_ascending' )
    def do_update_editor ( self ):
        """ Updates the editor when any change the requires resynching the
            editor contents occurs.
        """
        if not self._no_update:
            self.changed = True
            self.gui_update_editor()


    def update_editor_check ( self ):
        """ Refreshes the contents of the editor when a change that only affects
            the visual appearance of the editor occurs and the user is not in
            the process of performing an in-cell edit.
        """
        if self.editing == 0:
            if not self._no_update:
                self.update_editor()
        else:
            self.update_pending = True


    @on_facet_set( 'search.[changed, active]' )
    def update_search ( self ):
        """ Computes a new selection set when the associated search filter is
            modified (deferred).
        """
        if ((self.factory.selection_mode in RowModes) and
            (self.search is not None)):
            do_after( 250, self._update_search )

    def _update_search ( self ):
        """ Computes a new selection set when the associated search filter is
            modified.
        """
        # Since this is invoked by 'do_after', make sure the editor hasn't
        # already been disposed of:
        factory = self.factory
        if factory is not None:
            indices  = []
            items    = []
            if self.search.active:
                filter   = self.search.filter
                get_item = self.grid_adapter.get_item
                index    = self.search_index
                for i in xrange( self.grid_adapter.len() ):
                    item = get_item( i )
                    if filter( ( i, item )[ index ] ):
                        indices.append( i )
                        items.append( item )

            if factory.selection_mode == 'row':
                if len( items ) == 0:
                    indices = -1
                    items   = None
                else:
                    indices = indices[0]
                    items   = items[0]

            # Update the selected, but don't handle the update since it will be
            # handled when we set 'selected_indices' next:
            self._no_update = True
            self.selected   = items
            self._no_update = False

            # Finally, update the selected indices, which will trigger the ui
            # selection update:
            self.selected_indices = indices


    @on_facet_set( 'grid_adapter:refresh' )
    def refresh_editor ( self ):
        """ Refreshes the contents of the editor when a change that only affects
            the visual appearance of the editor occurs.
        """
        self.gui_update_editor()


    @on_facet_set( 'grid_adapter:columns' )
    def rebuild_all ( self ):
        """ Rebuilds the structure of the list control, then refreshes its
            contents.
        """
        self.gui_rebuild()
        self.refresh_editor()


    def data_row_for ( self, row ):
        """ Return the data space row that corresponds to a specified screen
            space row.
        """
        if row < 0:
            row = self.grid_adapter.len() - 1

        if not self.mapping:
            return row

        return self.mapped_rows[ row ]


    def set_selection ( self, selection ):
        """ Sets the editor selection to the specified selection. Selection
            should be a list of selected items, where the format of the items
            depends upon the factory 'selection_mode'. Note that any row
            indices in the selection should be in screen space.
        """
        self._no_update = True
        try:
            getattr( self, '_set_%s_selection' % self.factory.selection_mode )(
                selection
            )
        finally:
            self._no_update = False


    def set_row_selection ( self, row ):
        """ Selects the specified screen space row.
        """
        rows_mode = (self.factory.selection_mode == 'rows')
        if row < 0:
            if rows_mode:
                index = item = []
            else:
                index = -1
                item  = None
        else:
            index = self.data_row_for( row )
            item  = self.grid_adapter.get_item( index )
            if rows_mode:
                index = [ index ]
                item  = [ item  ]

        self._no_update = True
        self.selected   = item
        self._no_update = False

        self.selected_indices = index

        self.gui_scroll_to( row )


    def set_ui_selection ( self ):
        """ Translate the current editor selection into a corresponding ui
            selection.
        """
        getattr( self, '_set_ui_%s_selection' % self.factory.selection_mode )()


    def get_selected ( self ):
        """ Returns the list of currently selected data space row indices.
        """
        data_row_for = self.data_row_for

        return [ data_row_for( row ) for row in self.gui_get_selected() ]


    def row_height ( self, height ):
        """ Sets the row size to use.
        """
        if height > self.height:
            self.height = height
            self.gui_row_height( height )


    def column_width ( self, column, width = None ):
        """ Caches the column width set by the user for a specified column.
        """
        if not self._no_update:
            if self._cached_widths is None:
                self._cached_widths = [ None ] * self.gui_column_count()

            self._cached_widths[ column ] = width


    def move_column ( self, from_column, to_column ):
        """ Adjust column information when the *from_column* is moved before the
            *to_column*.
        """
        cw = self._cached_widths
        if cw is not None:
            # Move the cached width of the 'from' column to its new position:
            width = cw[ from_column ]
            if from_column < to_column:
                cw.insert( to_column, width )
                del cw[ from_column ]
            elif from_column > to_column:
                del cw[ from_column ]
                cw.insert( to_column, width )

            # For each column in the affected range, adjust the physical column
            # width as needed:
            start = min( from_column, to_column )
            end   = min( max( from_column, to_column ) + 1, len( cw ) )
            for i in xrange( start, end ):
                if cw[ i ] < 0:
                    cw[ i ] = None
                else:
                    self.gui_column_width( i, cw[ i ] )


    def set_column_widths ( self ):
        """ Set all column widths based upon current user preferences.
        """
        do_later( self._set_column_widths )


    def paint_cell ( self, cell ):
        """ Paints a grid cell.
        """
        g               = cell.graphics
        x               = cell.x
        y               = cell.y
        dx              = cell.width
        dy              = cell.height
        indent          = cell.indent
        theme           = cell.state_theme
        paint           = cell.paint
        text            = cell.text
        alignment       = AlignmentMap[ cell.alignment ]
        image_alignment = AlignmentMap[ cell.image_alignment ]
        font            = cell.state_font
        color           = cell.state_text_color or 0x000000
        image           = cell.state_image

        # Set the correct font:
        if font is not None:
            g.font = font

        # Paint the rest of the cell based upon whether it has a theme or not:
        if theme is None:
            # Set the clipping bounds so the normal or custom painter can
            # determine the region it can draw in:
            g.clipping_bounds = ( x, y, dx, dy )

            # If there is a custom cell painter, let it do the painting:
            if paint is not None:
                cell.paint_background = True
                paint( cell )

                return

            # Draw the cell background:
            g.pen   = None
            g.brush = cell.state_bg_color
            g.draw_rectangle( x, y, dx, dy )

            # Set the correct text color:
            g.text_color = color

            # Initialize the text and image sizes:
            tdx = tdy = idx = 0

            # Determine if there is any text to display:
            lines    = text.split( '\n' )
            has_text = ((len( lines[0] ) > 0) or (len( lines ) > 1))

            # Calculate the image requirements (if any):
            if image is not None:
                idx = image.width

                # If the image is cell aligned, draw it now:
                if image_alignment & CELL:
                    if image_alignment & LEFT:
                        tx = x + Spacing
                    elif image_alignment & RIGHT:
                        tx = x + dx - idx - Spacing
                    else:
                        tx = x + ((dx - idx) / 2)

                    g.draw_bitmap(
                        image.bitmap, tx, y + ((dy - image.height) / 2)
                    )

                    image = None
                else:
                    # Include room for some spacing (if necessary):
                    idx += Spacing * has_text

            # Calculate the text requirements (if any):
            if has_text:
                sizes = []
                for line in lines:
                    ldx, ldy = g.text_size( line )
                    tdx      = max( tdx, ldx )
                    tdy     += ldy
                    sizes.append( ( ldx, ldy ) )

            # Calculate the leftmost drawing point based on the alignment:
            if alignment & LEFT:
                tx = x + Spacing + indent
            elif alignment & RIGHT:
                bx = x + dx - Spacing
                tx = bx - tdx - idx
            else:
                bx = x + ((dx + idx) / 2)
                tx = bx - (tdx / 2) - idx

            # Perform image drawing setup:
            if image is not None:
                if len( text ) > 1:
                    iy = y + 2 + ((tdy - image.height) / 2)
                else:
                    iy = y + ((dy - image.height) / 2)

                # Draw the image now if it is to the left of the text:
                if image_alignment & LEFT:
                    g.draw_bitmap( image.bitmap, tx, iy )
                    tx   += idx
                    image = None

            # Draw the text (if required):
            if has_text:
                if len( lines ) == 1:
                    g.draw_text( text, tx, y + ((dy - tdy) / 2) )
                else:
                    ey = y + dy
                    y += 2
                    for i, line in enumerate( lines ):
                        ldx, ldy = sizes[ i ]
                        if (i > 0) and (y + ldy) > ey:
                            break

                        if alignment & RIGHT:
                            tx = bx - ldx
                        elif (alignment & LEFT) == 0:  # Center
                            tx = bx - (ldx / 2)

                        g.draw_text( line, tx, y )

                        y += ldy

            # Draw the image (if any) to the right of the text:
            if image is not None:
                g.draw_bitmap( image.bitmap, tx + tdx + Spacing, iy )
        else:
            # Use the theme to draw the cell background:
            theme.fill( g, x, y, dx, dy )

            # Set up the correct theme clipping bounds:
            g.clipping_bounds = theme.bounds( x, y, dx, dy )

            # If there is a custom painter, let it paint the cell contents:
            if paint is not None:
                cell.paint_background = False
                paint( cell )

                return

            # Set the correct text color:
            g.text_color = color

            # Draw the text and image:
            # fixme: This code does not currently support the various image
            # alignment options other than drawing to the left of the text...
            tdx, tdy = theme.draw_text(
                g, text, alignment, x, y + 1, dx, dy, image
            )

            # If we have not seen this theme before, then calculate its
            # required row height:
            if theme not in self._themes:
                self._themes.add( theme )
                self.row_height( tdy + theme.size_for( g, text )[1] )

        # If the cell has focus, draw the cell highlighting:
        if cell.has_focus:
            g.pen   = Pen( color = color, style = 'dot' )
            g.brush = None
            g.draw_rectangle( x, y, dx, dy )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'changed' )
    def _get_mapping ( self ):
        filter = self.filter

        return ((((filter is not None) and filter.active) or
                (self.sorter is not None)) and
                (self.grid_adapter.len() > 0))


    @property_depends_on( 'changed' )
    def _get_mapped_rows ( self ):
        sorter     = self.sorter
        filter     = self.filter
        has_filter = ((filter is not None) and filter.active)
        if (not has_filter) and (sorter is None):
            return []

        get_item = self.grid_adapter.get_item
        items    = [ ( i, get_item( i ) )
                     for i in xrange( self.grid_adapter.len() ) ]

        if has_filter:
            filter = filter.filter
            index  = self.filter_index
            items  = [ item for item in items if filter( item[ index ] ) ]

        if sorter is not None:
            items = self.grid_adapter.sort( items, sorter, self.sort_ascending )

        return [ item[0] for item in items ]


    @property_depends_on( 'changed' )
    def _get_screen_rows ( self ):
        screen_rows = {}
        for screen_row, data_row in enumerate( self.mapped_rows ):
            screen_rows[ data_row ] = screen_row

        return screen_rows


    @property_depends_on( 'changed' )
    def _get_rows ( self ):
        if self.mapping:
            return len( self.mapped_rows )

        return self.grid_adapter.len()

    #-- List Control Event Handlers --------------------------------------------

    def _key_pressed ( self, event ):
        """ Handles the user pressing a key in the list control.
        """
        key = event.key_code
        if key == 'Ctrl-Page Down':
            self._append_new()
        elif key in ( 'Backspace', 'Delete' ):
            self._delete_current()
        elif key == 'Insert':
            self._insert_current()
        elif key == 'Ctrl-Up':
            self._move_up_current()
        elif key == 'Ctrl-Down':
            self._move_down_current()
        #elif key in ( 'Enter', 'Esc' ):
        #    self._edit_current()
        else:
            event.handled = False

    #-- Private Methods --------------------------------------------------------

    def _item_monitors ( self, remove = False ):
        """ Adds/removes listeners for item changes.
        """
        monitor = self.factory.monitor
        if monitor == 'selected':
            if self.factory.selection_mode in RowModes:
                self.on_facet_set( self.update_editor_check, 'selected:-',
                                   dispatch = 'ui', remove = remove )
        elif monitor == 'all':
            self.context_object.on_facet_set(
                self.update_editor_check, self.extended_name + ':-',
                dispatch = 'ui', remove = remove
            )


    def _edit_current ( self ):
        """ Allows the user to edit the current item.
        """
        if 'edit' in self.operations:
            selected = self.get_selected()
            if len( selected ) == 1:
                # fixme: Refactor this into a GUI specific toolkit call...
                self.control.EditLabel( selected[0] )


    def _find_item ( self, item ):
        """ Find the screen space row (if any) that corresponds to the
            specified item.
        """
        get_item = self.grid_adapter.get_item
        for i in xrange( self.grid_adapter.len() ):
            if item is get_item( i ):
                return self._find_index( i )

        return None


    def _find_index ( self, data_row ):
        """ Returns the screen space row for a specified data space row.
        """
        if not self.mapping:
            return data_row

        return self.screen_rows.get( data_row )


    def _set_row_selection ( self, selection ):
        """ Set the editor row selection using the specified selection.
        """
        if len( selection ) == 0:
            self.selected_indices = -1
            self.selected         = None
        else:
            self.selected_indices = index = self.data_row_for( selection[0] )
            self.selected         = self.grid_adapter.get_item( index )


    def _set_rows_selection ( self, selection ):
        """ Set the editor rows selection using the specified information.
        """
        get_item = self.grid_adapter.get_item
        drf      = self.data_row_for
        self.selected_indices = rows = [ drf( row ) for row in selection ]
        self.selected                = [ get_item( row ) for row in rows ]


    def _set_column_selection ( self, selection ):
        """ Set the editor column selection using the specified selection.
        """
        if len( selection ) == 0:
            self.selected_indices = -1
            self.selected         = None
        else:
            self.selected_indices = index = selection[0]
            self.selected         = self.grid_adapter.column_map[ index ]


    def _set_columns_selection ( self, selection ):
        """ Set the editor columns selection using the specified information.
        """
        column_map            = self.grid_adapter.column_map
        self.selected_indices = selection
        self.selected         = [ column_map[ column ] for column in selection ]


    def _set_cell_selection ( self, selection ):
        """ Set the editor cell selection using the specified selection.
        """
        raise NotImplementedError


    def _set_cells_selection ( self, selection ):
        """ Set the editor cells selection using the specified information.
        """
        raise NotImplementedError


    def _set_ui_row_selection ( self ):
        """ Set the ui selection from a single editor row selection.
        """
        if self.selected is None:
            self._set_ui_rows_selection( [] )
        else:
            rows = self._set_ui_rows_selection( [ self.selected ] )
            if len( rows ) == 1:
                self.gui_scroll_to( rows[0] )


    def _set_ui_rows_selection ( self, selected = None ):
        """ Set the ui selection from an editor row list selection.
        """
        if selected is None:
            selected = self.selected

        self.gui_deselect()

        rows     = []
        n        = self.grid_adapter.len()
        get_item = self.grid_adapter.get_item
        if len( selected ) == 1:
            item = selected[0]
            for index in xrange( n ):
                next_item = get_item( index )
                if item == next_item:
                    row = self._find_index( index )
                    if row is not None:
                        rows.append( row )

                    break
        else:
            cache = {}
            next  = 0
            for item in selected:
                index = cache.get( item )
                if index is None:
                    for index in xrange( next, n ):
                        next_item = get_item( index )
                        if item == next_item:
                            next = index + 1

                            break

                        cache[ next_item ] = index

                row = self._find_index( index )
                if row is not None:
                    rows.append( row )

        self.gui_select_rows( rows )

        return rows


    def _set_ui_column_selection ( self ):
        """ Set the ui selection from a single editor column selection.
        """
        if self.selected == '':
            self._set_ui_columns_selection( [] )
        else:
            self._set_ui_columns_selection( [ self.selected ] )


    def _set_ui_columns_selection ( self, selected = None ):
        """ Set the ui selection from an editor column list selection.
        """
        if selected is None:
            selected = self.selected

        self.gui_deselect()

        reverse_map = dict( [
            ( name, index )
            for index, name in enumerate( self.grid_adapter.column_map )
        ] )
        self.gui_select_columns(
            [ reverse_map[ column ] for column in selected ]
        )


    def _set_ui_cell_selection ( self ):
        """ Set the ui selection from a single editor cell selection.
        """
        raise NotImplementedError


    def _set_ui_cells_selection ( self ):
        """ Set the ui selection from an editor cell list selection.
        """
        raise NotImplementedError

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        """ Handles the editor's 'selected' facet being changed.
        """
        if not self._no_update:
            self.set_ui_selection()


    def _selected_indices_set ( self, selected ):
        """ Handles the editor's 'selected_indices' facet being changed.
        """
        if not self._no_update:
            handler = getattr( self, '_selected_%s_indices_changed' %
                                     self.factory.selection_mode, None )
            if handler is not None:
                handler( selected )

    def _selected_row_indices_set ( self, index ):
        self._selected_rows_indices_set( [] if index < 0 else [ index ] )


    def _selected_rows_indices_set ( self, indices ):
        self.gui_deselect()
        rows = []
        for index in indices:
            row = self._find_index( index )
            if row is not None:
                rows.append( row )

        self.gui_select_rows( rows )


    def _object_set ( self ):
        """ Handles the 'object' facet being changed.
        """
        if self.grid_adapter is not None:
            self.grid_adapter.object = self.object
            self.do_update_editor()

    #-- UI Preference Save/Restore Interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self._cached_widths = cws = prefs.get( 'cached_widths' )
        if cws is not None:
            self._no_update  = True
            set_column_width = self.gui_column_width
            for i, width in enumerate( cws ):
                if width is not None:
                    set_column_width( i, width )
            self._no_update = False

        gsp = prefs.get( 'gui' )
        if gsp is not None:
            self.gui_restore_prefs( gsp )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        cws = self._cached_widths
        if cws is not None:
            cws = [ ( None, cw )[ cw >= 0 ] for cw in cws ]

        result = { 'cached_widths': cws }
        gsp    = self.gui_save_prefs()
        if gsp is not None:
            result[ 'gui' ] = gsp

        return result

    #-- Private Methods --------------------------------------------------------

    def _left_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        self._mouse_event( event, 'left_down' )


    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        self._mouse_event( event, 'left_up' )


    def _left_dclick ( self, event ):
        """ Handles the left mouse button being double clicked.
        """
        self._mouse_event( event, 'left_dclick' )


    def _right_down ( self, event ):
        """ Handles the right mouse button being pressed.
        """
        self._mouse_event( event, 'right_down' )


    def _right_up ( self, event ):
        """ Handles the right mouse button being released.
        """
        self._mouse_event( event, 'right_up' )


    def _right_dclick ( self, event ):
        """ Handles the right mouse button being double clicked.
        """
        self._mouse_event( event, 'right_dclick' )


    def _mouse_move ( self, event ):
        """ Handles the mouse moving.
        """
        self._mouse_event( event, 'mouse_move' )


    def _item_selected ( self, event ):
        """ Handles an item being selected.
        """
        self._no_update = True
        try:
            get_item      = self.grid_adapter.get_item
            selected_rows = self.get_selected()
            if self.factory.selection_mode in MultipleModes:
                self.multi_selected_rows = selected_rows
                self.multi_selected      = [ get_item( row )
                                             for row in selected_rows ]
            elif len( selected_rows ) == 0:
                self.selected_row = -1
                self.selected     = None
            else:
                self.selected_row = selected_rows[0]
                self.selected     = get_item( selected_rows[0] )
        finally:
            self._no_update = False


    def _column_right_clicked ( self, event ):
        """ Handles the user right-clicking a column header.
        """
        column = event.column
        if ((self._cached_widths is not None) and
            (0 <= column < len( self._cached_widths ))):
            self._cached_widths[ column ] = None
            self._size_modified( event )


    def _column_clicked ( self, event ):
        """ Handles the user clicking a column header.
        """
        editor_event = GridEditorEvent(
            editor = self,
            row    = 0,
            column = event.column
        )

        setattr( self, 'column_clicked', editor_event )

        event.handled = False


    def _size_modified ( self, event ):
        # fixme: Need to handle the wx specific caller's of this method...
        """ Handles the size of the list control being changed.
        """
        n = self.gui_column_count()
        if n == 1:
            dx, dy = self.adapter.client_size
            self.gui_column_width( 0, dx - 1 )
        elif n > 1:
            self.set_column_widths()

        event.handled = False


    def _motion ( self, event ):
        """ Handles the user moving the mouse.
        """
        row, column, below = self.gui_xy_to_row_column( event.x, event.y )
        if (row != self._last_row) or (column != self._last_column):
            self._last_row, self._last_column = row, column
            if (row == -1) or (column is None):
                tooltip = ''
            else:
                tooltip = self.grid_adapter.get_tooltip( row, column )

            if tooltip != self._last_tooltip:
                self._last_tooltip = tooltip
                self.adapter.tooltip = tooltip


    def _dropped_on ( self, row, column, item ):
        """ Helper method for handling a single item dropped on the list
            control.
        """
        adapter = self.grid_adapter

        # Obtain the destination of the dropped item relative to the target:
        destination = adapter.get_dropped( row, column, item )

        # Adjust the target index accordingly:
        if destination == 'after':
            row += 1

        # Insert the dropped item at the requested position:
        adapter.insert( row, item )

        # If the source for the drag was also this list control, we need to
        # adjust the original source indices to account for their new position
        # after the drag operation:
        rows = self._drag_rows
        if rows is not None:
            for i in range( len( rows ) - 1, -1, -1 ):
                if rows[i] < row:
                    break

                rows[i] += 1


    def _set_column_widths ( self ):
        """ Set the column widths for the current set of columns.
        """
        adapter = self.adapter
        if adapter is None:
            return

        object, name = self.object, self.name
        dx           = self.gui_control_width()
        n            = self.gui_column_count()
        get_width    = self.grid_adapter.get_width
        pdx          = 0
        wdx          = 0.0
        widths       = []
        cached       = self._cached_widths
        current      = [ self.gui_column_width( i )   for i in xrange( n ) ]
        visible      = [ self.gui_column_visible( i ) for i in xrange( n ) ]
        if (cached is None) or (len( cached ) != n):
            self._cached_widths = cached = [ None ] * n

        for i in xrange( n ):
            width = 0
            if visible[i]:
                cw = cached[i]
                w  = current[i]
                if (cw is None) or (-cw == w) or (w == 0):
                    width = float( get_width( i ) )
                    if width <= 0.0:
                        width = 0.1
                    if width <= 1.0:
                        wdx += width
                        cached[i] = -1
                    else:
                        width = int( width )
                        pdx  += width
                        if cw is None:
                            cached[i] = width
                else:
                    cached[i] = width = w
                    pdx += width

            widths.append( width )

        adx = max( 0, dx - pdx )

        adapter.frozen = True

        for i in xrange( n ):
            if visible[i]:
                width = cached[i]
                if width < 0:
                    width = widths[i]
                    if width <= 1.0:
                        widths[i] = w = max( 30,
                                             int( round( (adx * width)/wdx ) ) )
                        wdx      -= width
                        width     = w
                        adx      -= width
                        cached[i] = -w

                self.gui_column_width( i, width )

        adapter.frozen = False


    def _get_column ( self, x, translate = False ):
        """ Returns the column index corresponding to a specified x position.
        """
        if x >= 0:
            for i in range( self.gui_column_count() ):
                x -= self.gui_column_width( i )
                if x < 0:
                    if translate:
                        return self.grid_adapter.get_column( i )

                    return i

        return None


    def _mouse_event ( self, event, method ):
        """ Handle a specified mouse event for a specified GridEventHandler
            method name.
        """
        # Check if the GUI toolkit wants to handle the mouse event:
        if self.gui_mouse_event( event, method ):
            event.handled = True

            return

        # If not, then we'll let the application handle it:
        x   = event.x
        row = self.gui_xy_to_row_column( x, event.y )[0]
        if row < 0:
            if self.factory.selection_mode in MultipleModes:
                self.multi_selected      = []
                self.multi_selected_rows = []
            else:
                self.selected     = None
                self.selected_row = -1
        else:
            if ((self.factory.selection_mode in MultipleModes) and
                event.shift_down):
                # Handle shift-click multi-selections because the wx.ListCtrl
                # does not (by design, apparently).
                # We must append this to the event queue because the
                # multi-selection will not be recorded until this event handler
                # finishes and lets the widget actually handle the event.
                do_later( self._item_selected, None )

            setattr( self, facet, Grid(
                editor = self,
                row    = row,
                column = self._get_column( x, translate = True )
            ) )

        event.handled = False


    def _append_new ( self ):
        """ Append a new item to the end of the list control.
        """
        if 'append' in self.operations:
            self._insert_new_at( self.grid_adapter.len() )


    def _insert_current ( self ):
        """ Inserts a new item after the currently selected list control item.
        """
        if 'insert' in self.operations:
            selected = self.get_selected()
            if len( selected ) == 1:
                self._insert_new_at( selected[0] )


    def _insert_new_at ( self, row ):
        """ Insert a new item at the specified data space index.
        """
        adapter = self.grid_adapter
        item    = adapter.get_default_value()
        adapter.insert( row, item )
        index = self._find_item( item )
        if index is None:
            index = -1

        self.set_row_selection( index )
        self.update_editor()


    def _delete_current ( self ):
        """ Deletes the currently selected items from the list control.
        """
        if 'delete' in self.operations:
            selected = self.get_selected()
            if len( selected ) == 0:
                return

            n      = self.gui_item_count()
            rows   = self.gui_get_selected()
            rows.sort()
            row    = rows[0]
            delete = self.grid_adapter.delete
            selected.sort( lambda l, r: cmp( r, l ) )

            self._no_update = True
            for index in selected:
                delete( index )
            self._no_update = False

            self.set_row_selection( min( row, n - len( selected ) - 1 ) )
            self.update_editor()


    def _move_up_current ( self ):
        """ Moves the currently selected item up one line in the list control.
        """
        if ('move' in self.operations) and (self.sorter is None):
            selected = self.get_selected()
            if len( selected ) == 1:
                row = selected[0]
                if row > 0:
                    adapter = self.grid_adapter
                    item    = adapter.get_item( row )
                    adapter.delete( row )
                    adapter.insert( row - 1, item )
                    self.gui_select_rows( row - 1 )


    def _move_down_current ( self ):
        """ Moves the currently selected item down one line in the list control.
        """
        if ('move' in self.operations) and (self.sorter is None):
            selected = self.get_selected()
            if len( selected ) == 1:
                row = selected[0]
                if row < (self.gui_item_count() - 1):
                    adapter = self.grid_adapter
                    item    = adapter.get_item( row )
                    adapter.delete( row )
                    adapter.insert( row + 1, item )
                    self.gui_select_rows( row + 1 )

    #-- Abstract Toolkit Specific Methods --------------------------------------

    def gui_create_control ( self, parent ):
        """ Create the GUI toolkit specific version of the control.
        """
        raise NotImplementedError


    def gui_dispose ( self ):
        """ Performs any GUI toolkit specific 'dispose' code.
        """
        raise NotImplementedError


    def gui_update_editor ( self ):
        """ Updates the GUI toolkit specific editor when the object facet or
            filter changes externally to the editor.
        """
        raise NotImplementedError


    def gui_rebuild ( self ):
        """ Rebuilds the contents of the editor's control.
        """
        raise NotImplementedError


    def gui_item_count ( self ):
        """ Returns the number of items in the list control.
        """
        raise NotImplementedError


    def gui_deselect ( self ):
        """ Deselect any currently selected data.
        """
        raise NotImplementedError


    def gui_select_rows ( self, rows ):
        """ Selects the specified rows. Rows may be a single row or a list of
            rows.
        """
        raise NotImplementedError


    def gui_select_columns ( self, columns ):
        """ Selects the specified columns. Columns may be a single column or a
            list of columns.
        """
        raise NotImplementedError


    def gui_get_selected ( self ):
        """ Returns a list of the rows of all currently selected list items.
        """
        raise NotImplementedError


    def gui_control_width ( self ):
        """ Returns the width of the control that can contain columns (i.e.
            excluding scroll bars).
        """
        raise NotImplementedError


    def gui_xy_to_row_column ( self, x, y ):
        """ Returns a tuple of the form: ( row, column, flags ) describing the
            cell containing a specified point. Also returns a flag specifying
            whether the point is below the last row (in cases where the point
            is not in a row).
        """
        raise NotImplementedError


    def gui_column_count ( self ):
        """ Returns the number of columns in the control.
        """
        raise NotImplementedError


    def gui_column_width ( self, column, width = None ):
        """ Gets/Sets the width (in pixels) of the specified column.
        """
        raise NotImplementedError


    def gui_column_visible ( self, column ):
        """ Returns whether a specified column is visible or not.
        """
        raise NotImplementedError


    def gui_row_height ( self, height ):
        """ Sets the row height to use.
        """
        raise NotImplementedError


    def gui_scroll_to ( self, row ):
        """ Make sure the specified screen row space row is visible.
        """
        raise NotImplementedError


    def gui_save_prefs ( self ):
        """ Returns any toolkit specific user preference data.
        """
        return None


    def gui_restore_prefs ( self, data ):
        """ Restores any previously saved toolkit specific user preference data.
        """
        pass


    def gui_mouse_event ( self, event, method ):
        """ Handles a specified mouse event. Returns True if the event has been
            handled, and False if the normal grid editor mouse event processing
            should be performed.
        """
        return True

#-------------------------------------------------------------------------------
#  'GridEditor' editor factory class:
#-------------------------------------------------------------------------------

class GridEditor ( BasicEditorFactory ):
    """ GUI toolkit neutral editor factory for gridable data editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Should column headers (i.e. titles) be displayed?
    show_titles = Bool( True )

    # Should the view automatically scroll to the bottom whenever items are
    # added to or removed from the grid?
    auto_scroll = Bool( False )

    # The selection mode of the table. The meaning of the various values are as
    # follows:
    #
    # row
    #    Entire rows are selected. At most one row can be selected at once.
    #    This is the default.
    # rows
    #    Entire rows are selected. More than one row can be selected at once.
    # column
    #   Entire columns are selected. At most one column can be selected at once.
    # columns
    #   Entire columns are selected. More than one column can be selected at
    #   once.
    # cell
    #   Single cells are selected. Only one cell can be selected at once.
    # cells
    #   Single cells are selected. More than one cell can be selected at once.
    selection_mode = Enum( 'row', 'rows', 'column', 'columns', 'cell', 'cells' )

    # What items should be monitored for changes:
    monitor = Enum( 'none', 'all', 'selected' )

    # The optional extended name of the facet that the current selection is
    # synced with:
    selected = Str

    # The optional extended facet name of the facet that the indices of the
    # current selection are synced with:
    selected_indices = Str

    # The drag and drop mode supported by the editor (note: 'move_only' means
    # only allow drag and drop from one row of the grid to another):
    drag_drop = Enum( 'drag_drop', 'drag_only', 'drop_only', 'move_only',
                      'none' )

    # The optional extended facet name of the IFilter object used to filter the
    # data. If not specified, no filtering is applied:
    filter = Str

    # The optional extended facet name of the IFilter object used to search
    # for specific items in the data. If not specified, no searching occurs:
    search = Str

    # A factory for creating a GridAdapter subclass for mapping from facet
    # values to editor values:
    adapter = Either( Callable, Instance( GridAdapter ) )

    # What type of operations are allowed on the data (note that 'move' and
    # 'copy' are mutually exclusive, if both are specified, 'move' is used):
    operations = List( Enum( 'delete', 'insert', 'append', 'edit', 'move',
                             'copy', 'sort', 'shuffle' ),
                       [ 'delete', 'insert', 'append', 'edit', 'move', 'sort',
                         'shuffle' ] )

    # The initial sort column name:
    sort_column = Str

    # Is the initial sort order ascending (True) or descending (False)?
    sort_ascending = Bool( True )

    # Should cell editors be resized to fit their cell (True) or cells be
    # resized to fit their editor (False)?
    resize_cell_editor = Bool( True )

    # The row height to use for each grid row (0 = use default):
    row_height = Int( 0 )

    # A factory to generate new rows:
    # NOTE: If None, then the user will not be able to add new rows via insert
    # or append. If not None, then it must be a callable that accepts
    # **row_factory_args** and **row_factory_kw** and returns a new object
    # that can be added to the table.
    row_factory = Callable

    # Arguments to pass to the **row_factory** callable when a new row is
    # created:
    row_factory_args = Tuple

    # Keyword arguments to pass to the **row_factory** callable when a new row
    # is created:
    row_factory_kw = Dict

#-- EOF ------------------------------------------------------------------------