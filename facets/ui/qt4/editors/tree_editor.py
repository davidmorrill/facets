"""
Defines the tree editor and the tree editor factory, for the PyQt user
interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import copy

from PyQt4.QtCore \
    import Qt, SIGNAL, QPoint

from PyQt4.QtGui                                                              \
    import QTreeWidget, QTreeWidgetItem, QStyle, QIcon, QMessageBox, QPixmap, \
           QPainter, QDrag, QAbstractItemView, QColor, QBrush

from facets.ui.pyface.resource_manager \
    import resource_manager

from facets.api                                                                \
    import HasFacets, Any, Dict, Enum, Bool, Int, List, Instance, Str, Event,  \
           TreeNode, ObjectTreeNode, MultiTreeNode, Editor, EditorFactory,     \
           ATheme, Theme, Image, toolkit

from facets.core.facet_base \
    import SequenceTypes

from facets.ui.undo \
    import ListUndoItem

from facets.ui.ui_facets \
    import image_for

from facets.ui.tree_node \
    import ITreeNodeAdapterBridge, COLLAPSED, CLOSED, EXPANDED

from facets.ui.menu \
    import Menu, Action, Separator

from facets.ui.graphics_text \
    import GraphicsText

from facets.ui.dock.dock_window_theme \
    import DockWindowTheme

from facets.ui.dock.api \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl

from facets.ui.pyface.timer.api \
    import do_after

from facets.ui.qt4.adapters.control \
    import control_adapter

from facets.ui.qt4.adapters.graphics \
    import QtGraphics

from facets.ui.qt4.clipboard \
    import clipboard

from facets.ui.qt4.adapters.drag \
    import PyMimeData

from facets.ui.qt4.helper \
    import pixmap_cache, Orientation

#-------------------------------------------------------------------------------
#  The core tree node menu actions:
#-------------------------------------------------------------------------------

NewAction    = 'NewAction'
CopyAction   = Action( name         = 'Copy',
                       action       = 'editor._menu_copy_node',
                       enabled_when = 'editor._is_copyable(object)' )
CutAction    = Action( name         = 'Cut',
                       action       = 'editor._menu_cut_node',
                       enabled_when = 'editor._is_cutable(object)' )
PasteAction  = Action( name         = 'Paste',
                       action       = 'editor._menu_paste_node',
                       enabled_when = 'editor._is_pasteable(object)' )
DeleteAction = Action( name         = 'Delete',
                       action       = 'editor._menu_delete_node(selected)',
                       enabled_when = 'editor._is_deletable(selected)' )
RenameAction = Action( name         = 'Rename',
                       action       = 'editor._menu_rename_node',
                       enabled_when = 'editor._is_renameable(object)' )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from factory selection modes to Qt selection modes:
SelectionMode = {
    'item':  QAbstractItemView.SingleSelection,
    'items': QAbstractItemView.ExtendedSelection
}

#-------------------------------------------------------------------------------
#  'TreeEditor' class:
#-------------------------------------------------------------------------------

class TreeEditor ( EditorFactory ):
    """ PyQt editor factory for tree editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Supported TreeNode objects:
    nodes = List( TreeNode )

    # Mapping from TreeNode tuples to MultiTreeNodes:
    multi_nodes = Dict

    # Are the individual nodes editable?
    editable = Bool( True )

    # Is the editor shared across trees?
    shared_editor = Bool( False )

    # Reference to a shared object editor:
    editor = Instance( EditorFactory )

    # The DockWindow graphical theme:
    dock_theme = Instance( DockWindowTheme )

    # Show icons for tree nodes?
    show_icons = Bool( True )

    # Hide the tree root node?
    hide_root = Bool( False )

    # Layout orientation of the tree and the editor:
    orientation = Orientation

    # Number of tree levels (down from the root) that should be automatically
    # opened:
    auto_open = Int

    # Called when a node is selected:
    on_select = Any

    # Called when a node is clicked:
    on_click = Any

    # Called when a node is double-clicked:
    on_dclick = Any

    # The selection mode of the tree. The meaning of the various values are as
    # follows:
    #
    # item
    #    At most one item can be selected at once. This is the default.
    # items
    #    More than one item can be selected at once.
    selection_mode = Enum( 'item', 'items' )

    # The optional extended name of the facet that the current selection is
    # synced with:
    selected = Str

    # The optional extended name of the facet containing an item that should be
    # made visible within the tree editor view, scrolling the view if necessary:
    show_item = Str

    # The optional extended facet name of the facet that should be assigned
    # a node object when a tree node is clicked on (Note: If you want to
    # receive repeated clicks on the same node, make sure the facet is defined
    # as an Event):
    click = Str

    # The optional extended facet name of the facet that should be assigned
    # a node object when a tree node is double-clicked on (Note: if you want to
    # receive repeated double-clicks on the same node, make sure the facet is
    # defined as an Event):
    dclick = Str

    # The optional extended facet name of the facet event that is fired
    # whenever the application wishes to veto a tree action in progress (e.g.
    # double-clicking a non-leaf tree node normally opens or closes the node,
    # but if you are handling the double-click event in your program, you may
    # wish to veto the open or close operation). Be sure to fire the veto event
    # in the event handler triggered by the operation (e.g. the 'dclick' event
    # handler:
    veto = Str

    # Mode for lines connecting tree nodes:
    #
    # * 'appearance': Show lines only when they look good.
    # * 'on': Always show lines.
    # * 'off': Don't show lines.
    # Note: This facet is ignored for Qt.
    lines_mode = Enum ( 'appearance', 'on', 'off' )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of tree editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the tree editor is scrollable? This value overrides the default:
    scrollable = True

    # Allows an external agent to set the tree selection:
    selection = Event

    # The currently selected item:
    selected = Any

    # The current item that should be made visible in the tree view:
    show_item = Any

    # The event fired when a tree node is clicked on:
    click = Event

    # The event fired when a tree node is double-clicked on:
    dclick = Event

    # The event fired when the application wants to veto an operation:
    veto = Event

    # The theme used to render a drag image:
    drag_theme = ATheme( Theme( '@xform:b6?H60L30S16a20',
                                content = ( 4, 4, 0, 4 ) ) )

    #-- Private Facets ---------------------------------------------------------

    # Used to convert icon string names to images:
    image = Image

    # Cache of tree node icons:
    _icon_cache = Any( {} )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory      = self.factory
        self._editor = None

        if factory.editable:

            # Check to see if the tree view is based on a shared facet editor:
            if factory.shared_editor:
                factory_editor = factory.editor

                # If this is the editor that defines the facet editor panel:
                if factory_editor is None:

                    # Remember which editor has the facet editor in the factory:
                    factory._editor = self

                    # Create the facet editor panel:
                    self.adapter = control = toolkit().create_panel( parent )
                    control._node_ui = control._editor_nid = None

                    # Check to see if there are any existing editors that are
                    # waiting to be bound to the facet editor panel:
                    editors = factory._shared_editors
                    if editors is not None:
                        for editor in factory._shared_editors:

                            # If the editor is part of this UI:
                            if editor.ui is self.ui:

                                # Then bind it to the facet editor panel:
                                editor._editor = control

                        # Indicate all pending editors have been processed:
                        factory._shared_editors = None

                    # We only needed to build the facet editor panel, so exit:
                    return

                # Check to see if the matching facet editor panel has been
                # created yet:
                editor = factory_editor._editor
                if (editor is None) or (editor.ui is not self.ui):
                    # If not, add ourselves to the list of pending editors:
                    shared_editors = factory_editor._shared_editors
                    if shared_editors is None:
                        factory_editor._shared_editors = shared_editors = []

                    shared_editors.append( self )
                else:
                    # Otherwise, bind our facet editor panel to the shared one:
                    self._editor = editor.adapter

                # Finally, create only the tree control:
                self.control = self._tree = _TreeWidget( parent(), self )
            else:
                # If editable, create a tree control and an editor panel:
                self._is_dock_window = True
                theme = factory.dock_theme or self.item.container.dock_theme
                dw    = DockWindow( parent, theme = theme )
                self.adapter = splitter = dw.control
                self._tree   = tree     = _TreeWidget( splitter(), self )
                self._editor = editor   = toolkit().create_scrolled_panel(
                                                                      splitter )
                editor._node_ui = editor._editor_nid = None
                hierarchy_name  = editor_name = ''
                item  = self.item
                style = 'fixed'
                name  = item.label
                if name != '':
                    hierarchy_name = name + ' Hierarchy'
                    editor_name    = name + ' Editor'
                    style          = item.dock

                dw.dock_sizer = DockSizer( contents =
                    DockSection( contents = [
                        DockRegion( contents = [
                            DockControl(
                                name    = hierarchy_name,
                                id      = 'tree',
                                control = control_adapter( tree ),
                                style   = style ) ] ),
                        DockRegion( contents = [
                            DockControl(
                                name    = editor_name,
                                id      = 'editor',
                                control = editor,
                                style   = style ) ] ) ],
                        is_row = (factory.orientation == 'horizontal') ) )
        else:
            # Otherwise, just create the tree control:
            self.control = self._tree = _TreeWidget( parent(), self )

        # Set up the selection style to use:
        self._tree.setSelectionMode( SelectionMode[ factory.selection_mode ] )

        # Set up the mapping between objects and tree id's:
        self._map = {}

        # Initialize the 'undo state' stack:
        self._undoable = []

        # Synchronize external object facets with the editor:
        self.sync_value( factory.selected,  'selected' )
        self.sync_value( factory.click,     'click',     'to'   )
        self.sync_value( factory.dclick,    'dclick',    'to'   )
        self.sync_value( factory.veto,      'veto',      'from' )
        self.sync_value( factory.show_item, 'show_item', 'from' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _selection_set ( self, items ):
        """ Handles the **selection** event.
        """
        if self.factory.selection_mode == 'item':
            try:
                self._tree.setCurrentItem( self._object_info( items )[2] )
            except:
                pass
        else:
            self._tree.clearSelection()
            for item in items:
                try:
                    self._object_info( item )[2].setSelected( True )
                except:
                    pass


    def _selected_set ( self, selected ):
        """ Handles the **selected** facet being changed.
        """
        if not self._no_update_selected:
            self._selection_set( selected )


    def _show_item_set ( self, item ):
        """ Handles the **show_item** facet being changed.
        """
        nid = self._get_object_nid( item )
        if nid is not None:
            self._tree.scrollToItem( nid, QAbstractItemView.PositionAtCenter )


    def _veto_set ( self ):
        """ Handles the 'veto' event being fired.
        """
        self._veto = True


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self._tree is not None:
            # Stop the chatter (specifically about the changing selection):
            self._tree.blockSignals( True )
            self._delete_node( self._tree.invisibleRootItem() )
            self._tree = None

        super( SimpleEditor, self ).dispose()


    def expand_levels ( self, nid, levels, expand = True ):
        """ Expands from the specified node the specified number of sub-levels.
        """
        if levels > 0:
            _, node, object = self._get_node_data( nid )
            if self._has_children( node, object ):
                self._expand_node( nid )
                if expand:
                    nid.setExpanded( True )

                for cnid in self._nodes_for( nid ):
                    self.expand_levels( cnid, levels - 1 )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        tree = self._tree
        saved_state = {}

        tree.clear()
        self._map.clear()

        object, node = self._node_for( self.value )
        if node is not None:
            hide_root = self.factory.hide_root
            if hide_root:
                nid = tree.invisibleRootItem()
                self._set_node_data( nid, ( COLLAPSED, node, object ) )
            else:
                nid = QTreeWidgetItem( tree )
                self._set_node_data( nid, ( COLLAPSED, node, object ) )
                nid.setText( 0, node.get_label( object ) )
                nid.setIcon( 0, self._get_icon( node, object ) )
                nid.setForeground( 0, QBrush( node.get_color( object ) ) )
                nid.setToolTip( 0, node.get_tooltip( object ) )

            self._map[ id( object ) ] = [ ( node.get_children_id( object ),
                                            nid ) ]
            self._add_listeners( node, object )
            if hide_root or self._has_children( node, object ):
                self._expand_node( nid )
                if not hide_root:
                    nid.setExpanded( True )
                    tree.setCurrentItem( nid )

            self.expand_levels( nid, self.factory.auto_open, False )
        # FIXME: Clear the current editor (if any)...


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self._tree


    def _append_node ( self, nid, node, object ):
        """ Appends a new node to the specified node.
        """
        return self._insert_node( nid, None, node, object )


    def _insert_node ( self, nid, index, node, object ):
        """ Inserts a new node before a specified index into the children of the
            specified node.
        """
        cnid = QTreeWidgetItem( nid )
        self._set_node_data( cnid, ( COLLAPSED, node, object ) )
        cnid.setText( 0, node.get_label( object ) )
        cnid.setIcon( 0, self._get_icon( node, object ) )
        cnid.setForeground( 0, QBrush( node.get_color( object ) ) )
        cnid.setToolTip( 0, node.get_tooltip( object ) )

        has_children = self._has_children( node, object )
        self._map.setdefault( id( object ), [] ).append(
            ( node.get_children_id( object ), cnid ) )
        self._add_listeners( node, object )

        # Automatically expand the new node (if requested):
        if has_children:
            if node.can_auto_open( object ):
                cnid.setExpanded( True )
            else:
                self._add_dummy_node( cnid )

        # Return the newly created node:
        return cnid


    def _add_dummy_node ( self, nid ):
        """ Qt only draws the control that expands the tree if there is a
            child.  As the tree is being populated lazily we create a dummy
            that will be removed when the node is expanded the first time:
        """
        if getattr( nid, '_dummy', None ) is None:
            nid._dummy = QTreeWidgetItem( nid )


    def _delete_node ( self, nid ):
        """ Deletes a specified tree node and all its children.
        """
        for cnid in self._nodes_for( nid ):
            self._delete_node( cnid )

        if nid is self._tree.invisibleRootItem():
            return

        # See if it is a dummy:
        pnid = nid.parent()
        if (pnid is not None) and getattr( pnid, '_dummy', None ) is nid:
            pnid.removeChild( nid )
            del pnid._dummy

            return

        _, node, object = self._get_node_data( nid )
        id_object   = id( object )
        object_info = self._map[ id_object ]
        for i, info in enumerate( object_info ):
            if nid == info[1]:
                del object_info[ i ]

                break

        if len( object_info ) == 0:
            self._remove_listeners( node, object )
            del self._map[ id_object ]

        if pnid is None:
            self._tree.takeTopLevelItem( self._tree.indexOfTopLevelItem( nid ) )
        else:
            pnid.removeChild( nid )

        # If the deleted node had an active editor panel showing, remove it:
        if (self._editor is not None) and (nid == self._editor._editor_nid):
            self._clear_editor()


    def _expand_node ( self, nid ):
        """ Expands the contents of a specified node (if required).
        """
        state, node, object = self._get_node_data( nid )

        # Lazily populate the item's children:
        if state == COLLAPSED:
            # Temporarily disable widget updates in case there are a lot of
            # children:
            self.control.setUpdatesEnabled( False )

            for child in node.get_children( object ):
                child, child_node = self._node_for( child )
                if child_node is not None:
                    self._append_node( nid, child_node, child )

            # Remove any dummy node:
            dummy = getattr( nid, '_dummy', None )
            if dummy is not None:
                nid.removeChild( dummy )
                del nid._dummy

            # Indicate the item is now populated:
            self._set_node_data( nid, ( EXPANDED, node, object ) )

            # Re-enable widget updates:
            self.control.setUpdatesEnabled( True )


    def _nodes_for ( self, nid ):
        """ Returns all child node ids of a specified node id.
        """
        return [ nid.child( i ) for i in range( nid.childCount() ) ]


    def _node_index ( self, nid ):
        pnid = nid.parent()
        if pnid is None:
            return ( None, None, None )

        for i in range( pnid.childCount() ):
            if pnid.child( i ) is nid:
                _, pnode, pobject = self._get_node_data( pnid )
                return ( pnode, pobject, i )


    STD_ICON_MAP = {
        '<item>':   QStyle.SP_FileIcon,
        '<group>':  QStyle.SP_DirClosedIcon,
        '<open>':   QStyle.SP_DirOpenIcon
    }


    def _has_children ( self, node, object ):
        """ Returns whether a specified object has any children.
        """
        return (node.allows_children( object ) and node.has_children( object ))


    def _is_droppable ( self, node, object, add_object, for_insert ):
        """ Returns whether a given object is droppable on the node.
        """
        if for_insert:
            return node.can_insert( object )

        return node.can_add( object, add_object )


    def _get_icon ( self, node, object, state = COLLAPSED ):
        """ Returns the index of the specified object icon.
        """
        if not self.factory.show_icons:
            return QIcon()

        icon_name = node.get_icon( object, state )
        if isinstance( icon_name, basestring ) and (icon_name[:1] == '@'):
            icon_name = image_for( icon_name )

        if not isinstance( icon_name, basestring ):
            # Assume it is an ImageResource, and return the icon directly:
            return QIcon( icon_name.bitmap )

        icon = self.STD_ICON_MAP.get( icon_name )

        if icon is not None:
            result = self._icon_cache.get( icon )
            if result is None:
                self._icon_cache[ icon ] = result = \
                    self._tree.style().standardIcon( icon )

            return result

        path = node.get_icon_path( object )
        if isinstance( path, basestring ):
            path = [ path, node ]
        else:
            path.append( node )

        reference = resource_manager.locate_image( icon_name, path )
        if reference is None:
            return QIcon()

        return QIcon( pixmap_cache( reference.filename ) )


    def _add_listeners ( self, node, object ):
        """ Adds the event listeners for a specified object.
        """
        if node.allows_children( object ):
            node.when_children_replaced( object, self._children_replaced,
                                         False )
            node.when_children_changed( object, self._children_updated, False )

        node.when_label_changed( object, self._label_updated, False )
        node.when_color_changed( object, self._color_updated, False )


    def _remove_listeners ( self, node, object ):
        """ Removes any event listeners from a specified object.
        """
        if node.allows_children( object ):
            node.when_children_replaced( object, self._children_replaced, True )
            node.when_children_changed(  object, self._children_updated,  True )

        node.when_label_changed( object, self._label_updated, True )
        node.when_color_changed( object, self._color_updated, True )


    def _selected_items ( self ):
        """ Returns a list of tuples of the form: ( nid, object, node,
            parent_object, parent_node ) describing the current selection.
        """
        info = []
        root = self._tree.invisibleRootItem()
        for nid in self._tree.selectedItems():
            _, node, object = self._get_node_data( nid )
            parent_node = parent_object = None
            parent_nid  = nid.parent()
            if (parent_nid is not None) and (parent_nid is not root):
                _, parent_node, parent_object = \
                    self._get_node_data( parent_nid )

            info.append( SelectedItem(
                object        = object,
                node          = node,
                nid           = nid,
                parent_object = parent_object,
                parent_node   = parent_node,
                parent_nid    = parent_nid
            ) )

        return info


    def _object_info ( self, object, name = '' ):
        """ Returns the tree node data for a specified object in the form:
            ( state, node, nid ).
        """
        info = self._map[ id( object ) ]
        for name2, nid in info:
            if name == name2:
                break
        else:
            nid = info[0][1]

        state, node, _ = self._get_node_data( nid )

        return ( state, node, nid )


    def _object_info_for ( self, object, name = '' ):
        """ Returns the tree node data for a specified object as a list of the
            form: [ ( state, node, nid ), ... ].
        """
        result = []
        info   = self._map[ id( object ) ]
        for name2, nid in info:
            if name == name2:
                state, node, _ = self._get_node_data( nid )
                result.append( ( state, node, nid ) )

        if len( result ) == 0:
            nid = info[0][1]
            state, node, _ = self._get_node_data( nid )
            result.append( ( state, node, nid ) )

        return result


    def _node_for ( self, object ):
        """ Returns the TreeNode associated with a specified object.
        """
        if ((type( object ) is tuple) and
            (len( object ) == 2)      and
            isinstance( object[1], TreeNode )):
            return object

        # Select all nodes which understand this object:
        factory = self.factory
        nodes   = [ node for node in factory.nodes
                    if node.is_node_for( object ) ]

        # If only one found, we're done, return it:
        if len( nodes ) == 1:
            return ( object, nodes[0] )

        # If none found, give up:
        if len( nodes ) == 0:
            return ( object, ITreeNodeAdapterBridge( adapter = object ) )

        # Use all selected nodes that have the same 'node_for' list as the
        # first selected node:
        base  = nodes[0].node_for
        nodes = [ node for node in nodes if base == node.node_for ]

        # If only one left, then return that node:
        if len( nodes ) == 1:
            return ( object, nodes[0] )

        # Otherwise, return a MultiTreeNode based on all selected nodes...

        # Use the node with no specified children as the root node. If not
        # found, just use the first selected node as the 'root node':
        root_node = None
        for i, node in enumerate( nodes ):
            if node.get_children_id( object ) == '':
                root_node = node
                del nodes[i]
                break
        else:
            root_node = nodes[0]

        # If we have a matching MultiTreeNode already cached, return it:
        key = ( root_node, ) + tuple( nodes )
        if key in factory.multi_nodes:
            return ( object, factory.multi_nodes[ key ] )

        # Otherwise create one, cache it, and return it:
        factory.multi_nodes[ key ] = multi_node = MultiTreeNode(
                                                       root_node = root_node,
                                                       nodes     = nodes )

        return ( object, multi_node )


    def _node_for_class ( self, klass ):
        """ Returns the TreeNode associated with a specified class.
        """
        for node in self.factory.nodes:
            if issubclass( klass, tuple( node.node_for ) ):
                return node

        return None


    def _node_for_class_name ( self, class_name ):
        """ Returns the node and class associated with a specified class name.
        """
        for node in self.factory.nodes:
            for klass in node.node_for:
                if class_name == klass.__name__:
                    return ( node, klass )

        return ( None, None )


    def _update_icon ( self, nid ):
        """ Updates the icon for a specified node.
        """
        state, node, object = self._get_node_data( nid )
        nid.setIcon( 0, self._get_icon( node, object, state ) )


    def _begin_undo ( self ):
        """ Begins an "undoable" transaction.
        """
        ui = self.ui
        self._undoable.append( ui._undoable )
        if (ui._undoable == -1) and (ui.history is not None):
            ui._undoable = ui.history.now


    def _end_undo ( self ):
        if self._undoable.pop() == -1:
            self.ui._undoable = -1


    def _get_undo_item ( self, object, name, event ):
        return ListUndoItem( object  = object,
                             name    = name,
                             index   = event.index,
                             added   = event.added,
                             removed = event.removed )


    def _undoable_append ( self, node, object, data, make_copy = True ):
        """ Performs an undoable append operation.
        """
        try:
            self._begin_undo()
            if make_copy:
                data = copy.deepcopy( data )
            node.append_child( object, data )
        finally:
            self._end_undo()


    def _undoable_insert ( self, node, object, index, data, make_copy = True ):
        """ Performs an undoable insert operation.
        """
        try:
            self._begin_undo()
            if make_copy:
                data = copy.deepcopy( data )

            node.insert_child( object, index, data )
        finally:
            self._end_undo()


    def _undoable_delete ( self, node, object, index ):
        """ Performs an undoable delete operation.
        """
        try:
            self._begin_undo()
            node.delete_child( object, index )
        finally:
            self._end_undo()


    def _get_object_nid ( self, object, name = '' ):
        """ Gets the ID associated with a specified object (if any).
        """
        info = self._map.get( id( object ) )
        if info is None:
            return None

        for name2, nid in info:
            if name == name2:
                return nid
        else:
            return info[0][1]


    def _clear_editor ( self ):
        """ Clears the current editor pane (if any).
        """
        editor = self._editor
        if editor._node_ui is not None:
            editor().setWidget( None )
            editor._node_ui.dispose()
            editor._node_ui = editor._editor_nid = None
            if editor.layout is not None:
                editor.layout.clear()


    @staticmethod
    def _get_node_data ( nid ):
        """ Gets the node specific data. """
        return nid._py_data


    @staticmethod
    def _set_node_data ( nid, data ):
        """ Sets the node specific data. """
        nid._py_data = data

    #-- User Callable Methods --------------------------------------------------

    def get_object ( self, nid ):
        """ Gets the object associated with a specified node.
        """
        return self._get_node_data( nid )[ 2 ]


    def get_parent ( self, object, name = '' ):
        """ Returns the object that is the immmediate parent of a specified
            object in the tree.
        """
        nid = self._get_object_nid( object, name )
        if nid is not None:
            pnid = nid.parent()
            if pnid is not self._tree.invisibleRootItem():
                return self.get_object( pnid )

        return None


    def get_node ( self, object, name = '' ):
        """ Returns the node associated with a specified object.
        """
        nid = self._get_object_nid( object, name )
        if nid is not None:
            return self._get_node_data( nid )[ 1 ]

        return None

    #-- Tree Event Handlers ----------------------------------------------------

    def _on_item_expanded ( self, nid ):
        """ Handles a tree node being expanded.
        """
        _, node, object = self._get_node_data( nid )

        # If 'auto_close' requested for this node type, close all of the node's
        # siblings:
        if node.can_auto_close( object ):
            parent = nid.parent()

            if parent is not None:
                for snid in self._nodes_for( parent ):
                    if snid is not nid:
                        snid.setExpanded( False )

        # Expand the node (i.e. populate its children if they are not there
        # yet):
        self._expand_node( nid )
        self._update_icon( nid )
        node.node_expanded( object, True )


    def _on_item_collapsed ( self, nid ):
        """ Handles a tree node being collapsed.
        """
        _, node, object = self._get_node_data( nid )

        # Indicate the item is now closed:
        self._set_node_data( nid, ( CLOSED, node, object ) )

        # Update the tree item to use its 'closed' icon:
        self._update_icon( nid )

        # Notify that the node has been closed:
        node.node_expanded( object, False )


    def _on_item_clicked ( self, nid, col ):
        """ Handles a tree item being clicked.
        """
        _, node, object = self._get_node_data( nid )

        if ((node.click( object ) is True) and
            (self.factory.on_click is not None)):
            self.ui.evaluate( self.factory.on_click, object )

        # Fire the 'click' event with the object as its value:
        self.click = object


    def _on_item_dclicked ( self, nid, col ):
        """ Handles a tree item being double-clicked.
        """
        _, node, object = self._get_node_data( nid )

        if node.dclick( object ) is True:
            if self.factory.on_dclick is not None:
                self.ui.evaluate( self.factory.on_dclick, object )
                self._veto = True
        else:
            self._veto = True

        # Fire the 'dclick' event with the clicked on object as value:
        self.dclick = object


    def _on_tree_sel_modified ( self ):
        """ Handles a tree node being selected.
        """
        # Get the new selection:
        items = []
        sel   = self._tree.selectedItems()
        if len( sel ) > 0:
            not_handled = False
            for nid in sel:
               # If there is a real selection, get the associated object:
               _, node, item = self._get_node_data( nid )

               # Try to inform the node specific handler of the selection:
               not_handled = node.select( item ) or not_handled

               # Add the selected object to the list of selected objects:
               items.append( item )

        else:
            nid         = None
            item        = None
            not_handled = True

        # Set the value of the new selection:
        self._no_update_selected = True
        if self.factory.selection_mode == 'item':
            self.selected = item
        else:
            self.selected = items
        self._no_update_selected = False

        # If no one has been notified of the selection yet, inform the editor's
        # select handler (if any) of the new selection:
        if not_handled is True:
            self.ui.evaluate( self.factory.on_select, item )

        # Check to see if there is an associated node editor pane:
        editor = self._editor
        if editor is not None:
            # If we already had a node editor, destroy it:
            editor.frozen = True
            self._clear_editor()

            # If there is a selected item, create a new editor for it:
            if item is not None:
                # Try to chain the undo history to the main undo history:
                view = node.get_view( item )
                if view is None:
                    view = item.facet_view()

                panel = toolkit().create_panel( editor )
                ui    = item.edit_facets( parent = panel, view = view,
                                          kind   = 'subpanel' )

                # Make our UI the parent of the new UI:
                ui.parent = self.ui

                # Remember the new editor's UI and node info:
                editor._node_ui    = ui
                editor._editor_nid = nid

                # Finish setting up the editor:
                if ui.is_control:
                    layout = toolkit().creat_box_layout()
                    layout.add( ui.control, stretch = 1 )
                    panel.layout = layout
                else:
                    panel.layout = ui.control

                editor().setWidget( panel() )

                layout = editor.layout
                if layout is None:
                    editor.layout = layout = toolkit().create_box_layout()

                layout.add( panel, stretch = 1 )

                from facets.extra.helper.debug import log_if
                log_if( 2, editor )

            # Allow the editor view to show any changes that have occurred:
            editor.frozen = False


    def _on_context_menu ( self, pos ):
        do_after( 100, self._display_context_menu, pos.x(), pos.y() )

    def _display_context_menu ( self, x, y ):
        """ Handles the user requesting a context menu by right clicking on a
            tree node.
        """
        pos = QPoint( x, y )
        nid = self._tree.itemAt( pos )

        if nid is None:
            return

        _, node, object = self._get_node_data( nid )

        self._data    = ( node, object, nid )
        self._context = { 'object':   object,
                          'selected': self._selected_items(),
                          'editor':   self,
                          'node':     node,
                          'info':     self.ui.info,
                          'handler':  self.ui.handler }

        # Try to get the parent node of the node clicked on:
        pnid = nid.parent()
        if (pnid is None) or (pnid is self._tree.invisibleRootItem()):
            parent_node = parent_object = None
        else:
            _, parent_node, parent_object = self._get_node_data( pnid )

        self._menu_node          = node
        self._menu_parent_node   = parent_node
        self._menu_parent_object = parent_object

        menu = node.get_menu( object )

        if menu is None:
            # Use the standard, default menu:
            menu = self._standard_menu( node, object )

        elif isinstance( menu, Menu ):
            # Use the menu specified by the node:
            group = menu.find_group( NewAction )
            if group is not None:
                # Only set it the first time:
                group.id = ''
                actions  = self._new_actions( node, object )
                if len( actions ) > 0:
                    group.insert( 0, Menu( name = 'New', *actions ) )

        else:
            # All other values mean no menu should be displayed:
            menu = None

        # Only display the menu if a valid menu is defined:
        if menu is not None:
            qmenu = menu.create_menu( self._tree, self )
            qmenu.exec_( self._tree.mapToGlobal( pos ) )

        # Reset all menu related cached values:
        self._data = self._context = self._menu_node = \
        self._menu_parent_node = self._menu_parent_object = None


    def _standard_menu ( self, node, object ):
        """ Returns the standard contextual pop-up menu.
        """
        actions = [ CutAction, CopyAction, PasteAction, Separator(),
                    DeleteAction, Separator(), RenameAction ]

        # See if the 'New' menu section should be added:
        items = self._new_actions( node, object )
        if len( items ) > 0:
            actions[0:0] = [ Menu( name = 'New', *items ), Separator() ]

        return Menu( *actions )


    def _new_actions ( self, node, object ):
        """ Returns a list of Actions that will create new objects.
        """
        object = self._data[1]
        items  = []
        add    = node.get_add( object )
        if len( add ) > 0:
            for klass in add:
                prompt = False
                if isinstance( klass, tuple ):
                    klass, prompt = klass

                add_node = self._node_for_class( klass )
                if add_node is not None:
                    class_name = klass.__name__
                    name       = add_node.get_name( object )
                    if name == '':
                        name = class_name

                    items.append(
                        Action( name   = name,
                                action = "editor._menu_new_node('%s',%s)" %
                                         ( class_name, prompt ) ) )
        return items


    def _is_copyable ( self, object ):
        parent = self._menu_parent_node
        if isinstance( parent, ObjectTreeNode ):
            return parent.can_copy( self._menu_parent_object )

        return ((parent is not None) and parent.can_copy( object ))


    def _is_cutable ( self, object ):
        parent = self._menu_parent_node
        if isinstance( parent, ObjectTreeNode ):
            can_cut = (parent.can_copy( self._menu_parent_object ) and
                       parent.can_delete( self._menu_parent_object ))
        else:
            can_cut = ((parent is not None) and
                       parent.can_copy( object ) and
                       parent.can_delete( object ))

        return (can_cut and self._menu_node.can_delete_me( object ))


    def _is_pasteable ( self, object ):
        return self._menu_node.can_add( object, clipboard.instance )


    def _is_deletable ( self, selected_items ):
        for item in selected_items:
            parent_node = item.parent_node
            if isinstance( parent_node, ObjectTreeNode ):
                if not parent_node.can_delete( item.parent_object ):
                    return False
            elif (not ((parent_node is not None) and
                       parent_node.can_delete( item.object ))):
                return False

            if not item.node.can_delete_me( item.object ):
                return False

        return True


    def _is_renameable ( self, object ):
        parent = self._menu_parent_node
        if isinstance( parent, ObjectTreeNode ):
            can_rename = parent.can_rename( self._menu_parent_object )
        else:
            can_rename = ((parent is not None) and parent.can_rename( object ))

        can_rename = (can_rename and self._menu_node.can_rename_me( object ))

        # Set the widget item's editable flag appropriately:
        nid   = self._get_object_nid( object )
        flags = nid.flags()
        if can_rename:
            flags |= Qt.ItemIsEditable
        else:
            flags &= ~Qt.ItemIsEditable

        nid.setFlags( flags )

        return can_rename


    def _drop_object ( self, node, object, dropped_object, make_copy = True ):
        """ Returns a droppable version of a specified object.
        """
        new_object = node.drop_object( object, dropped_object )
        if (new_object is not dropped_object) or (not make_copy):
            return new_object

        return copy.deepcopy( new_object )

    #-- pyface.action 'controller' Interface Implementation --------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        action = menu_item.item.action
        self.eval_when( action.enabled_when, menu_item, 'enabled' )
        self.eval_when( action.checked_when, menu_item, 'checked' )


    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        self.add_to_menu( toolbar_item )


    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        if action.defined_when != '':
            try:
                if not eval( action.defined_when, globals(), self._context ):
                    return False
            except:
                of_fbi()

        if action.visible_when != '':
            try:
                if not eval( action.visible_when, globals(), self._context ):
                    return False
            except:
                of_fbi()

        return True


    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return self.can_add_to_menu( action )


    def perform ( self, action, action_event = None ):
        """ Performs the action described by a specified Action object.
        """
        self.ui.do_undoable( self._perform, action )


    def _perform ( self, action ):
        node, object, nid = self._data
        method_name       = action.action
        info              = self.ui.info
        handler           = self.ui.handler

        if method_name.find( '.' ) >= 0:
            if method_name.find( '(' ) < 0:
                method_name += '()'

            try:
                eval( method_name, globals(), self._context )
            except:
                # Report the exception (then ignore it):
                import traceback
                traceback.print_exc()

            return

        method = getattr( handler, method_name, None )
        if method is not None:
            method( info, object )

            return

        if action.on_perform is not None:
            action.on_perform( object )

    #-- Menu Support Methods ---------------------------------------------------

    def eval_when ( self, condition, object, facet ):
        """ Evaluates a condition within a defined context, and sets a
            specified object facet based on the result, which is assumed to be a
            Boolean.
        """
        if condition != '':
            value = True
            if not eval( condition, globals(), self._context ):
                value = False

            setattr( object, facet, value )

    #-- Menu Event Handlers ----------------------------------------------------

    def _menu_copy_node ( self ):
        """ Copies the current tree node object to the paste buffer.
        """
        clipboard.instance = self._data[1]
        self._data = None


    def _menu_cut_node ( self ):
        """ Cuts the current tree node object into the paste buffer.
        """
        node, object, nid  = self._data
        clipboard.instance = object
        self._data         = None
        self._undoable_delete( *self._node_index( nid ) )


    def _menu_paste_node ( self ):
        """ Pastes the current contents of the paste buffer into the current
            node.
        """
        node, object, nid = self._data
        self._data        = None
        self._undoable_append( node, object, clipboard.instance, False )


    def _menu_delete_node ( self, selected_items ):
        """ Deletes the currently selected nodes from the tree.
        """
        for item in selected_items:
            rc = item.node.confirm_delete( item.object )
            if rc is not False:
                if rc is not True:
                    if self.ui.history is None:
                        # If no undo history, ask user to confirm the delete:
                        if QMessageBox.question(
                                self._tree,
                                "Confirm Deletion",
                                "Are you sure you want to delete %s?" %
                                item.node.get_label( item.object ),
                                QMessageBox.Yes | QMessageBox.No
                            ) != QMessageBox.Yes:
                            continue

                self._undoable_delete( *self._node_index( item.nid ) )


    def _menu_rename_node ( self ):
        """ Rename the current node.
        """
        _, _, nid = self._data
        self._data = None
        self._tree.editItem( nid )


    def _on_nid_modified ( self, nid, col ):
        """ Handle changes to a widget item.
        """
        # The node data may not have been set up for the nid yet. Ignore it if
        # it hasn't:
        try:
            _, node, object = self._get_node_data( nid )
        except:
            return

        new_label = unicode( nid.text( col ) )
        old_label = node.get_label( object )

        if new_label != old_label:
            if new_label != '':
                node.set_label( object, new_label )
            else:
                nid.setText( col, old_label )


    def _menu_new_node ( self, class_name, prompt = False ):
        """ Adds a new object to the current node.
        """
        node, object, nid   = self._data
        self._data          = None
        new_node, new_class = self._node_for_class_name( class_name )
        new_object          = new_class()
        if ((not prompt) or
            new_object.edit_facets( parent = self.control,
                                    kind   = 'livemodal' ).result):

            self._undoable_append( node, object, new_object, False )

            # Automatically select the new object:
            self._expand_node( nid )
            self._tree.setCurrentItem( nid.child( nid.childCount() - 1 ) )

    #-- Model Event Handlers ---------------------------------------------------

    def _children_replaced ( self, object, facet = '' ):
        """ Handles the children of a node being completely replaced.
        """
        tree             = self._tree
        state, node, nid = self._object_info( object, facet )
        can_auto_open    = node.can_auto_open( object )

        # Only add/remove the changes if the node has already been expanded:
        if state != COLLAPSED:
            # Delete all current child nodes:
            for cnid in self._nodes_for( nid ):
                self._delete_node( cnid )

            # Add all of the children back in as new nodes:
            children = node.get_children( object )
            for child in children:
                child, child_node = self._node_for( child )
                if child_node is not None:
                    self._append_node( nid, child_node, child )
        elif (not can_auto_open) and self._has_children( node, object ):
            self._add_dummy_node( nid )

        # Try to expand the node (if requested):
        if can_auto_open:
            nid.setExpanded( True )


    def _children_updated ( self, object, facet, event ):
        """ Handles the children of a node being changed.
        """
        # Remove the trailing '_items' from the name:
        facet = facet[:-6]

        # Get information about the node that was changed:
        try:
            start = event.index
        except:
            self._children_replaced( object, facet )

            return

        # Log the change that was made made:
        self.log_change( self._get_undo_item, object, facet, event )

        n    = len( event.added )
        end  = start + len( event.removed )
        tree = self._tree

        for state, node, nid in self._object_info_for( object, facet ):
            children = node.get_children( object )

            # If the new children aren't all at the end, remove/add them all:
            if (n > 0) and ((start + n) != len( children )):
                self._children_replaced( object, facet )

                return

            # Only add/remove the changes if the node has already been expanded:
            if state != COLLAPSED:
                # Remove all of the children that were deleted:
                for cnid in self._nodes_for( nid )[ start: end ]:
                    self._delete_node( cnid )

                # Add all of the children that were added:
                remaining = n - len( event.removed )
                if n > 0:
                    for child in children[-n:]:
                        child, child_node = self._node_for( child )
                        if child_node is not None:
                            if start < remaining:
                                self._insert_node(
                                    nid, start, child_node, child
                                )
                                start     += 1
                                remaining += 1
                            else:
                                self._append_node( nid, child_node, child )

            # Try to expand the node (if requested):
            if node.can_auto_open( object ):
                nid.setExpanded( True )


    def _label_updated ( self, object ):
        """  Handles the label of an object being changed.
        """
        self._update_node(
            object,
            lambda nid, node: nid.setText( 0, node.get_label( object ) )
        )


    def _color_updated ( self, object ):
        """  Handles the color of an object being changed.
        """
        self._update_node(
            object,
            lambda nid, node: nid.setForeground( 0,
                                      QBrush( node.get_color( object ) ) )
        )


    def _update_node ( self, object, callable ):
        """ Invokes callable( nid, node ) for each nid, node pair corresponding
            to the specified *object*. All calls are made with tree itemChanged
            signals blocked.
        """
        # Prevent itemChanged() signals from being emitted:
        block = self._tree.blockSignals( True )
        nids  = set()
        if id( object ) not in self._map :
            print 'Warning: id for ', object, 'not in tree _map'
            self._tree.blockSignals( block )

            return

        for name, nid in self._map[ id( object ) ]:
            if nid not in nids:
                nids.add( nid )
                node = self._get_node_data( nid )[1]
                callable( nid, node )
                self._update_icon( nid )

        self._tree.blockSignals( block )

    #-- UI Preference Save/Restore Interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if self._is_dock_window:
            if isinstance( prefs, dict ):
                structure = prefs.get( 'structure' )
            else:
                structure = prefs

            self.adapter.layout().layout.set_structure( self.control,
                                                        structure )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        if self._is_dock_window:
            return {
                'structure': self.adapter.layout().layout.get_structure()
            }

        return None

#-------------------------------------------------------------------------------
#  'SelectedItem' class:
#-------------------------------------------------------------------------------

class SelectedItem ( HasFacets ):
    """ Provides information about a selected tree item.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The selected object:
    object = Any

    # The TreeNode object for the selected object:
    node = Any

    # The tree node id for the selected object:
    nid = Any

    # The parent object of the selected object:
    parent_object = Any

    # The TreeNode for the parent object:
    parent_node = Any

    # The tree node id of the parent object:
    parent_nid = Any

#-------------------------------------------------------------------------------
#  '_TreeWidget' class:
#-------------------------------------------------------------------------------

class _TreeWidget ( QTreeWidget ):
    """ The _TreeWidget class is a specialised QTreeWidget that reimplements
        the drag'n'drop support so that it hooks into the provided Facets
        support.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent, editor ):
        """ Initialise the tree widget.
        """
        QTreeWidget.__init__( self, parent )

        self.header().hide()
        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.setDragEnabled( True )
        self.setAcceptDrops( True )

        self.connect( self, SIGNAL( 'itemExpanded(QTreeWidgetItem *)' ),
                      editor._on_item_expanded )
        self.connect( self, SIGNAL( 'itemCollapsed(QTreeWidgetItem *)' ),
                      editor._on_item_collapsed )
        self.connect( self, SIGNAL( 'itemClicked(QTreeWidgetItem *, int)' ),
                      editor._on_item_clicked )
        self.connect( self,
                      SIGNAL( 'itemDoubleClicked(QTreeWidgetItem *, int)' ),
                      editor._on_item_dclicked )
        self.connect( self, SIGNAL( 'itemSelectionChanged()' ),
                      editor._on_tree_sel_modified )
        self.connect( self, SIGNAL( 'customContextMenuRequested(QPoint)' ),
                      editor._on_context_menu )
        self.connect( self, SIGNAL( 'itemChanged(QTreeWidgetItem *, int)' ),
                      editor._on_nid_modified )

        self._editor   = editor
        self._dragging = None


    def startDrag ( self, actions ):
        """ Reimplemented to start the drag of a tree widget item(s).
        """
        nid = self.currentItem()
        if nid is None:
            return

        nids = self.selectedItems()
        if nid not in nids:
            nids = [ nid ]

        editor = self._editor
        data   = []
        gnd    = editor._get_node_data
        for a_nid in nids:
            _, node, item = gnd( a_nid )
            data.append( node.get_drag_object( item ) )

        n = len( nids )
        if n == 1:
            data = data[0]

        self._dragging = nids

        # Render the current item being dragged as a pixmap:
        text     = GraphicsText( text = '%d item%s' % ( n, 's'[ n == 1: ] ) )
        theme    = editor.drag_theme
        pm       = QPixmap( 75, 50 )
        pm.fill( QColor( 0, 0, 0, 0 ) )
        painter  = QPainter( pm )
        g        = QtGraphics( painter )
        idx, idy = theme.size_for( g, text )
        theme.fill( g, 0, 0, idx, idy )
        theme.draw_graphics_text( g, text, 0, 0, idx, idy )
        painter.end()

        # Start the drag:
        drag = QDrag( self )
        drag.setMimeData( PyMimeData( data ) )
        drag.setPixmap( pm )
        drag.setHotSpot( QPoint( idx / 2, idy / 2 ) )
        drag.exec_( actions )


    def dragEnterEvent ( self, e ):
        """ Reimplemented to see if the current drag can be handled by the
            tree.
        """
        super( _TreeWidget, self ).dragEnterEvent( e )

        # Assume the drag is invalid:
        e.ignore()

        # Check what is being dragged:
        md = PyMimeData.coerce( e.mimeData() )
        if md is None:
            return

        # We might be able to handle it (but it depends on what the final
        # target is):
        e.acceptProposedAction()


    def dragMoveEvent ( self, e ):
        """ Reimplemented to see if the current drag can be handled by the
            particular tree widget item underneath the cursor.
        """
        super( _TreeWidget, self ).dragMoveEvent( e )

        # Assume the drag is invalid:
        e.ignore()

        # Get the tree widget item under the cursor:
        nid = self.itemAt( e.pos() )
        if nid is None:
            return

        # Check that the target is not the source of a child of the source:
        if self._dragging is not None:
            pnid = nid
            while pnid is not None:
                if pnid in self._dragging:
                    return

                pnid = pnid.parent()

        # A copy action is interpreted as moving the source to a particular
        # place within the target's parent.  A move action is interpreted as
        # moving the source to be a child of the target:
        if e.proposedAction() == Qt.CopyAction:
            node, object, _ = self._editor._node_index( nid )
            insert = True
        else:
            _, node, object = self._editor._get_node_data( nid )
            insert = False

        # See if the model will accept a drop:
        data = PyMimeData.coerce( e.mimeData() ).instance()
        if not isinstance( data, SequenceTypes ):
            data = [ data ]

        for item in data:
            if self._editor._is_droppable( node, object, item, insert ):
                e.acceptProposedAction()

                break


    def dropEvent ( self, e ):
        """ Reimplemented to update the model and tree.
        """
        # Assume the drop is invalid:
        e.ignore()

        dragging, self._dragging = self._dragging, None

        # Get the tree widget item under the cursor:
        nid = self.itemAt( e.pos() )
        if nid is None:
            return

        # If the drag originated from this tree, then clear the selection
        # (otherwise we have problems when the selected items get deleted):
        if dragging is not None:
            self.clearSelection()

        # Get the data being dropped (as a list):
        data = PyMimeData.coerce( e.mimeData() ).instance()
        if not isinstance( data, SequenceTypes ):
            data = [ data ]

        editor = self._editor
        _, node, object = editor._get_node_data( nid )

        can_move = (dragging is not None)
        editor._begin_undo()
        try:
            # If there is more than one node that is being dropped, the
            # _undoable_delete will mess up the indices for the later ones. Look
            # up the nodes in advance and then adjust the node indices
            # appropriately:
            dragging_node_indices = [ list( editor._node_index( d ) )
                                      for d in dragging ]
            for i, item in enumerate( data ):
                if e.proposedAction() == Qt.MoveAction:
                    if not editor._is_droppable( node, object, item, False ):
                        continue

                    mode = node.drop_mode( object, item, can_move )
                    item = editor._drop_object( node, object, item,
                                                mode == 'copy' )
                    if item is not None:
                        if (mode == 'move') and can_move:
                            dri = dragging_node_indices[ i ]
                            editor._undoable_delete( *dri )

                            # The position of some nodes may have shifted:
                            for j, drj in enumerate( dragging_node_indices ):
                                if ((j > i) and (drj[0] == dri[0]) and
                                    (drj[2] > dri[2])):
                                    drj[2] -= 1

                        editor._undoable_append( node, object, item, False )
                else:
                    to_node, to_object, to_index = editor._node_index( nid )
                    if to_node is not None:
                        if not editor._is_droppable( node, object, item, True ):
                            continue

                        mode = node.drop_mode( object, item, can_move )
                        item = editor._drop_object( node, to_object, item,
                                                    mode == 'copy' )
                        if item is not None:
                            if (mode == 'move') and can_move:
                                from_node, from_object, from_index = \
                                    editor._node_index( dragging[ i ] )
                                if ((to_object is from_object) and
                                    (to_index > from_index)):
                                    to_index -= 1

                                editor._undoable_delete( from_node, from_object,
                                                         from_index )

                            editor._undoable_insert( to_node, to_object,
                                                     to_index, item, False )
        finally:
            editor._end_undo()

        e.acceptProposedAction()

#-- EOF ------------------------------------------------------------------------