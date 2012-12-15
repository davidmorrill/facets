"""
A Qt-based facets UI editor for editing gridable data (arrays, list of tuples,
lists of objects, etc).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cPickle \
    import dumps, loads

from PyQt4.QtCore \
    import QAbstractTableModel, Qt, QVariant, QModelIndex, QRect, QPoint, \
           SIGNAL

from PyQt4.QtGui \
    import QBrush, QTableView, QAbstractItemView, QHeaderView, QFontMetrics, \
           QItemSelectionModel, QStyledItemDelegate, QItemSelection, QPalette, \
           QWidget, QApplication

from facets.api \
    import Property, Int, ViewElement

from facets.ui.editors.grid_editor \
    import _GridEditor, GridEditor

from facets.ui.menu \
    import Menu

from facets.ui.action_controller \
    import ActionController

from facets.ui.pyface.timer.api \
    import do_later

from facets.ui.qt4.adapters.control \
    import control_adapter

from facets.ui.qt4.adapters.cell \
    import QtCell

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from Qt roles to method names:
RoleMap = {
    Qt.BackgroundRole:    '_data_background',
    Qt.ForegroundRole:    '_data_foreground',
    Qt.DisplayRole:       '_data_display',
    Qt.EditRole:          '_data_edit',
    Qt.DecorationRole:    '_data_image',
    Qt.FontRole:          '_data_font',
    Qt.TextAlignmentRole: '_data_text_alignment',
    Qt.ToolTipRole:       '_data_tooltip'
}

# Mapping from standard facets horizontal alignment values to Qt values:
AlignmentMap = {
    'left':   Qt.AlignLeft    + Qt.AlignVCenter,
    'center': Qt.AlignHCenter + Qt.AlignVCenter,
    'right':  Qt.AlignRight   + Qt.AlignVCenter
}

# Mapping from factory selection modes to Qt selection behaviors:
SelectionBehavior = {
    'row':     QAbstractItemView.SelectRows,
    'rows':    QAbstractItemView.SelectRows,
    'column':  QAbstractItemView.SelectColumns,
    'columns': QAbstractItemView.SelectColumns,
    'cell':    QAbstractItemView.SelectItems,
    'cells':   QAbstractItemView.SelectItems
}

# Mapping from factory selection modes to Qt selection modes:
SelectionMode = {
    'row':     QAbstractItemView.SingleSelection,
    'rows':    QAbstractItemView.ExtendedSelection,
    'column':  QAbstractItemView.SingleSelection,
    'columns': QAbstractItemView.ExtendedSelection,
    'cell':    QAbstractItemView.SingleSelection,
    'cells':   QAbstractItemView.ExtendedSelection
}

# Mapping from editor drag and drop mode to equivalent Qt mode:
DragDropMode = {
    'drag_drop': QAbstractItemView.DragDrop,
    'drag_only': QAbstractItemView.DragOnly,
    'drop_only': QAbstractItemView.DropOnly,
    'move_only': QAbstractItemView.InternalMove,
    'none':      QAbstractItemView.NoDragDrop
}

# The width of a Qt vertical scroll bar:
# fixme: Try to find a more robust definition of this value...
scrollbar_dx = 19

# The mime type used to represent Python object state data:
PythonMimeType = 'application/x-pythonobjectstate'

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The cell adapter used to render each cell:
cell_adapter = QtCell()

#-------------------------------------------------------------------------------
#  'QGridModel' class:
#-------------------------------------------------------------------------------

class QGridModel ( QAbstractTableModel ):
    """ The model for grid data.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor, parent ):
        """ Initialise the object.
        """
        QAbstractTableModel.__init__( self, parent )

        self.setSupportedDragActions( Qt.CopyAction | Qt.MoveAction )

        self._editor = editor
        self._row    = editor.data_row_for
        self._font   = set()

    #-- QAbstractTableModel Interface Implementation ---------------------------

    def setData ( self, index, value, role ):
        """ Reimplemented to allow setting data.
        """
        if role == Qt.EditRole:
            # This works because a Facets Editor will have already set the value
            # on the object, and so we don't need to do anything here:
            return True

        return QAbstractTableModel.setData( self, index, value, role )


    def data ( self, mi, role ):
        """ Reimplemented to return the data.
        """
        row = mi.row()

        return getattr( self, RoleMap.get( role, '_data_default' ) )(
                                           self._row( row ), mi.column(), row )


    def _data_display ( self, row, column, screen_row ):
        """ Returns the data to be displayed.
        """
        return QVariant( self._editor.grid_adapter.get_text( row, column ) )


    def _data_edit ( self, row, column, screen_row ):
        """ Returns the data to be edited.
        """
        return QVariant( self._editor.grid_adapter.get_content( row, column ) )


    def _data_image ( self, row, column, screen_row ):
        """ Returns the image to be displayed.
        """
        image = self._editor.grid_adapter.get_image( row, column )
        if image is None:
            return QVariant()

        return QVariant( image.icon )


    def _data_foreground ( self, row, column, screen_row ):
        """ Returns the text color to use.
        """
        color = self._editor.grid_adapter.get_text_color( row, column,
                                                          screen_row )
        if color is not None:
            return QVariant( QBrush( color ) )

        return QVariant()


    def _data_background ( self, row, column, screen_row ):
        """ Returns the background color brush to use.
        """
        color = self._editor.grid_adapter.get_bg_color( row, column,
                                                        screen_row )
        if color is not None:
            return QVariant( QBrush( color ) )

        return QVariant()


    def _data_font ( self, row, column, screen_row ):
        """ Returns the font to use.
        """
        editor = self._editor
        font   = editor.grid_adapter.get_font( row, column )
        if font is not None:
            if font not in self._font:
                self._font.add( font )
                editor.row_height( QFontMetrics( font ).height() + 2 )

            return QVariant( font )

        return QVariant()


    def _data_text_alignment ( self, row, column, screen_row ):
        """ Returns the text alignment to use.
        """
        return QVariant( AlignmentMap.get(
            self._editor.grid_adapter.get_alignment( row, column ),
            Qt.AlignLeft
        ) )


    def _data_tooltip ( self, row, column, screen_row ):
        """ Returns the tooltip to use.
        """
        adapter = self._editor.grid_adapter
        tooltip = adapter.get_tooltip( row, column )
        if (tooltip == '') and adapter.get_auto_tooltip( row, column ):
            tooltip = adapter.get_text( row, column )

        return QVariant( tooltip )


    def _data_default ( self, row, column, screen_row ):
        """ Returns the default data for roles we don't handle.
        """
        return QVariant()


    def headerData ( self, section, orientation, role ):
        """ Reimplemented to return the header data.
        """
        if orientation == Qt.Horizontal:
            return getattr( self,
                '_header' + RoleMap.get( role, '_data_default' ) )( section )

        return QVariant()


    def _header_data_display ( self, column ):
        """ Returns the header data text.
        """
        return QVariant( self._editor.grid_adapter.get_title( column ) )


    def _header_data_image ( self, column ):
        """ Returns the header image to be displayed.
        """
        image = self._editor.grid_adapter.get_column_image( column )
        if image is None:
            return QVariant()

        return QVariant( image.icon )


    def _header_data_foreground ( self, column ):
        """ Returns the header text color to use.
        """
        color = self._editor.grid_adapter.get_column_text_color( column )
        if color is not None:
            return QVariant( QBrush( color ) )

        return QVariant()


    def _header_data_background ( self, column ):
        """ Returns the header background color brush to use.
        """
        color = self._editor.grid_adapter.get_column_bg_color( column )
        if color is not None:
            return QVariant( QBrush( color ) )

        return QVariant()


    def _header_data_font ( self, column ):
        """ Returns the header font to use.
        """
        font = self._editor.grid_adapter.get_column_font( column )
        if font is not None:
            return QVariant( font )

        return QVariant()


    def _header_data_text_alignment ( self, column ):
        """ Returns the header text alignment to use.
        """
        return QVariant( AlignmentMap.get(
            self._editor.grid_adapter.get_alignment( 0, column ),
            Qt.AlignLeft ) )


    def _header_data_tooltip ( self, column ):
        """ Returns the header tooltip to use.
        """
        return QVariant(
            self._editor.grid_adapter.get_column_tooltip( column ) )


    def _header_data_default ( self, column ):
        """ Returns the default header data for roles we don't handle.
        """
        return QVariant()


    def rowCount ( self, mi ):
        """ Reimplemented to return the number of rows.
        """
        return self._editor.rows


    def columnCount ( self, mi ):
        """ Reimplemented to return the number of columns.
        """
        return len( self._editor.grid_adapter.columns )


    def flags ( self, index ):
        """ Returns the set of things allowed for the specified item index.
        """
        row     = self._row( index.row() )
        column  = index.column()
        adapter = self._editor.grid_adapter
        result  = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDropEnabled

        if ((self._editor._in_popup is not True) and
            ('edit' in self._editor.operations)  and
            adapter.get_can_edit( row, column )):
            result |= Qt.ItemIsEditable

        if adapter.get_drag( row, column ) is not None:
            result |= Qt.ItemIsDragEnabled

        return result


    def mimeTypes ( self ):
        """ Returns the set of mime types that drag data can be encoded in.
        """
        result = QAbstractTableModel.mimeTypes( self )
        result.append( PythonMimeType )

        return result


    def mimeData ( self, indices ):
        """ Returns the serialized MIME data for the specified list of model
            indices.
        """
        result   = QAbstractTableModel.mimeData( self, indices )
        get_drag = self._editor.grid_adapter.get_drag
        rows     = set()
        items    = []
        for index in indices:
            row    = self._row( index.row() )
            column = index.column()
            if row not in rows:
                rows.add( row )
                item = get_drag( row, column )
                if item is not None:
                    items.append( item )

        result.setData( PythonMimeType, dumps( items, -1 ) )
        self._editor.drag_rows( list( rows ) )

        return result


    def dropMimeData ( self, mime_data, drop_action, row, column, parent ):
        """ Handles the data supplied by a drag and drop operation that ended
            with the given action. Returns True if the data and action can be
            handled by the model; otherwise returns False.
        """
        # Save whether the associated editor is in the dragging state (we'd let
        # the editor figure it out, but the state seems to change by the time
        # the editor method below is called):
        dragging = (self._editor.control.state() ==
                    QAbstractItemView.DraggingState)

        if mime_data.hasFormat( PythonMimeType ):
            try:
                data = loads( str( mime_data.data( PythonMimeType ) ) )
                self._editor.data_dropped_on( self._row( parent.row() ),
                                              parent.column(), data, dragging )

                return True
            except:
                pass

        return QAbstractTableModel.dropMimeData( self, mime_data, drop_action,
                                                 row, column, parent )


    def supportedDropActions ( self ):
        """ Returns which drop operations are supported by the model.
        """
        return (Qt.CopyAction | Qt.MoveAction)


    def sort ( self, column, sort_order = Qt.AscendingOrder ):
        """ Sort the specified column in the specified sort_order.
        """
        editor  = self._editor
        adapter = editor.grid_adapter
        if adapter.get_sortable( column ):
            editor.sort_ascending = (sort_order == Qt.AscendingOrder)
            editor.sorter         = adapter.get_sorter( column )

#-------------------------------------------------------------------------------
#  'QGridDelegate' class:
#-------------------------------------------------------------------------------

class QGridDelegate ( QStyledItemDelegate ):
    """ Custom item delegate for displaying and editing grid data.
    """

    def __init__ ( self, parent, editor, grid_color, selection_color ):
        QStyledItemDelegate.__init__( self, parent )

        self._editor          = editor
        self._grid_color      = grid_color
        self._selection_color = selection_color


    def createEditor ( self, parent, option, index ):
        """ Handles a request to create a cell editor.
        """
        # Mark the editor as currently performing an in-cell edit so that
        # facet changes to the edited object won't cause the grid to be
        # refreshed:
        editor              = self._editor
        editor.editing     += 1
        editor._edit_row    = index.row()
        editor._edit_column = index.column()

        return self._editor.edit_cell( parent, index.row(), index.column() )


    def paint ( self, painter, option, index ):
        """ Handles a request to paint a specific cell.
        """
        editor    = self._editor
        index_row = index.row()
        row       = editor.data_row_for( index_row )
        column    = index.column()
        rect      = option.rect
        xl        = rect.x()
        yt        = rect.y()
        dx        = rect.width()
        dy        = rect.height()

        if self._grid_color is not None:
            dx         -=1
            dy         -= 1
            xr          = xl + dx
            yb          = yt + dy
            option.rect = QRect( xl, yt, dx, dy )
            pen         = painter.pen()
            painter.setPen( self._grid_color )
            painter.drawLine( xl, yb, xr, yb )
            painter.drawLine( xr, yt, xr, yb )
            painter.setPen( pen )

        if (index_row == editor._edit_row) and (column == editor._edit_column):
            painter.setPen( Qt.NoPen )
            painter.setBrush( QBrush( self._selection_color ) )
            painter.drawRect( xl, yt, dx, dy )

            return

        cell_adapter.init(
            painter, option, editor.grid_adapter, row, column, index_row
        )
        painter.save()
        editor.paint_cell( cell_adapter )
        painter.restore()

#-------------------------------------------------------------------------------
#  'QGridView' class:
#-------------------------------------------------------------------------------

class QGridView ( QTableView ):
    """ Subclass of the standard QTableView to add grid editor specific code.
    """

    def contextMenuEvent ( self, event ):
        """ Handles a context menu event for the grid editor control.
        """
        self.editor.display_context_menu( event )

#-------------------------------------------------------------------------------
#  'QGridHeader' class:
#-------------------------------------------------------------------------------

class QGridHeader ( QHeaderView ):
    """ Subclass of the standard QHeaderView to add grid editor specific code.
    """

    def contextMenuEvent ( self, event ):
        """ Handles a context menu event for the grid editor control.
        """
        self.editor.display_header_context_menu( event )

#-------------------------------------------------------------------------------
#  '_QtGridEditor' class:
#-------------------------------------------------------------------------------

class _QtGridEditor ( _GridEditor ):
    """ A Qt specific facets UI editor for editing gridable data (arrays, list
        of tuples, lists of objects, etc).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The value of the current cell being edited:
    cell_value  = Property
    cell_value_ = Property

    # The item row for the cell currently being edited:
    cell_row = Int

    # The item column for the cell currently being edited:
    cell_column = Int

    #-- Property Implementations -----------------------------------------------

    def _get_cell_value ( self ):
        return self.grid_adapter.get_content( self.cell_row, self.cell_column )

    def _set_cell_value ( self, value ):
        if self._in_popup or (self._editor is not None):
            self.grid_adapter.set_text( self.cell_row, self.cell_column, value )


    def _get_cell_value_ ( self ):
        return self.cell_value

    #-- Public Methods ---------------------------------------------------------

    def edit_cell ( self, parent, row, column ):
        """ Returns the editor widget to use for editing a specified cell's
            value.
        """
        self.cell_row = self.data_row_for( row )

        # Get the editor factory to use. If none, exit (read-only cell):
        editor_factory = self.grid_adapter.get_editor( self.cell_row, column )
        if editor_factory is None:
            return None

        # Create the requested type of editor from the editor factory:
        # Note: We save the editor reference so that the editor doesn't get
        # garbage collected too soon.
        self.cell_column = column
        object, name     = self.grid_adapter.get_alias(  self.cell_row, column )
        editor           = editor_factory.simple_editor(
                               self.ui, object, name, '' ).set(
                               item        = self.item,
                               object_name = '' )

        # Tell the editor to actually build the editing widget:
        editor.prepare( control_adapter( parent ) )

        # Make sure that the editor is a control (and not a layout):
        self._editor = editor
        control      = editor.control
        if not isinstance( control, QWidget ):
            layout  = control
            control = QWidget( parent )
            control.setLayout( layout )
            layout.setContentsMargins( 5, 0, 5, 0 )

        control._editor = editor

        header       = self.control.horizontalHeader()
        column_width = header.sectionSize( column )
        if self.factory.resize_cell_editor:
            control.setGeometry( 0, 0, column_width, self.height )
        else:
            # Adjust the row height of the grid row to fit the editor control:
            height = control.height()
            if height > self.height:
                control._row = row
                self.control.verticalHeader().resizeSection( row, height )

            # Resize the grid column width to fit the editor if necessary:
            width = control.width()
            if width > column_width:
                control._column = column
                control._width  = column_width
                header.resizeSection( column, width )

        # Return the editing widget as the result:
        return control


    def display_context_menu ( self, event ):
        """ Displays the context menu for the cell specified by the
            QContextMenuEvent *event*.
        """
        row, column, flags = self.gui_xy_to_row_column( event.x(), event.y() )
        if (row >= 0) and (column >= 0):
            adapter = self.grid_adapter
            menu    = adapter.get_menu( self.data_row_for( row ), column )
            if isinstance( menu, Menu ):
                self._show_menu( menu, event.globalPos(), ActionController(
                    ui      = self.ui,
                    object  = adapter.item,
                    context = { 'adapter': adapter,
                                'handler': self.ui.handler,
                                'object':  adapter.item }
                ) )


    def display_header_context_menu ( self, event ):
        """ Displays the context menu for the header section specified by the
            QContextMenuEvent *event*.
        """
        column = self.control.horizontalHeader().logicalIndexAt( event.pos() )
        if column >= 0:
            adapter = self.grid_adapter
            menu    = adapter.get_column_menu( column )
            if isinstance( menu, Menu ):
                self._show_menu(  menu, event.globalPos(), ActionController(
                    ui      = self.ui,
                    context = { 'adapter': adapter, 'handler': self.ui.handler }
                ) )

    #-- Drag and Drop Event Handlers -------------------------------------------

    def drag_rows ( self, rows ):
        """ Save the list of rows being dragged.
        """
        self._drag_rows = rows[:]


    def data_dropped_on ( self, row, column, data, dragging ):
        """ Handles a Python object being dropped on the grid editor.
        """
        # If we have a valid drop target row, proceed:
        if not isinstance( data, list ):
            # Handle the case of just a single item being dropped:
            self._dropped_on( row, column, data )
        else:
            # Handles the case of a list of items being dropped, being
            # careful to preserve the original order of the source items if
            # possible:
            data.reverse()
            for item in data:
                self._dropped_on( row, column, item )

        # If this was an inter-list drag...
        if dragging and (self._drag_rows is not None):
            # Then delete all of the original items (in reverse order from
            # highest to lowest, so the indices don't need to be adjusted):
            adapter = self.grid_adapter
            rows    = self._drag_rows
            rows.sort( lambda l, r: l >= r )
            for row in rows:
                adapter.delete( row )

    #-- Private Methods --------------------------------------------------------

    def _refresh_row ( self, row ):
        """ Updates the editor control when a specified table row changes.
        """
        control = self.control
        rect    = control.visualRect( control.model().index( row, 0 ) )
        rect.setWidth( control.width() )
        control.update( rect )


    def _edit_current ( self ):
        """ Allows the user to edit the current item in the list control.
        """
        if 'edit' in self.operations:
            selected = self.gui_get_selected()
            if len( selected ) == 1:
                control = self.control
                index   = control.model().index( selected[0], 0 )
                control.setCurrentIndex( index )
                control.edit( index )


    def _row_selection_modified ( self, selected, deselected ):
        """ Handles a grid row being selected/deselected.
        """
        if not self._no_update:
            self.set_selection(
                [ index.row()
                  for index in self.control.selectionModel().selectedRows() ] )

    _rows_selection_modified = _row_selection_modified


    def _column_selection_modified ( self, selected, deselected ):
        """ Handles a grid column being selected/deselected.
        """
        if not self._no_update:
            self.set_selection( [ index.column()
                for index in self.control.selectionModel().selectedColumns()
            ] )

    _columns_selection_modified = _column_selection_modified


    def _cell_selection_modified ( self, selected, deselected ):
        """ Handles a grid cell being selected/deselected.
        """
        # fixme: Implement this...
        raise NotImplementedError

    _cells_selection_modified = _cell_selection_modified


    def _editing_completed ( self, control, hint ):
        """ Handles an in-cell edit being completed.
        """
        # Clean up the cell editor (if necessary):
        editor = getattr( control, '_editor', None )
        if editor is not None:
            editor.dispose()

        grid = self.control
        if grid is not None:
            # Restore the size of the edited grid row (if necessary):
            row = getattr( control, '_row', None )
            if row is not None:
                header = grid.verticalHeader()
                header.resizeSection( row, header.defaultSectionSize() )

            # Restore the size of the edited grid column (if necessary):
            column = getattr( control, '_column', None )
            if column is not None:
                do_later( self._restore_column_width, column, control._width )

            self.editing -= 1
            if self.editing == 0:
                self._edit_row = self._editor = None
                self.update_editor()


    def _restore_column_width ( self, column, width ):
        """ Restores the grid editor column width after an edit completes (if
            necessary).
        """
        if self.control is not None:
            if (self._edit_row is None) or (self._edit_column != column):
                self.control.horizontalHeader().resizeSection( column, width )
            else:
                control         = self._editor.control
                control._column = column
                control._width  = width


    def _hide_show_section ( self, column, show ):
        """ Handles hiding/showing a column section.
        """
        header = self.control.horizontalHeader()
        if show:
            if header.sectionsHidden():
                self._no_update = True
                for i in xrange( header.count() ):
                    header.showSection( i )
                self._no_update = False

                self.set_column_widths()

        else:
            n = header.count()
            for i in xrange( n ):
                n -= header.isSectionHidden( i )
            if n > 1:
                self._no_update = True
                header.hideSection( column )
                self._no_update = False
                self.set_column_widths()


    def _handle_click ( self, column, allow_shift = True ):
        """ Perform 'special' click handling on either a cell or column header.
            Returns True if special handling occurred, or False to indicate that
            normal handling can proceed.
        """
        modifiers = int( QApplication.keyboardModifiers() )
        control   = modifiers & Qt.ControlModifier
        if allow_shift and (modifiers & Qt.ShiftModifier):
            do_later( self._hide_show_section, column, control )

            return True

        if control:
            self.column_width( column )
            self.set_column_widths()

            return True

        return False


    def _on_section_resized ( self, column, old, new ):
        """ Handles a column being resized.
        """
        if not self._no_update:
            self.column_width( column, new )
            self.set_column_widths()


    def _on_section_pressed ( self, column ):
        """ Handles a column being pressed with a mouse button.
        """
        self._handle_click( column, True )


    def _on_section_click ( self, column ):
        """ Handles the user clicking on a section header.
        """
        self._set_section_bounds( column )
        self.grid_adapter.get_column_clicked( column )


    def _on_section_double_click ( self, column ):
        """ Handles the user double clicking on a section header.
        """
        self._set_section_bounds( column )
        self.grid_adapter.get_column_double_clicked( column )


    def _on_click ( self, index ):
        """ Handles the user clicking on a grid cell.
        """
        self._in_popup = False
        if not self._handle_click( index.column(), False ):
            self._handle_event( 'get_clicked', index )


    def _on_double_click ( self, index ):
        """ Handles the user double clicking on a grid cell.
        """
        self._handle_event( 'get_double_clicked', index )


    def _handle_event ( self, method, index ):
        """ Handles the user clicking on a grid cell.
        """
        self._set_bounds( index )
        self.cell_row    = row    = self.data_row_for( index.row() )
        self.cell_column = column = index.column()
        adapter          = self.grid_adapter
        result           = getattr( adapter, method )( row, column )
        if result == 'edit':
            if (('edit' in self.operations) and
                adapter.get_can_edit( row, column )):
                #self.control.setCurrentIndex( index )
                self.control.edit( index )
        elif result in ( 'popup', 'popout' ):
            self._in_popup = True
            adapter.popup_for( kind = result )
        elif isinstance( result, ( ViewElement, basestring ) ):
            self._in_popup = True
            adapter.popup_for( result )


    def _set_bounds ( self, index ):
        """ Sets the grid adapter bounds to the absolute screen coordinates of
            the specified grid index.
        """
        rect = self.control.visualRect( index )
        tl   = self.control.viewport().mapToGlobal( rect.topLeft() )
        self.grid_adapter.bounds = ( tl.x(), tl.y(),
                                     rect.width(), rect.height() )


    def _set_section_bounds ( self, column ):
        """ Sets the grid adapter to the absolute screen coordinates of the
            specified section header column.
        """
        header   = self.control.horizontalHeader()
        x        = header.sectionViewportPosition( column )
        dx       = header.sectionSize( column )
        viewport = header.viewport()
        tl       = viewport.mapToGlobal( QPoint( x, 0 ) )
        self.grid_adapter.bounds = ( tl.x(), tl.y(), dx, viewport.height() )


    def _show_menu ( self, menu, position, controller ):
        """ Displays the context menu specified by *menu* at the screen position
            specified by *position* using the ActionController specified by
            *controller*.
        """
        menu.create_menu( self.control, controller ).exec_(
            QPoint( position.x() - 20, position.y() - 10 )
        )

    #-- Toolkit Specific Method Implementations --------------------------------

    def gui_create_control ( self, parent ):
        """ Create the GUI toolkit specific version of the control.
        """
        factory = self.factory

        # Create the table view control:
        self.control   = control = QGridView( parent() )
        control.editor = self
        control.setModel( QGridModel( self, control ) )

        # Configure the column headings:
        vheader = control.verticalHeader()
        vheader.hide()
        vheader.setResizeMode( QHeaderView.Fixed )

        if factory.show_titles:
            hheader        = QGridHeader( Qt.Horizontal )
            hheader.editor = self
            hheader.setHighlightSections( False )
            hheader.setClickable( True )
            hheader.setMovable( 'shuffle' in self.operations )
            hheader.connect( hheader,
                             SIGNAL( 'sectionResized(int,int,int)' ),
                             self._on_section_resized )
            hheader.connect( hheader, SIGNAL( 'sectionPressed(int)' ),
                             self._on_section_pressed )
            hheader.connect( hheader, SIGNAL( 'sectionClicked(int)' ),
                             self._on_section_click )
            hheader.connect( hheader, SIGNAL( 'sectionDoubleClicked(int)' ),
                             self._on_section_double_click )

            control.setHorizontalHeader( hheader )
        else:
            control.horizontalHeader().hide()

        # Set up the selection style to use:
        sm = factory.selection_mode
        control.setSelectionBehavior( SelectionBehavior[ sm ] )
        control.setSelectionMode( SelectionMode[ sm ] )

        # Set up the drag and drop mode:
        drag_drop = factory.drag_drop
        control.setDragDropMode( DragDropMode[ factory.drag_drop ] )
        if drag_drop in ( 'drag_drop', 'drag_only', 'move_only' ):
            control.setDragEnabled( True )

        if drag_drop in ( 'drag_drop', 'drop_only', 'move_only' ):
            control.setAcceptDrops( True )
            control.setDropIndicatorShown( True )

        # Set up event listeners on the selection model:
        control.connect( control.selectionModel(),
            SIGNAL( 'selectionChanged(QItemSelection, QItemSelection)' ),
            getattr( self, '_%s_selection_modified' % sm )
        )

        # Set up the grid line visibility and color:
        adapter = self.grid_adapter
        if adapter.get_grid_visible():
            grid_color = adapter.get_grid_color()
            if grid_color is not None:
                control.setShowGrid( False )
        else:
            grid_color = None
            control.setShowGrid( False )

        # Set the starting grid row height:
        row_height = factory.row_height
        if row_height <= 0:
            # Calculate the default row height:
            row_height = (QFontMetrics( control.font() ).height() +
                          6 + (2 * ('edit' in self.operations)))

        self.row_height( row_height )

        # Set up the item delegate:
        delegate = QGridDelegate(
            control.itemDelegate().parent(), self, grid_color,
            control.palette().color( QPalette.Highlight )
        )

        control.setItemDelegate( delegate )
        control.connect( delegate, SIGNAL(
            'closeEditor(QWidget *, QAbstractItemDelegate::EndEditHint)' ),
            self._editing_completed )

        # Set up the cell click handler:
        control.connect( control, SIGNAL( 'clicked(QModelIndex)' ),
                         self._on_click )
        control.connect( control, SIGNAL( 'doubleClicked(QModelIndex)' ),
                         self._on_double_click )

        # Set up the initial sort order if sorting is supported:
        if 'sort' in self.operations:
            index  = 0
            column = factory.sort_column
            if column != '':
                try:
                    index = adapter.column_map.index( column )
                except:
                    try:
                        index = adapter.label_map.index( column )
                    except:
                        print ("'%s' is not a valid GridEditor 'sort_column' "
                               "column name and is being ignored." % column)

            self.sorter         = adapter.get_sorter( index )
            self.sort_ascending = factory.sort_ascending
            control.sortByColumn(
                index,
                ( Qt.DescendingOrder, Qt.AscendingOrder )[ self.sort_ascending ]
            )


    def gui_dispose ( self ):
        """ Performs any GUI toolkit specific 'dispose' code.
        """
        self.control.editor = None


    def gui_update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if self.control is not None:
            # Clean up any active cell editor:
            if self._editor is not None:
                editor, self._editor = self._editor, None
                self.control.closeEditor( editor.control, 0 )
                editor.dispose()
                self._edit_row = None
                self.editing   = 0

            self.control.model().reset()
            self.set_column_widths()
            self.set_ui_selection()
            if self.factory.auto_scroll:
                self.control.scrollToBottom()


    def gui_rebuild ( self ):
        """ Rebuilds the contents of the editor's control.
        """
        if self.control is not None:
            enabled = False
            if 'sort' in self.operations:
                adapter = self.grid_adapter
                for i in xrange( len( adapter.columns ) ):
                    if adapter.get_sortable( i ):
                        enabled = True
                        break

            self.control.setSortingEnabled( enabled )


    def gui_item_count ( self ):
        """ Returns the number of items in the list control.
        """
        return self.control.model().rowCount( QModelIndex() )


    def gui_deselect ( self ):
        """ Deselect any currently selected data.
        """
        self._no_update = True
        self.control.selectionModel().clearSelection()
        self._no_update = False


    def gui_select_rows ( self, rows ):
        """ Selects the specified rows. Rows may be a single row or a list of
            rows.
        """
        if isinstance( rows, int ):
            rows = [ rows ]

        if len( rows ) > 0:
            self._no_update = True
            sm              = self.control.selectionModel()
            selection       = sm.selection()
            model_index     = self.control.model().index
            for row in rows:
                index = model_index( row, 0 )
                selection.merge( QItemSelection( index, index ),
                                 QItemSelectionModel.Select )

            sm.select( selection, QItemSelectionModel.Select |
                                  QItemSelectionModel.Rows )
            self._no_update = False


    def gui_select_columns ( self, columns ):
        """ Selects the specified columns. Columns may be a single column or a
            list of columns.
        """
        if isinstance( columns, int ):
            columns = [ columns ]

        if len( columns ) > 0:
            self._no_update = True
            sm              = self.control.selectionModel()
            selection       = sm.selection()
            model_index     = self.control.model().index
            for column in columns:
                index = model_index( 0, column )
                selection.merge( QItemSelection( index, index ),
                                 QItemSelectionModel.Select )

            sm.select( selection, QItemSelectionModel.Select |
                                  QItemSelectionModel.Columns )
            self._no_update = False


    def gui_get_selected ( self ):
        """ Returns a list of the rows of all currently selected list items.
        """
        return [ index.row()
                 for index in self.control.selectionModel().selectedRows() ]


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
        row = self.control.rowAt( y )

        return ( row, self.control.columnAt( x ), row == -1 )


    def gui_column_count ( self ):
        """ Returns the number of columns in the control.
        """
        return self.control.model().columnCount( QModelIndex() )


    def gui_column_width ( self, column, width = None ):
        """ Gets/Sets the width (in pixels) of the specified column.
        """
        if width is None:
            return self.control.columnWidth( column )

        self._no_update = True
        self.control.setColumnWidth( column, width )
        self._no_update = False


    def gui_column_visible ( self, column ):
        """ Returns whether a specified column is visible or not.
        """
        return (not self.control.horizontalHeader().isSectionHidden( column ))


    def gui_row_height ( self, height ):
        """ Sets the row height to use.
        """
        self.control.verticalHeader().setDefaultSectionSize( height )
        self.control.model().reset()


    def gui_scroll_to ( self, row ):
        """ Make sure the specified screen row space row is visible.
        """
        control = self.control
        control.scrollTo( control.model().index( row, 0 ),
                          QAbstractItemView.PositionAtCenter )


    def gui_save_prefs ( self ):
        """ Returns any toolkit specific user preference data.
        """
        if self.factory.show_titles:
            header = self.control.horizontalHeader()
            n      = header.count()
            return {
                'hidden': [ header.isSectionHidden( i ) for i in xrange( n ) ],
                'order':  [ header.logicalIndex( i )    for i in xrange( n ) ]
            }

        return None


    def gui_restore_prefs ( self, data ):
        """ Restore any previously saved toolkit specific user preference data.
        """
        if self.factory.show_titles:
            self._no_update = True
            header          = self.control.horizontalHeader()
            n               = header.count()
            hidden          = data.get( 'hidden' )
            if (hidden is not None) and (n == len( hidden )):
                for i in xrange( n ):
                    header.setSectionHidden( i, hidden[i] )

            order = data.get( 'order' )
            if (order is not None) and (n == len( order )):
                current = range( n )
                for i, j in enumerate( order ):
                    if j != current[i]:
                        k = current.index( j )
                        header.moveSection( k, i )
                        del current[k]
                        current.insert( i, j )

            self._no_update = False

#-------------------------------------------------------------------------------
#  'QtGridEditor' editor factory class:
#-------------------------------------------------------------------------------

class QtGridEditor ( GridEditor ):
    """ Qt editor factory for grid editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _QtGridEditor

#-- EOF ------------------------------------------------------------------------