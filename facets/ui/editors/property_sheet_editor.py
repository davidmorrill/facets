"""
Defines the PropertySheetEditor that allows editing a HasFacets object's
editable facets using a two-column property sheet based on the GridEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from types \
    import NoneType

from weakref \
    import WeakValueDictionary

from facets.api \
    import HasPrivateFacets, HasFacets, Instance, Bool, Int, Any, List, Enum, \
           Callable, Str, Event, Property, DelegatesTo, Color, Undefined,     \
           WeakRef, View, Item, UIEditor, GridEditor, ListEditor, TextEditor, \
           TupleEditor, BasicEditorFactory, EditorFactory, on_facet_set

from facets.core.facet_base \
    import user_name_for

from facets.ui.property_sheet_adapter \
    import PropertySheetAdapter, EditMode, ChangeMode

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.i_filter \
    import Filter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Property sheet color sets:
ColorSchemes = {
    'grey':  ( 0xFFFFFF, 0xE8E8E0, 0x606060, 0x000000, 0xFFFFFF ),
    'blue':  ( 0xFFFFFF, 0xE6E9F4, 0x294393, 0x000000, 0xFFFFFF ),
    'olive': ( 0xFFFFFF, 0xEEEEDA, 0x646440, 0x000000, 0xFFFFFF ),
    'black': ( 0x505050, 0x707070, 0x202020, 0xFFFFFF, 0xFE9824 ),
    'white': ( 0xFFFFFF, 0xF0F0F0, 0xD4D4D4, 0x000000, 0x112CCF ),
}

# Number of pixels/indent level:
INDENT = 15

# Set of types we don't handle:
BadTypes = ( NoneType, set )

# Set of easily editable simple types:
SimpleTypes = ( basestring, int, long, float, tuple )

# Set of indexable types:
IndexTypes = ( list, tuple, dict )

# Set of substitutable list/dictionary editors:
ItemEditors = (
    TextEditor().__class__, TupleEditor().__class__, ListEditor().__class__
)

# Mapping of item editing modes to grid editor clicked results:
ModeMap = {
    'inline':   'edit',
    'popup':    'popup',
    'popout':   'popout',
    'readonly': None
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def indexed_item ( index, values, is_indexed ):
    if is_indexed:
        return values[ index ]

    return values

#-------------------------------------------------------------------------------
#  'PropertySheetFilter' class:
#-------------------------------------------------------------------------------

class PropertySheetFilter ( Filter ):
    """ Filter used to determine which property sheet items are visible.
    """

    #-- IFilter Interface ------------------------------------------------------

    def filter ( self, object ):
        """ Determines whether the specified object matches the filter criteria.
        """
        return (object.visible and (not object.masked))

#-------------------------------------------------------------------------------
#  'PropertySheetBase' class:
#-------------------------------------------------------------------------------

class PropertySheetBase ( HasPrivateFacets ):
    """ Defines the base class for an item that can appear in the GridEditor
        used to create the property sheet.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The user interface name of the facet this item is editing:
    label = Str

    # The owner for this item:
    owner = Instance( 'PropertySheetGroup' )

    # Is this item currently visible?
    visible = Property

    # The amount of indenting to use for the label:
    indent = Int

    # Is this item being masked by a filter?
    masked = Bool( False )

    #-- Public Interface -------------------------------------------------------

    def dispose ( self ):
        """ Called when the property sheet editor gets disposed of.
        """
        pass

    #-- Property Implementations -----------------------------------------------

    def _get_visible ( self ):
        return ((self.owner is None) or
                (self.owner.visible and self.owner.is_open))

#-------------------------------------------------------------------------------
#  'PropertySheetGroup' class:
#-------------------------------------------------------------------------------

class PropertySheetGroup ( PropertySheetBase ):
    """ Defines a group of related property sheet items. A group is a container
        for other property sheet groups or items. Groups can be opened or closed
        to reveal or hide their contained items.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Are the children of this item open (i.e. visible)?
    is_open = Bool( True )

    # The number of immediate children of this item:
    count = Int

    # The total number of children of this item (including grandchildren, ...):
    total = Int

    # The PropertySheetEditor this group is part of:
    editor = Any

    # The HasFacets object the items in this group are contained in:
    parent = Instance( HasFacets )

    # The object.name that created this group (if any):
    object = Instance( HasFacets )
    name   = Str

    # Is the 'object.name' information valid?
    has_object_name = Property

    #-- PropertySheetBase Interface --------------------------------------------

    def dispose ( self ):
        """ Removes any facet change listeners when the editor is closed.
        """
        if self.has_object_name:
            self.object.on_facet_set( self._resynch, self.name, remove = True )

        if self.parent is not None:
            self.parent.on_facet_set( self._facet_added, 'facet_added',
                                      remove = True )

    #-- Property Implementations -----------------------------------------------

    def _get_has_object_name ( self ):
        return ((self.object is not None) and (self.name != ''))

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'object, name' )
    def _owner_modified ( self ):
        """ Handles the 'owner' or 'name' facet being changed.
        """
        if self.has_object_name:
            self.object.on_facet_set( self._resynch, self.name )


    def _parent_set ( self, parent ):
        """ Handles the 'parent' facet being changed.
        """
        if parent is not None:
            parent.on_facet_set( self._facet_added, 'facet_added' )

    #-- Private Methods --------------------------------------------------------

    def _resynch ( self ):
        """ Resynchronizes the property sheet when an object with facets is
            replaced.
        """
        if self.parent is not None:
            self.parent.on_facet_set( self._facet_added, 'facet_added',
                                      remove = True )

        if self.has_object_name:
            self.object.on_facet_set( self._resynch, self.name, remove = True )

        self.editor.modified = self


    def _facet_added ( self, name ):
        """ Handles a new facet being added to the parent object.
        """
        if self.has_object_name and (name[:1] != '_'):
            self._resynch()

#-------------------------------------------------------------------------------
#  'PropertySheetItemBase' class:
#-------------------------------------------------------------------------------

class PropertySheetItemBase ( PropertySheetBase ):
    """ Defines the base class for any simple item that can appear in a
        GridEditor property sheet.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The HasFacets object this item is editing:
    object = Instance( HasFacets )

    # The name of the facet this item in editing:
    name = Str

    # The PropertySheetAdapter associated with this item:
    adapter = WeakRef( PropertySheetAdapter )

    # Event fired when some visual aspect of this item needs to be updated:
    update = Event

    # The editing mode to use for this item's value:
    mode = EditMode

    # The editing change mode to use for this item's value:
    change_mode = ChangeMode

    # The editor to use when editing this item's value:
    editor = Instance( EditorFactory )

    #-- Public Methods ---------------------------------------------------------

    def value_for ( self, name ):
        return getattr( self.adapter, 'get_' + name )( self.object, self.name )

#-------------------------------------------------------------------------------
#  'PropertySheetItem' class:
#-------------------------------------------------------------------------------

class PropertySheetItem ( PropertySheetItemBase ):
    """ Defines an item that can appear in the GridEditor used to create the
        property sheet. In effect, the property sheet is really a GridEditor
        that is editing a list of PropertySheetItem objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The value of the facet this item is editing (it is dynamically created
    # when the instance is constructed):
    # value = DelegatesTo ( 'object', name )

    #-- HasFacets Interface ----------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        # Dynamically create the 'value' facet this item will delegate to
        # based upon the 'facet' name supplied:
        self.add_facet( 'value', DelegatesTo( 'object', self.name ) )

    #-- PropertySheetBase Interface --------------------------------------------

    def dispose ( self ):
        """ Removes any facet change listeners when the editor is closed.
        """
        self.remove_facet( 'value' )

#-------------------------------------------------------------------------------
#  'PropertySheetEventItem' class:
#-------------------------------------------------------------------------------

class PropertySheetEventItem ( PropertySheetItem ):
    """ Special class for property sheet items that are 'events'.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The logical 'content' of the property sheet item:
    content = Any

    #-- Facet Default Values ---------------------------------------------------

    def _content_default ( self ):
        if self.editor is not None:
            return getattr( self.editor, 'label', self.name )

        return self.name

#-------------------------------------------------------------------------------
#  'PropertySheetIndexedItem' class:
#-------------------------------------------------------------------------------

class PropertySheetIndexedItem ( PropertySheetItemBase ):
    """ Defines an item that represents the value of a particular indexed item
        in an associated facets list or dictionary.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The index of this item within the parent list:
    index = Any

    # The value of the list item:
    value = Any

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        if self.facets_inited():
            items = getattr( self.object, self.name )
            if isinstance( items, tuple ):
                items = list( items )
                items[ self.index ] = value
                setattr( self.object, self.name, tuple( items ) )
            else:
                items[ self.index ] = value

    #-- Public Methods ---------------------------------------------------------

    def value_for ( self, name ):
        values = getattr( self.adapter, 'get_' + name )(
            self.object, self.name
        )
        if isinstance( values, IndexTypes ):
            return values[ self.index ]

        return values

#-------------------------------------------------------------------------------
#  'PropertySheetGridAdapter' class:
#-------------------------------------------------------------------------------

class PropertySheetGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping PropertySheetItem objects to the grid editor.
    """

    columns = [
        ( 'Name',  'label' ),
        ( 'Value', 'value' )
    ]

    # Item text color:
    text_color                             = Color

    # Group related values:
    PropertySheetGroup_bg_color            = Color
    PropertySheetGroup_selected_bg_color   = Color
    PropertySheetGroup_text_color          = Color
    PropertySheetGroup_selected_text_color = Color
    PropertySheetGroup_value_text          = Str( '' )
    PropertySheetGroup_can_edit            = Bool( False )

    # Item related values:
    PropertySheetItem_label_can_edit       = Bool( False )

    #-- HasFacets Interface ----------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        scheme = ColorSchemes[ self.object.factory.scheme ]
        self.odd_bg_color                           = scheme[0]
        self.even_bg_color                          = scheme[1]
        self.text_color                             = scheme[3]
        self.PropertySheetGroup_bg_color            = \
        self.PropertySheetGroup_selected_bg_color   = scheme[2]
        self.PropertySheetGroup_text_color          = \
        self.PropertySheetGroup_selected_text_color = scheme[4]

    #-- Adapter Value Methods --------------------------------------------------

    def label_indent ( self ):
        return self.item.indent


    def label_title ( self ):
        filter = self.object.name_filter

        return ('Name' if filter == '' else ('Name [%s]' % filter))


    def label_column_image ( self ):
        if not self.object.name_filter_enabled:
            return None

        suffix = ('off' if self.object.name_filter == '' else 'on')

        return ('@icons:filter_' + suffix)



    def label_column_clicked ( self ):
        if self.object.name_filter_enabled:
            if self.object.name_filter != '':
                self.object.name_filter = ''
                self.changed = True
            else:
                self.popup_for( Item( 'name_filter', show_label = False ),
                                self.object )


    def value_title ( self ):
        filter = self.object.value_filter

        return ('Value' if filter == '' else ('Value [%s]' % filter))


    def value_column_clicked ( self ):
        if self.object.value_filter_enabled:
            if self.object.value_filter != '':
                self.object.value_filter = ''
                self.changed = True
            else:
                self.popup_for( Item( 'value_filter', show_label = False ),
                                self.object )


    def value_column_image ( self ):
        if not self.object.value_filter_enabled:
            return None

        suffix = ('off' if self.object.value_filter == '' else 'on')

        return ('@icons:filter_' + suffix)



    def PropertySheetGroup_label_image ( self ):
        return ('@icons:open' if self.item.is_open else '@icons:closed')


    def PropertySheetGroup_clicked ( self ):
        self.item.is_open = not self.item.is_open
        self.changed      = True


    def PropertySheetItemBase_selected_bg_color ( self ):
        return (self.odd_bg_color if (self.row % 2) == 0 else
                self.even_bg_color)


    def PropertySheetItemBase_value_clicked ( self ):
        mode = self.item.mode
        if isinstance( mode, basestring ) and (mode not in ModeMap):
            mode = getattr( self.object.property_sheet_adapter, mode, mode )

        if callable( mode ):
            mode = mode( self.item )

        return ModeMap.get( mode, mode )


    def PropertySheetItemBase_value_change_mode ( self ):
        return self.item.change_mode


    def PropertySheetItemBase_value_can_edit ( self ):
        return ((self.item.editor is not None) and
                (self.item.mode != 'readonly'))


    def PropertySheetItemBase_value_editor ( self ):
        return self.item.editor


    def PropertySheetItemBase_value_formatter ( self ):
        return self.item.value_for( 'formatter' )


    def PropertySheetItemBase_value_image ( self ):
        return self.item.value_for( 'image' )


    def PropertySheetItemBase_value_image_alignment ( self ):
        return self.item.value_for( 'image_alignment' )


    def PropertySheetItemBase_value_paint ( self ):
        return self.item.value_for( 'paint' )


    def PropertySheetItemBase_value_theme ( self ):
        return self.item.value_for( 'theme' )


    def PropertySheetItemBase_label_image ( self ):
        return self.item.value_for( 'label_image' )


    def PropertySheetItemBase_label_image_alignment ( self ):
        return self.item.value_for( 'label_image_alignment' )


    def PropertySheetItemBase_label_paint ( self ):
        return self.item.value_for( 'label_paint' )


    def PropertySheetItemBase_label_theme ( self ):
        return self.item.value_for( 'label_theme' )


    def PropertySheetItemBase_label_menu ( self ):
        return self.item.value_for( 'label_menu' )


    def PropertySheetItemBase_tooltip ( self ):
        return self.item.value_for( 'tooltip' )


    def PropertySheetEventItem_value_content ( self ):
        return self.item.content


    def PropertySheetItem_value_alias ( self ):
        return ( self.item.object, self.item.name )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'object:[name_filter, value_filter]' )
    def _filter_modified ( self ):
        """ Handles the contents of a filter being changed.
        """
        self.changed = True

#-------------------------------------------------------------------------------
#  '_PropertySheetEditor' class:
#-------------------------------------------------------------------------------

class _PropertySheetEditor ( UIEditor ):
    """ Editor that allows editing a HasFacets object's editable facets using
        a two-column property sheet based on the GridEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the shell editor is scrollable? This value overrides the default.
    scrollable = True

    # The target object being edited:
    target = Instance( HasFacets )

    # The adapter used to manage the property sheet items:
    property_sheet_adapter = Instance( PropertySheetAdapter )

    # The list of PropertySheetItem object's corresponding to each editable
    # facet in the target object:
    items = List

    # Event fired when one of the items in the property sheet is modified:
    modified = Event

    # The filter used to determine which properties are visible:
    filter = Instance( PropertySheetFilter, () )

    # Mapping from (object,name) -> PropertySheetGroup objects, used to help
    # maintain state when property sheet groups get rebuilt dynamically:
    group_map = Any

    #-- Filter Related Facets --------------------------------------------------

    # The string used to filter property sheet names:
    name_filter = Str

    # The string used to filter property sheet values:
    value_filter = Str

    # Is name filtering supported?
    name_filter_enabled = Bool( False )

    # I value filtering enabled?
    value_filter_enabled = Bool( False )

    #-- UIEditor Interface -----------------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.init_data()

        return self.edit_facets(
            view = View(
                Item( 'items',
                      show_label = False,
                      editor     = GridEditor(
                          adapter     = PropertySheetGridAdapter,
                          operations  = [ 'edit' ],
                          drag_drop   = 'none',
                          show_titles = self.factory.show_titles,
                          monitor     = self.factory.monitor,
                          filter      = 'filter'
                      )
                )
            ),
            parent  = parent,
            kind    = 'editor'
        ).set(
            history = self.ui.history
        )


    def init_data ( self ):
        """ Initializes internal editor data.
        """
        factory                     = self.factory
        self.property_sheet_adapter = factory.adapter()
        self.target = self.object if factory.edit_object else self.value


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        if not self.factory.edit_object:
            self.target = self.value


    def dispose ( self ):
        """ Disposes of the contents of the editor.
        """
        for item in self.items:
            item.dispose()

        # Unset the following traits to avoid triggering the '_target_modified'
        # handler after this editor has been disposed of:
        self.property_sheet_adapter = None
        self.facet_setq( target = None)

        super( _PropertySheetEditor, self ).dispose()

    #-- Facets Default Values --------------------------------------------------

    def _name_filter_enabled_default ( self ):
        return ('name' in self.factory.filters)


    def _value_filter_enabled_default ( self ):
        return ('value' in self.factory.filters)


    def _group_map_default ( self ):
        return WeakValueDictionary()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'target.facet_added, property_sheet_adapter:updated' )
    def _target_modified ( self ):
        """ Handles the 'target' facet being changed.
        """
        items   = []
        adapter = self.property_sheet_adapter
        if adapter is not None:
            object        = self.target
            self._visited = set()

            for name in adapter.get_facets( object ):
                items.extend( self._item_for( object, name, 0 ) )

            self._visited = None

        self.items = items


    @on_facet_set( 'name_filter, value_filter' )
    def _filter_modified ( self ):
        """ Handles a filter value being changed.
        """
        name  = self.name_filter.lower()
        value = self.value_filter.lower()
        items = self.items
        i     = 0
        n     = len( items )
        while i < n:
            item = items[ i ]
            if isinstance( item, PropertySheetGroup ):
                i = self._filter_group( item, i + 1, name, value )
            else:
                self._filter_item( item, name, value )
                i += 1


    def _modified_set ( self, group ):
        """ Handles the 'modified' event being fired. The event is fired when
            the specified group has been modified in such a way that it (and
            all of its children) must be replaced.
        """
        items         = self.items
        index         = items.index( group )
        self._visited = set()
        items[ index: index + group.total + 1 ] = self._item_for(
            group.object, group.name, 0, False
        )
        self._visited = None

    #-- Private Methods --------------------------------------------------------

    def _item_for ( self, object, name, depth, alias = True ):
        """ Returns the list of PropertySheetItem objects for the specified
            item.
        """
        adapter = self.property_sheet_adapter
        if isinstance( name, basestring ):
            # Get the label we will display for the item:
            label = adapter.get_label( object, name )

            if alias:
                object, name = adapter.get_alias( object, name )

            # Handle the special case of an 'event' facet, which is write-only:
            value = Undefined
            facet = object.facet( name )
            if facet.type != 'event':
                value = getattr( object, name )

            # Refuse to handle any item on the list of invalid types:
            if isinstance( value, BadTypes ):
                # Temporary fix: Use the 'include_ui' metadata to decide if this
                # value should be displayed in the property sheet.
                facet = object.facet( name )
                if (facet is not None) and (not facet.include_ui):
                    return []

            # If the value is an object with facets, create a new group for it:
            if (isinstance( value, HasFacets ) and
                adapter.get_show_children( object, name )):
                if ((depth >= self.factory.maximum_depth) or
                    (value in self._visited)):
                    # Ignore object if it would exceed the maximum tree depth
                    # or if we have already processed it somewhere else:
                    return []

                self._visited.add( value )

                return self._group_for(
                    value, label, adapter.get_facets( value ),
                    adapter.get_show_group( object, name ),
                    adapter.get_is_open( object, name ), depth, object, name )

            # If the value is a small list, tuple or dictionary of simple types,
            # create a special group for it. Otherwise, refuse to handle more
            # complex lists, tuples or dictionaries:
            if (isinstance( value, IndexTypes ) and
                adapter.get_show_children( object, name )):
                if 0 < len( value ) <= self.factory.maximum_items:
                    indices = None
                    if isinstance( value, dict ):
                        indices = value.keys()
                        indices.sort()
                        value = [ value[ key ] for key in indices ]

                    if self._has_simple_types( value ):
                        return self._list_for( object, name, indices, value,
                                               label, depth )

                return []

            # Otherwise, it is just a simple value, so create an item for it:
            editor = None
            mode   = 'readonly'
            if not self.factory.readonly:
                mode   = adapter.get_mode(   object, name )
                editor = adapter.get_editor( object, name )

            # Create either a PropertySheetItem (normal case) or a
            # PropertySheetEventItem (for an 'event' facet-based item):
            klass = PropertySheetItem
            if value is Undefined:
                klass = PropertySheetEventItem

            return [ klass(
                object      = object,
                name        = name,
                adapter     = adapter,
                label       = label,
                mode        = mode,
                change_mode = adapter.get_change_mode( object, name ),
                editor      = editor,
                indent      = depth * INDENT
            ) ]

        # The 'name' is a developer specified group consisting of the group
        # id and its associated list of contained facets:
        name, facets = name

        return self._group_for(
            object, adapter.get_label( object, name ), facets, True,
            adapter.get_is_open( object, name ), depth
        )


    def _group_for ( self, item, label, facets, show_group, is_open, depth,
                     object = None, name = '' ):
        """ Returns the list of all PropertySheetItem objects that belong to the
            specified group.
        """
        owner = None
        if show_group:
            # If we have previously created a group for this item, re-use it;
            # otherwise create a new one:
            owner = self._current_group_for( object, name )
            if owner is None:
                owner = PropertySheetGroup( is_open = is_open )
                self._current_group_for( object, name, owner )

            owner.set(
                label  = label,
                indent = depth * INDENT,
                editor = self,
                parent = item,
                object = object,
                name   = name
            )
            depth += 1

        children = []
        for name in facets:
            children.extend( self._item_for( item, name, depth ) )

        if owner is None:
            return children

        count = 0
        for child in children:
            if child.owner is None:
                child.owner = owner
                count      += 1

        owner.count = count
        owner.total = len( children )

        return ([ owner ] + children)


    def _current_group_for ( self, object, name, group = None ):
        """ Returns/Sets the current PropertySheetGroup object for the specified
            *object* and *name*.
        """
        if (object is None) or (name == ''):
            return None

        key = '%s.%s' % ( id( object ), name )
        if group is not None:
            self.group_map[ key ] = group

        return self.group_map.get( key )


    def _list_for ( self, object, name, indices, values, label, depth ):
        """ Returns the list of all PropertySheetIndexedItem objects that belong
            to the specified list group.
        """
        adapter = self.property_sheet_adapter
        items   = []
        owner   = None
        if adapter.get_show_group( object, name ):
            owner = self._current_group_for( object, name )
            if owner is None:
                owner = PropertySheetGroup(
                    is_open = adapter.get_is_open( object, name )
                )
                self._current_group_for( object, name, owner )

            owner.set(
                label  = label,
                indent = depth * INDENT,
                count  = len( values )
            )
            items.append( owner )
            depth += 1

        editor      = adapter.get_editor( object, name )
        labels      = adapter.get_labels( object, name )
        change_mode = adapter.get_change_mode( object, name )
        mode        = 'readonly'
        if not self.factory.readonly:
            mode = adapter.get_mode( object, name )

        if indices is None:
            indices = range( len( values ) )
            if labels is None:
                labels  = [ '' ] * len( values )
        elif labels is None:
            labels = [ user_name_for( str( index ) ) for index in indices ]

        indexed_editor = isinstance( editor, IndexTypes )
        indexed_mode   = isinstance( mode,   IndexTypes )

        for label, index, value in zip( labels, indices, values ):
            item_editor = indexed_item( index, editor, indexed_editor )
            item_mode   = indexed_item( index, mode,   indexed_mode   )
            if ((item_editor is None) or
                (isinstance( item_editor, ItemEditors ) and
                 (item_mode == 'inline'))):
                item_editor = TextEditor( evaluate = type( value ),
                                          strict   = True )

            items.append( PropertySheetIndexedItem(
                object      = object,
                name        = name,
                adapter     = adapter,
                label       = label,
                index       = index,
                value       = value,
                editor      = item_editor,
                mode        = item_mode,
                change_mode = change_mode,
                indent      = depth * INDENT,
                owner       = owner
            ) )

        return items


    def _has_simple_types ( self, items ):
        """ Make sure all the items in a list are of simple, easily editable
            types.
        """
        for item in items:
            if not isinstance( item, SimpleTypes ):
                return False

        return True


    def _filter_group ( self, item, start, name, value ):
        """ Computes the masking value for all items in the group and for the
            group itself. Returns the index of the next item after the group
            (and any of its sub-groups).
        """
        items  = self.items
        masked = 0

        # Handle the special case of a name only match that matches the group
        # name by saying that it matches all of the group's children:
        if ((name != '')  and
            (value == '') and
            (item.label.lower().find( name ) >= 0)):
            name = ''

        for i in xrange( item.count ):
            an_item = items[ start ]
            if isinstance( an_item, PropertySheetGroup ):
                start = self._filter_group( an_item, start + 1, name, value )
            else:
                self._filter_item( an_item, name, value )
                start += 1

            if an_item.masked:
                masked += 1

        item.masked = (masked == item.count)

        return start


    def _filter_item ( self, item, name, value ):
        """ Computes the masking value for the specified item.
        """
        item.masked = (((name != '') and
                        (item.label.lower().find( name ) < 0)) or
                       ((value != '') and
                        (str( item.value ).lower().find( value ) < 0)))

#-------------------------------------------------------------------------------
#  'PropertySheetEditor' class:
#-------------------------------------------------------------------------------

class PropertySheetEditor ( BasicEditorFactory ):

    # The class used to construct editor objects:
    klass = _PropertySheetEditor

    # A factory for creating a PropertySheetAdapter subclass for mapping from
    # facet values to editor values:
    adapter = Callable( PropertySheetAdapter )

    # Should the 'Name/Value' column headers be displayed?
    show_titles = Bool( True )

    # Should the editor edit the specified facet or the entire object?
    edit_object = Bool( False )

    # Maximum number of items to display for a list or tuple:
    maximum_items = Int( 30 )

    # Maximum depth to allow in object nesting:
    maximum_depth = Int( 5 )

    # The filters available to the user:
    filters = List( Enum( 'name', 'value' ), [ 'name' ] )

    # Are the contents of the editor read-only?
    readonly = Bool( False )

    # What items should be monitored for changes:
    monitor = Enum( 'selected', 'all', 'none' )

    # The color scheme to use:
    scheme = Enum( 'grey', 'blue', 'olive', 'black', 'white' )

#-- EOF ------------------------------------------------------------------------