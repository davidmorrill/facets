"""
A GUI toolkit independent image and text-based control that can be used as a
normal, radio or toolbar button.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Int, Str, Range, Enum, Instance, Event, Bool, \
           Image, Control, toolkit

from facets.ui.pyface.image_slice \
    import paint_parent

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Text color used when a button is disabled:
DisabledTextColor = ( 128, 128, 128 )

#-------------------------------------------------------------------------------
#  'ImageButton' class:
#-------------------------------------------------------------------------------

class ImageButton ( HasPrivateFacets ):
    """ An image and text-based control that can be used as a normal, radio or
        toolbar button.
    """

    #-- Class Constants --------------------------------------------------------

    # Pens (light, dark) used to draw the 'selection' marker:
    pens = ( ( 192, 192, 192 ), ( 80, 80, 80 ) )

    #-- Facet Definitions ------------------------------------------------------

    # The GUI toolkit neutral control associated with this widget:
    control = Instance( Control )

    # The image:
    image = Image

    # The maximum size of the image to display (0 = No maximum):
    image_size = Int

    # The (optional) label:
    label = Str

    # Extra padding to add to both the left and right sides:
    width_padding = Range( 0, 31, 7 )

    # Extra padding to add to both the top and bottom sides:
    height_padding = Range( 0, 31, 5 )

    # Presentation style:
    style = Enum( 'button', 'radio', 'toolbar', 'checkbox' )

    # Orientation of the text relative to the image:
    orientation = Enum( 'vertical', 'horizontal' )

    # Is the control selected ('radio' or 'checkbox' style)?
    selected = Bool( False )

    # Fired when a 'button' or 'toolbar' style control is clicked:
    clicked = Event

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, parent, **facets ):
        """ Creates a new image control.
        """
        super( ImageButton, self ).__init__( **facets )

        # Calculate the size of the button:
        idx   = idy = tdx = tdy = 0
        image = self.image
        if image is not None:
            idx, idy, size = image.width, image.height, self.image_size
            if size > 0:
                idx_dy = max( idx, idy )
                if size != idx_dy:
                    self.image = image = image.scale( size / float( idx_dy ) )
                    idx, idy   = image.width, image.height

        self.control = control = toolkit().create_control( parent )

        if self.label != '':
            tdx, tdy = control.text_size( self.label )

        wp2 = self.width_padding  + 2
        hp2 = self.height_padding + 2

        if self.orientation == 'horizontal':
            self._ix = wp2
            spacing  = (idx > 0) * (tdx > 0) * 4
            self._tx = self._ix + idx + spacing
            dx       = idx + tdx + spacing
            dy       = max( idy, tdy )
            self._iy = hp2 + ((dy - idy) / 2)
            self._ty = hp2 + ((dy - tdy) / 2)
        else:
            self._iy = hp2
            spacing  = (idy > 0) * (tdy > 0) * 2
            self._ty = self._iy + idy + spacing
            dx       = max( idx, tdx )
            dy       = idy + tdy + spacing
            self._ix = wp2 + ((dx - idx) / 2)
            self._tx = wp2 + ((dx - tdx) / 2)

        # Finish initializing the control:
        self._dx            = dx + wp2 + wp2
        self._dy            = dy + hp2 + hp2
        control.size        = control.min_size = ( self._dx, self._dy )
        self.control._owner = self
        self._mouse_over    = self._button_down = False

        # Set up mouse event handlers:
        control.set_event_handler(
            enter     = self._on_enter_window,
            leave     = self._on_leave_window,
            left_down = self._on_left_down,
            left_up   = self._on_left_up,
            paint     = self._on_paint
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _image_set ( self, image ):
        """ Handles the 'image' facet being changed.
        """
        if self.control is not None:
            self.control.refresh()


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if selected and (self.style == 'radio'):
            for control in self.control.parent.children:
                owner = getattr( control, '_owner', None )
                if (isinstance( owner, ImageButton ) and owner.selected and
                    (owner is not self)):
                    owner.selected = False
                    break

        self.control.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def _on_enter_window ( self, event ):
        """ Called when the mouse enters the widget.
        """
        if self.style != 'button':
            self._mouse_over = True
            self.control.refresh()


    def _on_leave_window ( self, event ):
        """ Called when the mouse leaves the widget.
        """
        if self._mouse_over:
            self._mouse_over = False
            self.control.refresh()


    def _on_left_down ( self, event ):
        """ Called when the left mouse button goes down on the widget.
        """
        self._button_down = True
        self.control.mouse_capture = True
        self.control.refresh()


    def _on_left_up ( self, event ):
        """ Called when the left mouse button goes up on the widget.
        """
        control               = self.control
        control.mouse_capture = False
        self._button_down     = False
        wdx, wdy              = control.client_size
        x, y                  = event.x, event.y
        control.refresh()

        if (0 <= x < wdx) and (0 <= y < wdy):
            if self.style == 'radio':
                self.selected = True
            elif self.style == 'checkbox':
                self.selected = not self.selected
            else:
                self.clicked = True


    def _on_paint ( self, event ):
        """ Called when the widget needs repainting.
        """
        control  = self.control
        g        = control.graphics.graphics_buffer()
        paint_parent( g, control )

        wdx, wdy = control.client_size
        ox       = (wdx - self._dx) / 2
        oy       = (wdy - self._dy) / 2
        bd       = self._button_down
        style    = self.style

        disabled = (not control.enabled)
        image    = self.image
        if image is not None:
            bitmap = image.bitmap
            if disabled:
                bitmap = image.mono_bitmap

            g.draw_bitmap( bitmap, ox + self._ix, oy + self._iy )

        if self.label != '':
            if disabled:
                g.text_color = DisabledTextColor

            if bd and (style == 'button') and (not disabled):
                ox += 1
                oy += 1

            g.draw_text( self.label, ox + self._tx, oy + self._ty )

        pens  = self.pens
        is_rc = (style in ( 'radio', 'checkbox' ))
        if bd or (style == 'button') or (is_rc and self.selected):
            if is_rc:
                bd = 1 - bd

            g.brush = None
            g.pen   = pens[ bd ]
            g.draw_line( 1, 1, wdx - 1, 1 )
            g.draw_line( 1, 1, 1, wdy - 1 )
            g.draw_line( 2, 2, wdx - 2, 2 )
            g.draw_line( 2, 2, 2, wdy - 2 )
            g.pen = pens[ 1 - bd ]
            g.draw_line( wdx - 2, 2, wdx - 2, wdy - 1 )
            g.draw_line( 2, wdy - 2, wdx - 2, wdy - 2 )
            g.draw_line( wdx - 3, 3, wdx - 3, wdy - 2 )
            g.draw_line( 3, wdy - 3, wdx - 3, wdy - 3 )

        elif self._mouse_over and (not self.selected):
            g.brush = None
            g.pen   = pens[ bd ]
            g.draw_line( 0, 0, wdx, 0 )
            g.draw_line( 0, 1, 0, wdy )
            g.pen = pens[ 1 - bd ]
            g.draw_line( wdx - 1, 1, wdx - 1, wdy )
            g.draw_line( 1, wdy - 1, wdx - 1, wdy - 1 )

        g.copy()

#-- EOF ------------------------------------------------------------------------