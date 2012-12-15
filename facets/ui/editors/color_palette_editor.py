"""
Defines a color picker editor based on choosing colors from a color palette
whose values are user defined HLSA color gradients.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import copysign

from colorsys \
    import rgb_to_hls, hls_to_rgb

from facets.api                                                                \
    import Instance, Color, Int, Bool, List, Any, Enum, Range, Image,          \
           Property, View, VGroup, UItem, toolkit, Editor, BasicEditorFactory, \
           on_facet_set, property_depends_on

from facets.ui.controls.themed_window \
    import ThemedWindow

from facets.ui.editors.hls_color_editor \
    import HLSColorEditor

from facets.ui.pyface.timer.api \
    import do_later, do_after

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The minimum and maximum number of cells that can be drawn:
MinCells = 8
MaxCells = 2048

# The length of a long mouse click (in milliseconds):
LongClick = 250

# The color drawn around the edges of the color palette cells:
EdgeColor = ( 0, 0, 0 )

# The color drawn around the edge of the current color palette selection:
SelectColor = ( 255, 0, 0 )

# The colors to use for an unassigned color palette cell:
UnassignedColor  = ( 56, 56, 56 )
UnassignedColor2 = ( 0, 0, 0 )

# The color to edit when editing an empty color palette cell:
DefaultColor = ( 255, 0, 0 )

# States in which the selection border is drawn:
SelectionStates = ( 'dragging', 'copying' )

# Special values used when calling '_color_at':
UseUnassigned   = -1   # Undefined colors should return the unassigned color
UseDefaultColor = -2   # Undefined colors should return the default color
UseNone         = -3   # Undefined colors should return 'None'

# Values for '_color_at' which are not valid colors:
NonColors = ( UseUnassigned, UseDefaultColor, UseNone )

# The tooltip displayed when the mouse pointer is over an empty cell:
EmptyTooltip = """
Click to assign a color.
Use scroll wheel to zoom.
"""[1:-1]

# The tooltip displayed when the mouse pointer is over a filled cell:
FilledTooltip = """
Click to select color.
Long click to edit color.
Drag to create color range.
Right-click to delete color.
Right-drag to delete selected colors.
Long press then drag or Ctrl-drag to copy color.
Ctrl-Shift-drag to move color.
Drag then add Ctrl to copy selection.
Drag then add Ctrl-Shift to move selection.
Use scroll wheel to zoom.
"""[1:-1]

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def clamp ( value ):
    """ Makes sure a specified value is in the range from 0.0 to 1.0.
    """
    return max( 0.0, min( 1.0, value ) )

#-------------------------------------------------------------------------------
#   'ColorPaletteControl' class:
#-------------------------------------------------------------------------------

class ColorPaletteControl ( ThemedWindow ):
    """ Defines a color picker control based on choosing colors from a color
        palette whose values are user defined HLSA color gradients.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Should the user be able to 'tab' into this control (override)?
    tab_stop = True

    # Does this control handle keyboard input (override)?
    handle_keys = True

    # The current selected color:
    color = Color( None )

    # The base color palette cell size:
    cell_size = Range( 9, 500, 15, facet_value = True )

    # The requested minimum number of cell rows to display:
    cell_rows = Range( 1, 50, 7, facet_value = True )

    # The requested minimum number of cell columns to display:
    cell_columns = Range( 1, 50, 7, facet_value = True )

    # The current set of palette colors being displayed (organized as a list of
    # rows, which are lists of columns of integer 0xAARRGGBB values):
    cell_colors = List( facet_value = True )

    # Allow using the color alpha channel?
    alpha = Bool( False, facet_value = True )

    # The current corners of the selected region (None or (int,int)):
    cell1 = Any
    cell2 = Any

    # The required size of the editing control:
    size = Property

    # The current color palette sample x and y coordinates:
    cxs = List
    cys = List

    # The 'transparent' image background used to help display partially
    # transparent colors being edited:
    transparent = Image( '@std:transparent' )

    # The colors currently being edited by a pop-up color editor:
    color1 = Color
    color2 = Color

    # Are changes to color1 automatically propagated to color2?
    linked = Bool

    # The number of hue divisions to create when using linking:
    divisions = Int

    # The current copy mode being used during a 'copying' operation:
    copy_mode = Enum( 'unknown', 'copy', 'erase' )

    # Can the cell size be zoomed by the user?
    can_zoom = Bool( True )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return self._init_view( View(
            VGroup(
                UItem( 'color1', editor = self._hsl_color_editor() ),
                group_theme = '@std:popup'
            )
        ) )

    #-- Public Methods ---------------------------------------------------------

    def copy_colors ( self, colors = None ):
        """ Returns a copy of the current colors in the color palette.
        """
        result = []

        if colors is None:
            colors = self.cell_colors

        for row in colors:
            result.append( row[:] )

        return result


    def dispose ( self ):
        """ Disposes of the control by removing its event handlers (override).
        """
        self.control.unset_event_handler(
            key_press = self._key_press,
            key       = self._key
        )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'cell_size, cell_rows, cell_columns' )
    def _get_size ( self ):
        return ( (self.cell_columns * (self.cell_size + 1)) + 1,
                 (self.cell_rows    * (self.cell_size + 1)) + 1 )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the underlying 'control' being created.
        """
        self._cached_size = ( -1, -1, -1, -1 )
        control.size = control.min_size = self.size
        control.size_policy             = ( 'fixed', 'fixed' )

        control.set_event_handler(
            key_press = self._key_press,
            key       = self._key
        )


    def _size_set ( self, size ):
        """ Handles the 'size' facet being changed.
        """
        control = self.control
        if control is not None:
            control.min_size = size
            self.refresh()


    @on_facet_set( 'color, alpha' )
    def _visuals_modified ( self ):
        """ Handles a facet affecting the visual appearanace of the control
            being modified.
        """
        self.refresh()


    def _color1_set ( self, color ):
        if self.linked:
            self.color2 = self._complementary_color_for( color, self.divisions )

        do_later( self._color_gradient )


    def _color2_set ( self ):
        do_later( self._color_gradient )

    #-- Control Event Handlers -------------------------------------------------

    def _key_press ( self, event ):
        """ Handles a key press event.
        """
        if event.control_down and (self.state == 'dragging'):
            self._copy_mode( event.shift_down )
            self._cell_colors        = self.copy_colors()
            self._cell1, self._cell2 = self.cell1, self.cell2


    def _key ( self, event ):
        """ Handles a key release event.
        """
        if (self.state == 'copying') and (not event.control_down):
            self.state = 'dragging'


    def normal_left_down ( self, x, y, event ):
        """ Handles the user pressing the left mouse button while in the normal
            color selection mode.
        """
        self.cell1 = self.cell2 = self._cell_at( x, y )
        if event.alt_down:
            self.state = 'dragging'
            self.refresh()
        elif event.control_down:
            self._start_copy( event.shift_down )
        else:
            self.state = 'pending'
            do_after( LongClick, self._start_drag )


    def normal_right_down ( self, x, y, event ):
        """ Handles the user pressing the right mouse button while in the normal
            color selection mode.
        """
        self.cell1 = self.cell2 = self._cell_at( x, y )
        self.state = 'dragging'
        self.refresh()


    def normal_wheel ( self, x, y, event ):
        """ Handles the mouse wheel moving while in the normal color selection
            mode.
        """
        if self.can_zoom:
            try:
                self.cell_size += ((1 + (int( 0.1 * self.cell_size ) *
                                   event.shift_down)) * event.wheel_change)
                self.cell_size  = self._cell_size()
            except:
                pass


    def normal_motion ( self, x, y, event ):
        """ Handles mouse motion while in the normal color selection mode.
        """
        cell = self._cell_at( x, y )
        if cell is not None:
            color = self._color_at( cell[0], cell[1], UseNone )
            self.control.tooltip = (EmptyTooltip if color is None else
                                    FilledTooltip)


    def pending_left_up ( self, x, y, event ):
        """ Handles the left mouse button being released while in pending mode
            which means the user simply clicked on a cell.
        """
        self.state = 'normal'
        color      = self._color_at( self.cell1[0], self.cell1[1], UseNone )
        if color is None:
            self._edit_colors( event )
        else:
            self.color = color
            self.cell1 = self.cell2 = None


    def pending_motion ( self, x, y, event ):
        """ Handles the mouse moving while in pending mode.
        """
        cell = self._cell_at( x, y )
        if cell != self.cell1:
            self.state = 'dragging'
            if cell is not None:
                self.cell2 = cell
                self.refresh()


    def dragging_left_up ( self, x, y, event ):
        """ Handles the left mouse button being released while in dragging mode.
        """
        self.state = 'normal'
        cell       = self._cell_at( x, y )
        if cell is None:
            self.cell1 = self.cell2 = None
            self.refresh()
        else:
            self.cell2 = cell
            if event.alt_down:
                self._clear_colors()
            else:
                self._edit_colors( event )


    def dragging_right_up ( self, x, y, event ):
        """ Handles the right mouse button being released while in dragging
            mode.
        """
        self.state = 'normal'
        cell       = self._cell_at( x, y )
        if cell is None:
            self.cell1 = self.cell2 = None
            self.refresh()
        else:
            self.cell2 = cell
            self._clear_colors()


    def dragging_motion ( self, x, y, event ):
        """ Handles the mouse moving while in dragging mode.
        """
        cell = self._cell_at( x, y )
        if (cell is not None) and (cell != self.cell2):
            self.cell2 = cell
            self.refresh()


    def copying_left_up ( self, x, y, event ):
        """ Handles the left mouse button being released while in copying mode.
        """
        self._drag_copy( x, y, event )
        self.state = 'normal'
        if ((self.copy_mode == 'copy')      or
            (self._cell_at( x, y ) is None) or
            event.control_down):
            self._cell_colors = self.cell1 = self.cell2 = None
            self.refresh()
        else:
            self._edit_colors( event )


    def copying_motion ( self, x, y, event ):
        """ Handles the mouse moving while in copying mode.
        """
        self._drag_copy( x, y, event )


    def paint ( self, g ):
        """ Paints the contents of the color palette control.
        """
        # Calculate the number of color palette samples to display:
        # Note that the current algorithm computes a fixed size grid, which
        # may have a partial extra row or column tacked onto the end. This makes
        # resizing the grid seem very smooth. Another approach is to resize the
        # grid dynamically to fit the actual window size. This always make the
        # grid fit the window exactly but seems to hop and jump around when the
        # user resizes the window. The code is set up so that the values
        # computed for 'adx' and 'ady' determine which algorithm is being used.
        cs       = self._cell_size()
        bs       = (cs / 16) + 1
        n        = cs / 7
        wdx, wdy = self.control.size
        size     = cs + bs
        adx      = ((wdx + cs - 1) / size) * size
        ady      = ((wdy + cs - 1) / size) * size
        columns  = adx / size
        rows     = ady / size

        # Calculate bounding x and y coordinates for each color palette sample:
        self.cxs = cxs = self._slice( adx, columns )
        self.cys = cys = self._slice( ady, rows )

        # Paint the background using the transparent background if alpha is
        # being used:
        if self.alpha:
            self._tfill( g, 0, 0, wdx, wdy )

        # Draw all of the color palette grid lines:
        g.pen = EdgeColor
        for x in cxs:
            for i in xrange( bs ):
                g.draw_line( x + i, 0, x + i, ady )

        for y in cys:
            for i in xrange( bs ):
                g.draw_line( 0, y + i, adx, y + i )

        # Draw all of the color palette cells:
        g.pen = None
        y0    = bs
        for row in xrange( rows ):
            y1 = cys[ row + 1 ]
            dy = y1 - y0
            x0 = bs
            for column in xrange( columns ):
                color     = self._color_at( row, column, UseNone )
                undefined = (color is None)
                if undefined:
                    color = UnassignedColor

                g.brush = color
                x1      = cxs[ column + 1 ]
                g.draw_rectangle( x0, y0, x1 - x0, dy )
                if undefined and (n > 0):
                    g.pen = UnassignedColor2
                    for i in xrange( n ):
                        g.draw_line( x1 - n + i, y0 + i, x1 - 1, y0 + i )

                    g.pen = None

                x0 = x1 + bs

            y0 = y1 + bs

        # Draw the selection markers (if necessary):
        if self.state in SelectionStates:
            row1, column1    = self.cell1
            row2, column2    = self.cell2
            row1, row2       = min( row1, row2 ), max( row1, row2 )
            column1, column2 = min( column1, column2 ), max( column1, column2 )
            g.pen   = SelectColor
            g.brush = None
            x1      = cxs[ column1 ]
            dx      = cxs[ column2 + 1 ] - x1 + bs
            y1      = cys[ row1 ]
            dy      = cys[ row2    + 1 ] - y1 + bs
            g.draw_rectangle( x1, y1, dx, dy )
            g.draw_rectangle( x1 + 1, y1 + 1, dx - 2, dy - 2 )

    #-- Private Methods --------------------------------------------------------

    def _start_drag ( self ):
        """ Handle a time out occurring while we wait for the user to decide if
            they are clicking a color or editing it.
        """
        if self.state == 'pending':
            self._start_copy()


    def _start_copy ( self, shift_down = False ):
        """ Start a drag copy operation.
        """
        self._copy_mode( shift_down )
        self._cell_colors        = self.copy_colors()
        self._cell1, self._cell2 = self.cell1, self.cell2
        self.refresh()


    def _copy_mode ( self, shift_down ):
        """ Makes sure that we are in 'copying' mode with the correct 'copy' or
            'erase' status set.
        """
        if self.state != 'copying':
            self.state     = 'copying'
            self.copy_mode = 'erase' if shift_down else 'unknown'
        elif self.copy_mode == 'unknown':
            self.copy_mode = 'erase' if shift_down else 'copy'


    def _init_view ( self, view ):
        """ Returns and initializes the specified view so that it will appear at
            the correct location.
        """
        x, y   = self.control.screen_position
        r, c   = self._cell1
        x1, y1 = self.cxs[ c ], self.cys[ r ]

        return view.facet_set(
            kind         = 'popup',
            popup_bounds = ( x + x1, y + y1,
                             self.cxs[ c + 1 ] - x1, self.cys[ r + 1 ] - y1 )
        )


    def _cell_at ( self, x, y ):
        """ Returns the color palette (row,column) corresponding to the
            specified (x,y) location.
        """
        wdx, wdy = self.control.size

        if (0 <= x < wdx) and (0 <= y < wdy):
            xs = self.cxs
            for i in xrange( 1, len( xs ) ):
                if x <= xs[ i ]:
                    column = i - 1

                    break

            ys = self.cys
            for i in xrange( 1, len( ys ) ):
                if y <= ys[ i ]:
                    return ( i - 1, column )

        return None


    def _color_at ( self, row, column, color = UseUnassigned ):
        """ Sets/Returns the current color at the specified color palette row
            and column location.
        """
        colors = self.cell_colors
        for i in xrange( row - len( colors ) + 1 ):
            colors.append( [] )

        colors = colors[ row ]
        extra  = column - len( colors )
        if extra >= 0:
            colors.extend( [ None ] * (extra + 1) )

        if color not in NonColors:
            colors[ column ] = color
        else:
            result = colors[ column ]
            if result is None:
                if color == UseDefaultColor:
                    result = DefaultColor
                elif color == UseUnassigned:
                    result = UnassignedColor

            return result


    def _slice ( self, space, n ):
        """ Slice the specified space up into a specified number of pieces,
            and return a list containing the coordinates of each piece.
        """
        x  = 0
        xs = [ x ]
        while n > 0:
            dx = int( round( float( space ) / n ) )
            x += dx
            xs.append( x )
            space -= dx
            n     -= 1

        return xs


    def _edit_colors ( self, event ):
        """ Displays a pop-up color editor based upon the currently selected
            color palette cells.
        """
        self._cell1, self.cell1 = self.cell1, None
        self._cell2, self.cell2 = self.cell2, None
        r1, c1      = self._cell1
        r2, c2      = self._cell2
        self.color1 = self._color_at( r1, c1, UseDefaultColor )
        color       = self._color_at( r2, c2, UseNone )
        self.linked = (color is None)
        if self.linked:
            dr, dc         = abs( r2 - r1 ), abs( c2 - c1 )
            self.linked    = (max( dr, dc ) > 0)
            color          = self.color1
            self.divisions = min( dr, dc ) + 1
            self.color2    = self._complementary_color_for( color,
                                                            self.divisions )
        else:
            self.color2 = color

        do_later( self._color_gradient )

        if (not event.shift_down) and (self._cell1 == self._cell2):
            self.edit_facets( parent = self.control )


    def _clear_colors ( self ):
        """ Resets all of the currently selected colors back to the 'undefined'
            state.
        """
        r1, c1     = self.cell1
        r2, c2     = self.cell2
        r1, r2     = min( r1, r2 ), max( r1, r2 )
        c1, c2     = min( c1, c2 ), max( c1, c2 )
        self.cell1 = self.cell2 = None
        for row in xrange( r1, r2 + 1 ):
            for column in xrange( c1, c2 + 1 ):
                self._color_at( row, column, None )

        self.refresh()


    def _hsl_color_editor ( self ):
        """ Returns an HSLAColorEditor to use for editing a color palette cell.
        """
        return HLSColorEditor(
            cell_size = min( max( min( self.control.size ), 200 ) / 9, 35 ),
            cells     = 13,
            space     = 0,
            edit      = 'all',
            alpha     = self.alpha
        )


    def _to_hlsa ( self, color ):
        """ Returns a GUI toolkit neutral color converted to an HLSA tuple.
        """
        color  = toolkit().from_toolkit_color( color )
        result = list( rgb_to_hls( color[0] / 255.0,
                                   color[1] / 255.0,
                                   color[2] / 255.0 ) )
        if len( color ) < 4:
            result.append( 1.0 )
        else:
            result.append( color[3] / 255.0 )

        return tuple( result )


    def _from_hlsa ( self, h, l, s, a ):
        """ Converts HLSA values to a GUI toolkit neutral color.
        """
        if h > 1.0:
            h -= 1.0
        elif h < 0.0:
            h += 1.0

        color = list( hls_to_rgb( h, clamp( l ), clamp( s ) ) ) + [ clamp( a ) ]

        return tuple( [ int( round( c * 255.0 ) ) for c in color ] )


    def _rgba_color ( self, color ):
        """ Returns a standard (r,g,b,a) tuple representation of the specified
            GUI toolkit specific color.
        """
        result = toolkit().from_toolkit_color( color )
        if len( result ) == 4:
            return result

        return (result + ( 255, ))


    def _complementary_color_for ( self, color, divisions ):
        """ Returns the complementary color for the specified color based upon
            the specified 'linked' style.
        """
        h, l, s, a = self._to_hlsa( color )

        h += 1.0 - (1.0 / divisions)

        if abs( l - 0.5 ) < 0.01:
            l = 0.95
        else:
            l = max( 0.05, min( 0.95, 1.0 - l ) )

        if s < 0.9:
            s = max( 0.05, 1.0 - s )

        return self._from_hlsa( h, l, s, a )


    def _color_gradient ( self ):
        """ Assigns a color gradient based on the range of the two colors
            currently being edited.
        """
        row1, column1 = self._cell1
        if self._cell1 == self._cell2:
            self._color_at( row1, column1, self._rgba_color( self.color1 ) )
        else:
            row2, column2  = self._cell2
            dr             = abs( row2    - row1 )    + 1
            dc             = abs( column2 - column1 ) + 1
            h1, l1, s1, a1 = self._to_hlsa( self.color1 )
            h2, l2, s2, a2 = self._to_hlsa( self.color2 )
            dh, dl, ds, da = h2 - h1, l2 - l1, s2 - s1, a2 - a1
            if self.linked and (0.01 < abs( dh ) < 0.5):
                dh = copysign( 1.0 - abs( dh ), dh )

            drc       = [ dh, dh, dl, dl, ds, ds, da, da ]
            divisions = min( dr, dc )
            if divisions > 1:
                deltas = [ ( dh, 0 ), ( dl, 2 ), ( ds, 4 ), ( da, 6 ) ]
                if self.linked or (divisions <= 3):
                    del deltas[0]
                deltas.sort( lambda l, r: cmp( abs( r[0] ), abs( l[0] ) ) )
                primary = deltas[0][1]
                offset  = (dr >= dc)
                for i in xrange( 0, 8, 2 ):
                    if i == primary:
                        drc[ i + offset ] = 0.0
                    else:
                        drc[ i + 1 - offset ] = 0.0

            ri = (2 * (row2    >= row1))    - 1
            ci = (2 * (column2 >= column1)) - 1
            rn = max( 1, dr - 1 )
            cn = max( 1, dc - 1 )
            for i in xrange( 0, dr ):
                rf = float( i ) / rn
                h  = h1 + (drc[0] * rf)
                l  = l1 + (drc[2] * rf)
                s  = s1 + (drc[4] * rf)
                a  = a1 + (drc[6] * rf)
                c  = column1
                for j in xrange( 0, dc ):
                    cf = float( j ) / cn
                    self._color_at( row1, c, self._from_hlsa(
                        h + (drc[1] * cf),
                        l + (drc[3] * cf),
                        s + (drc[5] * cf),
                        a + (drc[7] * cf) ) )
                    c += ci

                row1 += ri

        self.refresh()


    def _drag_copy ( self, x, y, event ):
        """ Copy the current color palette cells being dragged to a new location
            if necessary.
        """
        cell = self._cell_at( x, y )
        if (cell is not None) and (cell != self.cell2):
            # Make sure the correct copy/erase mode has been set:
            self._copy_mode( event.shift_down )

            # Restore the original colors at the beginning of the drag copy
            # operation:
            self.cell_colors = self.copy_colors( self._cell_colors )

            # Compute the new 'copy to' location:
            row2, column2 = cell
            row1, column1 = self.cell1
            row,  column  = self.cell2
            row1         += (row2 - row)
            column1      += (column2 - column)

            # Make sure the target location is inside the control palette grid:
            if not ((0 <= row1    < (len( self.cys ) - 1)) and
                    (0 <= column1 < (len( self.cxs ) - 1))):
                return

            self.cell1 = ( row1, column1 )
            self.cell2 = cell

            # Make a copy of the original colors being copied from:
            r1, c1 = self._cell1
            r2, c2 = self._cell2
            r1, r2 = min( r1, r2 ), max( r1, r2 )
            c1, c2 = min( c1, c2 ), max( c1, c2 )
            colors = []
            erase  = (self.copy_mode == 'erase')
            for row in xrange( r1, r2 + 1 ):
                for column in xrange( c1, c2 + 1 ):
                    colors.append( self._color_at( row, column, UseNone ) )
                    if erase:
                        self._color_at( row, column, None )

            # Copy the copied colors to their new location:
            row1,    row2    = min( row1, row2 ),       max( row1, row2 )
            column1, column2 = min( column1, column2 ), max( column1, column2 )
            i                = 0
            for row in xrange( row1, row2 + 1 ):
                for column in xrange( column1, column2 + 1 ):
                    color = colors[i]
                    i    += 1
                    self._color_at( row, column, color )

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


    def _cell_size ( self ):
        """ Returns the cell size to use based on the user requested size and
            the size of the control.
        """
        cell_size = self.cell_size
        wdx, wdy  = self.control.size
        cwdx, cwdy, ccell_size, ucell_size = self._cached_size
        if (wdx == cwdx) and (wdy == cwdy) and (cell_size == ccell_size):
            return ucell_size

        while True:
            size = cell_size + ((cell_size / 16) + 1)
            adx  = ((wdx + cell_size - 1) / size) * size
            ady  = ((wdy + cell_size - 1) / size) * size
            cells = (adx / size) * (ady / size)
            if cells < MinCells:
                if cell_size <= 5:
                    break

                cell_size -= 1
            elif cells > MaxCells:
                cell_size += 1
            else:
                break

        self._cached_size = ( wdx, wdy, self.cell_size, cell_size )

        return cell_size

#-------------------------------------------------------------------------------
#  '_ColorPaletteEditor' class:
#-------------------------------------------------------------------------------

class _ColorPaletteEditor ( Editor ):

    #-- Facet Definitions ------------------------------------------------------

    # The ColorPaletteControl control used by the editor:
    selector = Instance( ColorPaletteControl, () )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory      = self.factory
        self.adapter = self.selector.set(
            cell_size     = factory.facet_value( 'cell_size' ),
            cell_rows     = factory.facet_value( 'cell_rows' ),
            cell_columns  = factory.facet_value( 'cell_columns' ),
            cell_colors   = factory.facet_value( 'cell_colors' ),
            alpha         = factory.facet_value( 'alpha' ),
            can_zoom      = self.item.resizable is True,
            parent        = parent
        )()

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if not self._no_update:
            self.selector.color = self.value

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        colors = prefs.get( 'cell_colors', None )
        if colors is not None:
            self.selector.cell_colors = self.selector.copy_colors( colors )


    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return { 'cell_colors': self.selector.copy_colors() }

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'selector:color' )
    def _color_modified ( self, color ):
        """ Handles the selector's 'color' facet being changed.
        """
        self._no_update = True
        self.value      = color
        self._no_update = False

#-------------------------------------------------------------------------------
#  'ColorPaletteEditor' class:
#-------------------------------------------------------------------------------

class ColorPaletteEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ColorPaletteEditor

    # The base cell size:
    cell_size = Range( 9, 50, 15, facet_value = True )

    # The minimum number of cell rows to display:
    cell_rows = Range( 1, 50, 7, facet_value = True )

    # The minimum number of cell columns to display:
    cell_columns = Range( 1, 50, 7, facet_value = True )

    # The set of palette colors to display:
    cell_colors = List( facet_value = True )

    # Allow using the color alpha channel?
    alpha = Bool( False, facet_value = True )

#-- EOF ------------------------------------------------------------------------