"""
Defines an editor for list-like collections (i.e. lists, tuples, numpy arrays).
It allows manipulating the contents of the list-like value using add, delete
and move operations, as well as live editing of the contents of each list
element.
"""

# fixme: Allow auto scrolling while moving items.
# fixme: Improve visuals for editing simple items, like strings.

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, Bool, Str, Unicode, Int, Long, Float, \
           Range, Callable, Any, Instance, List, Enum, Tuple, Theme, ATheme,  \
           UI, Property, View, HGroup, Item, UItem, TextEditor, on_facet_set

from facets.core.facet_base \
    import inn

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.theme \
    import LEFT

from facets.ui.constants \
    import screen_dy

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from basic types to their corresponding Facets type:
FacetsMap = {
    str:     Str,
    unicode: Unicode,
    int:     Int,
    long:    Long,
    float:   Float
}

# The set of simple types handled by the default list view adapter:
SimpleTypes = ( basestring, int, float, long )

# The set of types having list-like behavior:
try:
    import numpy

    ListTypes = ( list, numpy.ndarray )
    FacetsMap.update( {
        numpy.int8:    Int,
        numpy.int16:   Int,
        numpy.int32:   Int,
        numpy.int64:   Int,
        numpy.uint8:   Int,
        numpy.uint16:  Int,
        numpy.uint32:  Int,
        numpy.uint64:  Int,
        numpy.float32: Float,
        numpy.float64: Float
    } )
except ImportError:
    numpy     = None
    ListTypes = ( list, )

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# Type used for item position and size:
IntTuple = Tuple( Int, Int )

# The ListViewEditor supported user operations:
# - 'delete': User can delete items
# - 'add':    User can add new items
# - 'move':   User can move (i.e. re-order) items
ListViewOperation = Enum( 'delete', 'add', 'move' )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def short_float ( value ):
    """ Returns a floating point value formatted to three digits to the right
        of the decimal, with excess trailing zeros removed.
    """
    result = '%.3f' % value
    col    = result.find( '.' )

    return (result if col < 0 else
            (result[ : col + 2 ] + result[ col + 2: ].rstrip( '0' )))

#-------------------------------------------------------------------------------
#  'EmptyList' class:
#-------------------------------------------------------------------------------

class EmptyList ( HasFacets ):
    """ Represents a dummy object used as a placeholder in an empty list.
    """

    #-- Facet Definitions ------------------------------------------------------

    message = Str( '<empty>' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HGroup( UItem( 'message', style = 'readonly', springy = True ) ),
        kind = 'editor'
    )

# Create a reusable empty list instance:
empty_list = EmptyList()

#-------------------------------------------------------------------------------
#  'ListViewItem' class:
#-------------------------------------------------------------------------------

class ListViewItem ( HasPrivateFacets ):
    """ Defines the visual representation of the list view items being edited.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The data item associated with this list view item:
    item = Any

    # The value (if any) associated with the data item (used for item's which
    # are a simple type):
    value = Any

    # The label for the item:
    label = Str

    # The labels to use for item elements (like lists, tuples, arrays):
    item_labels = List( value = [ '' ] )

    # The editor that owns this item:
    owner = Any # Instance( _ListViewEditor )

    # The view used to create the item's user interface:
    view = Any( '' ) # Either( Str, View )

    # The UI for this item's View:
    ui = Instance( UI )

    # The theme used for the item:
    theme = Property # ATheme

    # The label theme used for the item:
    label_theme = Property # ATheme

    # The width of the item label (in pixels):
    label_width = Property

    # The logical position of the item within the editor control:
    position = IntTuple

    # The actual position of the item within the editor control:
    draw_position = IntTuple( ( -1, -1 ) )

    # The offset of the item's View's control from the top-left corner of the
    # item:
    control_offset = IntTuple

    # The size of the item within the editor control:
    size = IntTuple

    # Is the item resizable vertically?
    resizable = Bool( False )

    # The minimum allowed height of the item:
    min_height = Int( -1 )

    # The height to use for new items (0 = default):
    height = Int

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, item = None, **facets ):
        """ Initializes the object.
        """
        if item is not None:
            self.item = item

        super( ListViewItem, self ).__init__( **facets )


    def __call__ ( self, item ):
        """ Returns a new list view item for the specified data *item*.
        """
        return self.clone_facets().set( item = item )


    def init ( self ):
        """ Initializes the object when its associated 'item' facet is set.
        """
        if self.item is empty_list:
            self.ui = empty_list.edit_facets( parent = self.owner() )
        else:
            self.ui = self.init_ui()
            if self.height > 0:
                control      = self.ui.control
                cdx, cdy     = control.size
                control.size = ( cdx, self.height )


    def init_ui ( self ):
        """ Initializes and returns the Facets UI for this item.
        """
        parent = self.owner()
        item   = self.item
        if isinstance( item, HasFacets ):
            return item.edit_facets(
                view   = self.view,
                parent = parent,
                kind   = 'editor'
            )

        if isinstance( item, ListTypes ):
            uitems = []
            labels = self.item_labels
            n      = len( labels )
            for i, value in enumerate( item ):
                style  = 'simple'
                editor = None
                facet  = FacetsMap.get( type( value ) )
                if facet is None:
                    facet = Any
                    if isinstance( value, HasFacets ):
                        facet = Instance( value.__class__ )
                        style = 'custom'
                elif facet is Float:
                    editor = TextEditor(
                        evaluate    = float,
                        format_func = short_float
                    )

                label = labels[ i % n ]
                name  = 'value_%d' % i
                self.add_facet( name, facet( value ) )
                uitems.append(
                    Item( name,
                          label      = label,
                          show_label = (label != ''),
                          style      = style,
                          editor     = editor,
                          springy    = True,
                          width      = -30
                    )
                )

            view = View( HGroup( *uitems ) )
        else:
            self.value = item
            editor     = (TupleEditor() if isinstance( item, tuple ) else
                          TextEditor( evaluate = type( item ) ) )
            view       = View( HGroup(
                             UItem( 'value', editor = editor, springy = True )
                         ) )

        return self.edit_facets( view = view, parent = parent, kind = 'editor' )


    def dispose ( self ):
        """ Handles an item being disposed of by the editor.
        """
        if self.ui is not None:
            self.ui.dispose()
            self.ui = None


    def activate ( self ):
        """ Activates an item by making it the top in the editor's z-order.
        """
        self.ui.control.activate()


    def paint ( self, g ):
        """ Draws the item within the specified graphics context *g*.
        """
        x,  y  = self.draw_position
        dx, dy = self.size

        theme = self.theme
        theme.fill( g, x, y, dx, dy )

        label = self.label
        if label != '':
            lx, ly, ldx, ldy = theme.bounds( x, y, dx, dy )
            ldx              = self.label_width
            label_theme      = self.label_theme
            label_theme.fill( lx, ly, ldx, ldy )
            label_theme.draw_text( g, label, LEFT, lx, ly, ldx, ldy )


    def best_size ( self, g ):
        """ Returns the best size for the item using the specified graphics
            context *g*.
        """
        x, y, dx, dy = self.theme.bounds( 0, 0, 0, 0 )

        ldx   = ldy = 0
        label = self.label
        if label != '':
            ldx = self.label_width
            ldy = self.label_theme.size_for( g, label )[1]

        cdx, cdy            = self.ui.control.size
        bdx                 = ldx - dx
        bdy                 = max( ldy, cdy )
        self.control_offset = ( bdx, y + ((bdy - cdy) / 2)  )

        return ( bdx + cdx, bdy - dy )


    def is_in ( self, x, y ):
        """ Returns **True** if the point specified by (*x*,*y*) is contained
            within the item, and **False** otherwise.
        """
        ix,  iy  = self.position
        idx, idy = self.size

        return ((ix <= x < (ix + idx)) and (iy <= y < (iy + idy)))


    def move_to ( self ):
        """ Animates a move of the item from its current draw position to its
            logical position.
        """
        dy = abs( self.draw_position[1] - self.position[1] )
        self.animate_facet(
            'draw_position', max( dy / 1000.0, 0.25 ), self.position
        )


    def refresh ( self ):
        """ Refreshes the display of the item.
        """
        x, y   = self.draw_position
        dx, dy = self.size
        self.owner.refresh( x, y, dx, dy )


    def reset_ui ( self ):
        """ Resets the position of the ui after the item is moved.
        """
        if self.ui is not None:
            x, y                     = self.draw_position
            ox, oy                   = self.control_offset
            self.ui.control.position = ( x + ox, y + oy )

        if self.owner is not None:
            self.owner.refresh()


    def adjust_height ( self, delta ):
        """ Increases or decreases the height of the item by the amount
           specified by *delta*. Returns *True* if the height is changed, and
           *False* otherwise.
        """
        dx, dy = self.size
        ndy    = max( dy + delta, self.min_height )
        if ndy == dy:
            return False

        self.size    = ( dx, ndy )
        control      = self.ui.control
        cdx, cdy     = control.size
        control.size = ( cdx, cdy + ndy - dy )

        return True

    #-- Facet Default Values ---------------------------------------------------

    def _default_label ( self ):
        item  = self.item
        label = (getattr( item, 'name',  None ) or
                 getattr( item, 'label', None ))

        return str( label if label is not None else
                    '[%d]' % self.owner.index_for( self ) )

    #-- Property Implementations -----------------------------------------------

    def _get_label_width ( self ):
        return self.owner.factory.label_width


    def _get_theme ( self ):
        return self.owner.theme_for( self )


    def _get_label_theme ( self ):
        return self.owner.label_theme_for( self )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self ):
        """ Handles the 'value' facet being set.
        """
        if self.value != self.item:
            self.item = self.value
            self.owner.value_for( self )


    def _anyfacet_set ( self, facet, old, new ):
        """ Handles any facet of the item being set.
        """
        if facet.startswith( 'value_' ):
            index              = int( facet[6:] )
            self.item[ index ] = new
            self.owner.value_for( self, index, new )


    def _draw_position_set ( self ):
        """ Handles any facet that affects the visual appearance of the editor
            being changed.
        """
        self.reset_ui()


    def _size_set ( self ):
        """ Handles the 'size' facet being set.
        """
        if self.ui is not None:
            dx, dy       = self.size
            x, y, dx, dy = self.theme.bounds( 0, 0, dx, dy )
            cx, cy       = self.control_offset
            control      = self.ui.control
            cdy          = control.size[1]
            control.size = ( dx - cx + x, cdy )

#-------------------------------------------------------------------------------
#  '_ListViewEditor' class:
#-------------------------------------------------------------------------------

class _ListViewEditor ( ControlEditor ):
    """ Defines the custom control editor used to edit the contents of the
        editor value's list.
    """

    #-- Class Constants --------------------------------------------------------

    # Global cache for ListViewEditor related themes:
    theme_cache = {}

    #-- Facet Definitions ------------------------------------------------------

    # The value being edited (defined by the editor):
    # value = List

    # The list of list view items being edited:
    items = List # ( SetItem )

    # The current editor mode for the active item ('normal', 'hover', 'add',
    # 'delete', 'move'):
    mode = Str( 'normal' )

    # The current active item (if any):
    active_item = Instance( ListViewItem )

    # The normal theme used for displaying items:
    normal_theme = ATheme

    # The theme used when the mouse is hovering over an item:
    hover_theme = ATheme

    # The theme used when duplicating/adding an item:
    add_theme = ATheme

    # The theme used when an item is being deleted:
    delete_theme = ATheme

    # The theme used for displaying an item being moved:
    move_theme = ATheme

    # The normal theme used for displaying item labels:
    normal_label_theme = ATheme

    # The label theme used when an item is being moved/duplicated/deleted:
    active_label_theme = ATheme

    # Temporary theme used when loading a new theme into the theme cache:
    temp_theme = ATheme

    #-- ControlEditor Method Overrides -----------------------------------------

    def init ( self ):
        """ Allows the control to perform any needed initialization. Called
            immediately after the constructor has run and all externally set
            attributes have been initialized.
        """
        # Set an initial virtual size so the editor will be scrollable (the
        # correct size is set later once the control has been created):
        self.virtual_size = ( 10, 10 )

        # Set the custom tooltip for the editor:
        self().tooltip = self._tooltip()


    def post_init ( self ):
        """ Allows the control to perform any needed initialization. Called
            after the parent editor has finished all initialization of the
            control.
        """
        self._init_items()
        self.on_facet_set( self._value_modified, 'value[]' )


    def dispose ( self ):
        """ Disposes of the editor when it is no longer needed.
        """
        for item in self.items:
            item.dispose()

        self.on_facet_set( self._value_modified, 'value[]', remove = True )

        super( _ListViewEditor, self ).dispose()

    #-- Public Methods ---------------------------------------------------------

    def index_for ( self, item ):
        """ Returns the index of the list view item specified by *item*.
        """
        return self.items.index( item )


    def theme_for ( self, item ):
        """ Returns the current theme for the list view item specified by
            *item*.
        """
        return (self.normal_theme if item is not self.active_item else
                getattr( self, self.mode + '_theme' ))


    def label_theme_for ( self, item ):
        """ Returns the current label theme for the list view item specified by
            *item*.
        """
        if ((item is not self.active_item) or
            (self.mode in ( 'normal', 'hover' ))):
            self.normal_label_theme

        return self.active_label_theme


    def value_for ( self, item, index_1 = None, new_value = None ):
        """ Updates the editor value associated with the list view item
            specified by *item*.
        """
        self._no_update = True

        index_0 = self.index_for( item )
        value   = self.value
        if index_1 is None:
            value[ index_0 ] = item.value
        elif isinstance( value, list ):
            value[ index_0 ][ index_1 ] = new_value
        else:
            # Assume the value is a numpy array:
            value[ index_0, index_1 ] = new_value

        self._no_update = False

    #-- Facet Default Values ---------------------------------------------------

    def _normal_theme_default ( self ):
        return self._theme_for(
            '' if len( self.factory.operations ) == 0 else 'normal'
        )


    def _hover_theme_default ( self ):
        return self._theme_for( 'hover' )


    def _add_theme_default ( self ):
        return self._theme_for( 'add' )


    def _delete_theme_default ( self ):
        return self._theme_for( 'delete' )


    def _move_theme_default ( self ):
        return self._theme_for( 'move' )


    def _normal_label_theme_default ( self ):
        return self._theme_for( 'normal_label' )


    def _active_label_theme_default ( self ):
        return self._theme_for( 'active_label' )

    #-- Private Methods --------------------------------------------------------

    def _theme_for ( self, name ):
        """ Returns the Theme object for the theme specified by *name*.
        """
        theme = getattr( self.factory, (name or 'normal') + '_theme' )
        if theme is None:
            theme = self.theme_cache.get( name )
            if theme is None:
                self.temp_theme = '#themes:ListViewEditor_%s_theme' % name
                self.theme_cache[ name ] = theme = self.temp_theme

        return theme


    def _tooltip ( self ):
        """ Returns the tooltip to use for the editor.
        """
        tooltip    = []
        operations = self.factory.operations
        add        = 'add' in operations
        if add:
            tooltip.append( 'Click to duplicate an item.' )

        if 'delete' in operations:
            if add:
                tooltip.extend( [
                    'Long click to delete an item,',
                    'or Alt-click to quickly delete an item.'
                ] )
            else:
                tooltip.append( 'Click to delete an item.' )

            if 'move' in operations:
                tooltip.append( 'Drag up or down to move an item.' )

        return ('\n'.join( tooltip ))

    #-- Paint Handler ----------------------------------------------------------

    def paint_content ( self, g ):
        """ Paints the contents of the custom control.
        """
        if self._first_paint is None:
            self._first_paint = False
            self._compute_size( g )

        _, vyt, _, vdy = self.control.visible_bounds
        vyb            = vyt + vdy
        active_item    = self.active_item
        for item in self.items:
            iyt = item.position[1]
            iyb = iyt + item.size[1]
            if iyt >= vyb:
                break

            if (iyb > vyt) and (item is not active_item):
                item.paint( g )

        # If there is an active item, draw it last so that it will be on top of
        # all other items:
        if active_item is not None:
            active_item.paint( g )

    #-- Resize Handler ---------------------------------------------------------

    def resize ( self, event ):
        """ Handles the control being resized.
        """
        self._resize()

        super( _ListViewEditor, self ).resize( event )

    #-- Mouse Event Handlers ---------------------------------------------------

    def normal_motion ( self, event ):
        """ Handles the mouse moving in normal mode.
        """
        self.state = 'normal'
        if len( self.factory.operations ) > 0:
            item        = self._item_at( event.x, event.y )
            active_item = self.active_item
            if item is not active_item:
                self.active_item = item
                inn( active_item ).refresh()
                inn( item ).refresh()

            self.mode = ('normal' if item is None else 'hover')

        return (self.active_item is not None)


    def normal_leave ( self ):
        """ Handles the mouse leaving the control in normal mode.
        """
        active_item, self.active_item = self.active_item, None
        inn( active_item ).refresh


    def normal_left_down ( self, event ):
        """ Handles the left mouse button being pressed in normal mode.
        """
        if self.normal_motion( event ):
            self._y    = event.y
            n          = len( self.value )
            factory    = self.factory
            operations = factory.operations
            delete     = 'delete' in operations
            add        = 'add'    in operations
            move       = 'move'   in operations
            self.state = ('pending' if move else 'clicking')
            mode       = None
            if (not event.alt_down) and add:
                max_len = factory.max_len
                mode    = 'add' if (max_len < 0) or (n < max_len) else 'hover'
                if delete:
                    do_after( 600, self._check_delete )

            self.mode = (mode     if mode is not None                 else
                        ('delete' if delete and (n > factory.min_len) else
                        ('move'   if move and (not (add or delete))   else
                         'hover')))
        else:
            self.state = 'ignoring'


    def normal_wheel ( self, event ):
        """ Handles the mouse wheel turing while in normal mode.
        """
        item = self._item_at( event.x, event.y )
        if (item is not None) and item.resizable:
            delta = event.wheel_change
            if not event.control_down:
                delta = (delta * screen_dy) / (15 if event.shift_down else 100)

            if item.adjust_height( delta ):
                self._rebuild_list()


    def clicking_left_up ( self, event ):
        """ Handles the left mouse button being released in clicking mode.
        """
        item        = self._item_at( event.x, event.y )
        active_item = self.active_item
        if item is active_item:
            if self.mode == 'add':
                self._add_item( item )
            elif self.mode == 'delete':
                self._delete_item( item )

        self.ignoring_left_up( event )


    def pending_left_up ( self, event ):
        """ Handles the left mouse button being released in pending mode.
        """
        self.clicking_left_up( event )


    def pending_motion ( self, event ):
        """ Handles the mouse moving in pending mode.
        """
        y = self._y
        if abs( event.y - y ) > 3:
            self.state  = 'moving'
            self.mode   = 'move'
            self._start = self.index_for( self.active_item )
            self.active_item.activate()
            self.moving_motion( event )


    def moving_motion ( self, event ):
        """ Handles the mouse moving in moving mode.
        """
        dy = event.y - self._y
        if dy != 0:
            item               = self.active_item
            self._y            = event.y
            x, y               = item.draw_position
            item.draw_position = ( x, y + dy )
            self._check_swap( dy )


    def moving_left_up ( self, event ):
        """ Handles the left mouse button being released in moving mode.
        """
        self.active_item.move_to()
        self._update_value()
        self.normal_motion( event )


    def ignoring_left_up ( self, event ):
        """ Handles the left mouse button being released in ignoring mode.
        """
        self.normal_motion( event )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_modified ( self ):
        """ Handles the 'value' facet being changed.
        """
        if not self._no_update:
            self._init_items()
            self.refresh()


    def _mode_set ( self ):
        """ Handles the 'mode' facet being set.
        """
        inn( self.active_item ).refresh()

    #-- Private Methods --------------------------------------------------------

    def _rebuild_list ( self ):
        """ Force the layout of the items list to be recalculated.
        """
        self._first_paint = None
        self.refresh()


    def _item_at ( self, x, y ):
        """ Returns the item (if any) containing the point specified by
            (*x*,*y*).
        """
        for item in self.items:
            if item.is_in( x, y ):
                return item

        return None


    def _default_factory ( self, item ):
        """ Returns a copy of the specified *item*.
        """
        if isinstance( item, HasFacets ):
            return item.clone_facets()

        return (list( item ) if isinstance( item, list ) else item)


    def _add_index ( self, index, data ):
        """ Inserts the data specified by *data* at the index specified by
            *index*.
        """
        value = self.value
        if isinstance( value, list ):
            value.insert( index, data )
        elif isinstance( value, tuple ):
            self.value = value[ : index ] + ( data, ) + value[ index: ]
        elif numpy is not None:
            # Assume it is a numpy array:
            self.value = numpy.insert( value, index, data, 0 )


    def _add_item ( self, item ):
        """ Adds a duplicate of the list view item specified by *item*.
        """
        self._no_update = True

        # Create a copy of the item's data:
        is_empty  = (item.item is empty_list)
        data      = (None if is_empty else item.item)
        factory   = self.factory.factory
        copy_data = None
        try:
            if issubclass( factory, HasFacets ):
                copy_data = (factory() if data is None else
                             self._default_factory( data ))
        except:
            pass

        if copy_data is None:
            if isinstance( factory, HasFacets ) or (not callable( factory )):
                copy_data = self._default_factory(
                    factory if data is None else data
                )
            else:
                copy_data = (factory or self._default_factory)( data )

        # Update the editor's value with the new data:
        index = self.index_for( item ) + (not is_empty)
        self._add_index( index, copy_data )

        # Create a new list view item for the copy of the data:
        copy_item = self.factory.adapter( copy_data ).set( owner = self )
        copy_item.init()

        if is_empty:
            # We are replacing the empty list item with a new item, so dispose
            # of the empty list item and completely replace the items list:
            item.dispose()
            self.items = [ copy_item ]
            self._rebuild_list()
        else:
            # Make the new item the same size/position as the one it is copied
            # from:
            copy_item.set(
                size           = item.size,
                position       = item.position,
                control_offset = item.control_offset,
                min_height     = item.min_height
            ).set(
                draw_position  = item.draw_position
            )
            copy_item.ui.control.size = item.ui.control.size

            # Update the editor's model with the copied item:
            self.items.insert( index, copy_item )

            # Increase the virtual size by the height of the new item:
            self._adjust_size( item.size[1] )

            # Rebuild the editor's view:
            self._rebuild()

        self._no_update = False


    def _delete_index ( self, index ):
        """ Deletes the value at the index specified by *index*.
        """
        value = self.value
        if isinstance( value, list ):
            del value[ index ]
        elif isinstance( value, tuple ):
            self.value = value[ : index ] + value[ index + 1: ]
        elif numpy is not None:
            # Assume it is a numpy array:
            self.value = numpy.delete( value, index, 0 )


    def _delete_item ( self, item ):
        """ Deletes the list view item specified by *item*.
        """
        self._no_update = True

        index = self.index_for( item )
        self._delete_index( index )

        # Dispose of the deleted item's user interface:
        item.dispose()

        if len( self.value ) == 0:
            # If the list is now empty, re-task the deleted item to be the
            # empty list placeholder:
            item.item = empty_list
            item.init()
            item.reset_ui()
            item.size = ( 0, 0 )
            self._rebuild_list()
        else:
            # Remove the list view item from the editor model:
            del self.items[ index ]

            # Decrease the virtual size by the height of the deleted item:
            self._adjust_size( -item.size[1] )

            # Rebuild the editor's view:
            self._rebuild()

        self._no_update = False


    def _reorder ( self ):
        """ Reset the position of each item based upon its current position in
            the items list and animate the movement from its old position to its
            new position.
        """
        _, vyt, _, vdy = self.control.visible_bounds
        vyb            = vyt + vdy
        y = 0 if self.theme is None else self.theme.bounds( 0, 0, 0, 0 )[1]
        for item in self.items:
            ix, iy = item.position
            if y != iy:
                item.position = ( ix, y )

                # Animate the move if either end point is visible, otherwise just
                # update its draw position to match its logical position. This
                # saves time when there are lots of items in the set:
                if (vyt <= y < vyb) or (vyt <= item.draw_position[1] < vyb):
                    item.move_to()
                else:
                    item.draw_position = ( ix, y )

            y += item.size[1]


    def _check_delete ( self ):
        """ Checks if we can switch from 'add' to 'delete' mode after a short
            delay has expired.
        """
        if self.state == 'pending':
            self.mode = ('delete' if (len( self.value ) > self.factory.min_len)
                         else 'hover')
            self.active_item.refresh()


    def _check_swap ( self, direction ):
        """ Checks to see if the moved item needs to be swapped with one of its
            neighbors.
        """
        item  = self.active_item
        dy    = item.size[1]
        y     = item.draw_position[1]
        items = self.items
        i     = items.index( item )
        if direction > 0:
            if (i + 1) < len( items ):
                item2 = items[ i + 1 ]
                dy2   = item2.size[1]
                if (y + dy) > (item2.position[1] + (dy2 / 2)):
                    items[ i ], items[ i + 1 ]    = item2, item
                    x, y                          = item.position
                    item.position, item2.position = ( x, y + dy2 ), ( x, y )
                    item2.move_to()
        elif i > 0:
            item2 = items[ i - 1 ]
            if y < (item2.position[1] + (item2.size[1] / 2)):
                items[ i ], items[ i - 1 ]    = item2, item
                x, y                          = item2.position
                item.position, item2.position = ( x, y ), ( x, y + dy )
                item2.move_to()


    def _update_value ( self ):
        """ Updates the current editor value at the end of a 'move' operation.
        """
        item        = self.active_item
        start, end  = self._start, self.items.index( item )
        if start != end:
            self._no_update = True

            self._delete_index( start )
            self._add_index( end, item.item )
            self._retab()

            self._no_update = False


    def _compute_size ( self, g ):
        """ Computes the sizes of all items and the total virtual size of the
            control using the graphics context specified by *g*.
        """
        dx, dy = self.control.size
        x = y  = tdx = tdy = 0
        if self.theme is not None:
            x, y, tdx, tdy = self.theme.bounds( 0, 0, 0, 0 )
            tdy            = y + tdy
            dx             = self.theme.bounds( 0, 0, dx, dy )[2]

        for item in self.items:
            bdx, bdy = item.size
            if bdy == 0:
                bdx, bdy = item.best_size( g )
                if item.min_height < 0:
                    item.min_height = bdy

            item.size     = ( dx, bdy )
            item.position = item.draw_position = ( x, y )
            y            += bdy

        self.virtual_size = ( 150, y + tdy )
        self._retab()


    def _adjust_size ( self, dy ):
        """ Adjusts the current virtual size by the vertical amount specified by
            *dy*.
        """
        vdx, vdy          = self.virtual_size
        self.virtual_size = ( vdx, vdy + dy )


    def _retab ( self ):
        """ Rebuilds the tab order for the editor based on the position of each
            list view item.
        """
        controls = []
        for control in self().children:
            y = control.screen_position[1] * 10000
            controls.extend( [ ( y + i, child )
                               for i, child in enumerate( control.children ) ] )

        controls.sort( key = lambda item: item[0] )
        controls = [ item[1] for item in controls ]

        # fixme: This Qt specific code needs to be moved into the abstraction
        # layer via a new API...
        from PyQt4.QtGui import QWidget

        for i in xrange( len( controls ) - 1 ):
            QWidget.setTabOrder( controls[ i ](), controls[ i + 1 ]() )


    def _resize ( self ):
        """ Recomputes the width of all items based upon the current control
            size.
        """
        dx, dy = self.control.size
        if self.theme is not None:
            dx = self.theme.bounds( 0, 0, dx, dy )[2]

        for item in self.items:
            idx, idy  = item.size
            item.size = ( dx, idy )


    def _rebuild ( self ):
        """ Refresh the display and its content positions.
        """
        self._reorder()
        do_after( 250, self._retab )


    def _init_items ( self ):
        """ Initializes the list of items based on the current editor value.
        """
        if not self._no_update:
            # Create a mapping of old values to their corresponding item:
            new = []
            old = dict(
                [ ( id( item.item ), item ) for item in self.items ]
            )
            n = len( old )

            # Build the list of items from the current editor value:
            adapter = self.factory.adapter
            for value in self.value:
                item = old.get( id( value ) )
                if item is None:
                    # If the value was not already being edited, create a new
                    # item for it:
                    item = adapter( value ).set( owner = self )
                    item.init()
                else:
                    # Else re-use the item and prevent it from being disposed:
                    del old[ id( value ) ]

                # Add the resulting item to the new list of items being edited:
                new.append( item )

            # Dispose of any items that are no longer in use:
            for item in old.values():
                item.dispose()

            # If there are no items now, and 'add' operations are allowed, make
            # sure that the list contains a placeholder item:
            if (len( new ) == 0) and ('add' in self.factory.operations):
                item = adapter( empty_list ).set( owner = self )
                item.init()
                new.append( item )

            # Set the new list of items being edited:
            self.items = new

            if (len( old ) == 0) and (len( new ) == n):
                # If we reused all old items and didn't add any new ones, then
                # we can just re-order them:
                self._reorder()
            else:
                # Force a recalculation of item sizes and positions:
                self._rebuild_list()

#-------------------------------------------------------------------------------
#  'ListViewEditor' class:
#-------------------------------------------------------------------------------

class ListViewEditor ( CustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The custom control editor class:
    klass = _ListViewEditor

    # The set of valid user operations that can be performed:
    operations = List( ListViewOperation, value = [ 'add', 'delete', 'move' ] )

    # Function to convert user items into editor items:
    adapter = Callable( ListViewItem )

    # Factory for creating new user items. It should be of the form:
    # new_item = factory( item ), where 'new_item' is a new user item, and
    # 'item' is an existing user item to use as the prototype for the new item,
    # or None if no prototype item is available. If the specified value is not
    # callable, it is assumed to be a prototype item that can be used to create
    # new items from. Also accepts special case values of any HasFacets class or
    # instance, or any simple type, such as a string, number or list, which can
    # be used to create a new value when adding to an empty list value:
    factory = Any

    # The minimum length allowed for the editor value:
    min_len = Int( 0 )

    # The maximum length allowed for the editor value (< 0 means unbounded):
    max_len = Int( -1 )

    # The normal theme used for displaying items:
    normal_theme = ATheme

    # The theme used when the mouse is hovering over an item:
    hover_theme = ATheme

    # The theme used when duplicating/adding an item:
    add_theme = ATheme

    # The theme used when an item is being deleted:
    delete_theme = ATheme

    # The theme used for displaying an item being moved:
    move_theme = ATheme

    # The normal theme used for displaying item labels:
    normal_label_theme = ATheme

    # The label theme used when an item is being moved/duplicated/deleted:
    active_label_theme = ATheme

    # The width of item labels (in pixels):
    label_width = Range( 0, 500, 60 )

#-- EOF ------------------------------------------------------------------------