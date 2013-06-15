"""
Defines an editor for optionally ordered sets. A set can be either a Python set,
list or tuple. The values of the set are constrained to be unique elements from
a specified finite pool of elements.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Bool, Int, Callable, Any, Str, Instance, List, \
           Enum, Tuple, Image, Theme, ATheme, on_facet_set

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.ui.ui_facets \
    import image_for

from facets.ui.theme \
    import LEFT

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The set of simple types handled by the default set adapter:
SimpleTypes = ( basestring, int, float, long )

# Facet type used for item position and size:
IntTuple = Tuple( Int, Int )

#-------------------------------------------------------------------------------
#  'SetItem' class:
#-------------------------------------------------------------------------------

class SetItem ( HasPrivateFacets ):
    """ Defines the visual representation of the set elements being edited.
    """

    #-- Class Definitions -------------------------------------------------------

    # The themes used for a SetItem (excluded, included):
    themes = (
        Theme( '@xform:b?L27', content = ( 6, 3, 1, 1 ) ),
        Theme( '@xform:b?L40', content = ( 6, 3, 1, 1 ) )
    )

    # The images used for a SetItem (excluded, included):
    images = ( None, )

    # The image used to indicate that a SetItem can be dragged:
    drag_image = image_for( '@facets:up_down?H95L14s64' )

    # The amount of margin between the drag image and the rest of the item:
    drag_margin = 4

    #-- Facet Definitions ------------------------------------------------------

    # The set element associated with this item:
    item = Any

    # The label for the item:
    label = Str

    # The image displayed for the item (if any):
    image = Image

    # The editor that owns this item:
    owner = Any # Instance( _SetEditor )

    # Is this item included in the set:
    included = Bool

    # Can the item be dragged by the user to a new location?
    can_drag = Bool

    # The theme used for the item:
    theme = ATheme

    # The logical position of the item within the editor control:
    position = IntTuple

    # The actual position of the item within the editor control:
    draw_position = IntTuple

    # The size of the item within the editor control:
    size = IntTuple

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, item = None, **facets ):
        """ Initializes the object.
        """
        if item is not None:
            self.item = item

        super( SetItem, self ).__init__( **facets )


    def init ( self ):
        """ Initializes the object when its associated 'item' facet is set.
        """
        label = self.item
        if not isinstance( label, SimpleTypes ):
            label = (getattr( label, 'name',  None ) or
                     getattr( label, 'label', None ) or
                     label.__class__.__name__)

        self.label = str( label )


    def paint ( self, g ):
        """ Draws the item within the specified graphics context *g*.
        """
        x,  y  = self.draw_position
        dx, dy = self.size

        self.theme.fill( g, x, y, dx, dy )
        self.theme.draw_text( g, self.label, LEFT, x, y, dx, dy, self.image )
        if self.can_drag:
            ix, iy = self._drag_position()
            g.draw_bitmap( self.drag_image.bitmap, ix, iy )


    def best_size ( self, g ):
        """ Returns the best size for the item using the specified graphics
            context *g*.
        """
        dx, dy = self.theme.size_for( g, self.label, self.image )
        if self.can_drag:
            dx += self.drag_image.width + self.drag_margin

        return ( dx, dy )


    def is_in ( self, x, y ):
        """ Returns **True** if the point specified by (*x*,*y*) is contained
            within the item, and **False** otherwise.
        """
        ix,  iy  = self.position
        idx, idy = self.size

        return ((ix <= x < (ix + idx)) and (iy <= y < (iy + idy)))


    def in_drag ( self, x, y ):
        """ Returns **True** if the point specified by (*x*,*y*) is in the drag
            area of the item, and **False** otherwise.
        """
        if not self.can_drag:
            return False

        ix, iy = self._drag_position()

        return ((ix <= x < (ix + self.drag_image.width)) and
                (iy <= y < (iy + self.drag_image.height)))


    def move_to ( self ):
        """ Animates a move of the item from its current draw position to its
            logical position.
        """
        self.animate_facet( 'draw_position', 0.25, self.position )

    #-- Facet Default Values ---------------------------------------------------

    def _theme_default ( self ):
        return self.themes[0]


    def _image_default ( self ):
        return self.images[0]

    #-- Facet Event Handlers ---------------------------------------------------

    def _item_set ( self ):
        """ Handles the 'item' facet being set.
        """
        self.init()


    def _included_set ( self, included ):
        """ Handles the 'included' facet being changed.
        """
        self.theme = self.themes[ 0 - included ]
        self.image = self.images[ 0 - included ]


    @on_facet_set( 'draw_position, included' )
    def _visuals_modified ( self ):
        """ Handles any facet that affects the visual appearance of the editor
            being changed.
        """
        if self.owner is not None:
            self.owner.refresh()

    #-- Private Methods --------------------------------------------------------

    def _drag_position ( self ):
        """ Returns the position of the top-left hand corner of the drag image.
        """
        tx, ty   = self.draw_position
        tdx, tdy = self.size
        ix, iy, idx, idy = self.theme.bounds( tx, ty, tdx, tdy )

        return ( ix + idx - self.drag_image.width,
                 iy + ((idy - self.drag_image.height) / 2) )

#-------------------------------------------------------------------------------
#  '_SetEditor' class:
#-------------------------------------------------------------------------------

class _SetEditor ( ControlEditor ):
    """ Defines the custom control editor used to edit the contents of the
        editor value's set.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of set items being edited:
    items = List # ( SetItem )

    # The current item being dragged (if any):
    drag_item = Instance( SetItem )

    # The last selected/deselected item:
    last_item = Instance( SetItem )

    # Are the items currently being dragged over to be included (or excluded)
    # from the set?
    included = Bool

    value = List

    #-- ControlEditor Method Overrides -----------------------------------------

    def init ( self ):
        """ Allows the control to perform any needed initialization. Called
            immediately after the constructor has run and all externally set
            attributes have been initialized.
        """
        # Set an initial virtual size so the editor will be scrollable (the
        # correct size is set later once the control has been created):
        self.virtual_size = ( 10, 10 )

        # Create the list of items to edit:
        self._init_items()

    #-- Paint Handler ----------------------------------------------------------

    def paint_content ( self, g ):
        """ Paints the contents of the custom control.
        """
        if self._first_paint is None:
            self._first_paint = False
            self._compute_size( g )
            self._resize()

        _, vyt, _, vdy = self.control.visible_bounds
        vyb            = vyt + vdy
        drag_item      = self.drag_item
        for item in self.items:
            iyt = item.position[1]
            iyb = iyt + item.size[1]
            if iyt >= vyb:
                break

            if (iyb > vyt) and (item is not drag_item):
                item.paint( g )

        # If there is an item being dragged, draw it last so that it will be on
        # top of all other items:
        if drag_item is not None:
            drag_item.paint( g )

    #-- Resize Handler ---------------------------------------------------------

    def resize ( self, event ):
        """ Handles the control being resized.
        """
        self._resize()

        super( _SetEditor, self ).resize( event )

    #-- Mouse Event Handlers ---------------------------------------------------

    def normal_motion ( self, event ):
        """ Handles the mouse moving in normal mode.
        """
        if self.factory.ordering == 'user':
            x, y   = event.x, event.y
            item   = self._item_at( x, y )
            cursor = 'arrow'
            if (item is not None) and item.in_drag( x, y ):
                cursor = 'sizens'

            self.control.cursor = cursor


    def normal_left_down ( self, event ):
        """ Handles the left mouse button being pressed while in normal mode.
        """
        x, y = event.x, event.y
        item = self._item_at( x, y )
        if item is not None:
            self.drag_item = item
            if item.in_drag( x, y ):
                self._y    = y
                self.state = 'dragging'
            else:
                self.state    = 'selecting'
                self.included = not item.included
                if not event.shift_down:
                    item.included = self.included
        else:
            self.state = 'ignoring'


    def selecting_motion ( self, event ):
        """ Handles a mouse motion event while in selecting mode.
        """
        if not event.shift_down:
            item = self._item_at( event.x, event.y )
            if item is not None:
                item.included = self.included


    def selecting_left_up ( self, event ):
        """ Handles the left mouse button being released in selecting mode.
        """
        self.state = 'normal'
        if self.included != self.drag_item.included:
            if event.shift_down:
                last_item = self.last_item
                if last_item is None:
                    self.drag_item.included = self.included
                else:
                    items          = self.items
                    last_index     = items.index( last_item )
                    drag_index     = items.index( self.drag_item )
                    self.drag_item = last_item
                    first          = min( last_index, drag_index )
                    last           = max( last_index, drag_index )
                    included       = last_item.included
                    for i in xrange( first, last + 1 ):
                        items[ i ].included = included
            else:
                self.drag_item.included = self.included

        self._separate_items()
        self._update_value()
        self.last_item = self.drag_item
        self.drag_item = None


    def dragging_motion ( self, event ):
        """ Handles a mouse motion event in dragging mode.
        """
        dy = event.y - self._y
        if dy != 0:
            item               = self.drag_item
            self._y            = event.y
            x, y               = item.draw_position
            item.draw_position = ( x, y + dy )
            self._check_swap()


    def dragging_left_up ( self, event ):
        """ Handles the left mouse button being released in dragging mode.
        """
        self.state = 'normal'
        self.drag_item.move_to()
        self._update_value()


    def ignoring_left_up ( self ):
        """ Handles the left mouse button being released while in ignoring mode.
        """
        self.state = 'normal'

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self ):
        """ Handles the 'value' facet being changed.
        """
        if not self._no_update:
            included = set( self.value )
            items    = self.items
            for item in items:
                item.included = (item.item in included)

            if self.factory.ordering == 'value':
                value_map = dict( [ ( item.item, item ) for item in items ] )
                included  = [ value_map[ value ] for value in self.value ]
                indices   = sorted( [ items.index( item )
                                      for item in included ] )
                items     = items[:]
                for i, item in enumerate( included ):
                    items[ indices[ i ] ] = item

                self._no_update = True
                self.items      = items
                self._no_update = False
                if not self.factory.separate:
                    self._reorder()

            self._separate_items()
            self.refresh()

    #-- Private Methods --------------------------------------------------------

    def _item_at ( self, x, y ):
        """ Returns the item (if any) containing the point specified by
            (*x*,*y*).
        """
        for item in self.items:
            if item.is_in( x, y ):
                return item

        return None


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
                # saves time when there a lots of items in the set:
                if (vyt <= y < vyb) or (vyt <= item.draw_position[1] < vyb):
                    item.move_to()
                else:
                    item.draw_position = ( ix, y )

            y += item.size[1]


    def _check_swap ( self ):
        """ Checks to see if the dragged item needs to be swapped with either
            of its neighbors.
        """
        item  = self.drag_item
        dy    = item.size[1]
        y     = item.draw_position[1]
        items = self.items
        i     = items.index( item )
        i2    = -1
        if (i + 1) < len( items ):
            item2 = items[ i + 1 ]
            if (((y + dy) > (item2.position[1] + (item2.size[1] / 2))) and
                ((not self.factory.separate) or
                 (item.included == item2.included))):
                i2 = i + 1

        if (i2 < 0) and (i > 0):
            item2 = items[ i - 1 ]
            if ((y < (item2.position[1] + (item2.size[1] / 2))) and
                ((not self.factory.separate) or
                 (item.included == item2.included))):
                i2 = i - 1

        if i2 >= 0:
            items[ i ], items[ i2 ] = item2, item
            item.position, item2.position = item2.position, item.position
            item2.move_to()


    def _update_value ( self ):
        """ Updates the current editor value.
        """
        value      = [ item.item for item in self.items if item.included ]
        self_value = self.value
        if isinstance( self_value, set ):
            value = set( value )
        elif isinstance( self_value, tuple ):
            value = tuple( value )

        if value != self_value:
            self._no_update = True
            self.value      = value
            self._no_update = False


    def _prepare_sort ( self ):
        """ Returns a tuple of the form: (compare,key), which are the item
            comparison and key extraction functions to use when sorting the
            set elements.
        """
        if self._compare_key is None:
            compare = self.factory.compare
            value   = self.factory.key
            if value is None:
                key = lambda item: item.item
            else:
                key = lambda item: value( item.item )

            self._compare_key = ( compare, key )

        return self._compare_key


    def _compute_size ( self, g ):
        """ Computes the sizes of all items and the total virtual size of the
            control using the graphics context specified by *g*.
        """
        x = y = tdx = tdy = dx = 0
        if self.theme is not None:
            x, y, tdx, tdy = self.theme.bounds( 0, 0, 0, 0 )
            tdy = y + tdy

        for item in self.items:
            bdx, bdy      = item.best_size( g )
            item.size     = ( bdx, bdy )
            item.position = item.draw_position = ( x, y )
            y            += bdy
            dx            = max( dx, bdx )

        self.virtual_size = ( dx - tdx, y + tdy )


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


    def _separate_items ( self ):
        """ Updates separated items after one or more items change their
            inclusion state.
        """
        if self.factory.separate:
            included = [ item for item in self.items if     item.included ]
            excluded = [ item for item in self.items if not item.included ]
            if self.factory.ordering == 'sort':
                compare, key = self._prepare_sort()
                included.sort( compare, key )
                excluded.sort( compare, key )

            self.items = (included + excluded)
            self._reorder()


    @on_facet_set( 'factory:values[]' )
    def _init_items ( self ):
        """ Initializes the list of items based on the current editor value.
        """
        factory  = self.factory
        adapter  = factory.adapter
        can_drag = (factory.ordering == 'user')

        # Create the list of initially included set elements:
        included   = []
        self_value = self.editor.value
        for value in self_value:
            included.append(
                adapter( value ).set(
                    owner    = self,
                    included = True,
                    can_drag = can_drag
                )
            )

        # Create the list of the remaining excluded set elements:
        self_value = set( self_value )
        excluded   = []
        for value in factory.values:
            if value not in self_value:
                excluded.append(
                    adapter( value ).set(
                        owner    = self,
                        included = False,
                        can_drag = can_drag
                    )
                )

        if factory.ordering != 'sort':
            # If items are not sorted, just concatenate the excluded items to
            # the end of the included items:
            included.extend( excluded )
        else:
            compare, key = self._prepare_sort()
            if not factory.separate:
                # If include and excluded are not kept separate, then combine
                # them and sort the result:
                included.extend( excluded )
                included.sort( compare, key )
            else:
                # If they are separate, sort them separately then combine them:
                included.sort( compare, key )
                excluded.sort( compare, key )
                included.extend( excluded )

        # Save the resulting item list:
        self.items = included

        # Force a recalculation of item sizes and positions:
        self._first_paint = None
        self.refresh()

#-------------------------------------------------------------------------------
#  'SetEditor' class:
#-------------------------------------------------------------------------------

class SetEditor ( CustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The custom control editor class:
    klass = _SetEditor

    # The set of all possible values:
    values = Any( facet_value = True )

    # Visual ordering of items in the set, where:
    # 'sort':  Items appear in the sort order specified by the 'compare' and
    #          'key' facets.
    # 'user':  Items can be re-arranged by user dragging.
    # 'value': Items appear in the order specified by the value being edited.
    ordering = Enum( 'sort', 'user', 'value' )

    # Separate selected items from unselected items:
    separate = Bool( True )

    # Function to convert user items into editor items:
    adapter = Callable( SetItem )

    # Function to compare items for sorting:
    compare = Callable

    # Function that returns the value to sort on:
    key = Callable

#-- EOF ------------------------------------------------------------------------
