"""
Facets UI simple, scrubber-based integer or float value editor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
   import log10, pow, copysign

try:
    from sys import float_info

    FloatMin = float_info.min
    FloatMax = float_info.max
except:
    FloatMin = 2.2250738585072014e-308
    FloatMax = 1.7976931348623157e+308

from facets.api \
    import Any, BaseRange, BaseEnum, Str, Float, Color, FacetError, \
           on_facet_set, View, Item, EnumEditor, BasicEditorFactory, toolkit

from facets.core.facet_base \
    import SequenceTypes, Undefined, ui_number

from facets.ui.ui_facets \
    import HorizontalAlignment

from facets.ui.pyface.timer.api \
    import do_after

from facets.ui.pyface.image_slice \
    import paint_parent

from facets.ui.colors \
    import ErrorColor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_ScrubberEditor' class:
#-------------------------------------------------------------------------------

class _ScrubberEditor ( Editor ):
    """ Facets UI simple, scrubber-based integer or float value editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The low end of the slider range:
    low = Any( event = 'reset' )

    # The high end of the slider range:
    high = Any( event = 'reset' )

    # The smallest allowed increment:
    increment = Float( event = 'reset' )

    # The current text being displayed:
    text = Str

    # The mapping to use (only for Enum's):
    mapping = Any

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Establish the range of the slider:
        low_name = high_name = ''
        low, high, increment = factory.low, factory.high, factory.increment
        if high <= low:
            low = high = None
            handler    = self.object.facet( self.name ).handler
            if isinstance( handler, BaseRange ):
                low_name, high_name = handler._low_name, handler._high_name

                if low_name == '':
                    low = handler._low

                if high_name == '':
                    high = handler._high

            elif isinstance( handler, BaseEnum ):
                increment = 1
                if handler.name == '':
                    mapping = handler.values
                    if isinstance( mapping, SequenceTypes ):
                        mapping = dict( [
                            ( i, item ) for i, item in enumerate( mapping )
                        ] )

                    self.mapping = mapping
                else:
                    self.sync_value( handler.name, 'mapping', 'from' )

                low, high = 0, self.high

        # Establish the slider increment:
        if increment <= 0.0:
            if (low is None) or (high is None) or isinstance( low, int ):
                increment = 1.0
            else:
                increment = pow( 10, int( log10( ( high - low ) / 1000.0 ) ) )

        # Create the control:
        self.adapter = control = toolkit().create_control( parent,
                                                           tab_stop = True )
        control.min_size = ( 10, 18 )

        # Set up the event handlers:
        control.set_event_handler(
            paint     = self._on_paint,
            size      = self._resize,
            get_focus = self._set_focus,
            enter     = self._enter_window,
            leave     = self._leave_window,
            left_down = self._left_down,
            left_up   = self._left_up,
            motion    = self._motion,
            wheel     = self._mouse_wheel
        )

        # Set the tooltip:
        self._can_set_tooltip = (not self.set_tooltip())

        # Save the values we calculated:
        self.facet_setq( low = low, high = high, increment = increment )
        self.sync_value( factory.low_name  or low_name,  'low',       'from' )
        self.sync_value( factory.high_name or high_name, 'high',      'from' )
        self.sync_value( factory.increment_name,         'increment', 'from' )

        # Force a reset (in case low = high = None, which won't cause a
        # notification to fire):
        self._reset_scrubber()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        # Remove all of the event handlers:
        self.adapter.unset_event_handler(
            paint     = self._on_paint,
            size      = self._resize,
            get_focus = self._set_focus,
            enter     = self._enter_window,
            leave     = self._leave_window,
            left_down = self._left_down,
            left_up   = self._left_up,
            motion    = self._motion,
            wheel     = self._mouse_wheel
        )

        # Disconnect the pop-up text event handlers:
        self._disconnect_text()

        super( _ScrubberEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.text       = self.string_value( self.value, ui_number )
        self._text_size = None
        self.adapter.refresh()

        self._enum_completed()


    def update_object ( self, value ):
        """ Updates the object when the scrubber value changes.
        """
        if self.mapping is not None:
            value = self.mapping.get( int( value ), Undefined )
            if value is Undefined:
                return
        else:
            low, high = self.low, self.high
            increment = (self.increment / 10) or 1

            if low is None:
                low = -FloatMax

            if high is None:
                high = FloatMax

            value = copysign( int( (abs( value ) + (increment / 2.0)) /
                              increment ) * increment, value )
            value = max( low, min( high, value ) )

        if value != self.value:
            try:
                self.value = value
                self.update_editor()
            except FacetError:
                value = int( value )
                if value != self.value:
                    self.value = value
                    self.update_editor()


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        pass

    #-- Facet Event Handlers ---------------------------------------------------

    def _mapping_set ( self, mapping ):
        """ Handles the Enum mapping being changed.
        """
        self.high = len( mapping ) - 1

    @on_facet_set( 'low, high, increment' )
    def _reset_scrubber ( self ):
        """ Sets the the current tooltip.
        """
        low, high, increment = self.low, self.high, self.increment
        if self._can_set_tooltip:
            if self.mapping is not None:
                tooltip = '[%s]' % ( ', '.join( self.mapping.values() ) )
                if len( tooltip ) > 80:
                    tooltip = ''
            elif high is None:
                tooltip = ''
                if low is not None:
                    tooltip = '[%g..]' % low
            elif low is None:
                tooltip = '[..%g]' % high
            else:
                tooltip = '[%g..%g]' % ( low, high )

            self.adapter.tooltip = tooltip

        # Establish the slider increment:
        if increment <= 0.0:
            if (low is None) or (high is None) or isinstance( low, int ):
                increment = 1.0
            else:
                increment = pow( 10, round( log10( (high - low) / 100.0 ) ) )

            self.increment = increment

        # Make sure the current editor value is within the new range:
        if (self.adapter is not None) and (self.mapping is None):
            self.update_object( self.value )

    #-- Private Methods --------------------------------------------------------

    def _get_text_bounds ( self, g ):
        """ Get the window bounds of where the current text should be
            displayed.
        """
        tdx, tdy  = self._get_text_size( g )
        wdx, wdy  = self.adapter.client_size
        ty        = ((wdy - tdy) / 2) - 1
        alignment = self.factory.alignment
        if alignment == 'left':
            tx = 0
        elif alignment == 'center':
            tx = (wdx - tdx) / 2
        else:
            tx = wdx - tdx

        return ( tx, ty, tdx, tdy )


    def _get_text_size ( self, g ):
        """ Returns the text size information for the window.
        """
        if self._text_size is None:
            tdx, tdy = self._text_size = g.text_size( self.text.strip() or 'M' )
            self.control.min_size = ( tdx + 10, tdy + 5 )

        return self._text_size


    def _set_scrubber_position ( self, event, delta ):
        """ Calculates a new scrubber value for a specified mouse position
            change.
        """
        clicks    = 3
        increment = self.increment
        if event.shift_down:
            increment *= 10.0
            clicks     = 7
        elif event.control_down:
            if isinstance( self.value, int ):
                increment = (int( increment ) / 10) or 1
            else:
                increment /= 10.0

        self.update_object( self._value + (delta / clicks) * increment )


    def _delayed_click ( self ):
        """ Handle a delayed click response.
        """
        self._pending = False


    def _pop_up_editor ( self ):
        """ Pop-up a text control to allow the user to enter a value using
            the keyboard.
        """
        self.adapter.cursor = 'arrow'

        if self.mapping is not None:
            self._pop_up_enum()
        else:
            self._pop_up_text()


    def _pop_up_enum ( self ):
        self._ui = self.object.edit_facets(
            view = View(
                Item( self.name,
                      id         = 'drop_down',
                      show_label = False,
                      padding    = -4,
                      editor     = EnumEditor( name = 'editor.mapping' ) ),
                kind = 'subpanel' ),
            parent  = self.control,
            context = { 'object': self.object, 'editor': self } )

        dx, dy           = self.adapter.size
        drop_down        = self._ui.info.drop_down.adapter
        drop_down.bounds = ( 0, 0, dx, dy )
        drop_down.set_focus()
        drop_down.set_event_handler( lose_focus = self._enum_completed )


    def _pop_up_text ( self ):
        self._text = text = toolkit().create_text_input( self.control,
                                         handle_enter = True,
                                         align        = self.factory.alignment )
        text.value     = self.str_value
        text.size      = self.adapter.size
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

        self._disconnect_text()

        self.adapter.destroy_children()

        self._text = None


    def _disconnect_text ( self ):
        """ Disconnects the event handlers for the pop up text editor.
        """
        if self._text is not None:
            self._text.unset_event_handler(
                text_enter = self._text_completed,
                lose_focus = self._text_completed,
                enter      = self._enter_text,
                leave      = self._leave_text,
                key        = self._key_entered
            )


    def _init_value ( self ):
        """ Initializes the current value when the user begins a drag or moves
            the mouse wheel.
        """
        if self.mapping is not None:
            try:
                self._value = self.mapping.values().index( self.value )
            except:
                self._value = 0
        else:
            self._value = self.value

    #--- Control Event Handlers ------------------------------------------------

    def _on_paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        control = self.adapter
        g       = control.graphics.graphics_buffer()

        # Draw the background:
        factory  = self.factory
        color    = factory.color
        if self._x is not None:
            if factory.active_color is not None:
                color = factory.active_color
        elif self._hover:
            if factory.hover_color is not None:
                color = factory.hover_color

        if color is None:
            paint_parent( g, control )
            brush = None
        else:
            brush = color

        color = factory.border_color
        if color is not None:
            pen = color
        else:
            pen = None

        if (pen is not None) or (brush is not None):
            wdx, wdy = control.client_size
            g.brush  = brush
            g.pen    = pen
            g.draw_rectangle( 0, 0, wdx, wdy )

        # Draw the current text value:
        g.text_background_color = None
        g.text_color            = factory.text_color
        g.font                  = control.font
        tx, ty, tdx, tdy        = self._get_text_bounds( g )
        g.draw_text( self.text, tx, ty )

        # Copy the buffer contents to the display:
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
            (self._text is None)):
            self._pop_up_editor()

        event.handled = False


    def _enter_window ( self, event ):
        """ Handles the mouse entering the window.
        """
        self._hover = True

        self.adapter.cursor = 'hand'

        if not self._ignore_focus:
            self._ignore_focus = True
            self.adapter.set_focus()

        self._ignore_focus = False

        if self._x is not None:
            if self.factory.active_color != self.factory.color:
                self.refresh()
        elif self.factory.hover_color != self.factory.color:
            self.adapter.refresh()


    def _leave_window ( self, event ):
        """ Handles the mouse leaving the window.
        """
        self._hover = False

        if self.factory.hover_color != self.factory.color:
            self.adapter.refresh()


    def _left_down ( self, event ):
        """ Handles the left mouse being pressed.
        """
        self._x, self._y = event.x, event.y
        self._pending    = True

        self._init_value()

        self.adapter.mouse_capture = True

        if self.factory.active_color != self.factory.hover_color:
            self.adapter.refresh()

        do_after( 200, self._delayed_click )


    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        self.adapter.mouse_capture = False
        if self._pending:
            self._pop_up_editor()

        self._x = self._y = self._value = self._pending = None

        if self._hover or (self.factory.active_color != self.factory.color):
            self.adapter.refresh()


    def _motion ( self, event ):
        """ Handles the mouse moving.
        """
        if self._x is not None:
            x, y = event.x, event.y
            dx   = x - self._x
            adx  = abs( dx )
            dy   = y - self._y
            ady  = abs( dy )
            if self._pending:
                if (adx + ady) < 3:
                    return

                self._pending = False

            if adx > ady:
                delta = dx
            else:
                delta = -dy

            if self.mapping is not None:
                delta /= 5.0

            self._set_scrubber_position( event, delta )


    def _mouse_wheel ( self, event ):
        """ Handles the mouse wheel moving.
        """
        if self._hover:
            self._init_value()
            clicks = 3
            if event.shift_down:
                clicks = 7

            delta = clicks * event.wheel_change
            self._set_scrubber_position( event, delta )


    def _update_value ( self, event ):
        """ Updates the object value from the current text control value.
        """
        control = event.control
        try:
            self.update_object( float( control.value ) )

            return True

        except FacetError:
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


    def _enum_completed ( self, event = None ):
        """ Handles the Enum drop-down control losing focus.
        """
        if self._ui is not None:
            self._ignore_focus = True
            self._ui.info.drop_down.adapter.unset_event_handler(
                lose_focus = self._enum_completed
            )
            self._ui.dispose()
            del self._ui


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

#-------------------------------------------------------------------------------
#  'ScrubberEditor' class:
#-------------------------------------------------------------------------------

class ScrubberEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ScrubberEditor

    # The low end of the scrubber range:
    low = Float

    # The high end of the scrubber range:
    high = Float

    # The normal increment (default: auto-calculate):
    increment = Float

    # The name of an [object.]facet that defines the low value for the scrubber
    # range:
    low_name = Str

    # The name of an [object.]facet that defines the high value for the scrubber
    # range:
    high_name = Str

    # The name of an [object.]facet that defines the increment value for the
    # scrubber range:
    increment_name = Str

    # The horizontal alignment of the text within the scrubber:
    alignment = HorizontalAlignment( 'center' )

    # The background color for the scrubber:
    color = Color( None )

    # The hover mode background color for the scrubber:
    hover_color = Color( None )

    # The active mode background color for the scrubber:
    active_color = Color( None )

    # The scrubber border color:
    border_color = Color( None )

    # The color to use for the value text:
    text_color = Color( 'black' )

#-- EOF ------------------------------------------------------------------------