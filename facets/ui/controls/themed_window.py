"""
Defines a GUI toolkit independent ThemedWindow base class for creating themed
windows.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, HasFacets, Instance, Str, Enum, Bool, Any, \
           Image, Property, DelegatesTo, Control, ATheme, toolkit

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# GUI toolkit independent colors:
RED = ( 255, 0, 0 )

# The set of events which have no associated (x,y) data:
NoXYData = { 'enter', 'leave' }

# An empty set of bounds:
EmptyBounds = ( 0, 0, 0, 0 )

#-------------------------------------------------------------------------------
#  'ThemedWindow' class:
#-------------------------------------------------------------------------------

class ThemedWindow ( HasPrivateFacets ):

    #-- Public Facets ----------------------------------------------------------

    # The theme associated with this window:
    theme = ATheme

    # Should the user be able to 'tab' into this control?
    tab_stop = Bool( False )

    # Does this control handle keyboard input?
    handle_keys = Bool( False )

    # The label to display in the theme's label area:
    label = Str

    # The image to display in the theme's label area:
    label_image = Image

    # The parent of the control:
    parent = Instance( Control )

    # The underlying control:
    control = Instance( Control )

    # The layout manager associated with this window:
    layout = Any

    # The default alignment to use:
    default_alignment = Enum( 'left', 'center', 'right' )

    # The current mouse event state:
    state = Str( 'normal' )

    # Optional controller used for overriding event handling:
    controller = Instance( HasFacets )

    # The bounds that the 'paint' method should use for drawing content:
    content_bounds = Property

    # The bounds that the 'paint' method should use for drawing labels:
    label_bounds = Property

    # Should debugging information be overlaid on the theme?
    debug = Bool( False )

    # Do we have the mouse capture?
    mouse_capture = DelegatesTo( 'control' )

    #-- Public Methods ---------------------------------------------------------

    def __call__ ( self ):
        """ Returns the GUI toolkit neutral 'control' associated with this
            control. If the control has not been created yet, it will be
            created.
        """
        if self.control is None:
            self.control = self.create_control()

        return self.control


    def create_control ( self ):
        """ Creates and returns the underlying toolkit neutral control used to
            implement the window.
        """
        control = toolkit().create_control( self.parent,
            tab_stop    = self.tab_stop,
            handle_keys = self.handle_keys
        )
        control.set_event_handler(
            paint         = self._paint,
            size          = self.resize,
            left_down     = self._left_down,
            left_up       = self._left_up,
            left_dclick   = self._left_dclick,
            middle_down   = self._middle_down,
            middle_up     = self._middle_up,
            middle_dclick = self._middle_dclick,
            right_down    = self._right_down,
            right_up      = self._right_up,
            right_dclick  = self._right_dclick,
            motion        = self._motion,
            enter         = self._enter,
            leave         = self._leave,
            wheel         = self._wheel
        )
        control.drop_target = self

        return control


    def paint_all ( self, g ):
        """ Paints the entire contents of the control into the graphics context
            specified by *g*.
        """
        self.paint_bg( g )
        self.paint( g )


    def paint_bg ( self, g ):
        """ Paints the background into the supplied graphics object using the
            associated ImageSlice object and returns the image slice used (if
            any).
        """
        from facets.ui.pyface.image_slice import paint_parent

        # Repaint the parent's theme (if necessary):
        paint_parent( g, self.control )

        # Draw the background theme (if any):
        theme = self.theme
        if theme is not None:
            wdx, wdy = self.control.client_size
            theme.fill( g, 0, 0, wdx, wdy )
            if self.debug:
                slice   = theme.image_slice
                g.pen   = RED
                g.brush = None
                border  = theme.border
                g.draw_rectangle( border.left, border.top,
                                  wdx - border.right  - border.left,
                                  wdy - border.bottom - border.top )
                g.draw_rectangle( border.left + 3, border.top + 3,
                                  wdx - border.right  - border.left - 6,
                                  wdy - border.bottom - border.top  - 6 )
                content = theme.content
                x = slice.xleft + content.left
                y = slice.xtop  + content.top
                g.draw_rectangle( x - 1, y - 1,
                       wdx - slice.xright  - content.right  - x + 2,
                       wdy - slice.xbottom - content.bottom - y + 2 )

                label = theme.label
                if slice.xtop >= slice.xbottom:
                    y, dy = 0, slice.xtop
                else:
                    y, dy = wdy - slice.xbottom, slice.xbottom

                if dy >= 13:
                    x  = slice.xleft + label.left
                    y += label.top
                    g.draw_rectangle( x - 1, y - 1,
                        wdx - slice.xright - label.right - x + 2,
                        dy - label.bottom - label.top + 2 )


    def paint ( self, g ):
        """ Paints the foreground of the window into the supplied device
            context. Note that only the regions defined by *content_bounds* and
            *label_bounds* should be painted into. Areas outside of these
            regions are part of the control's "theme".

            Can be overridden by a subclass.
        """
        theme = self.theme
        if (theme is not None) and theme.has_label:
            g.clipping_bounds = self.label_bounds
            self.paint_label( g )

        g.clipping_bounds = self.content_bounds
        self.paint_content( g )


    def paint_content ( self, g ):
        """ Paints the content of the window into the device context specified
            by *g*.

            Should be overridden by a subclass.
        """
        pass


    def paint_label ( self, g ):
        """ Paints the label of the window into the supplied device
            context.

            Can be overridden by a subclass.
        """
        label = self.label
        if label != '':
            dx, dy = self.control.client_size
            g.font = self.theme.label_font
            self.theme.draw_label( g, label, None, 0, 0, dx, dy,
                                   self.label_image )


    def dispose ( self ):
        """ Disposes of the control by removing its event handlers.
        """
        control               = self.control
        control.mouse_capture = False
        control.unset_event_handler(
            paint         = self._paint,
            size          = self.resize,
            left_down     = self._left_down,
            left_up       = self._left_up,
            left_dclick   = self._left_dclick,
            middle_down   = self._middle_down,
            middle_up     = self._middle_up,
            middle_dclick = self._middle_dclick,
            right_down    = self._right_down,
            right_up      = self._right_up,
            right_dclick  = self._right_dclick,
            motion        = self._motion,
            enter         = self._enter,
            leave         = self._leave,
            wheel         = self._wheel
        )
        control.drop_target = None


    def in_control ( self, x, y = None ):
        """ Returns whether a specified (x,y) coordinate is inside the control
            or not. If *y* is **None**, then *x* is assumed to be an event.
        """
        wdx, wdy = self.control.client_size
        if y is None:
            x, y = x.x, x.y

        return ((0 <= x < wdx) and (0 <= y < wdy))


    def refresh ( self, x = None, y = None, dx = None, dy = None ):
        """ Refreshes the contents of the control.
        """
        if self.control is not None:
            self.control.refresh( x, y, dx, dy )


    def update ( self ):
        """ Updates the control by laying out its contents and refreshing it on
            the display.
        """
        if self.control is not None:
            self.control.update()

    #-- Property Implementations -----------------------------------------------

    def _get_content_bounds ( self ):
        wdx, wdy = self.control.client_size
        theme    = self.theme
        if theme is not None:
            slice = theme.image_slice
            if slice is not None:
                content = theme.content
                x       = slice.xleft + content.left
                y       = slice.xtop  + content.top

                return ( x, y,
                         max( 0, wdx - slice.xright  - content.right  - x ),
                         max( 0, wdy - slice.xbottom - content.bottom - y ) )

        return ( 0, 0, wdx, wdy )


    def _get_label_bounds ( self ):
        wdx, wdy = self.control.client_size
        theme    = self.theme
        if theme is not None:
            slice = theme.image_slice
            if slice is not None:
                label = theme.label
                if slice.xtop >= slice.xbottom:
                    y, dy = 0, slice.xtop
                else:
                    y, dy = wdy - slice.xbottom, slice.xbottom

                if dy >= 13:
                    x  = slice.xleft + label.left
                    y += label.top

                    return ( x, y,
                             max( 0, wdx - slice.xright - label.right - x ),
                             max( 0, dy - label.bottom - label.top ) )

        return EmptyBounds

    #-- Facet Event Handlers ---------------------------------------------------

    def _theme_set ( self ):
        """ Handles the 'theme' facet being changed.
        """
        self.refresh()


    def _layout_set ( self, layout ):
        """ Handles the 'layout' facet being changed.
        """
        if layout is None:
            self.control.layout = None
        else:
            self.control.layout = toolkit().layout_adapter_for( layout )

    #-- Window Event Handlers --------------------------------------------------

    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        g = self.control.graphics.graphics_buffer()
        self.paint_all( g )
        g.copy()


    def resize ( self, event ):
        """ Handles the control being resized.
        """
        self.control.update()


    def _left_down ( self, event ):
        """ Handles a left mouse button down event.
        """
        self.control.set_focus()
        self.mouse_capture = True
        self._mouse_event( 'left_down', event )


    def _left_up ( self, event ):
        """ Handles a left mouse button up event.
        """
        self.mouse_capture = False
        self._mouse_event( 'left_up', event )


    def _left_dclick ( self, event ):
        """ Handles a left mouse button double click event.
        """
        self.mouse_capture = True
        self._mouse_event( 'left_dclick', event )


    def _middle_down ( self, event ):
        """ Handles a middle mouse button down event.
        """
        self.mouse_capture = True
        self._mouse_event( 'middle_down', event )


    def _middle_up ( self, event ):
        """ Handles a middle mouse button up event.
        """
        self.mouse_capture = False
        self._mouse_event( 'middle_up', event )


    def _middle_dclick ( self, event ):
        """ Handles a middle mouse button double click event.
        """
        self.mouse_capture = True
        self._mouse_event( 'middle_dclick', event )


    def _right_down ( self, event ):
        """ Handles a right mouse button down event.
        """
        self.mouse_capture = True
        self._mouse_event( 'right_down', event )


    def _right_up ( self, event ):
        """ Handles a right mouse button up event.
        """
        self.mouse_capture = False
        self._mouse_event( 'right_up', event )


    def _right_dclick ( self, event ):
        """ Handles a right mouse button double click event.
        """
        self.mouse_capture = True
        self._mouse_event( 'right_dclick', event )


    def _motion ( self, event ):
        """ Handles a mouse move event.
        """
        self._mouse_event( 'motion', event )


    def _enter ( self, event ):
        """ Handles the mouse entering the window event.
        """
        # Some GUI toolkits only route mouse wheel events to the control if it
        # has focus, so if there is a handler for 'wheel' events, make sure that
        # the control has focus when the mouse enters it:
        if self._check_mouse_event( 'wheel' ) is not None:
            self.control.set_mouse_focus()

        self._mouse_event( 'enter', event )


    def _leave ( self, event ):
        """ Handles the mouse leaving the window event.
        """
        self._mouse_event( 'leave', event )


    def _wheel ( self, event ):
        """ Handles a mouse wheel event.
        """
        self._mouse_event( 'wheel', event )

    #-- Drag and Drop Event Handlers -------------------------------------------

    def drag_leave ( self, event ):
        """ Handles a drag 'leave' event.
        """

    def drag_move ( self, event ):
        """ Handles a drag 'move' event.
        """

    def drag_drop ( self, event ):
        """ Handles a drag 'drop' event.
        """

    #-- Private Methods --------------------------------------------------------

    def _handler_for ( self, object, state, name ):
        """ Returns the method (if any) corresponding to the specified *state*
            and event *name* defined on the specified *object*.
        """
        method = getattr( object, '%s_%s' % ( state, name ), None )
        if method is None:
            method = getattr( object, name, None )
            if method is None:
                method = getattr( object, state + '_mouse', None )
                if method is None:
                    method = getattr( object, 'mouse', None )

        return method


    def _check_mouse_event ( self, name ):
        """ Returns the handler method (if any) associated with a specified
            mouse event.
        """
        controller = self.controller
        method     = (None if controller is None else
                      self._handler_for( controller,
                          getattr( controller, 'state', self.state ), name ))

        if method is None:
            method = self._handler_for( self, self.state, name )

        return method


    def _mouse_event ( self, name, event ):
        """ Routes a mouse event to the proper handler (if any).
        """
        self._route_event( self._check_mouse_event( name ), event )


    def _route_event ( self, handler, event ):
        """ Routes an *event* to the specified *handler* (if any).
        """
        if handler is not None:
            args = handler.im_func.func_code.co_argcount - 1
            if args == 1:
                handler( event )
            else:
                x = y = 0
                if event.name not in NoXYData:
                    x, y = event.x, event.y

                handler( *( ( x, y, event )[ : args ]) )

#-- EOF ------------------------------------------------------------------------