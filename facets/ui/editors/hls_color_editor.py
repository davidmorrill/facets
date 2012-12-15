"""
Defines a new type of HSL-based color editor and its associated control.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import fmod

from colorsys \
    import rgb_to_hls, hls_to_rgb

from facets.api \
    import Instance, RGBAInt, Tuple, Int, Float, Bool, Enum, List, Range, \
           Image, Property, Editor, BasicEditorFactory, on_facet_set,     \
           property_depends_on

from facets.ui.controls.themed_window \
    import ThemedWindow

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The color drawn around the edges of the HLSSelector:
EdgeColor = ( 0, 0, 0 )

# The colors drawn around the 'center' cell to indicate a match or not with the
# current color value:
CenterColors = ( ( 255, 0, 0 ), ( 240, 240, 240 ) )

# List of HLSA names:
HLSANames = [ 'HUE', 'LIGHTNESS', 'SATURATION', 'ALPHA' ]

#-------------------------------------------------------------------------------
#   'HLSControl' class:
#-------------------------------------------------------------------------------

class HLSControl ( ThemedWindow ):
    """ HLS-based color selector implementing a selection scheme that allows a
        user to quickly navigate the 3D HLS color space using a simple 2D
        control.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Should the user be able to 'tab' into this control (override)?
    tab_stop = True

    # Does this control handle keyboard input (override)?
    handle_keys = True

    # The current selected color:
    color = RGBAInt( None )

    # The HLSA values corresponding to the current color:
    hlsa = Tuple( Float, Float, Float, Float )

    # The base cell size:
    cell_size = Range( 9, 200, 15, facet_value = True )

    # The requested number of cells to display:
    cells = Range( 5, 50, 7, facet_value = True )

    # The current number of color cells being displayed:
    current_cells = Int

    # The cell border thickness:
    border        = Range( 0, 2, 1, facet_value = True )
    actual_border = Property

    # The space between adjacent cells:
    space = Range( 0, 5, 1, facet_value = True )

    # The orientation of the editor:
    orientation   = Enum( 'horizontal', 'vertical', facet_value = True )
    is_horizontal = Property

    # The color components that can be edited:
    edit = Enum( 'any', 'all', 'hue', 'lightness', 'saturation', 'alpha',
                 facet_value = True )
    edit_all = Property

    # Allow editing the color alpha channel?
    alpha = Bool( False, facet_value = True )

    # Number of HLSA channels being edited:
    channels = Property

    # The current editing mode:
    edit_mode = Int

    # The current editing HLSA value
    edit_hlsa = List

    # The current editing HLSA value ranges:
    edit_range = List( Float, [ 1.0, 1.0, 1.0, 1.0 ] )

    # The current color sample values:
    colors = List

    # The current edit mode selection x-coordinates:
    exs = List

    # The current color sample x-coordinates:
    cxs = List

    # The required size of the editing control:
    size = Property

    # The 'transparent' image background used to help display partially
    # transparent colors being edited:
    transparent = Image( '@std:transparent' )

    #-- Public Methods ---------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the control by removing its event handlers (override).
        """
        self.control.unset_event_handler(
            key_press = self._key_press,
            key       = self._key
        )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'cell_size, cells, orientation, actual_border, space, edit_all' )
    def _get_size ( self ):
        border = self.actual_border
        space  = self.space or (-border)
        dy     = self.cell_size + (2 * border)
        dx     = (self.cells * (dy + space)) - space

        if self.edit_all:
            dy = (self.channels * (dy + space)) - space

        return ( dx, dy ) if self.orientation == 'horizontal' else ( dy, dx )


    @property_depends_on( 'orientation' )
    def _get_is_horizontal ( self ):
        return (self.orientation == 'horizontal')


    @property_depends_on( 'edit' )
    def _get_edit_all ( self ):
        return (self.edit == 'all')


    @property_depends_on( 'alpha' )
    def _get_channels ( self ):
        return (3 + self.alpha)


    @property_depends_on( 'border, space' )
    def _get_actual_border ( self ):
        return min( 1, self.border ) if self.space == 0 else self.border

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the underlying 'control' being created.
        """
        control.size = control.min_size = self.size
        control.size_policy = ( 'fixed', 'fixed' )

        control.set_event_handler(
            key_press = self._key_press,
            key       = self._key
        )


    def _color_set ( self, color ):
        """ Updates the display when the current color changes.
        """
        self.hlsa = self._to_hlsa( color )
        self.refresh()


    def _hlsa_set ( self, hlsa ):
        """ Handles the 'hlsa' facet being changed.
        """
        self.edit_hlsa = [ list( hlsa ) for i in xrange( 4 ) ]


    def _size_set ( self, size ):
        """ Handles the 'size' facet being changed.
        """
        control = self.control
        if control is not None:
            control.size = control.min_size = size
            self.refresh()


    def _edit_set ( self, edit ):
        """ Handles the 'edit' facet being changed.
        """
        if edit != 'any':
            self.state     = 'editing'
            self.edit_mode = [ 'hue', 'lightness', 'saturation', 'alpha', 'all'
                             ].index( edit )
            self.refresh()


    def _alpha_set ( self ):
        """ Handles the 'alpha' facet being changed.
        """
        self.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def _key_press ( self, event ):
        """ Handles a key press event.
        """
        if event.alt_down and (self.state == 'editing'):
            color = self.color
            index = self._alt_index
            if index >= 0:
                if self.edit_all:
                    color = self.colors[ self.edit_mode ][ index ]
                else:
                    color = self.colors[ index ]

            self._alt_color = color
            self.state      = 'show'
            self.refresh()


    def _key ( self, event ):
        """ Handles a key release event.
        """
        if (self.state == 'show') and (not event.alt_down):
            self.state = 'editing'
            self.refresh()


    def normal_enter ( self, x, y, event ):
        """ Handles the mouse entering the window while not in edit mode.
        """
        self.state = 'pending'
        self.refresh()


    def pending_leave ( self, x, y, event ):
        """ Handles the mouse leaving the window while waiting for an edit to
            begin.
        """
        self.state = 'normal'
        self.refresh()


    def pending_left_up ( self, x, y, event ):
        """ Handles the user releasing the mouse button to enter an edit mode.
        """
        if self._in_control( x, y ):
            self.state = 'editing'
            if not self.is_horizontal:
                x = y

            for i, xi in enumerate( self.exs ):
                if x <= xi:
                    self.edit_mode = i
                    break
        else:
            self.state = 'normal'

        self.refresh()


    def editing_left_down ( self, x, y, event ):
        """ Handles the left mouse button being pressed while in edit mode.
        """
        self._index    = self._index_at( x, y, True )
        self._dragging = False
        self._last     = None


    def editing_left_up ( self, x, y, event ):
        """ Handles the left mouse button being released while in edit mode.
        """
        if not self._dragging:
            if event.control_down:
                if (not self.edit_all) and self._in_control( x, y ):
                    self.edit_mode = (self.edit_mode + 1) % self.channels
                    self.refresh()
            else:
                index = self._index_at( x, y )
                if index >= 0:
                    if self.edit_all:
                        self.color = self.colors[ self.edit_mode ][ index ]
                    else:
                        self.color = self.colors[ index ]
                        if self.edit == 'any':
                            self.state = 'pending'
                            self.refresh()

        self._index = None


    def editing_right_up ( self, x, y, event ):
        """ Handles the right mouse button being released while in edit mode.
        """
        if self.edit == 'any':
            self.state = 'pending'
            self.refresh()
        elif not self.edit_all:
            self.edit_mode = (self.edit_mode + 1) % self.channels
            self.refresh()


    def editing_motion ( self, x, y, event ):
        """ Handles the mouse moving while in edit mode.
        """
        index = self._index
        if index is not None:
            if self._last is not None:
                if self.is_horizontal:
                    value = y
                    delta = self._last - value
                else:
                    value = x
                    delta = value - self._last

                if delta != 0:
                    self._zoom_value( index, delta / 10.0 )
                    self._last = value
            else:
                new_index = self._index_at( x, y )
                if new_index < 0:
                    self._dragging = True
                    if self.is_horizontal:
                        self._last = y
                    else:
                        self._last = x
                elif new_index != index:
                    self._dragging = True
                    self._index    = new_index
                    mode = self.edit_mode
                    hlsa = self.edit_hlsa[ mode ]
                    hlsa[ mode ] = (hlsa[ mode ] - (self.edit_range[ mode ] /
                            (self.current_cells - 1)) * (new_index - index))
                    self.refresh()
        else:
            self._alt_index = self._index_at( x, y, True )


    def editing_wheel ( self, x, y, event ):
        """ Handles the mouse wheel moving.
        """
        index = self._index_at( x, y, True )
        if index >= 0:
            if event.control_down:
                delta = 1 - (2 * ((event.wheel_change > 0) ^
                                  self.is_horizontal))
                mode  = self.edit_mode
                hlsa  = self.edit_hlsa[ mode ]
                hlsa[ mode ] = (hlsa[ mode ] - (self.edit_range[ mode ] /
                        (self.current_cells - 1)) * delta)
                self.refresh()
            else:
                self._zoom_value( index, event.wheel_change )


    def show_left_up ( self, x, y, event ):
        """ Handles the left mouse button being released while in show mode.
        """
        if self._in_control( x, y ):
            self.color = self._alt_color


    def show_leave ( self, x, y, event ):
        """ Handles the mouse leaving the control while in show mode.
        """
        self.state = 'editing'
        self.refresh()


    def paint ( self, g ):
        """ Paints the contents of the color editing control.
        """
        getattr( self, '_paint_' + self.state )( g )


    def _paint_normal ( self, g, color = None ):
        """ Paints the contents of the color editing control in normal mode.
        """
        wdx, wdy = self.control.size
        if self.alpha:
            self._tfill( g, 1, 1, wdx - 2, wdy - 2 )

        g.pen   = EdgeColor
        g.brush = color or self.color
        g.draw_rectangle( 0, 0, wdx, wdy )


    def _paint_show ( self, g ):
        """ Paints the contents of the color editing control in show mode.
        """
        self._paint_normal( g, self._alt_color )


    def _paint_pending ( self, g ):
        """ Paints the contents of the color editing control in edit pending
            mode.
        """
        alpha      = self.alpha
        horz       = self.is_horizontal
        wdx, wdy   = self.control.size

        g.brush    = self.color
        text_color = self._text_color_for( self.color )
        x0         = -1
        n          = self.channels
        self.exs   = exs = [ (i * ( wdy, wdx )[ horz ]) / n
                             for i in xrange( 1, n + 1 ) ]

        # Determine if the longest name will fit, and if not, use abbreviations:
        k = [ 10, 1 ][ (not horz) or
                       (g.text_size( 'SATURATION' )[0] > (exs[0] - x0 - 7)) ]

        for i, c in enumerate( HLSANames[ : n ] ):
            c  = c[ : k ]
            x1 = exs[ i ]
            if horz:
                dx = x1 - x0 - 1
                if alpha:
                    self._tfill( g, x0 + 2, 1, dx - 2, wdy - 2 )
                g.pen = EdgeColor
                g.draw_rectangle( x0 + 1, 0, dx, wdy )
                g.text_color = text_color
                self._draw_text( g, x0, 0, dx, wdy, c )
            else:
                dy = x1 - x0 - 1
                if alpha:
                    self._tfill( g, 1, x0 + 2, wdx - 2, dy - 2 )
                g.pen = EdgeColor
                g.draw_rectangle( 0, x0 + 1, wdx, dy )
                g.text_color = text_color
                self._draw_text( g, 0, x0, wdx, dy, c )

            x0 = x1


    def _paint_editing ( self, g ):
        """ Paints the contents of the color editing control in editing mode.
        """
        # Calculate the number of color samples to display:
        wdx, wdy = cdx, cdy = self.control.size
        space    = self.space or (-self.actual_border)
        horz     = self.is_horizontal

        if self.edit_all:
            ddx = ddy = 0
            if horz:
                idy = cdy = ((cdy + space) / self.channels) - space
                ddy = cdy + space
            else:
                idx = cdx = ((cdx + space) / self.channels) - space
                ddx = cdx + space

        if horz:
            adx = wdx + space
            n   = max( 5, adx / (cdy + space) )
        else:
            adx = wdy + space
            n   = max( 5, adx / (cdx + space) )

        # Calculate the bounding x-coordinates for each color sample:
        self.current_cells = count = n
        x  = 0
        xs = [ x ]
        while n > 0:
            dx = int( round( float( adx ) / n ) )
            x += dx
            xs.append( x )
            adx -= dx
            n   -= 1

        self.cxs = xs

        if self.edit_all:
            colors = []
            x = y  = 0
            for i in xrange( self.channels ):
                colors.append(
                    self._paint_cells( g, i, count, x, y, cdx, cdy )
                )
                x += ddx
                y += ddy
        else:
            colors = self._paint_cells( g, self.edit_mode, count, 0, 0,
                                        wdx, wdy )

        self.colors = colors

    #-- Private Methods --------------------------------------------------------

    def _paint_cells ( self, g, channel, count, x, y, dx, dy ):
        """ Paints a specified range of color cells in the specified region.
        """
        alpha  = self.alpha
        border = self.actual_border
        space  = self.space or (-border)
        horz   = self.is_horizontal
        xs     = self.cxs
        equal  = (abs( self.edit_hlsa[ channel ][ channel ] -
                       self.hlsa[ channel ] ) < 0.005 )

        # Calculate the current range of color samples to paint:
        colors = self._colors_for( count, channel )

        # Handle the special case of no space with alpha enabled by filling in
        # the alpha background for the entire control, thus bypassing the
        # visual problem of misalignment of the background pattern within each
        # cell:
        if alpha and (space <= 0):
            self._tfill( g, x + border, y + border,
                            dx - (2 * border), dy - (2 * border) )
            alpha = False

        # Draw the current color sample chips:
        border_color = EdgeColor
        pen          = None
        if border > 0:
            pen = EdgeColor

        g.pen = pen
        n2    = count / 2
        x0    = xs[0]
        for i in xrange( count ):
            g.brush = colors[ i ]
            if i == n2:
                g.pen        = EdgeColor
                border       = 3
                border_color = CenterColors[ equal ]
            x1  = xs[ i + 1 ]
            dxy = x1 - x0 - space
            if horz:
                if alpha:
                    self._tfill( g, x0 + border, y + border,
                                    dxy - (2 * border), dy - (2 * border) )
                g.draw_rectangle( x0, y, dxy, dy )
                if border > 1:
                    g.brush = None
                    g.pen   = border_color
                    for j in xrange( 1, border ):
                        g.draw_rectangle( x0 + j, y + j,
                                          dxy - (2 * j), dy - (2 * j) )
                        g.pen = EdgeColor
            else:
                if alpha:
                    self._tfill( g, x + border, x0 + border,
                                    dx - (2 * border), dxy - (2 * border) )
                g.draw_rectangle( x, x0, dx, dxy )
                if border > 1:
                    g.brush = None
                    g.pen   = border_color
                    for j in xrange( 1, border ):
                        g.draw_rectangle( x + j, x0 + j,
                                          dx - (2 * j), dxy - (2 * j) )
                        g.pen = EdgeColor

            x0 = x1
            if i == n2:
                g.pen        = pen
                border       = self.actual_border
                border_color = EdgeColor

        # Return the set of colors drawn (for use when color picking):
        return colors


    def _draw_text ( self, g, x, y, dx, dy, text ):
        """ Draws the specified text centered in the specified region.
        """
        tdx, tdy = g.text_size( text )
        g.draw_text( text, x + ((dx - tdx) / 2), y + ((dy - tdy) / 2) - 1 )


    def _colors_for ( self, n, channel ):
        """ Returns the range of colors for the specified channel.
        """
        n2               = n / 2
        dhlsa            = [ 0.0, 0.0, 0.0, 0.0 ]
        dhlsa[ channel ] = self.edit_range[ channel ] / (n - 1)
        hlsa             = self.edit_hlsa[ channel ]
        h, l, s, a       = [ hlsa[ i ] - (dhlsa[ i ] * n2)
                             for i in xrange( 4 ) ]
        dh, dl, ds, da   = dhlsa
        colors           = []
        for i in xrange( n ):
            ch = h + (i * dh)
            cl = self._check_range( l + (i * dl), dl )
            cs = self._check_range( s + (i * ds), ds )
            ca = self._check_range( a + (i * da), da )
            colors.append( self._from_hlsa( ch, cl, cs, ca ) )

        return colors


    def _index_at ( self, x, y, set_edit_mode = False ):
        """ Returns the color index corresponding to the specified mouse
            position.
        """
        wdx, wdy = self.control.size
        if not self.is_horizontal:
            x, y, wdx, wdy = y, x, wdy, wdx

        if (0 <= x) and (0 <= y < wdy):
            if self.edit_all:
                edit_mode = (y * self.channels) / wdy
                if set_edit_mode:
                    self.edit_mode = edit_mode
                elif edit_mode != self.edit_mode:
                    return -1

            xs = self.cxs
            for i in xrange( 1, len( xs ) ):
                if x <= xs[ i ]:
                    return (i - 1)

        return -1


    def _in_control ( self, x, y ):
        """ Returns whether a specified (x,y) point is in the control or not.
        """
        wdx, wdy = self.control.size

        return ((0 <= x < wdx) and (0 <= y < wdy))


    def _to_hlsa ( self, color ):
        """ Returns a GUI toolkit neutral color converted to an HLSA tuple.
        """
        return tuple( list( rgb_to_hls( color[0] / 255.0,
                                        color[1] / 255.0,
                                        color[2] / 255.0 ) ) +
                      [ color[3] / 255.0 ] )


    def _from_hlsa ( self, h, l, s, a ):
        """ Converts HLSA values to a GUI toolkit neutral color.
        """
        color = list( hls_to_rgb( h, l, s ) ) + [ a ]

        return tuple( [ int( round( c * 255.0 ) ) for c in color ] )


    def _text_color_for ( self, color ):
        """ Return a good text color to use when drawing on a background of the
            specified *color* (based on an algorithm found on
            stackoverflow.com).
        """
        r, g, b, a = color

        # Counting the perceptive luminance - human eye favors green color:
        if (1.0 - (((0.299 * r) + (0.587 * g) + (0.114 * b)) / 255.0)) < 0.5:
            # Bright colors => black font:
            return 0

        # Dark colors => white font:
        return 0xFFFFFF


    def _check_range ( self, value, delta ):
        """ Make sure that a specified HLSA value is in the range: 0.0...1.0.
        """
        if value < 0.0:
            mv = fmod( value, 1.0 )
            if mv > -(delta / 2.0):
                return 0.0

            return (1.0 + mv)

        if value > 1.0:
            mv = fmod( value, 1.0 )
            if mv < (delta / 2.0):
                return 1.0

            return mv

        return value


    def _zoom_value ( self, index, amount ):
        """ Zooms the value at the specified color index in or out by the
            specified amount.
        """
        mode      = self.edit_mode
        hlsa      = self.edit_hlsa[ mode ]
        old       = hlsa[ mode ]
        old_range = self.edit_range[ mode ]
        new_range = min( old_range * (1 - (0.1 * amount)), 1.0 )
        n         = self.current_cells
        new       = (old - ((n / 2) - index) *
                            ((old_range - new_range) / (n - 1)))
        if ((self.edit_range[ mode ] != new_range) or (hlsa[ mode ] != new)):
            self.edit_range[ mode ] = new_range
            hlsa[  mode ]           = new
            self.refresh()


    def _tfill ( self, g, x, y, dx, dy ):
        """ Fills the specified rectangular region with the 'transparent'
            background image used to display colors with alpha channels.
        """
        transparent = self.transparent
        tbitmap     = transparent.bitmap
        tdx         = transparent.width
        tdy         = transparent.height
        cdy         = dy
        while cdy > 0:
            itdy = min( cdy, tdy )
            cdx  = dx
            cx   = x
            while cdx > 0:
                itdx = min( cdx, tdx )
                g.blit( cx, y, itdx, itdy, tbitmap )
                cx  += itdx
                cdx -= itdx

            y   += itdy
            cdy -= itdy

#-------------------------------------------------------------------------------
#  '_HLSColorEditor' class:
#-------------------------------------------------------------------------------

class _HLSColorEditor ( Editor ):

    #-- Facet Definitions ------------------------------------------------------

    # The HLSControl control used by the editor:
    selector = Instance( HLSControl, () )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory      = self.factory
        self.adapter = self.selector.set(
            cell_size   = factory.facet_value( 'cell_size' ),
            cells       = factory.facet_value( 'cells' ),
            orientation = factory.facet_value( 'orientation' ),
            border      = factory.facet_value( 'border' ),
            space       = factory.facet_value( 'space' ),
            edit        = factory.facet_value( 'edit' ),
            alpha       = factory.facet_value( 'alpha' ),
            parent      = parent
        )()

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if not self._no_update:
            self.selector.color = self.value

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'selector:color' )
    def _color_modified ( self, color ):
        self._no_update = True
        self.value      = color
        self._no_update = False

#-------------------------------------------------------------------------------
#  'HLSColorEditor' class:
#-------------------------------------------------------------------------------

class HLSColorEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _HLSColorEditor

    # The base cell size:
    cell_size = Range( 9, 200, 15, facet_value = True )

    # The number of cells to display:
    cells = Range( 5, 50, 7, facet_value = True )

    # The cell border thickness:
    border = Range( 0, 2, 1, facet_value = True )

    # The space between adjacent cells:
    space = Range( 0, 5, 1, facet_value = True )

    # The orientation of the editor:
    orientation = Enum( 'horizontal', 'vertical', facet_value = True )

    # The color components that can be edited:
    edit = Enum( 'any', 'all', 'hue', 'lightness', 'saturation', 'alpha',
                 facet_value = True )

    # Allow editing the color alpha channel?
    alpha = Bool( False, facet_value = True )

#-- EOF ------------------------------------------------------------------------