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
    import Event, Bool, Range, on_facet_set

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

    # The current selection state of the control:
    selected = Bool( False )

    # The amount of padding to draw around the image:
    padding = Range( 0, 50, 10 )

    # Should images automatically be scaled to fit the control size?
    auto_scale = Bool( True, facet_value = True )

    # Event fired when the control is clicked:
    clicked = Event

    #-- Private Facet Definitions ----------------------------------------------

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
        if self.control is not None:
            self.control.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def enter ( self, event ):
        """ Handles the mouse entering the control.
        """
        if self.selectable:
            self._mouse_over = True
            self.control.refresh()


    def leave ( self, event ):
        """ Handles the mouse leaving the control.
        """
        if self._mouse_over:
            self._mouse_over = False
            self.control.refresh()


    def left_down ( self, event ):
        """ Handles the user pressing the mouse button.
        """
        if self.selectable:
            self.control.mouse_capture = self._button_down = True
            self.control.refresh()


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
                    control.refresh()

                self.clicked = True

                return

        if need_refresh:
            control.refresh()


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
        if image is not None:
            idx, idy   = image.width, image.height
            if (wdx > 0) and (wdy > 0):
                if ((idx > wdx) or
                    (idy > wdy) or
                    (self.auto_scale and ((idx != wdx) or (idy != wdy)))):
                    rdx, rdy = float( idx ) / wdx, float( idy ) / wdy
                    if rdx >= rdy:
                        ddx, ddy = wdx, int( round( idy / rdx ) )
                    else:
                        ddx, ddy = int( round( idx / rdy ) ), wdy

                    draw_image = self._draw_image
                    idx, idy   = ddx, ddy
                    if (draw_image is None) or (ddx != draw_image.width):
                        self._draw_image = draw_image = \
                            image.scale( ( ddx, ddy ) )
                else:
                    self._draw_image = None

                g.draw_bitmap( draw_image.bitmap,
                               wx + (wdx - idx) / 2, wy + (wdy - idy) / 2 )

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