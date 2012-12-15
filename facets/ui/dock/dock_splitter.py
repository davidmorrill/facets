"""
Defines a splitter bar used to adjust the size of items contained in a
DockSection.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Enum, Int, Property

from dock_constants \
    import SPLIT_HTOP, SPLIT_HMIDDLE, SPLIT_HBOTTOM, SPLIT_VLEFT, \
           SPLIT_VMIDDLE, SPLIT_VRIGHT, DragColor

from dock_item \
    import DockItem

#-------------------------------------------------------------------------------
#  'DockSplitter' class:
#-------------------------------------------------------------------------------

class DockSplitter ( DockItem ):
    """ Defines a splitter bar used to adjust the size of items contained in a
        DockSection.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Style of the splitter bar:
    style = Enum( 'horizontal', 'vertical' )

    # Index of the splitter within its parent:
    index = Int

    # Current state of the splitter (i.e. its position relative to the things
    # it splits):
    state = Property

    #-- Property Overrides -----------------------------------------------------

    def _get_theme ( self ):
        return self.parent.control.parent.owner.theme

    #-- Public Methods ---------------------------------------------------------

    def draw ( self, g ):
        """ Draws the contents of the splitter.
        """
        if (self._live_drag is False) and (self._first_bounds is not None):
            x, y, dx, dy = self._first_bounds
        else:
            x, y, dx, dy = self.bounds

        dw_theme = self.theme
        if self.style == 'horizontal':
            theme = dw_theme.horizontal_splitter
        else:
            theme = dw_theme.vertical_splitter

        theme.image_slice.fill( g, x, y, dx, dy )

        if dw_theme.splitter_open_close:
            image, idx, idy = dw_theme.images.get_splitter_image( self.state )
            ox, oy          = theme.label.left, theme.label.top
            tis             = theme.image_slice
            tc              = theme.content

            if self.style == 'horizontal':
                iy = y + oy + ((dy + tis.xtop + tc.top - tis.xbottom -
                                tc.bottom - idy) / 2)
                if theme.alignment == 'center':
                    ix = x = x + ox + ((dx + tis.xleft + tc.left - tis.xright -
                                        tc.right - idx) / 2)
                elif theme.alignment == 'right':
                    ix = x = x + ox + dx - tis.xright - tc.right - idx
                else:
                    ix = x = x + ox + tis.xleft + tc.left
                dx = idx
            else:
                ix = x + ox + ((dx + tis.xleft + tc.left - tis.xright -
                                tc.right - idx) / 2)
                if theme.alignment == 'center':
                    iy = y = y + oy + ((dy + tis.xtop + tc.top - tis.xbottom -
                                        tc.bottom - idy) / 2)
                elif theme.alignment == 'right':
                    iy = y = y + oy + dy - tis.xbottom - tc.bottom - idy
                else:
                    iy = y = y + oy + tis.xtop + tc.top
                dy = idy

            g.draw_bitmap( image, ix, iy )
            self._hot_spot = ( x, y, dx, dy )
        else:
            self._hot_spot = ( 0, 0, 0, 0 )


    def set_hot_spot ( self ):
        """ Calculate the bounds of the splitter's 'hot spot' (i.e. the open and
            close icons.
        """
        self._hot_spot = ( 0, 0, 0, 0 )
        if self.theme.splitter_open_close:
            x, y, dx, dy = self.bounds
            _, idx, idy  = self.theme.images.get_splitter_image( self.state )
            if self.style == 'horizontal':
                dx = idx
            else:
                dy = idy

            self._hot_spot = ( x, y, dx, dy )


    def get_cursor ( self, event ):
        """ Gets the cursor to use when the mouse is over the splitter bar.
        """
        if (self._hot_spot is None) or self.is_in( event, *self._hot_spot ):
            return 'arrow'

        if self.style == 'horizontal':
            return 'sizens'

        return 'sizeew'


    def get_structure ( self ):
        """ Returns a copy of the splitter 'structure', minus the actual
            content.
        """
        return self.clone_facets( [ '_last_bounds' ] )


    def mouse_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        self._live_drag     = (not event.control_down)
        self._click_pending = self.is_in( event, *self._hot_spot )
        if not self._click_pending:
            self._xy           = ( event.x, event.y )
            self._max_bounds   = self.parent.get_splitter_bounds( self )
            self._first_bounds = self.bounds
            self.index         = self.parent.splitters.index( self )
            if not self._live_drag:
                self._draw_bounds( event, self.bounds )


    def mouse_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._click_pending:
            hx, hy, hdx, hdy = self._hot_spot
            if not self.is_in( event, hx, hy, hdx, hdy ):
                return

            is_horizontal = (self.style == 'horizontal')
            x, y, dx, dy  = self.bounds
            if self._last_bounds is not None:
                if is_horizontal:
                    y = self._last_bounds[1]
                else:
                    x = self._last_bounds[0]

            state                = self.state
            contents             = self.parent.visible_contents
            ix1, iy1, idx1, idy1 = contents[ self.index ].bounds
            ix2, iy2, idx2, idy2 = contents[ self.index + 1 ].bounds
            if is_horizontal:
                if state != SPLIT_HMIDDLE:
                    if ((y == self.bounds[1]) or
                        (y < iy1)             or
                        ((y + dy) > (iy2 + idy2))):
                        y = (iy1 + iy2 + idy2 - dy) / 2
                else:
                    self._last_bounds = self.bounds
                    if event.x < (hx + (hdx / 2)):
                        y = iy1
                    else:
                        y = iy2 + idy2 - dy
            elif state != SPLIT_VMIDDLE:
                if ((x == self.bounds[0]) or
                    (x < ix1)             or
                    ((x + dx) > (ix2 + idx2))):
                    x = (ix1 + ix2 + idx2 - dx) / 2
            else:
                self._last_bounds = self.bounds
                if event.y < (hy + (hdy / 2)):
                    x = ix2 + idx2 - dx
                else:
                    x = ix1
            self.bounds = ( x, y, dx, dy )
        else:
            self._last_bounds, self._first_bounds = self._first_bounds, None
            if not self._live_drag:
                self._draw_bounds( event )

        self.parent.update_splitter( self, event.control )


    def mouse_move ( self, event ):
        """ Handles the mouse moving while the left mouse button is pressed.
        """
        if not self._click_pending:
            x, y, dx, dy     = self._first_bounds
            mx, my, mdx, mdy = self._max_bounds

            if self.style == 'horizontal':
                y = y + event.y - self._xy[1]
                y = min( max( y, my ), my + mdy - dy )
            else:
                x = x + event.x - self._xy[0]
                x = min( max( x, mx ), mx + mdx - dx )

            bounds = ( x, y, dx, dy )
            if bounds != self.bounds:
                self.bounds = bounds
                if self._live_drag:
                    self.parent.update_splitter( self, event.control )
                else:
                    self._draw_bounds( event, bounds )


    def hover_enter ( self ):
        """ Handles the mouse hovering over the item.
        """
        pass


    def hover_exit ( self ):
        """ Handles the mouse exiting from hovering over the item.
        """
        pass


    def _draw_bounds ( self, event, bounds = None ):
        """ Draws the splitter bar in a new position while it is being dragged.
        """
        # Set up the drawing environment:
        window        = event.control
        g, x0, y0     = window.screen_graphics
        g.xor_mode    = True
        g.pen         = None
        g.brush       = DragColor
        is_horizontal = (self.style == 'horizontal')
        nx = ox       = None

        # Draw the new bounds (if any):
        if bounds is not None:
            ax = ay = adx = ady = 0
            nx, ny, ndx, ndy = bounds
            if is_horizontal:
                ady = (ndy - 6)
                ay  = ady / 2
            else:
                adx = (ndx - 6)
                ax  = adx / 2
            nx  += ax
            ny  += ay
            ndx -= adx
            ndy -= ady

        if self._bounds is not None:
            ax = ay = adx = ady = 0
            ox, oy, odx, ody = self._bounds
            if is_horizontal:
                ady = (ody - 6)
                ay  = ady / 2
            else:
                adx = (odx - 6)
                ax  = adx / 2

            ox  += ax
            oy  += ay
            odx -= adx
            ody -= ady

        if nx is not None:
            tx, ty, tdx, tdy = nx, ny, ndx, ndy
            if ox is not None:
                if is_horizontal:
                    yoy = oy - ty
                    if 0 <= yoy < tdy:
                        tdy = yoy
                    elif -ody < yoy <= 0:
                        ty  = oy + ody
                        tdy = tdy - ody - yoy
                else:
                    xox = ox - tx
                    if 0 <= xox < tdx:
                        tdx = xox
                    elif -odx < xox <= 0:
                        tx  = ox + odx
                        tdx = tdx - odx - xox

            g.draw_rectangle( tx + x0, ty + y0, tdx, tdy )

        # Erase the old bounds (if any):
        if ox is not None:
            if nx is not None:
                if is_horizontal:
                    yoy = ny - oy
                    if 0 <= yoy < ody:
                        ody = yoy
                    elif -ndy < yoy <= 0:
                        oy  = ny + ndy
                        ody = ody - ndy - yoy
                else:
                    xox = nx - ox
                    if 0 <= xox < odx:
                        odx = xox
                    elif -ndx < xox <= 0:
                        ox  = nx + ndx
                        odx = odx - ndx - xox

            g.draw_rectangle( ox + x0, oy + y0, odx, ody )

        # Save the new bounds for the next call:
        self._bounds = bounds

    #-- Property Implementations -----------------------------------------------

    def _get_state ( self ):
        contents             = self.parent.contents
        x, y, dx, dy         = self.bounds
        ix1, iy1, idx1, idy1 = contents[ self.index ].bounds
        ix2, iy2, idx2, idy2 = contents[ self.index + 1 ].bounds

        if self.style == 'horizontal':
            if y == iy1:
                return SPLIT_HTOP

            if (y + dy) == (iy2 + idy2):
                return SPLIT_HBOTTOM

            return SPLIT_HMIDDLE
        else:
            if x == ix1:
                return SPLIT_VLEFT

            if (x + dx) == (ix2 + idx2):
                return SPLIT_VRIGHT

            return SPLIT_VMIDDLE

#-- EOF ------------------------------------------------------------------------