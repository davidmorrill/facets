"""
Facets UI simple, themed slider-based integer or float value editor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
   import log10, pow

from facets.api \
    import Range, Str, Float, Bool, Color, FacetError, BasicEditorFactory, \
           toolkit

from facets.ui.colors \
    import ErrorColor

from facets.ui.ui_facets \
    import HorizontalAlignment

from facets.ui.pyface.timer.api \
    import do_after

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

ResettableFloat = Float( event = 'reset' )

#-------------------------------------------------------------------------------
#  '_ThemedSliderEditor' class:
#-------------------------------------------------------------------------------

class _ThemedSliderEditor ( Editor ):
    """ Facets UI simple, themed slider-based integer or float value editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The low end of the slider range:
    low = ResettableFloat

    # The high end of the slider range:
    high = ResettableFloat

    # The smallest allowed increment:
    increment = ResettableFloat

    # The current text being displayed:
    text = Str

    #-- Method Definitions -----------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Establish the range of the slider:
        low, high, increment = factory.low, factory.high, factory.increment
        if high <= low:
            low = high = None
            range      = self.object.facet( self.name ).handler
            if isinstance( range, Range ):
                low, high = range._low, range._high

            if low is None:
                if high is None:
                    high = 1.0
                low = high - 1.0
            elif high is None:
                high = low + 1.0

        # Establish the slider increment:
        if increment <= 0.0:
            if isinstance( low, int ):
                increment = 1.0
            else:
                increment = pow( 10, int( log10( ( high - low ) / 1000.0 ) ) )

        # Save the values we calculated:
        self.set( low = low, high = high, increment = increment )

        # Synchronize with any dynamically specified range values:
        self.sync_value( factory.low_name,       'low',       'from' )
        self.sync_value( factory.high_name,      'high',      'from' )
        self.sync_value( factory.increment_name, 'increment', 'from' )

        # Create the control:
        self.adapter = control = toolkit().create_control( parent,
                                                           tab_stop = True )
        control.min_size = ( 30, 20 )

        # Set up the event handlers:
        control.set_event_handler(
            paint     = self._on_paint,
            get_focus = self._set_focus,
            left_down = self._left_down,
            left_up   = self._left_up,
            motion    = self._motion,
            wheel     = self._mouse_wheel,
            enter     = self._enter_window,
            leave     = self._leave_window,
            size      = self._resize
        )

        # Set the tooltip:
        if not self.set_tooltip():
            self._set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.adapter.unset_event_handler(
            paint     = self._on_paint,
            get_focus = self._set_focus,
            left_down = self._left_down,
            left_up   = self._left_up,
            motion    = self._motion,
            wheel     = self._mouse_wheel,
            enter     = self._enter_window,
            leave     = self._leave_window,
            size      = self._resize
        )

        if self._text is not None:
            self._text.unset_event_handler(
                text_enter = self._text_completed,
                lose_focus = self._text_completed,
                enter      = self._enter_text,
                leave      = self._leave_text,
                key        = self._key_entered
            )

        super( _ThemedSliderEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.text       = self.string_value( self.value, lambda v: '%g' % v )
        self._text_size = None
        self.adapter.refresh()

        if self._text is not None:
            self._text.value = self.text


    def update_object ( self, value ):
        """ Updates the object when the control slider value changes.
        """
        try:
            self.value = value
        except FacetError:
            self.value = int( value )

        self.update_editor()


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        pass

    #-- Private Methods --------------------------------------------------------

    def _set_tooltip ( self ):
        """ Sets the current tooltip value for the slider.
        """
        self.adapter.tooltip = '[%g..%g]' % ( self.low, self.high )


    def _get_text_bounds ( self ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy  = self._get_text_size()
        wdx, wdy  = self.adapter.client_size
        ty        = ((wdy - tdy) / 2) - 2
        alignment = self.factory.alignment
        if alignment == 'left':
            tx = 4
        elif alignment == 'center':
            tx = (wdx - tdx) / 2
        else:
            tx = wdx - tdx - 4

        return ( tx, ty, tdx, tdy )


    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        if self._text_size is None:
            self._text_size = self.adapter.text_size( self.text.strip() or 'M' )

        return self._text_size


    def _set_slider_position ( self, x ):
        """ Calculates a new slider value for a specified (x,y) coordinate.
        """
        wdx, wdy = self.adapter.size
        if 3 <= x < wdx:
            value = self.low + (((x - 3) * (self.high - self.low)) / (wdx - 4))
            increment = self.increment
            if increment > 0:
                value = round( value / increment ) * increment
            self.update_object( value )


    def _delayed_click ( self ):
        """ Handle a delayed click response.
        """
        if self._pending:
            self._pending = False
            self._set_slider_position( self._x )


    def _pop_up_text ( self ):
        """ Pop-up a text control to allow the user to enter a value using
            the keyboard.
        """
        control    = self.adapter
        self._text = text = toolkit().create_text_input( control(),
                                    align        = self.factory.alignment,
                                    handle_enter = True )
        text.size      = control.size
        text.value     = self.text
        text.selection = ( -1, -1 )
        text.set_focus()
        text.set_event_handler(
            text_enter = self._text_completed,
            lose_focus = self._text_completed,
            enter      = self._enter_text,
            leave      = self._leave_text,
            key        = self._key_entered
        )


    def _destroy_text ( self ):
        """ Destroys the current text control.
        """
        self._ignore_focus = self._in_text_window
        self._text.unset_event_handler(
            text_enter = self._text_completed,
            lose_focus = self._text_completed,
            enter      = self._enter_text,
            leave      = self._leave_text,
            key        = self._key_entered
        )
        self.adapter.destroy_children()
        self._text = None

    #--- Control Event Handlers ------------------------------------------------

    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control = self.adapter
        g       = control.graphics.graphics_buffer()

        # Draw the slider bar:
        wdx, wdy = control.client_size
        dx       = max( 0, min( wdx - 2,
                        int( round( ((wdx - 3) * (self.value - self.low)) /
                                                 (self.high - self.low)) ) ) )

        factory = self.factory
        if control.enabled:
            g.brush = factory.slider_color_
        else:
            g.brush = ( 240, 240, 240 )
        g.pen = None
        g.draw_rectangle( 0, 0, dx + 3, wdy )

        # Draw the rest of the background:
        g.brush = factory.bg_color_
        g.draw_rectangle( dx + 3, 0, wdx - dx - 3, wdy )

        # Draw the slider tip:
        if control.enabled:
            g.brush = factory.tip_color_
            g. draw_rectangle( dx, 0, 3, wdy )

        # Draw the current text value (if requested):
        if factory.show_value:
            g.text_background_color = None
            if control.enabled:
                g.text_color = factory.text_color_
            else:
                g.text_color = ( 160, 160, 160 )
            g.font           = control.font
            tx, ty, tdx, tdy = self._get_text_bounds()
            g.draw_text( self.text, tx, ty )

        # Copy the buffer to the display:
        g.copy()


    def _resize ( self, event ):
        """ Handles the control being resized.
        """
        if self._text is not None:
            self._text.size = self.adapter.size


    def _set_focus ( self, event ):
        """ Handle the control getting the keyboard focus.
        """
        if ((not self._ignore_focus) and
            (self._x is None)        and
            (self._text is None) ):
            self._pop_up_text()

        event.handled = False


    def _left_down ( self, event ):
        """ Handles the left mouse being pressed.
        """
        if self.adapter.enabled:
            self._x, self._y = event.x, event.y
            self._pending    = True
            self.adapter.mouse_capture = True
            do_after( 150, self._delayed_click )


    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            self.adapter.mouse_capture = False

        if self._pending:
            self._pop_up_text()

        self._x = self._y = self._pending = None


    def _motion ( self, event ):
        """ Handles the mouse moving.
        """
        if self._x is not None:
            x, y = event.x, event.y
            if self._pending:
                if (abs( x - self._x ) + abs( y - self._y )) < 3:
                    return

                self._pending = False

            self._set_slider_position( x )


    def _mouse_wheel ( self, event ):
        """ Handles the mouse wheel rotating.
        """
        if self.adapter.enabled and self._in_window:
            increment = event.wheel_change
            delta     = (self.high - self.low) / 100.0
            if isinstance( self.value, int ) and (abs( delta ) < 1):
                delta = int( abs( delta ) / delta )

            self.update_object( min( max( self.value + increment * delta,
                                          self.low ), self.high ) )


    def _enter_window ( self, event ):
        """ Handles the mouse pointer entering the control.
        """
        self._in_window = True

        if not self._ignore_focus:
            self._ignore_focus = True
            self.adapter.set_focus()

        self._ignore_focus = False


    def _leave_window ( self, event ):
        """ Handles the mouse pointer leaving the control.
        """
        self._in_window = False


    def _update_value ( self, event ):
        """ Updates the object value from the current text control value.
        """
        control = event.control
        try:
            self.update_object( float( control.value ) )

            return True

        except ( FacetError, ValueError ):
            control.background_color = ErrorColor
            control.refresh()

            return False


    def _enter_text ( self, event ):
        """ Handles the mouse entering the pop-up text control.
        """
        self._in_text_window = True


    def _leave_text ( self, event ):
        """ Handles the mouse leaving the pop-up text control.
        """
        self._in_text_window = False


    def _text_completed ( self, event ):
        """ Handles the user pressing the 'Enter' key in the text control.
        """
        if self._update_value( event ):
            self._destroy_text()


    def _key_entered ( self, event ):
        """ Handles individual key strokes while the text control is active.
        """
        key_code = event.key_code
        if key_code == 'Esc':
            self._destroy_text()

            return

        if key_code == 'Tab':
            if self._update_value( event ):
                self.adapter.tab( not event.shift_down )

            return

        event.handled = False

    #-- Facet Event Handlers ---------------------------------------------------

    def _reset_set ( self ):
        """ Handles one of the slider range values being changed.
        """
        if self.adapter is not None:
            low, high, increment = self.low, self.high, self.increment or 1.0
            value = (int( (self.value + (increment / 2.0)) / increment ) *
                     increment)

            if value < low:
                value += increment

            if value > high:
                value -= increment

            self.update_object( max( low, min( high, value ) ) )
            self._set_tooltip()

#-------------------------------------------------------------------------------
#  'ThemedSliderEditor' class:
#-------------------------------------------------------------------------------

class ThemedSliderEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ThemedSliderEditor

    # The low end of the slider range:
    low = Float

    # The high end of the slider range:
    high = Float

    # The smallest allowed increment:
    increment = Float

    # The name of an [object.]facet that defines the low value for the range:
    low_name = Str

    # The name of an [object.]facet that defines the high value for the range:
    high_name = Str

    # The name of an [object.]facet that defines the increment value for the
    # range:
    increment_name = Str

    # Should the current value be displayed as text?
    show_value = Bool( True )

    # The horizontal alignment of the text within the slider:
    alignment = HorizontalAlignment( 'center' )

    # The color to use for the slider bar:
    slider_color = Color( 0xC0C0C0 )

    # The background color for the slider:
    bg_color = Color( 'white' )

    # The color of the slider tip:
    tip_color = Color( 0xFF7300 )

    # The color to use for the value text:
    text_color = Color( 'black' )

#-- EOF ------------------------------------------------------------------------