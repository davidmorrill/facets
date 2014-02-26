"""
Defines an ImageControl control that is used by facet editors to display facet
values iconically.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Event, Bool, Tuple, Float, Range, on_facet_set

from facets.ui.ui_facets \
    import Image

from themed_window \
    import ThemedWindow

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The pen colors used to draw the image border:
Pens = ( ( 255, 255, 255 ), ( 112, 112, 112 ) )

#-------------------------------------------------------------------------------
#  'ImageControl' class:
#-------------------------------------------------------------------------------

class ImageControl ( ThemedWindow ):
    """ A control that displays an image which can be selected or unselected by
        mouse clicks.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The image to display in the control:
    image = Image

    # Can the control be selected?
    selectable = Bool( False )

    # The amount of padding to draw around the image:
    padding = Range( 0, 50, 10 )

    # Event fired when the control is clicked:
    clicked = Event

    # The current selection state of the control:
    selected = Bool( False )

    # Should images automatically be scaled to fit the control size?
    auto_scale = Bool( True, facet_value = True )

    # Can the user zoom the image?
    user_zoom = Bool( False, facet_value = True )

    #-- Private Facet Definitions ----------------------------------------------

    # Has the user zoomed the image?
    user_zoomed = Bool( False )

    # The current image scaling factor:
    scale = Float( 1.0 )

    # The origin of the scaled image relative to the control:
    origin = Tuple( Float, Float )

    # Is the mouse button currently being pressed:
    _button_down = Bool( False )

    # Is the mouse currently over the control:
    _mouse_over = Bool( False )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self, control ):
        """ Handles the underlying 'control' being created.
        """
        # Create a back link from the control to us:
        control._image_control = self

        if not self.auto_scale:
            # Make sure the control is sized correctly:
            dx, dy = self.image.width, self.image.height
            if self.theme is not None:
                tdx, tdy = self.theme.bounds()
                size     = ( dx + tdx, dy + tdy )
            else:
                size = ( dx + self.padding, dy + self.padding )

            control.min_size = control.size = size


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        control = self.control
        if self.selectable and (control is not None):
            if selected:
                for child in control.parent.children:
                    ic = getattr( child, '_image_control', None )
                    if (ic is not None) and ic.selected and (ic is not self):
                        ic.selected = False
                        break

            control.refresh()


    @on_facet_set( 'image, auto_scale' )
    def _image_modified ( self ):
        """ Handles the 'image' or 'auto_scale' facet being changed.
        """
        self._draw_image = None
        self.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def enter ( self, event ):
        """ Handles the mouse entering the control.
        """
        if self.selectable:
            self._mouse_over = True
            self.refresh()


    def leave ( self, event ):
        """ Handles the mouse leaving the control.
        """
        if self._mouse_over:
            self._mouse_over = False
            self.refresh()


    def left_down ( self, event ):
        """ Handles the user pressing the mouse button.
        """
        if self.selectable:
            self.control.mouse_capture = self._button_down = True
            self.refresh()


    def left_up ( self, event ):
        """ Handles the user clicking the control.
        """
        control      = self.control
        need_refresh = self._button_down
        if need_refresh:
            control.mouse_capture = self._button_down = False

        if self.selectable:
            wdx, wdy = control.client_size
            x, y     = event.x, event.y
            if (0 <= x < wdx) and (0 <= y < wdy):
                if not self.selected:
                    self.selected = True
                elif need_refresh:
                    self.refresh()

                self.clicked = True

                return

        if need_refresh:
            self.refresh()


    def wheel ( self, event ):
        """ Handles the mouse wheel rotating.
        """
        if self.user_zoom:
            delta, scale = event.wheel_change, self.scale
            divisor      = 50.0 if event.control_down else 5.0
            new_scale    = max( scale * (1.0 + (delta / divisor)), 0.1 )
            if new_scale != scale:
                x, y             = event.x, event.y
                ox, oy           = self.origin
                adjust           = new_scale / scale
                self.origin      = ( x - (adjust * (x - ox)),
                                     y - (adjust * (y - oy)) )
                self.scale       = new_scale
                self.user_zoomed = True
                self.refresh()


    def paint ( self, g ):
        """ Handles the control being re-painted.
        """
        global Pens

        bd       = self._button_down
        wx = wy  = 0
        wdx, wdy = self.control.client_size
        if self.theme is not None:
            wx, wy, wdx, wdy = self.theme.bounds( wx, wx, wdx, wdy )

        draw_image = image = self.image
        if (image is not None) and (wdx > 0) and (wdy > 0):
            idx, idy = image.width, image.height
            if self.user_zoomed:
                ox, oy = self.origin
                ox, oy = int( round( ox ) ), int( round( oy ) )
                scale  = self.scale
                if scale != self._scale:
                    pdx      = int( round( scale * idx ) )
                    pdy      = int( round( scale * idy ) )
                    oxr, oyb = ox + pdx, oy + pdy
                    wxr, wyb = wx + wdx, wy + wdy
                    if (ox < wx) or (oy < wy) or (oxr > wxr) or (oyb > wyb):
                        cx  = max( 0, int( round( (wx - ox) / scale ) ) )
                        cy  = max( 0, int( round( (wy - oy) / scale ) ) )
                        cdx = max( 0, int( (oxr - wxr) / scale ) )
                        cdy = max( 0, int( (oyb - wyb) / scale ) )
                        if cx > 0: ox = wx
                        if cy > 0: oy = wy
                        image        = image.crop( cx, cy,
                                             idx - cx - cdx, idy - cy - cdy )

                    self._scale      = scale
                    self._origin     = ( ox, oy )
                    self._draw_image = draw_image = image.scale( scale )
                elif self._draw_image is not None:
                    draw_image = self._draw_image
                    ox, oy     = self._origin

                g.draw_bitmap( draw_image.bitmap, ox, oy )
            else:
                if ((idx > wdx) or
                    (idy > wdy) or
                    (self.auto_scale and ((idx != wdx) or (idy != wdy)))):
                    rdx, rdy = float( wdx ) / idx, float( wdy ) / idy
                    if rdx <= rdy:
                        scale    = rdx
                        ddx, ddy = wdx, int( round( scale * idy ) )
                    else:
                        scale    = rdy
                        ddx, ddy = int( round( scale * idx ) ), wdy

                    draw_image = self._draw_image
                    idx, idy   = ddx, ddy
                    if (draw_image is None) or (ddx != draw_image.width):
                        self.scale       = scale
                        self._draw_image = draw_image = \
                            image.scale( ( ddx, ddy ) )
                else:
                    self._draw_image = None

                ox, oy      = wx + (wdx - idx) / 2, wy + (wdy - idy) / 2
                self.origin = ( ox, oy )
                g.draw_bitmap( draw_image.bitmap, ox, oy )

        wxdx = wx + wdx
        wydy = wy + wdy

        if self._mouse_over:
            g.brush = None
            g.pen   = Pens[ bd ]
            g.draw_line( wx, wy, wxdx, wy )
            g.draw_line( wx, wy + 1, wx, wydy )
            g.pen = Pens[ 1 - bd ]
            g.draw_line( wxdx - 1, wy + 1, wxdx - 1, wydy )
            g.draw_line( wx + 1, wydy - 1, wxdx - 1, wydy - 1 )

        if self.selected is True:
            g.brush = None
            g.pen   = Pens[ bd ]
            g.draw_line( wx + 1, wy + 1, wxdx - 1, wy + 1 )
            g.draw_line( wx + 1, wy + 1, wx + 1, wydy - 1 )
            g.draw_line( wx + 2, wy + 2, wxdx - 2, wy + 2 )
            g.draw_line( wx + 2, wy + 2, wx + 2, wydy - 2 )
            g.pen = Pens[ 1 - bd ]
            g.draw_line( wxdx - 2, wy + 2, wxdx - 2, wydy - 1 )
            g.draw_line( wx + 2, wydy - 2, wxdx - 2, wydy - 2 )
            g.draw_line( wxdx - 3, wy + 3, wxdx - 3, wydy - 2 )
            g.draw_line( wx + 3, wydy - 3, wxdx - 3, wydy - 3 )

#-- EOF ------------------------------------------------------------------------