"""
An editor for working with a collection of images using a 'collage' style that
allows images to be moved, scaled and selected using a virtual pasteboard.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
   import fmod

from os.path \
    import basename

from facets.api \
    import HasPrivateFacets, Int, Float, Bool, Str, Any, Instance, List, \
           Tuple, Range, Image, Theme, ATheme, WeakRef, Property,        \
           property_depends_on, on_facet_set, image_for, inn

from facets.core.facet_base \
    import clamp

from facets.ui.custom_control_editor \
    import CustomControlEditor, DefaultCustomControlEditor, ControlEditor

from facets.animation.api \
    import RampTweener

from facets.extra.helper.image \
    import hlsa_derived_image

from facets.ui.pyface.timer.api \
    import do_later, do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The minimum width and height for a collage image item:
MinItemSize = 100

# The minimum scale factor allowed for an image:
MinScale = 0.05

# The maximum scale factor allowed for an image:
MaxScale = 4.0

# Width of resize corner zones:
ResizeCWidth = 20

# Width of normal resize side zones:
ResizeSWidth = 10

# Bit mask for each collage image item edge:
TOP      = 1
BOTTOM   = 2
LEFT     = 4
RIGHT    = 8
SCALE    = 16
AllSides = TOP + BOTTOM + LEFT + RIGHT

# The tweener used to activate the zone overlay:
ZoneTweener = RampTweener( cycle = 0.3, start = 1.0 )

# The themes used for drawing zones:
ZoneInactive      = Theme( '@xform:b?L20' )
ZoneActive        = Theme( '@xform:b?H51L10S40' )
ZoneLongPress     = Theme( '@xform:b?H28L10S40' )
ZoneLongMovePress = Theme( '@xform:b?L10S40' )

# Zone definitions:
# Abbreviations: T = Top, B = Bottom, L = Left, R = Right
NoZone     = -1
ResizeTL   = 0
ResizeTR   = 1
ResizeBL   = 2
ResizeBR   = 3
ResizeT    = 4
ResizeB    = 5
ResizeL    = 6
ResizeR    = 7
Hue        = 8
Saturation = 9
Lightness  = 10
Alpha      = 11
Move       = 12
Zoom       = 13
Pan        = 14

# The set of 'lockable' operations:
LockableZones = {
    ResizeTL, ResizeTR, ResizeBL, ResizeBR, ResizeT, ResizeB, ResizeL, ResizeR,
    Move
}

# Total number of zones:
Zones = Pan + 1

# Indexed mapping from a zone to its bounds description:
ZoneBounds = [
    ( 0, 0, ResizeCWidth, ResizeCWidth ),                          # ResizeTL
    ( -ResizeCWidth, 0, ResizeCWidth, ResizeCWidth ),              # ResizeTR
    ( 0, -ResizeCWidth, ResizeCWidth, ResizeCWidth ),              # ResizeBL
    ( -ResizeCWidth, -ResizeCWidth, ResizeCWidth, ResizeCWidth ),  # ResizeBR
    ( ResizeCWidth,  0, 1.0, ResizeSWidth ),                       # ResizeT
    ( ResizeCWidth, -ResizeSWidth, 1.0, ResizeSWidth ),            # ResizeB
    ( 0, ResizeCWidth, ResizeSWidth, 1.0 ),                        # ResizeL
    ( -ResizeSWidth, ResizeCWidth, ResizeSWidth, 1.0 ),            # ResizeR
    ( 0.00, 0.00, 0.25, 0.25 ),                                    # Hue
    ( 0.25, 0.00, 0.25, 0.25 ),                                    # Saturation
    ( 0.00, 0.25, 0.25, 0.25 ),                                    # Lightness
    ( 0.25, 0.25, 0.25, 0.25 ),                                    # Alpha
    ( 0.50, 0.00, 0.50, 0.50 ),                                    # Move
    ( 0.00, 0.50, 0.50, 0.50 ),                                    # Zoom
    ( 0.50, 0.50, 0.50, 0.50 )                                     # Pan
]

# Mapping from a zone to its cursor shape:
ZoneCursor = [
    'sizenwse',   # ResizeTL
    'sizenesw',   # ResizeTR
    'sizenesw',   # ResizeBL
    'sizenwse',   # ResizeBR
    'sizens',     # ResizeT
    'sizens',     # ResizeB
    'sizeew',     # ResizeL
    'sizeew',     # ResizeR
    'hand',       # Hue
    'hand',       # Saturation
    'hand',       # Lightness
    'hand',       # Alpha
    'sizing',     # Move
    'hand',       # Zoom
    'sizing'      # Pan
]

# Mapping from a zone to its tooltip:
ZoneTooltip = [
    'Drag to resize image',                         # ResizeTL
    'Drag to resize image',                         # ResizeTR
    'Drag to resize image',                         # ResizeBL
    'Drag to resize image',                         # ResizeBR
    'Drag to resize image',                         # ResizeT
    'Drag to resize image',                         # ResizeB
    'Drag to resize image',                         # ResizeL
    'Drag to resize image',                         # ResizeR
    'Drag horizontally to adjust hue',              # Hue
    'Drag horizontally to adjust saturation',       # Saturation
    'Drag horizontally to adjust lightness',        # Lightness
    'Drag horizontally to adjust alpha',            # Alpha
    'Drag to move image\nCtrl-drag to copy image',  # Move
    'Drag (or use mouse wheel) to zoom image',      # Zoom
    'Drag to pan image'                             # Pan
]

# Mapping from a zone to its corresponding overlay icon:
ZoneIcons = {
    Move:       [ image_for( '@xform:move' ),
                  image_for( '@xform:move?H51l32S~H14L32S24' ),
                  image_for( '@xform:delete?l32S' ) ],
    Zoom:       [ image_for( '@xform:zoom' ),
                  image_for( '@xform:zoom?H51l32S~H14L32S24' ),
                  image_for( '@xform:zoom?H28l32S~H14L32S24' ) ],
    Pan:        [ image_for( '@xform:pan2' ),
                  image_for( '@xform:pan2?H51l32S~H14L32S24' ),
                  image_for( '@xform:pan2?H28l32S~H14L32S24' ) ],
    Hue:        [ image_for( '@xform:hue' ),
                  image_for( '@xform:hue?H51l32S~H14L32S24' ),
                  image_for( '@xform:hue?H28l32S~H14L32S24' ) ],
    Saturation: [ image_for( '@xform:saturation' ),
                  image_for( '@xform:saturation?H51l32S~H14L32S24' ),
                  image_for( '@xform:saturation?H28l32S~H14L32S24' ) ],
    Lightness:  [ image_for( '@xform:lightness' ),
                  image_for( '@xform:lightness?H51l32S~H14L32S24' ),
                  image_for( '@xform:lightness?H28l32S~H14L32S24' ) ],
    Alpha:      [ image_for( '@xform:alpha' ),
                  image_for( '@xform:alpha?H51l32S~H14L32S24' ),
                  image_for( '@xform:alpha?H28l32S~H14L32S24' ) ]
}

# Mapping from a zone to its drag handler state and associated drag data:
ZoneDrag = [
    ( 'resizing',      TOP    + LEFT  + SCALE      ),  # ResizeTL
    ( 'resizing',      TOP    + RIGHT + SCALE      ),  # ResizeTR
    ( 'resizing',      BOTTOM + LEFT  + SCALE      ),  # ResizeBL
    ( 'resizing',      BOTTOM + RIGHT + SCALE      ),  # ResizeBR
    ( 'resizing',      TOP                         ),  # ResizeT
    ( 'resizing',      BOTTOM                      ),  # ResizeB
    ( 'resizing',      LEFT                        ),  # ResizeL
    ( 'resizing',      RIGHT                       ),  # ResizeR
    ( 'hue',           None                        ),  # Hue
    ( 'saturation',    None                        ),  # Saturation
    ( 'lightness',     None                        ),  # Lightness
    ( 'alpha',         None                        ),  # Alpha
    ( 'moving',        TOP + BOTTOM + LEFT + RIGHT ),  # Move
    ( 'zooming',       None                        ),  # Zoom
    ( 'panning',       None                        )   # Pan
]

#-------------------------------------------------------------------------------
#  'CollageItem' class:
#-------------------------------------------------------------------------------

class CollageItem ( HasPrivateFacets ):
    """ Represents an image displayed within a collage.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor value this item was created from:
    value = Any

    # The Collage instance owning this item:
    owner = WeakRef # ( Collage )

    # The bounds of the item within the collage:
    bounds = Tuple( Int, Int, Int, Int )

    # The base image:
    image = Image

    # The scaled version of the base image:
    scaled_image = Image

    # The cropped version of the scaled image:
    cropped_image = Property

    # The current scale factor for the image:
    scale = Float( 1.0 )

    # The offset of the scaled image from the item's origin:
    offset = Tuple( Float, Float )

    # The size available for drawing the image (excludes theme):
    image_size = Property

    # The current theme used to draw the item background:
    theme = Property

    # Is the item selected?
    selected = Bool( False )

    # The current overlay zone the mouse pointer is currently in (if any):
    zone = Int( NoZone )

    # The current opacity level for drawing the overlay controls:
    opacity = Float

    # Is the item currently being zoomed?
    zooming = Bool( False )

    # Is a long press action pending?
    long_press = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Draws the item within the graphics context specified by *g*.
        """
        image = self.image

        # Get the size and position of the item:
        ax, ay, adx, ady = x, y, dx, dy = self.bounds

        # Draw the themed background and title (if any):
        theme = self.theme
        if theme is not None:
            theme.fill( g, x, y, dx, dy )
            theme.draw_label( g, basename( image.name ), None, x, y, dx, dy )
            ax, ay, adx, ady = theme.bounds( x, y, dx, dy )

        # Draw the image:
        if self.zooming:
            idx, idy = image.width, image.height
            scale    = self.scale
            idx      = int( round( scale * idx ) )
            idy      = int( round( scale * idy ) )
        else:
            image    = self.scaled_image
            idx, idy = image.width, image.height

        ix, iy = self.offset
        ix, iy = int( round( ix ) ), int( round( iy ) )
        if ix < 0:
            sx   = -ix
            idx -= sx
        else:
            sx   = 0
            ax  += ix
            adx -= ix

        if iy < 0:
            sy   = -iy
            idy -= sy
        else:
            sy   = 0
            ay  += iy
            ady -= iy

        if self.zooming:
            sdx, sdy = min( adx, idx ), min( ady, idy )
            g.blit(
                ax, ay, sdx, sdy, image.bitmap,
                int( round( sx  / scale ) ), int( round( sy  / scale ) ),
                int( round( sdx / scale ) ), int( round( sdy / scale ) )
            )
        else:
            g.blit(
                ax, ay, min( adx, idx ), min( ady, idy ), image.bitmap,
                sx, sy
            )

        # Draw the overlays (if any):
        # Note that there is some kind of a Qt bug that does not handle low
        # values of opacity correctly, which is why we treat anything below a
        # certain limit as transparent:
        if self.opacity > 0.01:
            g.opacity = self.opacity
            zone      = self.zone
            for cur_zone in xrange( Zones ):
                x, y, dx, dy = self._zone_bounds_for( cur_zone )
                active_zone  = (cur_zone == zone)
                theme        = ZoneInactive
                if active_zone:
                    theme = ZoneActive
                    if self.long_press:
                        theme = (ZoneLongMovePress if zone == Move else
                                 ZoneLongPress)

                theme.fill( g, x, y, dx, dy )
                icons = ZoneIcons.get( cur_zone )
                if icons is not None:
                    ax, ay, adx, ady = theme.bounds( x, y, dx, dy )
                    icon   = icons[ active_zone * (1 + self.long_press) ]
                    idxy   = icon.width  # Assume icon is square
                    factor = 0.6 if min( adx, ady ) >= 100 else 0.9
                    dxy    = min( factor * adx, factor * ady, idxy )
                    scaled_icon = icon.scale( min( float( dxy ) / idxy, 2.0 ) )
                    sdxy        = scaled_icon.width
                    g.draw_bitmap(
                        scaled_icon.bitmap,
                        ax + ((adx - sdxy) / 2),
                        ay + ((ady - sdxy) / 2)
                    )

            g.opacity = 1.0


    def zone_at ( self, x, y ):
        """ Returns the zone (if any) located at the position specified by
            (*x*,*y*).
        """
        ix, iy, idx, idy = self.bounds
        if (ix <= x < (ix + idx)) and (iy <= y < (iy + idy)):
            for zone in xrange( Zones - 1, -1, -1 ):
                zx, zy, zdx, zdy = self._zone_bounds_for( zone )
                if (zx <= x < (zx + zdx)) and (zy <= y < (zy + zdy)):
                    return zone

        return NoZone


    def scale_to ( self, scale, x = None, y = None ):
        """ Scales the image to the scale factor specified by *scale* around the
            collage view coordinate specified by (*x*,*y*).
        """
        scale = clamp( scale, MinScale, MaxScale )
        if scale != self.scale:
            theme            = self.theme
            ax, ay, adx, ady = (self.bounds if theme is None else
                                theme.bounds( *self.bounds ))
            if x is None: x = ax + (adx / 2 )
            if y is None: y = ay + (ady / 2 )
            ox, oy   = self.offset
            opx, opy = x - ax - ox, y - ay - oy
            if self.zooming:
                ratio    = scale / self.scale
                npx, npy = ratio * opx, ratio * opy
            else:
                old_image = self.scaled_image
                new_image = self.scaled_image = self.image.scale( scale )
                odx, ody  = old_image.width, old_image.height
                ndx, ndy  = new_image.width, new_image.height
                npx       = (float( opx ) / odx) * ndx
                npy       = (float( opy ) / ody) * ndy

            self.scale  = scale
            self.offset = ( x - ax - npx, y - ay - npy )


    def reset_zone ( self ):
        """ Performs the 'reset' action for the currently active zone.
        """
        inn( self, '_reset_' + ZoneDrag[ self.zone ][0] )()

    #-- Property Implementations -----------------------------------------------

    def _get_theme ( self ):
        return (self.owner.factory.item_selected_theme if self.selected else
                self.owner.factory.item_theme)


    def _get_image_size ( self ):
        return (self.bounds[2:] if self.theme is None else
                self.theme.bounds( *self.bounds )[2:])


    def _get_cropped_image ( self ):
        _, _, adx, ady = x, y, dx, dy = self.bounds
        if self.theme is not None:
            _, _ay, adx, ady = self.theme.bounds( x, y, dx, dy )

        image    = self.scaled_image
        idx, idy = image.width, image.height
        ix, iy   = self.offset
        ix, iy   = int( round( ix ) ), int( round( iy ) )
        if ix < 0:
            sx   = -ix
            idx -= sx
        else:
            sx   = 0
            adx -= ix

        if iy < 0:
            sy   = -iy
            idy -= sy
        else:
            sy   = 0
            ady -= iy

        return image.crop( sx, sy, min( adx, idx ), min( ady, idy ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _zone_set ( self, zone ):
        """ Handles the 'zone' facet being changed.
        """
        self.owner.update_item( self )

        if zone != NoZone:
            self.owner.control.set(
                cursor  = ZoneCursor[  zone ],
                tooltip = ZoneTooltip[ zone ]
            )


    @on_facet_set( 'selected, opacity, long_press, offset, scaled_image, image:modified' )
    def _refresh_needed ( self ):
        """ Handles any facet being changed that requires the item to be
            refreshed.
        """
        if self.owner is not None:
            self.owner.update_item( self )


    def _bounds_set ( self ):
        """ Handles the 'bounds' facet being changed.
        """
        if self.owner is not None:
            self.owner.refresh()


    def _zooming_set ( self ):
        """ Handles the 'zooming' facet being changed.
        """
        if not self.zooming:
            self.scaled_image = self.image.scale( self.scale )

    #-- Private Methods --------------------------------------------------------

    def _zone_bounds_for ( self, zone ):
        """ Returns a list of bounds for the zone specified by *zone*.
        """
        x, y, dx, dy     = self.bounds
        zx, zy, zdx, zdy = ZoneBounds[ zone ]

        if isinstance( zx, int ):
            rx = (x + zx) if zx >= 0 else (x + dx + zx)
        else:
            rx = (x + ResizeSWidth +
                  int( zx * (dx - (2 * ResizeSWidth)) ))

        if isinstance( zy, int ):
            ry = (y + zy) if zy >= 0 else (y + dy + zy)
        else:
            ry = (y + ResizeSWidth +
                  int( zy * (dy - (2 * ResizeSWidth)) ))

        rdx = zdx
        if isinstance( zdx, float ):
            if zdx == 1.0:
                rdx = dx - (2 * ResizeCWidth)
            else:
                rdx = (x + ResizeSWidth +
                      int( (zx + zdx) * (dx - (2 * ResizeSWidth)) ) - rx)

        rdy = zdy
        if isinstance( zdy, float ):
            if zdy == 1.0:
                rdy = dy - (2 * ResizeCWidth)
            else:
                rdy = (y + ResizeSWidth +
                      int( (zy + zdy) * (dy - (2 * ResizeSWidth)) ) - ry)

        return ( rx, ry, rdx, rdy )


    def _reset_hue ( self ):
        """ Resets the current hue adjustement.
        """
        self.image.transform.hue = 0.0
        self._zooming_set()


    def _reset_saturation ( self ):
        """ Resets the current saturation adjustement.
        """
        self.image.transform.saturation = 0.0
        self._zooming_set()


    def _reset_lightness ( self ):
        """ Resets the current lightness adjustement.
        """
        self.image.transform.lightness = 0.0
        self._zooming_set()


    def _reset_alpha ( self ):
        """ Resets the current alpha adjustement.
        """
        self.image.transform.alpha = 0.0
        self._zooming_set()


    def _reset_moving ( self ):
        """ Deletes the item.
        """
        self.owner.delete_item( self )


    def _reset_zooming ( self ):
        """ Resets the current scale.
        """
        idx, idy   = self.image.width, self.image.height
        tidx, tidy = self.image_size
        scale      = min( float( tidx ) / idx, float( tidy ) / idy )
        if scale != self.scale:
            self.scale = scale
            self._reset_panning()
            self._zooming_set()


    def _reset_panning ( self ):
        """ Resets the current pan offset.
        """
        idx, idy    = self.scaled_image.width, self.scaled_image.height
        tidx, tidy  = self.image_size
        self.offset = ( max( 0.0, (tidx - idx) / 2.0 ),
                        max( 0.0, (tidy - idy) / 2.0 ) )

#-------------------------------------------------------------------------------
#  '_CollageEditor' class:
#-------------------------------------------------------------------------------

class _CollageEditor ( ControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The input list of images to be displayed by the editor:
    value = List # ( Image )

    # The current list of collage image items:
    items = List # ( CollageItem )

    # The current item the mouse is interacting with:
    item = Any # Instance( CollageItem )

    # The maximum snapping distance:
    max_snap = Range( 0, 20, 10 )

    # The start point for the current drag operation:
    drag_xy = Any # Tuple( Int, Int )

    # The starting bounds of the current drag item:
    drag_bounds = Any # Tuple( Int, Int, Int, Int )

    # The starting scale of the current drag item:
    drag_scale = Float

    # The starting offset of the current drag item:
    drag_offset = Any # Tuple( Float, Float )

    # The drag data associated with the current drag operation:
    drag_data = Any

    # Is the current drag operation pending a motion delta?
    drag_pending = Bool

    # Has the item being dragged been cloned yet?
    drag_cloned = Bool

    # The list of collage image items locked to the current item during a drag
    # operation, along with the original bounds and the set of locked edges:
    drag_locked = Any # None or List( (item, bounds, offset, scale, side_mask) )

    # The list of collage image items that are not locked to the current item
    # during a drag operation:
    drag_unlocked = Any # None or List( item )

    # Used to convert an input string value to an image:
    image = Image

    # Indicate that the editor should support scrolling:
    virtual_size = ( 10, 10 )

    # The mapping from image objects to editor values:
    image_map = Any( {} )

    #-- ControlEditor Method Overrides -----------------------------------------

    def paint_content ( self, g ):
        """ Paints the list of collage image items.
        """
        items = self.items
        for i in xrange( len( items ) - 1, -1, -1 ):
            items[ i ].paint( g )


    def resize ( self, event ):
        """ Handles the control being resized.
        """
        self._check_virtual_size()

        super( _CollageEditor, self ).resize( event )

    #-- Public Methods ---------------------------------------------------------

    def update_item ( self, item ):
        """ Schedules a refresh of the specified collage image item.
        """
        self.refresh( *item.bounds )


    def delete_item ( self, item ):
        """ Deletes the collage image item specified by *item* from the collage.
        """
        items = self.items
        if item in items:
            items.remove( item )
            image = item.image.base_image
            for an_item in items:
                if image is an_item.image.base_image:
                    break
            else:
                # The item was the only reference to the image, so we need to
                # delete it from the editor's value:
                values = self.value
                for value in self.image_map.pop( image ):
                    values.remove( value )

            # If the deleted item was also the currently selected item, then
            # clear the selection:
            if item is self.editor.selected_item:
                self._select_item( None )


    def check_size ( self ):
        """ Refreshes the view and checks its virtual size.
        """
        self._check_virtual_size()
        self.refresh()


    def select_value ( self, value ):
        """ Selects the collage image item with the specified editor *value*.
        """
        for item in self.items:
            if value == item.value:
                self._select_item( item )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'value[]' )
    def _value_modified ( self ):
        """ Handles the list of input images being changed.
        """
        do_later( self._update_images )


    @on_facet_set( 'factory:[item_theme, item_selected_theme]' )
    def _theme_modified ( self ):
        """ Handles one of the factory item themes being changed.
        """
        self.refresh()

    #-- Mouse Event Handlers ---------------------------------------------------

    def left_up ( self, x, y, event ):
        """ Handles the user releasing the left mouse button in any state.
        """
        # Reset the 'zooming' state of any locked items that were being dragged:
        if self.drag_locked is not None:
            for item in self.drag_locked:
                item[0].zooming = False

        # Release any locked/unlocked items used during a drag operation:
        del self.drag_locked
        del self.drag_unlocked

        self.state = 'normal'
        item       = self.item
        if item is None:
            self._select_item( None )
        else:
            self._check_virtual_size()
            item.zooming = False
            item.zone    = item.zone_at( x, y )
            if item.zone != NoZone:
                if self.drag_pending:
                    self.drag_pending = False
                    if item.long_press:
                        item.reset_zone()
                    elif event.control_down:
                        self._deactivate_item( item )
                    else:
                        if self._occluded_item( item ):
                            self._activate_item( item )

                        self._select_item( item )

                item.long_press = False
                item.animate_facet( 'opacity', 0.25, 0.8, replace = True )

                return

            self.item = None

        self.normal_motion( x, y )


    def normal_motion ( self, x, y ):
        """ Handles a mouse motion event in normal mode.
        """
        zone = NoZone
        for item in self.items:
            zone = item.zone_at( x, y )
            if zone != NoZone:
                break

        self_item = self.item
        if zone != NoZone:
            if item is not self_item:
                if self_item is not None:
                    self._cancel_item( self_item )

                item.animate_facet(
                    'opacity', 0.5, 0.9, tweener = ZoneTweener, replace = True
                )

            self.item = item
            item.zone = zone
        elif self_item is not None:
            self._cancel_item( self_item )
            self.control.tooltip = ''


    def normal_left_down ( self, x, y, event ):
        """ Handles the use pressing the left mouse button in normal mode.
        """
        self.normal_motion( x, y )
        item = self.item
        if (item is not None) and (item.zone != NoZone):
            self.state, self.drag_data = ZoneDrag[ item.zone ]
            self.drag_xy      = ( x, y )
            self.drag_bounds  = item.bounds
            self.drag_offset  = item.offset
            self.drag_scale   = item.scale
            self.drag_pending = True
            self.drag_cloned  = False
            if item.zone in LockableZones:
                if event.shift_down:
                    self.drag_locked = self._locked_items()
                else:
                    self.drag_locked = [ ( item, item.bounds, item.offset,
                                           item.scale, self.drag_data ) ]

                locked = set( [ item[0] for item in self.drag_locked ] )
                self.drag_unlocked = [ item for item in self.items
                                            if item not in locked ]

            do_after( 500, self._long_press )


    def normal_leave ( self ):
        """ Handles the mouse leaving the control in normal mode.
        """
        item = self.item
        if item is not None:
            item.zone = NoZone
            do_after( 200, self._cancel_item, item, True )


    def moving_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in moving mode.
        """
        if not self._drag_pending( x, y ):
            self._drag_clone( event )
            ox, oy = self.drag_xy
            if event.alt_down:
                self._move_by( x - ox, y - oy )

                return

            dx, dy             = x - ox, y - oy
            bxl, byt, bdx, bdy = self.drag_bounds
            bxl               += dx
            byt               += dy
            bxr                = bxl + bdx
            byb                = byt + bdy
            nxl, nyt, nxr, nyb = bxl, byt, bxr, byb
            max_snap           = self.max_snap
            sdx = sdy          = max_snap + 1
            item               = self.item
            for cur_item in self.drag_unlocked:
                cxl, cyt, cxr, cyb = self._edges_for( cur_item )
                if ((cxr >= (bxl - max_snap)) and
                    (cxl <  (bxr + max_snap))):
                    nyt1, sdy1 = self._check_snaps( nyt, byt, cyt, cyb, sdy )
                    nyb1, sdy2 = self._check_snaps( nyb, byb, cyt, cyb, sdy )
                    if sdy2 < sdy1:
                        nyt += nyb1 - nyb
                        nyb  = nyb1
                        sdy  = sdy2
                    else:
                        nyb += nyt1 - nyt
                        nyt  = nyt1
                        sdy  = sdy1

                if ((cyb >= (byt - max_snap)) and
                    (cyt <  (byb + max_snap))):
                    nxl1, sdx1 = self._check_snaps( nxl, bxl, cxl, cxr, sdx )
                    nxr1, sdx2 = self._check_snaps( nxr, bxr, cxl, cxr, sdx )
                    if sdx2 < sdx1:
                        nxl += nxr1 - nxr
                        nxr  = nxr1
                        sdx  = sdx2
                    else:
                        nxr += nxl1 - nxl
                        nxl  = nxl1
                        sdx  = sdx1

            bxl, byt = self.drag_bounds[:2]
            self._move_by( nxl - bxl, nyt - byt )


    def resizing_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in snap resizing mode.
        """
        if not self._drag_pending( x, y ):
            if event.alt_down:
                ox, oy = self.drag_xy
                self._resize_by( *self._resize_amount( x - ox, y - oy ) )

                return

            bxl, byt, bdx, bdy = self._resize_bounds( x, y )
            bxr, byb           = bxl + bdx, byt + bdy
            nxl, nyt, nxr, nyb = bxl, byt, bxr, byb
            max_snap           = self.max_snap
            sdx = sdy          = max_snap + 1
            sides              = self.drag_data
            item               = self.item
            if (sides & SCALE) == 0:
                oxl, oyt, odx, ody = self.drag_bounds
                oxr, oyb           = oxl + odx, oyt + ody
                ox, oy             = self.drag_offset
                ox                 = int( ox ) + (oxl - nxl)
                oy                 = int( oy ) + (oyt - nyt)
                odx, ody           = self._image_area( item, bdx, bdy )
                image              = item.scaled_image
                idx, idy           = image.width, image.height
                if sides & TOP:
                    noy, sdy = self._check_snap( oy, 0, sdy )
                    nyt     += (oy - noy)
                elif sides & BOTTOM:
                    ndy, sdy = self._check_snap( ody, idy + oy, sdy )
                    nyb     += (ndy - ody)
                elif sides & LEFT:
                    nox, sdx = self._check_snap( ox, 0, sdx )
                    nxl     += (ox - nox)
                elif sides & RIGHT:
                    ndx, sdx = self._check_snap( odx, idx + ox, sdx )
                    nxr     += (ndx - odx)

            for cur_item in self.drag_unlocked:
                cxl, cyt, cxr, cyb = self._edges_for( cur_item )
                if ((sides & (TOP | BOTTOM))  and
                    (cxr >= (bxl - max_snap)) and
                    (cxl <  (bxr + max_snap))):
                    if sides & TOP:
                        nyt, sdy = self._check_snaps( nyt, byt, cyt, cyb, sdy )
                    else:
                        nyb, sdy = self._check_snaps( nyb, byb, cyt, cyb, sdy )

                if ((sides & (LEFT | RIGHT))  and
                    (cyb >= (byt - max_snap)) and
                    (cyt <  (byb + max_snap))):
                    if sides & LEFT:
                        nxl, sdx = self._check_snaps( nxl, bxl, cxl, cxr, sdx )
                    else:
                        nxr, sdx = self._check_snaps( nxr, bxr, cxl, cxr, sdx )

            bxl, byt, bdx, bdy = self.drag_bounds
            bxr, byb           = bxl + bdx, byt + bdy
            dx                 = nxl - bxl if sides & LEFT else nxr - bxr
            dy                 = nyt - byt if sides & TOP  else nyb - byb
            self._resize_by( *self._resize_amount( dx, dy ) )


    def panning_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in panning mode.
        """
        if not self._drag_pending( x, y ):
            ox, oy   = self.drag_xy
            dox, doy = self.drag_offset
            item     = self.item
            image    = item.scaled_image
            idx, idy = image.width, image.height
            adx, ady = item.image_size

            # Scale up the pan amount if the shift key is pressed:
            cdx, cdy = x - ox, y - oy
            if event.shift_down:
                cdx *= 4
                cdy *= 4

            nox, noy = dox + cdx, doy + cdy
            if not event.alt_down:
                noxr, noyb = nox + idx, noy + idy
                noxc, noyc = nox + (idx / 2), noy + (idy / 2)
                sdxy       = self.max_snap + 1
                nox,  sdx1 = self._check_snap( nox,  0,       sdxy )
                noxr, sdx2 = self._check_snap( noxr, adx,     sdxy )
                noxc, sdx3 = self._check_snap( noxc, adx / 2, sdxy )
                noy,  sdy1 = self._check_snap( noy,  0,       sdxy )
                noyb, sdy2 = self._check_snap( noyb, ady,     sdxy )
                noyc, sdy3 = self._check_snap( noyc, ady / 2, sdxy )
                if sdx2 < sdx1:
                    nox  = noxr - idx
                    sdx1 = sdx2

                if sdx3 < sdx1:
                    nox = noxc - (idx / 2)

                if sdy2 < sdy1:
                    noy  = noyb - idy
                    sdy1 = sdy2

                if sdy3 < sdy1:
                    noy = noyc - (idy / 2)

            item.offset = (
                clamp( nox, min( 0, 5 - idx ), max( 0, adx - 5 ) ),
                clamp( noy, min( 0, 5 - idy ), max( 0, ady - 5 ) )
            )


    def zooming_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in zooming mode.
        """
        if not self._drag_pending( x, y ):
            ox, oy = self.drag_xy
            factor = 500.0 if event.control_down else 100.0
            dy     = (oy - y) / factor
            scale  = ((self.drag_scale * (1.0 + dy)) if dy >= 0.0 else
                      (self.drag_scale * (1.0 / (1.0 - dy))))
            self.item.zooming = True
            self.item.scale_to( scale )


    def hue_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in hue adjustment mode.
        """
        if not self._drag_pending( x, y ):
            xform     = self.item.image.transform
            hue       = fmod( xform.hue + ((x - self.drag_xy[0]) / 300.0), 1.0 )
            xform.hue = hue if hue >= 0.0 else hue + 1.0
            self.drag_xy      = ( x, y )
            self.item.zooming = True


    def saturation_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in saturation adjustment mode.
        """
        if not self._drag_pending( x, y ):
            xform = self.item.image.transform
            xform.saturation = clamp(
                xform.saturation + ((x - self.drag_xy[0]) / 300.0), -1.0, 1.0
            )
            self.drag_xy      = ( x, y )
            self.item.zooming = True


    def lightness_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in lightness adjustment mode.
        """
        if not self._drag_pending( x, y ):
            xform = self.item.image.transform
            xform.lightness = clamp(
                xform.lightness + ((x - self.drag_xy[0]) / 300.0), -1.0, 1.0
            )
            self.drag_xy      = ( x, y )
            self.item.zooming = True


    def alpha_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in alpha adjustment mode.
        """
        if not self._drag_pending( x, y ):
            xform = self.item.image.transform
            xform.alpha = clamp(
                xform.alpha + ((x - self.drag_xy[0]) / 300.0), -1.0, 1.0
            )
            self.drag_xy      = ( x, y )
            self.item.zooming = True

    #-- Private Methods --------------------------------------------------------

    def _cancel_item ( self, item, check_zone = False ):
        """ Cancels any current overlay related state for the item specified by
            *item*.
        """
        if (not check_zone) or (item.zone == NoZone):
            item.zone = NoZone
            item.animate_facet( 'opacity', 0.5, 0.0, replace = True )
            self.item           = None
            self.control.cursor = 'arrow'


    def _resize_amount ( self, dx, dy ):
        """ Returns the resize amount (dx,dy) based on the proposed amount
            (*dx*,*dy*) and the amount each locked collage image item currently
            being dragged can legally resize by.
        """
        for item, bounds, _, _, sides in self.drag_locked:
            bx, by, bdx, bdy = bounds
            if sides & TOP:
                dy = max( min( dy, bdy - MinItemSize ), -by )
            elif sides & BOTTOM:
                dy = max( dy, MinItemSize - bdy )

            if sides & LEFT:
                dx = max( min( dx, bdx - MinItemSize ), -bx )
            elif sides & RIGHT:
                dx = max( dx, MinItemSize - bdx )

        return ( dx, dy )


    def _resize_by ( self, dx, dy ):
        """ Resizes all currently dragged collage image items by the amount
            specified by (*dx*,*dy*).
        """
        for item, bounds, offset, scale, sides in self.drag_locked:
            bx, by, bdx, bdy = bounds
            odx, ody         = bdx, bdy
            ox, oy           = offset
            if sides & TOP:
                by  += dy
                bdy -= dy
                oy  -= dy
            elif sides & BOTTOM:
                bdy += dy

            if sides & LEFT:
                bx  += dx
                bdx -= dx
                ox  -= dx
            elif sides & RIGHT:
                bdx += dx

            item.zooming = True
            item.bounds  = ( bx, by, bdx, bdy )
            if sides & SCALE:
                item.offset = offset
                ndx, ndy    = item.image_size
                if item.theme is not None:
                    odx, ody = item.theme.bounds( odx, ody )

                new_scale = min( float( ndx ) / odx, float( ndy ) / ody )
                item.scale_to( scale * new_scale )
            else:
                item.offset = ( ox, oy )


    def _resize_bounds ( self, x, y ):
        """ Resizes the bounds of the currently dragged collage image item based
            on the location specified by (*x*,*y*).
        """
        ox, oy           = self.drag_xy
        dx, dy           = x - ox, y - oy
        bx, by, bdx, bdy = self.drag_bounds
        sides            = self.drag_data
        if sides & TOP:
            dy   = max( min( dy, bdy - MinItemSize ), -by )
            by  += dy
            bdy -= dy
        elif sides & BOTTOM:
            bdy = max( bdy + dy, MinItemSize )

        if sides & LEFT:
            dx   = max( min( dx, bdx - MinItemSize ), -bx )
            bx  += dx
            bdx -= dx
        elif sides & RIGHT:
            bdx = max( bdx + dx, MinItemSize )

        return ( bx, by, bdx, bdy )


    def _image_area ( self, item, dx, dy ):
        """ Returns the area available for displaying an image for an item
            with size specified by *dx* and *dy*.
        """
        return (( dx, dy ) if item.theme is None else
                item.theme.bounds( dx, dy ))


    def _drag_clone ( self, event ):
        """ Creates a clone of the current collage image item being dragged if
            the user has pressed the control key.
        """
        if (not self.drag_cloned) and event.control_down:
            self.drag_cloned = True
            item     = self.item
            new_item = item.clone_facets( [
                'value', 'owner', 'scaled_image', 'scale', 'offset'
            ] ).set(
                image  = hlsa_derived_image( item.image ),
                bounds = self.drag_bounds
            )
            item.zooming = True
            self.items.insert( 1, new_item )
            self.drag_unlocked.insert( 0, new_item )


    def _check_snap ( self, v, t, dv ):
        """ For a current value of *v* and a snapping target of *t* with a
            current snapping distance *dv*, return the new best value and
            snapping distance: (vp, dvp).
        """
        dvp = abs( v - t )

        return ( t, dvp ) if dvp < dv else ( v, dv )


    def _check_snaps ( self, bv, v, v1, v2, dv ):
        """ For a current best value of *bv* and a proposed value *v* and two
            snapping targets *v1* and *v2*, with a current best snapping
            distance *dv*, return the new best value and snapping distance:
            (bvp, dvp).
        """
        nv = bv
        if abs( v - v1 ) < dv:
            nv, dv = v1, abs( v - v1 )

        if abs( v - v2 ) < dv:
            nv, dv = v2, abs( v - v2 )

        return ( nv, dv )


    def _locked_items ( self ):
        """ Returns the list of collage image items locked to the current drag
            item based on the operation being performed. The items in the list
            are of the form: ( item, side_mask ), where item is a locked item
            and side_mask is a bit mask defining the sides the item is locked
            to the dragged item on.
        """
        item   = self.item
        mask   = AllSides if item.zone == Move else 0
        result = [ ( item, item.bounds, item.offset, item.scale,
                     self.drag_data ) ]
        items  = self.items[:]
        items.remove( item )

        i = 0
        while i < len( result ):
            item, _, _, _, sides = result[ i ]
            bxl, byt, bxr, byb   = self._edges_for( item )
            i += 1
            for cur_item in items[:]:
                cxl, cyt, cxr, cyb = self._edges_for( cur_item )
                matches            = 0
                if ((sides & (TOP | BOTTOM)) and
                    (max( bxl, cxl ) <= min( bxr, cxr ))):
                    if sides & TOP:
                        if byt == cyt:
                            matches |= TOP
                        elif byt == cyb:
                            matches |= BOTTOM

                    if sides & BOTTOM:
                        if byb == cyt:
                            matches |= TOP
                        elif byb == cyb:
                            matches |= BOTTOM

                if ((sides & (LEFT | RIGHT)) and
                    (max( byt, cyt ) <= min( byb, cyb ))):
                    if sides & LEFT:
                        if bxl == cxl:
                            matches |= LEFT
                        elif bxl == cxr:
                            matches |= RIGHT

                    if sides & RIGHT:
                        if bxr == cxl:
                            matches |= LEFT
                        elif bxr == cxr:
                            matches |= RIGHT

                if matches != 0:
                    result.append(
                        ( cur_item, cur_item.bounds, cur_item.offset,
                          cur_item.scale, matches | mask )
                    )
                    items.remove( cur_item )

        return result


    def _edges_for ( self, item ):
        """ Returns the edge coordinates for the collage image item specified by
            *item* as a tuple of the form: ( left, top, right, bottom ).
        """
        xl, yt, dx, dy = item.bounds

        return ( xl, yt, xl + dx, yt + dy )


    def _move_by ( self, dx, dy ):
        """ Moves all 'locked' collage image items by the amount specified by
            (*dx*,*dy*).
        """
        for _, bounds, _, _, _ in self.drag_locked:
            x, y = bounds[:2]
            if x + dx < 0:
                dx = -x

            if y + dy < 0:
                dy = -y

        for item, bounds, _, _, _ in self.drag_locked:
            bx, by, bdx, bdy = bounds
            item.bounds      = ( bx + dx, by + dy, bdx, bdy )


    def _drag_pending ( self, x, y ):
        """ Returns whether the current drag operation has begun or is still
            pending a small mouse motion.
        """
        if self.drag_pending:
            ox, oy            = self.drag_xy
            self.drag_pending = ((abs( x - ox ) + abs( y - oy )) <= 3)
            if not self.drag_pending:
                item            = self.item
                item.long_press = False
                self._activate_item( item )
                item.animate_facet( 'opacity', 0.2, 0.0, replace = True )

        return self.drag_pending


    def _activate_item ( self, item ):
        """ Activates the collage image item specified by *item*.
        """
        items = self.items
        i     = items.index( item )
        if i > 0:
            del items[ i ]
            items.insert( 0, item )
            self.refresh()


    def _deactivate_item ( self, item ):
        """ Deactivates the collage image item specified by *item* by moving it
            to the bottom of the display list.
        """
        items = self.items
        i     = items.index( item )
        if i < (len( items ) - 1):
            del items[ i ]
            items.append( item )
            self.refresh()


    def _select_item ( self, item ):
        """ Selects the collage image item specified by *item*.
        """
        self.editor.select_item( item )


    def _occluded_item ( self, item ):
        """ Returns whether the collage image item specified by *item* is
            occluded by any other items.
        """
        ix, iy, idx, idy = item.bounds
        items            = self.items
        for i in xrange( items.index( item ) ):
            bx, by, bdx, bdy = items[ i ].bounds
            if (((ix + idx) >= bx) and
                (ix < (bx + bdx))  and
                ((iy + idy) >= by) and
                (iy < (by + bdy))):
                return True

        return False


    def _update_images ( self ):
        """ Updates the list of collage image items.
        """
        items      = self.items[:]
        new_items  = []
        kept_items = set()
        image_map = self.image_map = {}
        for value in self.value:
            # Make sure the input value is an image:
            image = value
            if isinstance( value, basestring ):
                self.image = value
                image      = self.image

            # Only process each unique image once, but collect all values that
            # generate the same image:
            values = image_map.setdefault( image, [] )
            values.append( value )
            if len( values ) > 1:
                continue

            # If the image is already represented in the editor, re-use all
            # existing collage image items matching the image:
            remove = []
            for item in items:
                if image is item.image.base_image:
                    remove.append( item )
                    kept_items.add( item )

            if len( remove ) == 0:
                # If it is a new image, create a collage image item for it:
                new_items.append( self._item_for( value, image ) )
            else:
                # Otherwise, discard all matched image items from the list:
                for item in remove:
                    items.remove( item )

        # Position all new items so that they do not overlap any existing items:
        cdx, cdy         = self.control.size
        ax, ay, adx, ady = self.theme.bounds( 0, 0, cdx, cdy )
        rx               = ax + adx
        cx, cy           = ax, ay
        max_dy           = 0

        for item in kept_items:
            ix, iy, idx, idy = item.bounds
            cy = max( cy, iy + idy)

        for item in new_items:
            ix, iy, idx, idy = item.bounds
            if ((cx + idx) > rx) and (cx > ax):
                cx     = ax
                cy    += max_dy
                max_dy = 0

            item.bounds = ( cx, cy, idx, idy )
            max_dy      = max( max_dy, idy )
            cx         += idx

        # Save the new list of collage image items:
        self.items = (
            [ item for item in self.items if item in kept_items ] + new_items
        )

        # Update the virtual size of the collage canvas:
        self.check_size()


    def _item_for ( self, value, image ):
        """ Returns a new collage image item for the image specified by *image*.
        """
        ax, ay   = self.theme.bounds( 0, 0, 200, 200 )[:2]
        factory  = self.factory
        idx, idy = image.width, image.height
        theme    = factory.item_theme
        tdx, tdy = ( 0, 0 ) if theme is None else theme.bounds()
        scale    = 1.0
        while True:
            dx       = clamp( idx + tdx, MinItemSize, factory.item_width  )
            dy       = clamp( idy + tdy, MinItemSize, factory.item_height )
            adx, ady = ( dx, dy ) if theme is None else theme.bounds( dx, dy )
            if (idx <= adx) and (idy <= ady):
                break

            scale = max(
                min( float( adx ) / idx, float( ady ) / idy ), MinScale
            )
            idx, idy = int( scale * idx ), int( scale * idy )

        return CollageItem(
            value        = value,
            owner        = self,
            image        = hlsa_derived_image( image ),
            scaled_image = image.scale( scale ),
            bounds       = ( ax, ay, dx, dy ),
            scale        = scale,
            offset       = ( (adx - idx) / 2, (ady - idy) / 2 )
        )


    def _check_virtual_size ( self ):
        """ Updates the virtual size of the collage canvas based on the bounds
            of all current collage image items.
        """
        ax, ay, adx, ady = self.theme.bounds( 0, 0, 0, 0 )
        max_x = max_y    = -1

        for item in self.items:
            x, y, dx, dy = item.bounds
            max_x, max_y = max( max_x, x + dx ), max( max_y, y + dy )

        self.virtual_size = ( max_x + adx - ax, max_y + ady - ay )


    def _long_press ( self ):
        """ Handles the long press time interval expiring.
        """
        inn( self.item ).set( long_press = self.drag_pending )

#-------------------------------------------------------------------------------
#  'CollageCustomControlEditor' class:
#-------------------------------------------------------------------------------

class CollageCustomControlEditor ( DefaultCustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The currently selected editor value:
    selected = Any

    # The currently selected collage image item:
    selected_item = Instance( CollageItem )

    #-- DefaultCustomControlEditor Method Overrides ----------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( CollageCustomControlEditor, self ).init( parent )

        self.sync_value( self.factory.selected,      'selected',      'both' )
        self.sync_value( self.factory.selected_item, 'selected_item', 'to' )

    #-- Public Methods ---------------------------------------------------------

    def select_item ( self, item ):
        """ Handles the collage image item specified by *item* being selected.
        """
        self._no_update = True
        cur_item        = self.selected_item
        if item is not cur_item:
            if cur_item is not None:
                cur_item.selected = False

            if item is not None:
                item.selected       = True
                self.selected       = item.value
                self.selected_item  = item
            else:
                self.selected = self.selected_item = None

        self._no_update = False

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, value ):
        """ Handles the 'selected' facet being changed.
        """
        if not self._no_update:
            self.editor_control.select_value( value )

#-------------------------------------------------------------------------------
#  'CollageEditor' class:
#-------------------------------------------------------------------------------

class CollageEditor ( CustomControlEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # The class of the editor created:
    editor_klass = CollageCustomControlEditor

    # The class of the editor control created:
    klass = _CollageEditor

    # The optional extended name of the facet that the currently selected value
    # is synced with:
    selected = Str

    # The optional extended name of the facet that the currently selected
    # CollageItem is synced with:
    selected_item = Str

    # The theme to use for the editor:
    theme = Theme( '@xform:b?l25', content = -1 )

    # The collage image item theme:
    item_theme = ATheme( Theme( '@xform:b?L20', content = -1 ),
                         facet_value = True )

    # The collage image item theme used when an item is selected:
    item_selected_theme = ATheme( Theme( '@xform:b?H63L20S20', content = -1 ),
                                  facet_value = True )

    # The maximum initial width of a collage image item:
    item_width = Range( 100, 1024, 256, facet_value = True )

    # The maximum initial height of a collage image item:
    item_height = Range( 100, 1024, 256, facet_value = True )

#-- EOF ------------------------------------------------------------------------
