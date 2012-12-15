"""
A wxPython-based facets UI editor for editing gridable data (arrays, list of
tuples, lists of objects, etc).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from wx \
    import PyEvtHandler, wxEVT_LEFT_DOWN, wxEVT_LEFT_UP, wxEVT_PAINT

from wx.grid \
    import Grid, GridCellAttr, GridTableMessage, PyGridCellRenderer, \
           PyGridTableBase, EVT_GRID_SELECT_CELL, EVT_GRID_RANGE_SELECT, \
           EVT_GRID_CELL_LEFT_CLICK, EVT_GRID_CELL_LEFT_DCLICK, \
           EVT_GRID_LABEL_LEFT_DCLICK, EVT_GRID_COL_SIZE, GRID_VALUE_STRING, \
           GRIDTABLE_NOTIFY_ROWS_APPENDED, GRIDTABLE_NOTIFY_ROWS_DELETED, \
           GRIDTABLE_NOTIFY_COLS_APPENDED, GRIDTABLE_NOTIFY_COLS_DELETED

from wx.lib.gridmovers \
    import GridColMover, EVT_GRID_COL_MOVE

from facets.api \
    import Property, Any, Int, Bool, Color, on_facet_set

from facets.ui.wx.constants \
    import scrollbar_dx, is_win32

from facets.ui.wx.adapters.control \
    import set_standard_font

from facets.ui.wx.adapters.cell \
    import WxCell

from facets.ui.editors.grid_editor \
    import _GridEditor, GridEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from factory selection modes to wx selection modes:
SelectionMode = {
    'row':     Grid.wxGridSelectRows,
    'rows':    Grid.wxGridSelectRows,
    'column':  Grid.wxGridSelectColumns,
    'columns': Grid.wxGridSelectColumns,
    'cell':    Grid.wxGridSelectCells,
    'cells':   Grid.wxGridSelectCells
}

# Mapping from standard facets horizontal alignment values to Qt values:
AlignmentMap = {
    'left':   wx.ALIGN_LEFT,
    'center': wx.ALIGN_CENTRE,
    'right':  wx.ALIGN_RIGHT
}

# Standard cell request:
CellKind = set( [ GridCellAttr.Cell, GridCellAttr.Any ] )

# Column sort order indicators:
SortOrder = ( '  <<', '  >>', u'  \u00ab', u'  \u00bb' )

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The cell adapter used to render each cell:
cell_adapter = WxCell()

#-------------------------------------------------------------------------------
#  'CellRenderer' class:
#-------------------------------------------------------------------------------

class CellRenderer ( PyGridCellRenderer ):
    """ Custom wx grid cell renderer for use with the grid editor.
    """

    #-- Public Methods ------------------------------------------------------

    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        self._editor = editor

        super( CellRenderer, self ).__init__()

    #-- GridCellRenderer Interface Implementation ------------------------------

    def Draw ( self, grid, attr, dc, rect, row, column, is_selected ):
        """ Renders the specified grid cell using the specified drawing
            information.
        """
        # Create a cell adapter, then ask the editor to paint the cell contents:
        editor = self._editor

        # Draw the 'missing' leftmost cell border (if necessary):
        x = rect.x
        if (x == 0) and (editor.grid_line_color is not None):
            rect.x      = x + 1
            rect.width -= 1
            dc.SetPen( wx.Pen( editor.grid_line_color ) )
            dc.DrawLine( x, rect.y, x, rect.y + rect.height )

        # Draw the contents of the cell:
        cell_adapter.init(
            set_standard_font( dc ), rect, editor.grid_adapter,
            editor.data_row_for( row ), editor.data_column_for( column ),
            row, is_selected, ''
        )
        editor.paint_cell( cell_adapter )

        # Reset the clipping region set by the editor; otherwise the wx.Grid
        # will not be able to do later updates correctly:
        dc.DestroyClippingRegion()


    def GetBestSize ( self, grid, attr, dc, row, column ):
        """ Returns the preferred size for the specified grid cell.
        """
        return wx.Size( 20, 20 )

#-------------------------------------------------------------------------------
#  'GridModel' class:
#-------------------------------------------------------------------------------

class GridModel ( PyGridTableBase ):
    """ The model for grid data.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor ):
        """ Initialise the object.
        """
        super( GridModel, self ).__init__()

        self._editor = editor
        self.reset()


    def reset ( self ):
        """ Resets the cached number of rows or columns.
        """
        self._rows = self._columns = None

    #-- GridTableBase Interface Implementation ---------------------------------

    def GetNumberRows ( self ):
        """ Return the number of rows in the model.
        """
        if self._rows is None:
            self._rows = self._editor.rows

        return self._rows


    def GetNumberCols ( self ):
        """ Return the number of columns in the model.
        """
        if self._columns is None:
            self._columns = n = len( self._editor.grid_adapter.columns )

            # Make sure all columns can have a 0 width (needed to hide columns):
            scmw = self._editor.control.SetColMinimalWidth
            for column in xrange( n ):
                scmw( column, 0 )

        return self._columns


    def IsEmptyCell ( self, row, column ):
        """ Is the specified cell empty?
        """
        return False


    def GetValue ( self, row, column ):
        """ Get the value at the specified row and column.
        """
        return self._editor.grid_adapter.get_text( row, column )


    def SetValue ( self, row, column, value ):
        print "SetValue:"
        """ Set the value at the specified row and column.
        """
        # This works because a Facets Editor will have already set the value on
        # the object, and so we don't need to do anything here:
        pass


    def GetColLabelValue ( self, grid_column ):
        print "GetColLabelValue:"
        """ Called when the grid needs to display a column label.
        """


    def GetTypeName ( self, row, column ):
        """ Called to determine the kind of editor/renderer to use.
        """
        return GRID_VALUE_STRING


    def GetAttr ( self, row, column, kind ):
        """ Retrieve the cell attribute object for the specified cell.
        """
        result = GridCellAttr()

        # Indicate whether or not this cell is editable:
        result.SetReadOnly(
            ('edit' in self._editor.operations) and
            self._editor.grid_adapter.get_can_edit( row, column )
        )

        return result

#-------------------------------------------------------------------------------
#  'LabelsEventHandler' class:
#-------------------------------------------------------------------------------

class LabelsEventHandler ( PyEvtHandler ):

    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        super( LabelsEventHandler, self ).__init__()

        self._editor   = editor
        self._dragging = False


    def ProcessEvent ( self, event ):
        """ Process a control event.
        """
        type   = event.EventType
        editor = self._editor
        grid   = editor.control
        if ((grid is not None) and
            (type in ( wxEVT_LEFT_DOWN, wxEVT_LEFT_UP, wxEVT_PAINT ))):
            if type == wxEVT_PAINT:
                control = event.EventObject
                dc      = wx.PaintDC( control )
                x, y    = grid.CalcUnscrolledPosition( 0, 0 )
                origin  = dc.GetDeviceOrigin()
                columns = grid.CalcColLabelsExposed( control.GetUpdateRegion() )
                dc.SetDeviceOrigin( origin.x - x, origin.y )
                editor.draw_column_labels( dc, columns,
                                           control.GetSizeTuple()[1] )

                return True

            x, y = grid.CalcUnscrolledPosition( event.X, event.Y )
            if type == wxEVT_LEFT_DOWN:
                if (event.ControlDown() or
                    ((not event.AltDown()) and (grid.XToEdgeOfCol( x ) < 0))):
                    self._xy = ( x, y )

                    return True

                self._dragging = True

            elif not self._dragging:
                x0, y0 = self._xy
                if (abs( x - x0 ) + abs( y - y0 )) <= 3:
                    column = grid.XToCol( x );
                    if column >= 0:
                        editor.label_click( column, event )

                return True
            else:
                self._dragging = False

        return super( LabelsEventHandler, self ).ProcessEvent( event )

#-------------------------------------------------------------------------------
#  '_WxGridEditor' class:
#-------------------------------------------------------------------------------

class _WxGridEditor ( _GridEditor ):
    """ A wxPython specific facets UI editor for editing gridable data (arrays,
        list of tuples, lists of objects, etc).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The value of the current cell being edited:
    cell_value  = Property
    cell_value_ = Property

    # The item row for the cell currently being edited:
    cell_row = Int

    # The item column for the cell currently being edited:
    cell_column = Int

    # The current logical sort column (-1: no sorting in effect):
    sort_column = Int( -1 )

    # The current physical grid sort column:
    grid_sort_column = Int( -1 )

    # Is the current sort column sorted normally (True) or reversed (False)?
    sort_normal = Bool( True )

    # The color to use for drawing grid lines (if any):
    grid_line_color = Color( None )

    # The mapping from physical to logical grid columns:
    column_order = Any # List( Int )

    #-- Public Methods ------------------------------------------------------

    def data_column_for ( self, column ):
        """ Returns the logical grid adapter column corresponding to a specified
            physical grid column.
        """
        return self.column_order[ column ]


    def label_click ( self, grid_column, event ):
        """ Handles a grid column label being clicked with the left mouse
            button.
        """
        if event.ShiftDown():
            # Handle the case of columns being made visible or hidden:
            grid = self.control
            n    = len( self.grid_adapter.columns )
            if event.ControlDown():
                # Make any hidden columns visible again:
                modified = False
                for column in xrange( n ):
                    if not self.gui_column_visible( column ):
                        grid.SetColSize( column, 1 )
                        self.column_width( column )
                        modified = True

                if modified:
                    self.set_column_widths()
            else:
                # Hide the specified column (as long as there will still be at
                # least one remaining visible column):
                visible = 0
                for column in xrange( n ):
                    visible += self.gui_column_visible( column )

                if visible >= 2:
                    grid.SetColSize( grid_column, 0 )
                    self.column_width( grid_column, 0 )
                    self.set_column_widths()

        elif event.ControlDown():
            if event.AltDown():
                # Reset any current sort column:
                self.sort_column = self.grid_sort_column = -1
                self.sorter      = None
            else:
                # Allow the column to have an adjustable width:
                self.column_width( grid_column )
                self.set_column_widths()

        else:
            # A normal click, process either as a column sort request (if
            # sorting is enabled) or as a user click:
            column  = self.data_column_for( grid_column )
            adapter = self.grid_adapter
            if (('sort' in self.operations) and adapter.get_sortable( column )):
                # Update our sub-class sorting information:
                if column != self.sort_column:
                    self.sort_column      = column
                    self.grid_sort_column = grid_column
                    self.sort_normal      = True
                else:
                    self.sort_normal = not self.sort_normal

                # Set the base editor sort values, which triggers the sorting:
                self.sort_ascending = self.sort_normal
                self.sorter         = adapter.get_sorter( column )
            else:
                # If sorting not enabled, send the click to the application:
                adapter.get_column_clicked( column )


    def draw_column_labels ( self, dc, columns, height ):
        """ Draws the set of column labels specified by *columns* using the
            device context specified by *dc*.
        """
        # Draw the contents of the column labels:
        grid         = self.control
        adapter      = self.grid_adapter
        dcf          = self.data_column_for
        ctr          = grid.ColToRect
        cell_adapter = WxCell()

        for column in columns:
            # Get the bounds of the current column:
            rect        = ctr( column )
            rect.height = height

            # Draw the label border (if necessary):
            if self.grid_line_color is not None:
                dc.SetPen( wx.Pen( self.grid_line_color ) )
                dc.SetBrush( wx.TRANSPARENT_BRUSH )
                x     = rect.x
                width = rect.width + 1
                if x != 0:
                    x     -= 1
                    width += 1
                else:
                    rect.x      = 1
                    rect.width -= 1

                dc.DrawRectangle( x, rect.y, width, height )
                rect.y      += 1
                rect.height -= 2

            # Determine any extra text to be added to the label if the current
            # column is also the current sort column:
            extra = ''
            if column == self.grid_sort_column:
                extra = SortOrder[ self.sort_normal + (2 * is_win32) ]

            # Set up the cell adapter and draw the current label:
            cell_adapter.init( set_standard_font( dc ), rect, adapter, -1,
                               dcf( column ), -1, False, extra )
            self.paint_cell( cell_adapter )

            # Reset the clipping region set by the editor; otherwise subsequent
            # updates will not work correctly:
            dc.DestroyClippingRegion()

    #-- Property Implementations -----------------------------------------------

    def _get_cell_value ( self ):
        return self.grid_adapter.get_content( self.cell_row, self.cell_column )

    def _set_cell_value ( self, value ):
        self.grid_adapter.set_text( self.cell_row, self.cell_column, value )


    def _get_cell_value_ ( self ):
        return self.cell_value

    #-- Default Facet Values ---------------------------------------------------

    def _column_order_default ( self ):
        return range( len( self.grid_adapter.columns ) )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'grid_adapter:columns[]' )
    def _columns_modified ( self ):
        """ Handles the grid adapter 'columns' trait being modified.
        """
        self.column_order = self._column_order_default()

    #-- Private Methods --------------------------------------------------------

    def _refresh ( self ):
        """ Refresh the contents of the grid control.
        """
        self.control.ForceRefresh()


    def _content_modified ( self ):
        """ Resets the grid whenever the content changes.
        """
        grid         = self.control
        table        = grid.GetTable()
        ptm          = grid.ProcessTableMessage
        last_rows    = table.GetNumberRows()
        last_columns = table.GetNumberCols()
        table.reset()
        rows         = table.GetNumberRows()
        columns      = table.GetNumberCols()

        # Make sure any current active editor has been disabled:
        grid.DisableCellEditControl()

        # Reset the grid rows if any rows have been added or removed:
        if rows > last_rows:
            ptm( GridTableMessage( table, GRIDTABLE_NOTIFY_ROWS_APPENDED,
                                   rows - last_rows ) )
        elif rows < last_rows:
            ptm( GridTableMessage( table, GRIDTABLE_NOTIFY_ROWS_DELETED,
                                   rows, last_rows - rows ) )

        # Reset the grid columns if any columns have been added or removed:
        if columns > last_columns:
            ptm( GridTableMessage( table, GRIDTABLE_NOTIFY_COLS_APPENDED,
                                   columns - last_columns ) )
        elif columns < last_columns:
            ptm( GridTableMessage( table, GRIDTABLE_NOTIFY_COLS_DELETED,
                                   columns, last_columns - columns ) )

    #-- wx Event Handlers ------------------------------------------------------

    def _on_column_move ( self, event ):
        """ Handles a grid column being moved.
        """
        gsc          = self.grid_sort_column
        move, before = event.moveColumn, event.beforeColumn
        column_order = self.column_order
        column       = column_order[ move ]

        if move < before:
            column_order.insert( before, column )
            del column_order[ move ]
            if move < gsc < before:
                self.grid_sort_column = gsc - 1
            elif gsc == move:
                self.grid_sort_column = before - 1

        elif move > before:
            del column_order[ move ]
            column_order.insert( before, column )
            if before <= gsc < move:
                self.grid_sort_column = gsc + 1
            elif gsc == move:
                self.grid_sort_column = before

        if move != before:
            self.move_column( move, before )
            self.set_column_widths()

        event.Skip()


    def _on_column_resize ( self, event ):
        """ Handles the user resizing a grid column.
        """
        grid_column = event.RowOrCol
        self.column_width( grid_column, self.control.GetColSize( grid_column ) )
        self.set_column_widths()

        event.Skip()


    def _on_select_cell ( self, event ):
        """ Handles a grid cell being selected.
        """
        print "_on_select_cell"
        event.Skip()


    def _on_row_select ( self, event ):
        """ Handles a grid row being selected.
        """
        if event.Selecting():
            grid = self.control
            row  = event.TopRow
            if ((row != event.BottomRow) or
                (len( grid.GetSelectionBlockTopLeft() ) > 1)):
                grid.SelectBlock( row, 0, row, 0 )
                grid.SetGridCursor( row, 0 )

            self.set_selection( [ row ] )

        event.Skip()


    def _on_rows_select ( self, event ):
        """ Handles a set of grid rows being selected.
        """
        if event.Selecting() and (not self._no_update):
            grid = self.control
            rows = []
            for tl, br in zip( grid.GetSelectionBlockTopLeft(),
                               grid.GetSelectionBlockBottomRight() ):
                rows.extend( range( tl[0], br[0] + 1 ) )

            rows.sort()
            self.set_selection( rows )

        event.Skip()


    def _on_column_select ( self, event ):
        """ Handles a grid column being selected.
        """
        # fixme: Implement this...
        print "_on_column_select", event.GetTopRow(), event.GetBottomRow(), event.GetLeftCol(), event.GetRightCol(), event.Selecting()
        event.Skip()


    def _on_columns_select ( self, event ):
        """ Handles a set of grid columns being selected.
        """
        # fixme: Implement this...
        print "_on_columns_select", event.GetTopRow(), event.GetBottomRow(), event.GetLeftCol(), event.GetRightCol(), event.Selecting()
        event.Skip()


    def _on_cell_select ( self, event ):
        """ Handles a grid cell being selected.
        """
        # fixme: Implement this...
        print "_on_cell_select", event.GetTopRow(), event.GetBottomRow(), event.GetLeftCol(), event.GetRightCol(), event.Selecting()
        event.Skip()


    def _on_cells_select ( self, event ):
        """ Handles a set of grid cells being selected.
        """
        # fixme: Implement this...
        print "_on_cells_select", event.GetTopRow(), event.GetBottomRow(), event.GetLeftCol(), event.GetRightCol(), event.Selecting()
        event.Skip()


    def _on_click ( self, event ):
        """ Handles a grid cell being clicked with the left mouse button.
        """
        print "_on_click"
        event.Skip()


    def _on_double_click ( self, event ):
        """ Handles a grid cell being double clicked with the left mouse button.
        """
        print "_on_double_click"
        event.Skip()


    def _on_label_double_click ( self, event ):
        """ Handles a grid column label being double clicked with the left mouse
            button.
        """
        self.grid_adapter.get_column_double_clicked(
            self.data_column_for( event.Col )
        )

        event.Skip()

    #-- Toolkit Specific Method Implementations --------------------------------

    def gui_create_control ( self, parent ):
        """ Create the GUI toolkit specific version of the control.
        """
        factory = self.factory

        # Create the table view control:
        self.control = grid = Grid( parent(), -1 )

        # Set up the grid model to use:
        grid.SetTable( GridModel( self ), True )

        # Don't display any extra space around the rows and columns:
        grid.SetMargins( 0, 0 )

        # Allow columns widths of 0 (needed to allow columns to be hidden):
        grid.SetColMinimalAcceptableWidth( 0 )

        # Provides more accurate scrolling behavior without creating large
        # margins on the bottom and right. The down side is that it makes
        # scrolling using the scroll bar buttons painfully slow:
        grid.SetScrollLineX( 1 )
        grid.SetScrollLineY( 1 )

        # Enable column moving (if allowed):
        if 'shuffle' in self.operations:
            grid.EnableDragColMove()
            GridColMover( grid )
            grid.Bind( EVT_GRID_COL_MOVE, self._on_column_move, grid )

        # Set up the selection mode to use:
        grid.SetSelectionMode( SelectionMode[ factory.selection_mode ] )

        # Initialize the wx handlers:
        EVT_GRID_COL_SIZE(          grid, self._on_column_resize      )
        EVT_GRID_CELL_LEFT_CLICK(   grid, self._on_click              )
        EVT_GRID_CELL_LEFT_DCLICK(  grid, self._on_double_click       )
        EVT_GRID_LABEL_LEFT_DCLICK( grid, self._on_label_double_click )
        EVT_GRID_SELECT_CELL(       grid, self._on_select_cell        )
        EVT_GRID_RANGE_SELECT(      grid, getattr( self,
                                    '_on_%s_select' % factory.selection_mode ) )

        # Set up the column labels as required:
        if factory.show_titles:
            # Completely override the column labels behavior to make it work
            # correctly:
            clw = grid.GetGridColLabelWindow()
            clw.PushEventHandler( LabelsEventHandler( self ) )
        else:
            grid.SetColLabelSize( 0 )

        # Don't display row labels:
        grid.SetRowLabelSize( 0 )

        # Prevent the user from resizing rows:
        grid.DisableDragRowSize()

        # Set up the selection colors to use:
        adapter = self.grid_adapter
        color   = adapter.get_selected_text_color()
        if color is not None:
            grid.SetSelectionForeground( color )

        color = adapter.get_selected_bg_color()
        if color is not None:
            grid.SetSelectionBackground( color )

        # Set up the grid line visibility and color:
        show_grid = False
        if adapter.get_grid_visible():
            self.grid_line_color = grid_color = adapter.get_grid_color()
            show_grid            = (grid_color is not None)
            if show_grid:
                grid.SetGridLineColour( grid_color )

        grid.EnableGridLines( show_grid )

        # Set the starting grid row height:
        row_height = factory.row_height
        if row_height <= 0:
            # Calculate the default row height:
            row_height = (grid.GetTextExtent( 'My' )[0] + 6 +
                          (2 * ('edit' in self.operations)))

        self.row_height( row_height )

        # Set up the cell renderer to use:
        grid.SetDefaultRenderer( CellRenderer( self ) )


    def gui_dispose ( self ):
        """ Performs any GUI toolkit specific 'dispose' code.
        """
        # Remove all wx handlers:
        grid = self.control
        EVT_GRID_COL_SIZE(          grid, None )
        EVT_GRID_CELL_LEFT_CLICK(   grid, None )
        EVT_GRID_CELL_LEFT_DCLICK(  grid, None )
        EVT_GRID_LABEL_LEFT_DCLICK( grid, None )
        EVT_GRID_SELECT_CELL(       grid, None )
        EVT_GRID_RANGE_SELECT(      grid, None )

        # Restore the original column label window's behavior (if necessary):
        if self.factory.show_titles:
            grid.GetGridColLabelWindow().PopEventHandler( True )


    def gui_update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self.control is not None:
            self._content_modified()
            self.set_ui_selection()
            self._refresh()
            if self.factory.auto_scroll:
                self.control.MakeCellVisible( self.gui_item_count() - 1, 0 )


    def gui_rebuild ( self ):
        """ Rebuilds the contents of the editor's control.
        """
        pass


    def gui_item_count ( self ):
        """ Returns the number of items in the list control.
        """
        return self.control.GetNumberRows()


    def gui_deselect ( self ):
        """ Deselect any currently selected data.
        """
        self._no_update = True
        self.control.ClearSelection()
        self._no_update = False


    def gui_select_rows ( self, rows ):
        """ Selects the specified rows. Rows may be a single row or a list of
            rows.
        """
        if isinstance( rows, int ):
            rows = [ rows ]

        if len( rows ) > 0:
            grid = self.control
            self._no_update = True
            for row in rows:
                grid.SelectBlock( row, 0, row, 0, True )
            self._no_update = False


    def gui_get_selected ( self ):
        """ Returns a list of the rows of all currently selected list items.
        """
        return self.control.GetSelectedRows()


    def gui_control_width ( self ):
        """ Returns the width of the control that can contain columns (i.e.
            excluding scroll bars).
        """
        return (self.adapter.client_size[0] - scrollbar_dx)


    def gui_xy_to_row_column ( self, x, y ):
        """ Returns a tuple of the form: ( row, column, flags ) describing the
            cell containing a specified point. Also returns a flag specifying
            whether the point is below the last row (in cases where the point
            is not in a row).
        """
        row = self.control.YToRow( y )

        return ( row, self.control.XToCol( x ), row == wx.NOT_FOUND )


    def gui_column_count ( self ):
        """ Returns the number of columns in the control.
        """
        return self.control.GetNumberCols()


    def gui_column_width ( self, column, width = None ):
        """ Gets/Sets the width (in pixels) of the specified column.
        """
        if width is None:
            return self.control.GetColSize( column )

        self.control.SetColSize( column, width )


    def gui_column_visible ( self, column ):
        """ Returns whether a specified column is visible or not.
        """
        return (self.control.GetColSize( column ) > 0)


    def gui_row_height ( self, height ):
        """ Sets the row height to use.
        """
        self.control.SetDefaultRowSize( height, True )


    def gui_scroll_to ( self, row ):
        """ Make sure the specified screen row space row is visible.
        """
        self.control.MakeCellVisible( row, 0 )


    def gui_save_prefs ( self ):
        """ Returns any toolkit specific user preference data.
        """
        if self.factory.show_titles:
            return { 'order': self.column_order }

        return None


    def gui_restore_prefs ( self, data ):
        """ Restore any previously saved toolkit specific user preference data.
        """
        column_order = data.get( 'order' )
        if ((column_order is not None) and
            (len( column_order ) == len( self.column_order ))):
            self.column_order = column_order

#-------------------------------------------------------------------------------
#  'WxGridEditor' editor factory class:
#-------------------------------------------------------------------------------

class WxGridEditor ( GridEditor ):
    """ wxPython editor factory for grid editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _WxGridEditor

#-- EOF ------------------------------------------------------------------------
