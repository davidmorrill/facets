"""
Defines the ImageZoomEditor, which displays an edited ImageResource object at
various zoom levels. It also provides the ability to display marked regions and
itemized pixel level details within a selected region of the edited image.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import log

from colorsys \
    import rgb_to_hls

from os.path \
    import splitext

from facets.api \
    import Any, Color, Str, Float, Instance, Tuple, List, Enum, Bool, Image, \
           Editor, on_facet_set, on_facet_set, toolkit, BasicEditorFactory, inn

from facets.animation.api \
    import Path, EaseOut, NoEasing

from facets.ui.pyface.i_image_resource \
    import AnImageResource

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The maximm amount to zoom when double-clicking on the image:
DClickZoom1 = 32.0
DClickZoom2 = 80.0

# The list of acceptable image types (for drag and drop):
ImageTypes = ( '.png', '.jpg', '.jpeg' )

#-------------------------------------------------------------------------------
#  'QuadraticPath' class:
#-------------------------------------------------------------------------------

class QuadraticPath ( Path ):
    """ Provides an animated path that follows a quadratic curve between the
        start and end points.
    """

    def at ( self, v0, v1, t ):
        """ Returns the value along the path at time t for a path whose start
            value is v0, and whose end value is v1.
        """
        return (v0 + ((v1 - v0) * (t * t)))

QPath = QuadraticPath()

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def clip_low ( ts, t, dt, scale ):
    """ Clips a scaled set of values on the low side, and returns the adjusted
        results.
    """
    nts   = ts - scale - ((ts / scale) * scale)
    delta = (nts - ts) / scale

    return ( nts, t + delta, dt - delta )


def hls ( bgra, as_float ):
    """ Convert a pixel's RGB data to HLS.
    """
    r          = int( bgra[2] )
    g          = int( bgra[1] )
    b          = int( bgra[0] )
    a          = int( bgra[3] )
    fr         = float( r ) / 255.0
    fg         = float( g ) / 255.0
    fb         = float( b ) / 255.0
    fa         = float( a ) / 255.0
    fh, fl, fs = rgb_to_hls( fr, fg, fb )
    il         = int( 255.0 * fl )

    if as_float:
        return [ fr, fg, fb, fa, fh, fl, fs, fa, a, il ]

    return [ r, g, b, a,
             int( 255.0 * fh ), il, int( 255.0 * fs ), a, a, il ]


def format_int ( value ):
    """ Returns a channel value formatted as an integer.
    """
    return ('%d' % value)


# Map for converting special float values to string:
float_map = {
     0.0: '0',
     1.0: '1',
    -1.0: '-1'
}

def format_float ( value ):
    """ Returns a channel value formatted as a float.
    """
    result = float_map.get( value )
    if result is not None:
        return result

    return (('-'[ value >= 0.0: ]) + ('%.3f' % abs( value ))[1:])

#-------------------------------------------------------------------------------
#  '_ImageZoomEditor' class:
#-------------------------------------------------------------------------------

class _ImageZoomEditor ( Editor ):
    """ Facets UI simple, slider-based integer or float value editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Make sure that the editor is stretchable:
    scrollable = True

    # The current image scaling (i.e. zoom) factor:
    scale   = Float( 1.0 )
    scaling = Float

    # The current image origin offset:
    offset = Tuple( 0.0, 0.0 )

    # The currently selected image region's bounds:
    selected = Tuple( -1, -1, 0, 0 )

    # The selection region while a drag selection is being performed:
    drag_selected = Any

    # The 'transparent' image background to display to help define transparent
    # areas of the image being edited:
    transparent = Image( '@std:transparent' )

    # Local reference to the image being edited:
    image = Instance( AnImageResource )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create the control:
        self.adapter = control = toolkit().create_control( parent )
        control.min_size = ( 150, 150 )

        # Set up the event handlers:
        control.set_event_handler(
            paint       = self._paint,
            left_down   = self._left_down,
            left_dclick = self._left_dclick,
            left_up     = self._left_up,
            middle_down = self._middle_down,
            middle_up   = self._middle_up,
            right_down  = self._right_down,
            right_up    = self._right_up,
            motion      = self._motion,
            wheel       = self._mouse_wheel,
            size        = self._size
        )
        if self.factory.allow_drop:
            control.drop_target = self

        self.sync_value( self.factory.selected, 'selected', 'both' )

        # Set the tooltip:
        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        control = self.adapter
        control.unset_event_handler(
            paint       = self._paint,
            left_down   = self._left_down,
            left_dclick = self._left_dclick,
            left_up     = self._left_up,
            middle_down = self._middle_down,
            middle_up   = self._middle_up,
            right_down  = self._right_down,
            right_up    = self._right_up,
            motion      = self._motion,
            wheel       = self._mouse_wheel,
            size        = self._size
        )
        control.drop_target = None

        super( _ImageZoomEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        # Save a local reference to the image being edited:
        self.image = self.value

        # Discard any cached image data:
        self._scale = self._scaled_image = None

        # Reset the initial editor values:
        if self.factory.auto_reset:
            self._reset_view()

        self.selected = ( -1, -1, 0, 0 )

        self.adapter.refresh()

    #--- Control Event Handlers ------------------------------------------------

    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        # Make sure view is initialized correctly the first time it is drawn:
        if self._initialized is None:
            self._initialized = True
            self._reset_view()

        factory  = self.factory
        control  = self.adapter
        wdx, wdy = control.client_size
        g        = control.graphics.graphics_buffer()

        if (wdx * wdy) > 0:
            # Draw the control background:
            g.pen   = None
            g.brush = factory.bg_color
            g.draw_rectangle( 0, 0, wdx, wdy )

            # Get the image to display (if any):
            image = self.image
            if image is None:
                return

            # Set up the appropriate image zooming factors:
            ox, oy    = self.offset
            scale     = self.scale
            if scale >= 2.0:
                scale = int( round( scale ) )

            idx  = bdx = image.width
            idy  = bdy = image.height
            sbdx = int( bdx * scale )
            sbdy = int( bdy * scale )
            ox   = int( ox * scale )
            oy   = int( oy * scale )
            if (scale < 2.0) and (scale != 1.0):
                if scale == self._scale:
                    image = self._scaled_image
                else:
                    self._scaled_image = image = image.scale( scale )
                    self._scale        = scale

                sbdx = bdx = image.width
                sbdy = bdy = image.height

            # Draw the 'transparent' background image (if necessary):
            if scale >= 2.0:
                transparent = self.transparent
                tbitmap     = transparent.bitmap
                tdx, tdy    = transparent.width, transparent.height
                tbdx, tbdy  = sbdx, sbdy
                ttx, ty     = ox, oy
                if ttx < 0:
                    ttx   = (ttx % tdx) - tdx
                    tbdx -= (ttx - ox)

                if ty < 0:
                    ty    = (ty % tdy) - tdy
                    tbdy -= (ty - oy)

                if (ox + sbdx) > wdx:
                    tbdx = wdx - ttx

                if (oy + sbdy) > wdy:
                    tbdy = wdy - ty

                while tbdy > 0:
                    itdy = min( tdy, tbdy )
                    tx   = ttx
                    ebdx = tbdx
                    while ebdx > 0:
                        itdx = min( tdx, ebdx )
                        g.blit( tx, ty, itdx, itdy, tbitmap )
                        tx   += itdx
                        ebdx -= itdx

                    ty   += itdy
                    tbdy -= itdy

            # Draw the properly zoomed version of the image:
            if scale <= 16.0:
                g.blit( ox, oy, sbdx, sbdy, image.bitmap, 0, 0, bdx, bdy )
            else:
                # For scale values > 16 which are not powers of 2, the Qt image
                # zooming code gets misaligned. So we use this special case code
                # to deal with that by drawing the individual pixels ourselves:
                bx, by, px, py, vdx, vdy = ox, oy, 0, 0, bdx, bdy
                if ox < 0:
                    bx   = (ox % scale) - scale
                    px   = (bx - ox) / scale
                    vdx -= px

                if oy < 0:
                    by   = (oy % scale) - scale
                    py   = (by - oy) / scale
                    vdy -= py

                edx, edy = wdx + scale, wdy + scale
                if (bx + (vdx * scale)) > edx:
                    vdx = (edx - bx) / scale

                if (by + (vdy * scale)) > edy:
                    vdy = (edy - by) / scale

                pixels = image.pixels
                last   = None
                for py in xrange( py, py + vdy ):
                    tbx = bx
                    for tpx in xrange( px, px + vdx ):
                        pixel = pixels[ py, tpx ]
                        if (last is None) or (pixel != last).any():
                            g.brush = ( pixel[2], pixel[1], pixel[0], pixel[3] )
                            last    = pixel

                        g.draw_rectangle( tbx, by, scale, scale )
                        tbx += scale

                    by += scale

            # Draw the grid (if possible):
            if scale >= 8:
                ex    = min( wdx, ox + sbdx )
                ey    = min( wdy, oy + sbdy )
                gx    = ox
                if gx < 0:
                    gx = (gx % scale) - scale

                y = oy
                if y < 0:
                    y = (y % scale) - scale

                g.pen = factory.grid_color
                x     = gx
                while x <= ex:
                    g.draw_line( x, y, x, ey )
                    x += scale

                while y <= ey:
                    g.draw_line( gx, y, ex, y )
                    y += scale

            # Draw the overlay regions (if any):
            for overlay in factory.overlays:
                n     = len( overlay )
                x0    = int( overlay[0] )
                y0    = int( overlay[1] )
                dx    = dy = 0
                color = factory.overlay_color
                brush = None
                if n >= 4:
                    dx = int( overlay[2] )
                    dy = int( overlay[3] )
                    if n >= 5:
                        color = overlay[4]
                        if n >= 6:
                            brush = overlay[5]

                if ((x0 < 0) or (dx < 0) or ((x0 + dx) > idx) or
                    (y0 < 0) or (dy < 0) or ((y0 + dy) > idy)):
                    continue

                x0      = int( ox + (x0 * scale) )
                y0      = int( oy + (y0 * scale) )
                g.pen   = color
                g.brush = brush
                if dx == 0:
                    if dy == 0:
                        width = ( 3, 5 )[ scale >= 8 ]
                        g.draw_rectangle( x0 - (width / 2), y0 - (width / 2),
                                          width, width )
                    else:
                        g.draw_line( x0, y0, x0, int( y0 + (dy * scale) ) )
                elif dy == 0:
                    g.draw_line( x0, y0, int( x0 + (dx * scale) ), y0 )
                else:
                    g.draw_rectangle(
                        x0, y0, int( dx * scale ) + 1, int( dy * scale ) + 1 )

            # Draw the selection overlay (if active):
            if self.drag_selected is not None:
                sx, sy, sdx, sdy = self.drag_selected
            else:
                sx, sy, sdx, sdy = self.selected

            if ((sdx * sdy) <= 1) and (((wdx / scale) * (wdy / scale)) <= 64):
                sx  = sy = 0
                sdx, sdy = bdx, bdy

            if (sdx * sdy) != 0:
                sx0     = ox + int( sx * scale )
                sy0     = oy + int( sy * scale )
                g.pen   = None
                g.brush = factory.selection_color
                g.draw_rectangle( sx0, sy0, sdx * scale, sdy * scale )

                # Draw the channel delta text overlays (if requested and there
                # is room available in each cell):
                if factory.channel != 'none':
                    if self._int_text_size is None:
                        self._int_text_size   = g.text_size( '-255' )
                        self._float_text_size = g.text_size( '1.777' )

                    tdx, tdy = self._int_text_size
                    if factory.float:
                        tdx, tdy = self._float_text_size

                    if factory.delta:
                        can_show = (((scale >= (tdx + 8))        and
                                     (scale >= (2 * tdy)))       or
                                    ((scale >= ((2 * tdx) + 10)) and
                                     (scale >= tdy)))
                    else:
                        can_show = ((scale >= (((3 * tdx) / 4) + 8)) and
                                    (scale >= tdy))

                    if can_show:
                        asx0, asy0 = sx0, sy0
                        if asx0 < 0:
                            asx0, sx, sdx = clip_low( asx0, sx, sdx, scale )

                        if asy0 < 0:
                            asy0, sy, sdy = clip_low( asy0, sy, sdy, scale )

                        sdx = min( sdx, (wdx + scale - asx0) / scale )
                        sdy = min( sdy, (wdy + scale - asy0) / scale )

                        if (sdx > 0) and (sdy > 0):
                            self._paint_channels( g, asx0, asy0,
                                                  sx, sy, sdx, sdy, scale )

        # Copy the buffer to the display:
        g.copy()


    def _size ( self, event ):
        """ Handles the control being resized.
        """
        if self.scale == 1.0:
            self._reset_view()


    def _left_down ( self, event ):
        """ Handles the left mouse being pressed.
        """
        self.adapter.mouse_capture = True
        self._x, self._y, self._offset = event.x, event.y, self.offset
        if event.control_down:
            self._mode = 'pan'
        else:
            self._mode = 'select'
            self._motion_select( event )


    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            if self._mode == 'select':
                self.selected, self.drag_selected = self.drag_selected, None

            self._x = self._y = self._offset = self._mode = None
            self.adapter.mouse_capture = False


    def _left_dclick ( self, event ):
        """ Handles the left mouse button being double-clicked.
        """
        self._ax, self._ay, scale = event.x, event.y, self.scale
        end     = DClickZoom1
        tweener = EaseOut
        if scale >= end:
            end     = DClickZoom2
            tweener = NoEasing
            if scale >= end:
                end = 1.0

        self._animation = self.animate_facet(
            'scaling', 0.8, end, scale,
            path    = QPath,
            tweener = tweener,
            start   = False
        )
        self._animation.start = True


    def _middle_down ( self, event ):
        self._x, self._y           = event.x, event.y
        self._offset, self._scale  = self.offset, self.scale
        self.adapter.mouse_capture = True
        if event.control_down:
            self._mode = 'zoom'


    def _middle_up ( self, event ):
        if self._x is not None:
            self._x = self._y = self._offset = self._scale = self._mode = None
            self.adapter.mouse_capture = False


    def _right_down ( self, event ):
        """ Handles the right mouse being pressed.
        """
        self.adapter.mouse_capture = True
        self._x, self._y, self._offset = event.x, event.y, self.offset
        self._mode = 'pan_pending'


    def _right_up ( self, event ):
        """ Handles the right mouse button being released.
        """
        if self._mode == 'pan_pending':
            self._reset_view()

        self._x = self._y = self._offset = self._mode = None
        self.adapter.mouse_capture = False


    def _motion ( self, event ):
        """ Handles the mouse moving.
        """
        if self._mode is not None:
            getattr( self, '_motion_' + self._mode )( event )


    def _motion_select ( self, event ):
        """ Handles the user drag selecting a region.
        """
        selected = ( -1, -1, 0, 0 )
        image    = self.image
        if image is not None:
            scale = self.scale
            if scale >= 2.0:
                scale = int( round( scale ) )

            bdx, bdy = image.width, image.height
            ox, oy   = self.offset
            ox       = int( round( ox * scale ) )
            oy       = int( round( oy * scale ) )
            sx       = int( (self._x - ox) / scale )
            sy       = int( (self._y - oy) / scale )
            ex       = int( (event.x - ox) / scale )
            ey       = int( (event.y - oy) / scale )
            sx, ex   = min( sx, ex ), max( sx, ex )
            sy, ey   = min( sy, ey ), max( sy, ey )

            if (ex >= 0) and (ey >= 0) and (sx < bdx) and (sy < bdy):
                sx, sy   = max( 0, sx ), max( 0, sy )
                selected = ( sx, sy, min( ex + 1, bdx ) - sx,
                                     min( ey + 1, bdy ) - sy )

        self.drag_selected = selected


    def _motion_pan_pending ( self, event ):
        """ Handles the user moving the mouse while in 'pan_pending' mode
            (meaning we are waiting to see if the user starts a panning drag).
        """
        if (abs( event.x - self._x ) + abs( event.y - self._y )) >= 3:
            self._mode = 'pan'


    def _motion_pan ( self, event ):
        """ Handles the user panning the image.
        """
        wdx, wdy = self.adapter.client_size
        ox, oy   = self._offset
        scale    = self.scale
        if scale >= 8.0:
            scale = round( scale )

        self.offset = ( ox + ((event.x - self._x) / scale),
                        oy + ((event.y - self._y) / scale) )


    def _motion_zoom ( self, event ):
        """ Handles the user zooming the image.
        """
        diff = float( self._y - event.y )
        if diff == 0.0:
            delta = 0.0
        elif diff < 0.0:
            delta = max( -0.999, diff / (50.0 * log( 1.0 - diff )) )
        else:
            delta = (diff / 300.0) * log( diff * diff )

        if delta != 0.0:
            self._zoom( self._x, self._y, self._scale * (1.0 + delta) )


    def _mouse_wheel ( self, event ):
        """ Handles the mouse wheel rotating.
        """
        delta, scale, rounding = event.wheel_change, self.scale, True
        if event.control_down:
            if scale >= 8.0:
                if (scale > 8.0) or (delta > 0):
                    scale += (8.0 * delta)
                else:
                    scale = 7.0
            elif scale <= 2.0:
                scale   *= (1.0 + (float( delta ) / 50.0))
                rounding = False
            else:
                scale = max( 2.0, scale + float( delta ) )
        else:
            scale *= (1.0 + (float( delta ) / 3.0))

        self._zoom( event.x, event.y, scale, rounding )

    #-- Drag and Drop Event Handlers -------------------------------------------

    def drag_move ( self, event ):
        """ Handles a drag 'move' event.
        """
        if event.has_files:
            files = event.files
            if len( event.files ) == 1:
                if splitext( files[0] )[1] in ImageTypes:
                    event.result = event.request

                    return

        event.result = 'ignore'


    def drag_drop ( self, event ):
        """ Handles a drag 'drop' event.
        """
        self.value = event.files[0]
        self.update_editor()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'offset, scale, selected, drag_selected, factory:[channel, float, delta, grid_color, bg_color, selection_color, overlay_color, overlays[]]' )
    def _editor_modified ( self ):
        """ Handles some value that affects the editor appearance being
            modified.
        """
        inn( self.adapter ).refresh()


    @on_facet_set( 'image:bitmap' )
    def _bitmap_modified ( self ):
        """ Handles the current image bitmap being modified.
        """
        self._scale = self._scaled_image = None
        inn( self.adapter ).refresh()


    def _scaling_set ( self, scaling ):
        """ Handles the 'scaling' facet being changed.
        """
        self._zoom( self._ax, self._ay, scaling,
                    scaling == self._animation.end )


    @on_facet_set( 'factory:auto_reset' )
    def _auto_reset_modified ( self, auto_reset ):
        """ Handles the factory 'auto_reset' facet being modified.
        """
        if auto_reset:
            self._reset_view()

    #-- Private Methods --------------------------------------------------------

    def _reset_view ( self ):
        """ Resets the view back to its initial values.
        """
        self.scale  = 1.0
        self.offset = ( 0.0, 0.0 )
        image       = self.image
        if image is not None:
            wdx, wdy    = self.adapter.client_size
            self.offset = ( (wdx - image.width) / 2, (wdy - image.height) / 2 )


    def _zoom ( self, x, y, new, rounding = True ):
        """ Zoom the view by a specified new scale factor relative to a
            specified point (x,y) within the control.
        """
        if self.image is None:
            return

        old = self.scale
        if rounding:
            if 0.75 <= new <= 1.25:
                new = 1.0
            elif new >= 8.0:
                scale = (int( round( new ) ) / 8) * 8
                if new > old:
                    if scale <= old:
                        scale += 8
                elif scale >= old:
                    scale -= 8

                new = float( scale )

        if new < old:
            new = min( old, max( new, 20.0 / min( self.image.width,
                                                  self.image.height ) ) )

        self.scale = new

        if old >= 2.0:
            old = round( old )

        if new >= 2.0:
            new = round( new )

        ox, oy      = self.offset
        self.offset = ( (x / new) - (x / old) + ox, (y / new) - (y / old) + oy )


    def _paint_channels ( self, g, x0, y0, sx, sy, sdx, sdy, scale ):
        """ Paints the channel text information in the specified region.
        """
        # Set up loop values:
        pixels       = self.image.pixels
        index        = 'rgbahls'.index( self.factory.channel[:1] )
        bindex       = (index / 4) * 4
        n            = 4
        delta        = self.factory.delta
        format       = format_int
        ntdx, ntdy   = self._int_text_size
        as_float     = self.factory.float
        if as_float:
            format     = format_float
            ntdx, ntdy = self._float_text_size

        # Determine which data will fit in a cell:
        show_2h      = (scale >= ((2 * ntdx) + 10))
        show_3h      = (scale >= ((2 * ntdx) + ((3 * ntdx) / 4) + 12))
        show_2v      = (scale >= (2 * ntdy))
        show_3v      = (scale >= (3 * ntdy))
        show_nv      = (scale >= (n * ntdy))
        both_1       = (show_3h or show_3v)
        both_n       = (show_3h and show_nv)
        show_value_1 = ((not delta) or both_1)
        show_value_n = (((not delta) and show_nv) or both_n)
        show_delta_1 = (delta or both_1)
        show_delta_n = ((delta and (show_2h and show_nv)) or both_n)

        # Iterate over all pixel rows:
        while sdy > 0:
            tx0  = x0
            tx   = sx
            tsdx = sdx

            # Iterate over all pixel columns:
            while tsdx > 0:
                # Get the pixel and neighboring (above, left) pixel data:
                p0 = hls( pixels[ sy, tx ], as_float )

                has_delta = ((sy > 0) and (tx > 0))
                if has_delta:
                    p1 = hls( pixels[ sy - 1, tx ], as_float )
                    p2 = hls( pixels[ sy, tx - 1 ], as_float )

                # Set up a contrasting text color based in the pixel color:
                c = 0x000000
                if (p0[8] > 200) and (p0[9] < 160):
                    c = 0xFFFFFF
                g.text_color = c

                # Based on the available space, display the appropriate data in
                # each pixel cell:
                if show_value_n or show_delta_n:
                    if show_delta_n and has_delta:
                        ty0 = y0 + scale - 2 - (n * ntdy)
                        for i in xrange( bindex, bindex + n ):
                            text     = format( (p0[ i ] - p2[ i ]) )
                            tdx, tdy = g.text_size( text )
                            g.draw_text( text, tx0 + 4, ty0 )
                            ty0 += ntdy

                        ty0 = y0
                        for i in xrange( bindex, bindex + n ):
                            text     = format( p0[ i ] - p1[ i ] )
                            tdx, tdy = g.text_size( text )
                            g.draw_text( text, tx0 + scale - tdx - 4, ty0 )
                            ty0 += ntdy

                    if show_value_n:
                        ty0 = y0 + ((scale - (n * ntdy)) / 2)
                        for i in xrange( bindex, bindex + n ):
                            text     = format( p0[ i ] )
                            tdx, tdy = g.text_size( text )
                            g.draw_text( text, tx0 + ((scale - tdx) / 2), ty0 )
                            ty0 += ntdy
                else:
                    if show_delta_1 and has_delta:
                        text     = format( p0[ index ] - p1[ index ] )
                        tdx, tdy = g.text_size( text )
                        g.draw_text( text, tx0 + scale - tdx - 4, y0 )
                        text     = format( p0[ index ] - p2[ index ] )
                        tdx, tdy = g.text_size( text )
                        g.draw_text( text, tx0 + 4, y0 + scale - tdy - 2 )

                    if show_value_1:
                        text     = format( p0[ index ] )
                        tdx, tdy = g.text_size( text )
                        g.draw_text( text, tx0 + ((scale - tdx) / 2),
                                           y0  + ((scale - tdy) / 2) )

                # Advance to the next pixel column:
                tx0  += scale
                tx   += 1
                tsdx -= 1

            # Advance to the next pixel row:
            y0  += scale
            sy  += 1
            sdy -= 1

#-------------------------------------------------------------------------------
#  'ImageZoomEditor' class:
#-------------------------------------------------------------------------------

class ImageZoomEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ImageZoomEditor

    # Should the view automatically reset when the input image is changed?
    auto_reset = Bool( True, facet_value = True )

    # The image grid color:
    grid_color = Color( 0x707070, facet_value = True )

    # The background color to use:
    bg_color = Color( 0x303030, facet_value = True )

    # The color to use for image selection:
    selection_color = Color( 0xD0FF5050, facet_value = True )

    # The default color to use for drawing overlay regions:
    overlay_color = Color( 0xFF0000, facet_value = True )

    # The list of overlay regions to display over the zoomed image:
    overlays = List( facet_value = True )

    # The extended facet name of the currently selected image region bounds:
    selected = Str

    # The image channel value to display in the selected region:
    channel = Enum( 'none', 'red', 'green', 'blue', 'alpha',
                    'hue', 'lightness', 'saturation', facet_value = True )

    # Should image channel values be displayed as floats (True) or
    # integers (False):
    float = Bool( False, facet_value = True )

    # Should image channel 'delta' values be shown in the selected region?
    delta = Bool( False, facet_value = True )

    # Should dragged image files be allowed to be dropped on the editor?
    allow_drop = Bool( False )

#-- EOF ------------------------------------------------------------------------