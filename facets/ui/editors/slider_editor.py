"""
Facets UI simple, slider-based integer or float range value editor.
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
    import Instance, Enum, Range, Float, Bool, Theme, FacetError, toolkit, \
           BasicEditorFactory, on_facet_set

from facets.core.facet_base \
    import ui_number

from facets.ui.colors \
    import ErrorColor

from facets.ui.pyface.timer.api \
    import do_later, do_after

from facets.ui.graphics_text \
    import GraphicsText

from facets.ui.ui_facets \
    import ATheme

from editor \
    import Editor

from range_slider_editor \
    import TextColor, DefaultTextColor, DisabledTextColor, \
           DisabledDefaultTextColor

#-------------------------------------------------------------------------------
#  '_SliderEditor' class:
#-------------------------------------------------------------------------------

class _SliderEditor ( Editor ):
    """ Facets UI simple, slider-based integer or float value editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The low end of the slider range:
    low = Float

    # The high end of the slider range:
    high = Float

    # The smallest allowed increment:
    increment = Float

    # The current text being displayed:
    value_text = Instance( GraphicsText, () )

    # The image slices used to draw the slider and track:
    middle_theme = ATheme
    right_theme  = ATheme
    track_theme  = ATheme

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

        # Make sure the slider and track image slices have been initialized:
        self._factory_tip_style_changed()
        self._factory_body_style_changed()
        self._factory_track_style_changed()

        # Create the control:
        self.adapter = control = toolkit().create_control(
            parent, self.factory.tab_stop, True
        )
        control.size_policy = ( 'expanding', 'fixed' )
        control.size        = control.min_size = ( 100, 19 )

        # Set up the event handlers:
        control.set_event_handler(
            paint = self._on_paint,
            size  = self._resize
        )
        if not factory.readonly:
            control.set_event_handler(
                get_focus = self._set_focus,
                left_down = self._left_down,
                left_up   = self._left_up,
                motion    = self._motion,
                wheel     = self._mouse_wheel,
                enter     = self._enter_window,
                leave     = self._leave_window
            )

        # Initialize widest tip size seen so far:
        self._tsz = 0

        # Set the tooltip:
        if not self.set_tooltip():
            self._set_tooltip()

        self._ignore_focus = True
        do_later( self.facet_set, _ignore_focus = False )


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.adapter.unset_event_handler(
            paint = self._on_paint,
            size  = self._resize
        )
        if not self.factory.readonly:
            self.adapter.unset_event_handler(
                get_focus = self._set_focus,
                left_down = self._left_down,
                left_up   = self._left_up,
                motion    = self._motion,
                wheel     = self._mouse_wheel,
                enter     = self._enter_window,
                leave     = self._leave_window
            )

        if self._text is not None:
            self._text.unset_event_handler(
                text_enter = self._text_completed,
                lose_focus = self._text_completed,
                enter      = self._enter_text,
                leave      = self._leave_text,
                key        = self._key_entered
            )

        super( _SliderEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.value_text = GraphicsText(
            text      = self.string_value( self.value, ui_number ),
            alignment = 'center'
        )

        self.adapter.refresh()

        if self._text is not None:
            self._text.value = self.value_text.text


    def update_object ( self, value ):
        """ Updates the object when the control slider value changes.
        """
        value = self._round( min( self.high, max( self.low, value ) ) )

        if value < self.low:
            value += self.increment

        if value > self.high:
            value -= self.increment

        try:
            self.value = value
        except FacetError:
            self.value = int( value )

        self.update_editor()
        self._set_tooltip()


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        pass

    #-- Private Methods --------------------------------------------------------

    def _set_tooltip ( self ):
        """ Sets the current tooltip value for the slider.
        """
        sv      = self.string_value
        tooltip = '[%s..%s]' % ( sv( self.low ), sv( self.high ) )
        if self.factory.show_value == 'None':
            tooltip = '%s %s' % ( sv( self.value ), tooltip )

        self.adapter.tooltip = tooltip


    def _set_slider_position ( self, x ):
        """ Calculates a new slider value for a specified x coordinate.
        """
        self.update_object( self._value + ((float( x - self._x ) *
                            (self.high - self.low)) / self._adx) )


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
        control        = self.adapter
        self._text     = text = toolkit().create_text_input( control(),
                                        handle_enter = True )
        text.size      = control.size
        text.value     = self.value_text.text
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


    def _tip_size ( self, g ):
        """ Calculates the size of the slider tip for the specified theme and
            text.
        """
        text = self.value_text
        if self.factory.show_value != 'Tip':
            text = None

        return (self.right_theme.size_for( g, self.value_text )[0] + 6)


    def _refresh ( self ):
        """ Refreshes the underlying control if it is defined.
        """
        if self.adapter is not None:
            self.adapter.refresh()


    def _text_color ( self, g, style ):
        """ Sets the correct text font color for the specified style.
        """
        if self.adapter.enabled:
            g.text_color = TextColor.get( style, DefaultTextColor )
        else:
            g.text_color = DisabledTextColor.get( style,
                                                  DisabledDefaultTextColor )

    #--- Control Event Handlers ------------------------------------------------

    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        factory  = self.factory
        control  = self.adapter
        g        = control.graphics.graphics_buffer()
        wdx, wdy = control.client_size

        # Draw the slider track:
        self.track_theme.fill( g, 0, 0, wdx, wdy )

        # Calculate the sizes of the slider tip:
        self._tsz = tsz = max( self._tsz, self._tip_size( g ) )

        # Calculate the available slider range (the slider tip is not
        # included):
        self._adx = adx = wdx - tsz - 1

        # Calculate the coordinate of the right side of the slider range:
        self._rx = rx = int( ((self.value - self.low) * float( adx )) /
                             (self.high - self.low) ) + 1

        # Draw the slider:
        self.middle_theme.fill( g, 1, 0, rx - 1, wdy )
        self.right_theme.fill( g, rx, 0, tsz, wdy )

        # Draw the current text value (if requested):
        if factory.show_value != 'None':
            g.font = control.font
            if factory.show_value == 'Tip':
                self._text_color( g, factory.tip_style )
                self.right_theme.draw_graphics_text( g, self.value_text,
                                                     rx, 0, tsz, wdy )
            else:
                self._text_color( g, factory.body_style or factory.tip_style )
                self.middle_theme.draw_graphics_text( g, self.value_text,
                                                      1, 0, rx, wdy )

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
            self._x, self._y           = event.x, event.y
            self._value                = self.value
            self._pending              = True
            self.adapter.mouse_capture = True
            do_after( 150, self._delayed_click )


    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            self.adapter.mouse_capture = False

        if self._pending:
            self._pop_up_text()

        self._x = self._y = self._pending = self._value = None


    def _motion ( self, event ):
        """ Handles the mouse moving.
        """
        x, y = event.x, event.y
        if self._x is not None:
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
            delta     = self.high - self.low
            if event.shift_down:
                delta /= 10.0
            elif event.control_down:
                delta /= 1000.0
            else:
                delta /= 100.0
            if isinstance( self.value, int ) and (abs( delta ) < 1):
                delta = int( abs( delta ) / delta )
            delta *= increment
            if abs( delta ) < self.increment:
                delta = (self.increment * delta) / abs( delta )

            self.update_object( self.value + delta )


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


    def _round ( self, value ):
        """ Rounds the specified value to our current increment.
        """
        increment = self.increment

        return (int( round( value / increment ) ) * increment)


    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:show_value' )
    def _factory_tooltip_modified ( self ):
        """ Handles one of the factory parameters that affects the appearance
            of the control and tooltip being changed.
        """
        self._tsz = 0
        self._set_tooltip()
        self.update_editor()


    @on_facet_set( 'factory:[tip_style, body_style, track_style]' )
    def _factory_refresh_modified ( self ):
        """ Handles one of the factory parameters that affects the appearance
            of the control being changed.
        """
        self._refresh()


    @on_facet_set( 'factory:[low, high, increment]' )
    def _factory_range_modified ( self, facet, new ):
        """ Handles one of the factory slider range values being changed.
        """
        setattr( self, facet, new )


    @on_facet_set( 'low, high, increment' )
    def _self_range_modified ( self ):
        """ Handles one of the slider range values being changed.
        """
        if self.adapter is not None:
            self.update_object( self.value )


    @on_facet_set( 'factory:tip_style' )
    def _factory_tip_style_modified ( self ):
        """ Handles the factory 'tip_style' facet being changed.
        """
        style            = self.factory.tip_style
        self.right_theme = Theme( image   = '@facets:slider_right_%d'  % style,
                                  content = 0 )
        if self.factory.body_style == 0:
            self.middle_theme = Theme(
                                    image = '@facets:slider_middle_%d' % style )

        self._refresh()


    @on_facet_set( 'factory:body_style' )
    def _factory_body_style_modified ( self ):
        """ Handles the factory 'body_style' facet being changed.
        """
        self.middle_theme = Theme( image = '@facets:slider_middle_%d' %
                           (self.factory.body_style or self.factory.tip_style) )

        self._refresh()


    @on_facet_set( 'factory:track_style' )
    def _factory_track_style_modified ( self ):
        """ Handles the factory 'track_style' facet being changed.
        """
        self.track_theme = Theme(
            image = '@facets:slider_track_%d' % self.factory.track_style
        )
        self._refresh()

#-------------------------------------------------------------------------------
#  'SliderEditor' class:
#-------------------------------------------------------------------------------

class SliderEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _SliderEditor

    # Can the user tab into the editor?
    tab_stop = Bool( False )

    # The low end of the slider range:
    low = Float( facet_value = True )

    # The high end of the slider range:
    high = Float( facet_value = True )

    # The smallest allowed increment:
    increment = Float( facet_value = True )

    # Where should the value be displayed:
    show_value = Enum( 'Tip', 'Body', 'None', facet_value = True )

    # The style to use for the slider tips:
    tip_style = Range( 1, 30, facet_value = True )

    # The style to use for the slider body:
    body_style = Range( 0, 30, facet_value = True )

    # The style to use for the slider track:
    track_style = Range( 1, 15, facet_value = True )

    # Is the editor reado-only (e.g. for use as a progress bar)?
    readonly = Bool( False )

#-- EOF ------------------------------------------------------------------------