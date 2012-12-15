"""
A GUI-toolkit independent editor for displaying image items in a vertically or
horizontally scrollable "filmstrip".
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, List, Instance, Str, Enum, Tuple, Int, Float, Image, ATheme,   \
           View, Item, UIEditor, BasicEditorFactory, StackEditor, ImageEditor, \
           on_facet_set

from facets.ui.theme \
    import CENTER

from facets.ui.i_stack_item \
    import BaseStackItem

from facets.ui.ui_facets \
    import Orientation, DragType

from facets.ui.stack_item_resizer \
    import StackItemResizer

from facets.ui.filmstrip_adapter \
    import FilmStripAdapter, ImageMode

from facets.ui.action_controller \
    import ActionController

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The normal states for an item:
NormalStates = ( 'normal', 'selected' )

# The hover states for an item:
HoverStates = ( 'hover', 'hover_selected' )

# The down states for an item:
DownStates = ( 'down', 'down_selected' )

#-------------------------------------------------------------------------------
#  'FilmStripItem' class:
#-------------------------------------------------------------------------------

class FilmStripItem ( BaseStackItem ):
    """ A stack item used for displaying images in a filmstrip editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The maximum 'level of detail' supported by the item (override):
    maximum_lod = 0

    # The image being displayed:
    image = Image

    # An (optional) scaled version of the image:
    scaled_image = Image

    # The scale factor used to create the current scaled image:
    scale = Float

    # The image display mode:
    mode = ImageMode

    # The label for the image:
    label = Str

    # The pop-up context menu for the item:
    menu = Any

    # Image display ratio (horizontal/vertical):
    ratio = Float( 1.0 )

    # The new size for the item proposed by the resizer tool:
    resize = Tuple( Int, Int )

    # The value to be dragged:
    drag_value = Any

    # The type of value being dragged:
    drag_type = DragType

    # The size of the popup view to use:
    popup_size = Tuple( ( 400, 400 ) )

    # The normal theme for the item:
    normal_theme = ATheme

    # The 'selected' state theme for the item:
    selected_theme = ATheme

    # The 'hover' state theme for the item:
    hover_theme = ATheme

    # The 'hover' and 'selected' state theme for the item:
    hover_selected_theme = ATheme

    # The 'down' state theme for the item:
    down_theme = ATheme

    # The 'down' and 'selected' state theme for the item:
    down_selected_theme = ATheme

    # The theme used for the image popup:
    popup_theme = ATheme

    # The current theme state of the item:
    theme_state = 'normal'

    # The current origin of the image (used when mode = 'actual'):
    origin = Tuple( Float, Float )

    # The editor associated with the item:
    editor = Any

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        pdx, pdy = self.popup_size

        return View(
            Item( 'image',
                  show_label = False,
                  editor     = ImageEditor( theme = self.popup_theme ),
                  width      = -pdx,
                  height     = -pdy
            ),
            kind         = 'popup',
            popup_bounds = self.screen_bounds
        )

    #-- Property Implementations -----------------------------------------------

    def _get_min_size ( self ):
        if self.editor.orientation == 'horizontal':
            return ( self.size[0], 20 )

        return ( 20, self.size[1] )

    #-- IStackItem Interface Methods -------------------------------------------

    def paint_item ( self, g, bounds ):
        """ Paints the text and optional label in the specified graphics
            context *g*.
        """
        x, y, dx, dy = self.bounds
        if self.label != '':
            self.current_theme.draw_label( g, self.label, CENTER, x, y, dx, dy )

        # Draw the image using the current draw mode:
        getattr( self, 'paint_%s' % self.mode )(
            g, *self.current_theme.bounds( x, y, dx, dy )
        )


    def paint_fit ( self, g, x, y, dx, dy ):
        """ Draws the image in 'fit' to available area mode.
        """
        image    = self.image
        idx, idy = image.width, image.height
        if (idx <= dx) and (idy <= dy):
            g.draw_bitmap( image.bitmap,
                           x + ((dx - idx) / 2), y + ((dy - idy) / 2) )
        else:
            self._draw_scaled( g, x, y, dx, dy )

    # 'popup' mode behaves just like 'fit' mode for painting purposes:
    paint_popup = paint_fit


    def paint_actual ( self, g, x, y, dx, dy ):
        """ Draws the image in 'actual' size mode.
        """
        image    = self.image
        idx, idy = image.width, image.height
        if (idx <= dx) and (idy <= dy):
            g.draw_bitmap( image.bitmap,
                           x + ((dx - idx) / 2), y + ((dy - idy) / 2) )
        else:
            ox, oy = self.origin
            ox     = min( int( round( ox ) ), idx - dx )
            oy     = min( int( round( oy ) ), idy - dy )
            g.blit( x, y, dx, dy, image.bitmap, ox, oy, dx, dy )


    def paint_zoom ( self, g, x, y, dx, dy ):
        """ Draws the image in 'zoom' to fit available area mode.
        """
        self._draw_scaled( g, x, y, dx, dy )

    #-- Mouse Event Handlers ---------------------------------------------------

    def enter ( self, event ):
        """ Handles the mouse pointer entering the item.
        """
        self.theme_state = HoverStates[ self.selected ]
        if self.mode == 'popup':
            bdx, bdy = self.current_theme.bounds( *self.bounds )[2:]
            if (self.image.width > bdx) or (self.image.width > bdy):
                self._show_popup()


    def leave ( self, event ):
        """ Handles the mouse pointer leaving the item.
        """
        self.theme_state = NormalStates[ self.selected ]


    def left_down ( self, event ):
        """ Handles the user pressing the left mouse button.
        """
        self.theme_state = DownStates[ self.selected ]
        if (self.mode == 'actual') or (self.drag_type is not None):
            self._xy     = ( event.x, event.y )
            self.capture = True


    def left_up ( self, event ):
        """ Handles the user releasing the left mouse button.
        """
        self.editor.select_item( self, event )
        self.theme_state = HoverStates[ self.selected ]
        self._xy         = None
        self.capture     = False


    def left_dclick ( self, event ):
        """ Handles the user double-clicking the left mouse button.
        """
        self.editor.dclick_item( self, event )


    def right_up ( self, event ):
        """ Handles the user clicking the right mouse button.
        """
        self.editor.show_menu( self, event )


    def motion ( self, event ):
        """ Handles the user moving the mouse.
        """
        if self._xy is not None:
            x, y     = self._xy
            ex, ey   = event.x, event.y
            if self.drag_type is not None:
                if (abs( ex - x ) + abs( ey - y )) >= 5:
                    self._xy     = None
                    self.capture = False
                    self.editor.adapter.drag( self.drag_value, self.drag_type,
                                              image = self.image )
            else:
                self._xy = ( ex, ey )
                image    = self.image
                idx, idy = image.width, image.height
                bdx, bdy = self.current_theme.bounds( *self.bounds )[2:]
                ox, oy   = self.origin
                nx       = min( max( 0, ox + ((x - event.x) * float( idx )) /
                                     bdx ), idx - bdx )
                ny       = min( max( 0, oy + ((y - event.y) * float( idy )) /
                                     bdy ), idy - bdy )
                if (nx != ox) or (ny != oy):
                    self.origin  = ( nx, ny )
                    self.refresh = True

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'ratio, bounds' )
    def _size_modified ( self ):
        """ Handles the bounds or aspect ratio of the item being changed.
        """
        bx, by, bdx, bdy = self.bounds
        x, y, dx, dy     = self.current_theme.bounds( bx, by, bdx, bdy )
        if self.editor.orientation == 'horizontal':
            self.size = ( bdx - dx + int( round( dy * self.ratio ) ), bdy )
        else:
            self.size = ( bdx, bdy - dy + int( round( dx / self.ratio ) ) )


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if self.theme_state in NormalStates:
            self.theme_state = NormalStates[ selected ]


    def _resize_set ( self, size ):
        """ Handles the 'resize' facet being changed.
        """
        bx, by, bdx, bdy = self.bounds
        x, y, dx, dy     = self.current_theme.bounds( bx, by, *size )
        if self.editor.orientation == 'horizontal':
            self.ratio = float( dx ) / dy
        else:
            self.ratio = float( dy ) / dx

    #-- Private Methods --------------------------------------------------------

    def _draw_scaled ( self, g, x, y, dx, dy ):
        """ Draws an image scaled to fit within the item's client area.
        """
        if (dx > 0) and (dy > 0):
            image    = self.image
            idx, idy = image.width, image.height
            rdx, rdy = float( idx ) / dx, float( idy ) / dy
            if rdx >= rdy:
                ddx, ddy = dx, int( round( idy / rdx ) )
            else:
                ddx, ddy = int( round( idx / rdy ) ), dy
                rdx      = rdy

            if rdx >= 1.5:
                if rdx != self.scale:
                    self.scale        = rdx
                    self.scaled_image = image.scale( 1.0 / rdx )

                image    = self.scaled_image
                idx, idy = image.width, image.height

            g.blit( x + ((dx - ddx) / 2), y + ((dy - ddy) / 2), ddx, ddy,
                    image.bitmap, 0, 0, idx, idy )


    def _show_popup ( self ):
        """ Displays a popup view showing a view of the image.
        """
        self.edit_facets( parent = self.editor.adapter )

#-------------------------------------------------------------------------------
#  'filmStripEditor' class:
#-------------------------------------------------------------------------------

class filmStripEditor ( UIEditor ):
    """ A GUI-toolkit independent editor for displaying image items in a
        vertically or horizontally scrollable "filmstrip".
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the value of the editor a list whose content changes should be handled
    # by the 'update_editor' method?
    is_list = True

    # The viewable filmstrip items corresponding to the items being edited:
    items = Any( [] )

    # The global image display ratio (horizontal/vertical):
    ratio = Float( 1.0 )

    # The filmstrip orientation:
    orientation = Orientation

    # The FilmStripAdapter being used:
    filmstrip_adapter = Instance( FilmStripAdapter )

    # The resizer tool to be used by each filmstrip item:
    resizer = Instance( StackItemResizer )

    # The item (if any) for which a double-click selection event is currently
    # pending
    dclick_pending = Any

    # The current set of selected edit items (dynamically added):
    #selected = Any/List

    # The current set of selected film strip items (dynamically added):
    #selected_item = Any/List

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        factory = self.factory

        return View(
            Item( 'items',
                  show_label = False,
                  editor     = StackEditor(
                      orientation = factory.orientation,
                      theme       = factory.theme
                  )
            )
        )

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory          = self.factory
        self.orientation = factory.orientation
        ratio            = factory.ratio
        if (ratio < 0.1) or (ratio > 10.0):
            ratio = 1.0

        self.ratio = ratio

        self.filmstrip_adapter = factory.adapter.facet_set( editor = self )
        self.resizer = StackItemResizer(
            is_vertical = (self.orientation == 'vertical'),
            min_size    = 50
        )
        is_list = (factory.selection_mode != 'item')
        if is_list:
            self.add_facet( 'selected',      List )
            self.add_facet( 'selected_item', List )
        else:
            self.add_facet( 'selected',      Any )
            self.add_facet( 'selected_item', Any )

        # Set up the selection listeners (if necessary):
        self.sync_value( factory.selected, 'selected', 'both',
                         is_list = is_list )

        # Create and return the editor view:
        return self.edit_facets( parent = parent, kind = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        values     = self.value
        get_item   = self.filmstrip_adapter.get_item
        self.items = items = [ get_item( value ) for value in values ]
        if self.factory.selection_mode == 'item':
            self.selected_item = None
            selected           = self.selected
            if selected is not None:
                if selected not in values:
                    self.selected = None
                else:
                    self.selected_item = items[ values.index( selected )
                                              ].facet_set( selected = True )

        else:
            selected      = []
            selected_item = []
            for value in self.selected:
                if value in values:
                    selected.append( value )
                    selected_item.append(
                        items[ values.index( value ) ].facet_set(
                                                           selected = True ) )

            self.selected_item = selected_item
            if len( selected ) != len( self.selected ):
                self.selected = selected


    def select_item ( self, item, event ):
        """ Handles the film strip item specified by *item* being selected by
            the user with the associated event data specified by *event*.
        """
        index  = self.items.index( item )
        value  = self.value[ index ]
        mode   = self.factory.selection_mode
        dclick = (self.dclick_pending is item)
        self.dclick_pending = None

        if mode == 'item':
            if item.selected:
                if event.control_down:
                    item.selected = False
                    self.selected = self.selected_item = None
            else:
                if self.selected_item is not None:
                    self.selected_item.selected = False

                item.selected      = True
                self.selected_item = item
                self.selected      = value
        elif (((mode == 'basket') or event.control_down) and (not dclick)):
            item.selected = not item.selected
            if item.selected:
                self.selected_item.append( item )
                self.selected.append( value )
            else:
                self.selected_item.remove( item )
                self.selected.remove( value )
        else:
            items = self.selected_item
            for an_item in items:
                if an_item is not item:
                    an_item.selected = False

            if (len( items ) != 1) or (items[0] is not item):
                item.selected      = True
                self.selected_item = [ item  ]
                self.selected      = [ value ]


    def dclick_item ( self, item, event ):
        """ Handles the film strip item specified by *item* being double-clicked
            by the user with the associated event data specified by *event*.
        """
        if self.factory.selection_mode == 'basket':
            self.dclick_pending = item


    def show_menu ( self, item, event ):
        """ Display the popup right-click context menu for the film strip item
            specified by *item* at the screen position described by *event*.
        """
        menu = item.menu
        if menu is not None:
            cx, cy = self.adapter.screen_position
            self.adapter.popup_menu(
                menu.create_menu( self.adapter(), ActionController(
                    ui      = self.editor_ui,
                    context = {
                        'object':  self.value[ self.items.index( item ) ],
                        'item':    item,
                        'editor':  self,
                        'adapter': self.filmstrip_adapter
                    }
                ) ),
                event.screen_x - cx - 10, event.screen_y - cy - 10
            )

#-------------------------------------------------------------------------------
#  'FilmStripEditor' class:
#-------------------------------------------------------------------------------

class FilmStripEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The class used to construct editor objects:
    klass = filmStripEditor

    # The adapter used to adapt editor items to values that can be displayed in
    # the filmstrip:
    adapter = Instance( FilmStripAdapter, () )

    # The optional extended name of the facet that the current selection is
    # synced with:
    selected = Str

    # The selection mode of the filmstrip (single or multiple items):
    # Note: 'basket' is a multiple item selection model which does not require
    # holding the shift-key to select multiple items. Each click on an item
    # either adds or removes the item from the 'basket', depending upon whether
    # the item was already in the basket or not. Double-clicking an item
    # replaces the contents of the basket with the double-clicked item.
    selection_mode = Enum( 'item', 'items', 'basket' )

    # The filmstrip orientation:
    orientation = Orientation( 'horizontal' )

    # The horizontal/vertical ratio the editor should use for images:
    ratio = Float( 1.0 )

    # The theme to use as the background theme for the editor:
    theme = ATheme( '@xform:bg?l20' )

#-- EOF ------------------------------------------------------------------------
