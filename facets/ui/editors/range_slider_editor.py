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
    import Instance, Enum, Range, Float, Bool, Theme, Property, FacetError, \
           BasicEditorFactory, toolkit, on_facet_set, property_depends_on

from facets.core.constants \
    import max_float

from facets.ui.colors \
    import ErrorColor

from facets.ui.pyface.timer.api \
    import do_after

from facets.ui.graphics_text \
    import GraphicsText

from facets.ui.ui_facets \
    import ATheme

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# User interface colors:
white  = ( 255, 255, 255 )
black  = (   0,   0,   0 )
dgrey  = ( 112, 112, 112 )
dgrey1 = (  80,  80,  80 )
dgrey2 = ( 170, 170, 170 )
dgrey3 = ( 200, 200, 200 )

# The text colors that complement the various slider styles:
TextColor = {
     2: white,
     3: white,
     9: white,
    10: white,
    18: white
}

# The default text color:
DefaultTextColor = black

# The disabled text colors that complement the various slider styles:
DisabledTextColor = {
     2: dgrey3,
     4: dgrey1,
     6: dgrey1,
     9: dgrey3,
    10: dgrey2,
    13: dgrey1,
    17: dgrey1,
    18: dgrey2,
    20: dgrey1
}

# The default disabled text color:
DisabledDefaultTextColor = dgrey

# The themes used when a range slider is in an error state (created on demand):
ErrorThemes = None

#-------------------------------------------------------------------------------
#  '_RangeSliderEditor' class:
#-------------------------------------------------------------------------------

class _RangeSliderEditor ( Editor ):
    """ Facets UI simple, slider-based integer or float range value editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The smallest allowed increment:
    increment = Property

    # The current 'range locked' range:
    range = Float

    # The current text being displayed:
    low_text   = Instance( GraphicsText, () )
    high_text  = Instance( GraphicsText, () )
    range_text = Instance( GraphicsText, () )

    # The image slices used to draw the slider and track:
    left_theme   = ATheme
    middle_theme = ATheme
    right_theme  = ATheme
    track_theme  = ATheme

    # Does the editor have an explicit developer-supplied tooltip?
    has_tooltip = Bool( False )

    #-- Method Definitions -----------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Make sure the slider and track image slices have been initialized:
        self._factory_tip_style_modified()
        self._factory_body_style_modified()
        self._factory_track_style_modified()

        # Create the control:
        self.adapter = control = toolkit().create_control(
            parent, tab_stop = self.factory.tab_stop
        )
        control.min_size = ( 100, 19 )

        # Set up the event handlers:
        control.set_event_handler(
            paint     = self._paint,
            get_focus = self._set_focus,
            left_down = self._left_down,
            left_up   = self._left_up,
            motion    = self._motion,
            wheel     = self._mouse_wheel,
            enter     = self._enter_window,
            leave     = self._leave_window,
            size      = self._resize
        )

        # Initialize widest tip size seen so far:
        self._tsz = 0

        # Set the tooltip:
        self.has_tooltip = self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.adapter.unset_event_handler(
            paint     = self._paint,
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

        super( _RangeSliderEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        low, high      = self.value
        self.low_text  = GraphicsText( text      = self.string_value( low ),
                                       alignment = 'center' )
        self.high_text = GraphicsText( text      = self.string_value( high ),
                                       alignment = 'center' )
        range_text     = self.string_value( high - low )
        if self.factory.show_ends == 'Body':
            body = '%s..%s' % ( self.low_text.text, self.high_text.text )
            if self.factory.show_range == 'Body':
                body += ' (%s)' % range_text
            range_text = body

        self.range_text = GraphicsText( text      = range_text,
                                        alignment = 'center' )

        self.adapter.refresh()

        if self._text is not None:
            self._text.value = '%s, %s' % ( self.low_text.text,
                                            self.high_text.text )

        self._set_tooltip()


    def update_object ( self, value ):
        """ Updates the object when the control slider value changes.
        """
        factory   = self.factory
        low       = factory.low
        high      = factory.high
        increment = factory.increment
        range_low, range_high = value
        range_low  = self._round( max( low,  range_low ) )
        range_high = self._round( min( high, range_high ) )

        if range_low < low:
            range_low += increment

        if range_high > high:
            range_high -= increment

        range = self._round( min(
                             max( range_high - range_low + (0.01 * increment),
                                  factory.min_range ), factory.max_range ) )
        range_high = range_low + range
        if range_high > high:
            range_low -= (range_high - high)
            range_high = high

        try:
            self.value = ( range_low, range_high )
        except FacetError:
            self.value = ( int( range_low ), int( range_high ) )

        self.update_editor()


    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's facet value.
        """
        pass


    def set_error_state ( self, state = None, control = None ):
        """ Sets the editor's current error state.
        """
        global ErrorThemes

        if self.get_error_state( state ):
            if self._saved_themes is None:
                if ErrorThemes is None:
                    ErrorThemes = (
                        Theme( image = '@facets:slider_left_9'   ),
                        Theme( image = '@facets:slider_middle_9' ),
                        Theme( image = '@facets:slider_right_9'  )
                    )

                self._saved_themes = ( self.left_theme, self.middle_theme,
                                       self.right_theme )
                self.left_theme, self.middle_theme, self.right_theme = \
                    ErrorThemes
                self.adapter.refresh()
        elif self._saved_themes is not None:
            self.left_theme, self.middle_theme, self.right_theme = \
                self._saved_themes
            del self._saved_themes
            self.adapter.refresh()

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'factory:[low, high, increment]' )
    def _get_increment ( self ):
        factory   = self.factory
        increment = factory.increment
        if increment <= 0.0:
            if isinstance( factory.low, int ):
                increment = 1.0
            else:
                increment = pow( 10, int( log10( ( factory.high - factory.low )
                                 / 1000.0 ) ) )

        return increment

    #-- Private Methods --------------------------------------------------------

    def _set_tooltip ( self ):
        """ Sets the current tooltip value for the slider.
        """
        # If the developer did not supply an explicit tooltip, then define a
        # tooltip showing the current range:
        if not self.has_tooltip:
            factory = self.factory
            sv      = self.string_value
            if (factory.show_ends != 'None') or (factory.show_range != 'None'):
                self.adapter.tooltip = '[%s..%s]' % (
                                       sv( factory.low ), sv( factory.high ) )
            else:
                low, high = self.value
                self.adapter.tooltip = '[%s..%s] (%s)' % (
                                       sv( low ), sv( high ), sv( high - low ) )


    def _set_slider_position ( self, x ):
        """ Calculates a new slider value for a specified x coordinate.
        """
        getattr( self, '_set_slider_position_' + self._drag )( x )

    def _set_slider_position_left ( self, x ):
        """ Handle dragging the left slider tip.
        """
        factory = self.factory
        low     = self._low + ((float( x - self._x ) *
                               (factory.high - factory.low)) / self._adx)
        self.update_object( ( max( min( low, self._high - factory.min_range ),
                                self._high - factory.max_range ), self._high ) )

    def _set_slider_position_middle ( self, x ):
        """ Handle dragging the entire slider.
        """
        factory = self.factory
        delta   = ((float( x - self._x ) * (factory.high - factory.low)) /
                   self._adx)
        if delta >= 0.0:
            delta = min( delta, factory.high - self._high )
        else:
            delta = max( delta, factory.low - self._low )

        self.update_object( ( self._low + delta, self._high + delta ) )

    def _set_slider_position_right ( self, x ):
        """ Handle dragging the right slider tip.
        """
        factory = self.factory
        high    = self._high + ((float( x - self._x ) *
                               (factory.high - factory.low)) / self._adx)
        self.update_object( ( self._low, min( max( high,
            self._low + factory.min_range ), self._low + factory.max_range ) ) )


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
                                    handle_enter = True )
        text.size      = control.size
        text.value     = '%s, %s' % ( self.low_text.text, self.high_text.text )

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


    def _tip_size ( self, g, theme, text, show_tip ):
        """ Calculates the size of the slider tip for the specified *theme* and
            *text* using the graphics context *g*. If *show_tip* is False, the
            *text* is ignored.
        """
        extra = 6
        if not show_tip:
            text, extra = None, 4

        return (theme.size_for( g, text )[0] + 4)


    def _refresh ( self ):
        """ Refreshes the underlying control if it is defined.
        """
        if self.adapter is not None:
            self.adapter.refresh()


    def _action_for ( self, event ):
        """ Returns the 'action' zone for a specified mouse event.
        """
        x = event.x
        if (self.factory.range_locked  or
            event.alt_down             or
            (self._lx <= x < self._rx) or
            (self._lx == self._rx) and (abs( x - self._lx ) <= 5)):
            return 'middle'

        if 0 <= x < self._lx:
            return 'left'

        return 'right'


    def _text_color ( self, g, style ):
        """ Sets the correct text font color for the specified style.
        """
        if self.adapter.enabled:
            g.text_color = TextColor.get( style, DefaultTextColor )
        else:
            g.text_color = DisabledTextColor.get( style,
                                                  DisabledDefaultTextColor )

    #--- Control Event Handlers ------------------------------------------------

    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        factory  = self.factory
        control  = self.adapter
        g        = control.graphics.graphics_buffer()
        wdx, wdy = control.client_size

        # Draw the slider track:
        self.track_theme.fill( g, 0, 0, wdx, wdy )

        # Calculate the sizes of the left and right slider 'tips':
        show_tip  = (factory.show_ends == 'Tip')
        self._tsz = tsz = max(
            self._tsz,
            self._tip_size( g, self.left_theme,  self.low_text,  show_tip ),
            self._tip_size( g, self.right_theme, self.high_text, show_tip )
        )

        # Calculate the available slider range (the slider tips are not
        # included):
        self._adx = adx = wdx - tsz - tsz

        # Calculate the coordinates of the left and right sides of the slider
        # range:
        flow, fhigh   = factory.low, factory.high
        rlow, rhigh   = self.value
        factor        = float( adx ) / (fhigh - flow)
        self._lx = lx = tsz + int( (rlow  - flow) * factor )
        self._rx = rx = tsz + int( (rhigh - flow) * factor )

        # Draw the slider:
        self.left_theme.fill(   g, lx - tsz, 0, tsz, wdy )
        self.middle_theme.fill( g, lx, 0, rx - lx, wdy )
        self.right_theme.fill(  g, rx, 0, tsz, wdy )

        # Draw the current text value (if requested):
        if (factory.show_ends != 'None') or (factory.show_range != 'None'):
            g.font = control.font
            if factory.show_ends == 'Tip':
                self._text_color( g, factory.tip_style )
                self.left_theme.draw_graphics_text( g, self.low_text,
                                                    lx - tsz - 1, 1, tsz, wdy )
                self.right_theme.draw_graphics_text( g, self.high_text,
                                                     rx - 1, 1, tsz, wdy )
            if (factory.show_ends == 'Body') or (factory.show_range == 'Body'):
                self._text_color( g, factory.body_style or factory.tip_style )
                self.middle_theme.draw_graphics_text( g, self.range_text,
                                                      lx, 1, rx - lx, wdy )

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
            self._wheel = self._mx     = self._my = None
            self._x, self._y           = event.x, event.y
            self._low, self._high      = self.value
            self._pending              = True
            self.adapter.mouse_capture = True
            self._drag                 = self._action_for( event )
            do_after( 150, self._delayed_click )


    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            self.adapter.mouse_capture = False

        if self._pending:
            self._pop_up_text()

        self._x    = self._y = self._pending = self._drag = self._low = \
        self._high = None


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

        elif self._wheel is not None:
            if (abs( x - self._mx ) + abs( y - self._my )) >= 5:
                self._wheel = self._mx = self._my = None


    def _mouse_wheel ( self, event ):
        """ Handles the mouse wheel rotating.
        """
        if self.adapter.enabled and self._in_window:
            increment = event.wheel_change
            if increment == 0:
                return

            delta = self.factory.high - self.factory.low
            if event.shift_down:
                delta /= 10.0
            elif event.control_down:
                delta /= 1000.0
            else:
                delta /= 100.0

            if isinstance( self.value[0], int ) and (abs( delta ) < 1):
                delta = int( abs( delta ) / delta )

            delta *= increment
            if abs( delta ) <= self.factory.increment:
                delta = (self.factory.increment * delta) / abs( delta )
                if delta > 0.0:
                    delta *= 1.0001

            if self._wheel is None:
                self._wheel = self._action_for( event )

            self._mx, self._my = event.x, event.y
            getattr( self, '_mouse_wheel_' + self._wheel )( delta )


    def _mouse_wheel_left ( self, delta ):
        """ Handles a mouse wheel change for the left slider tip.
        """
        factory   = self.factory
        low, high = self.value
        self.update_object( ( max( min( low + delta, high - factory.min_range ),
                                   high - factory.max_range ), high ) )


    def _mouse_wheel_middle ( self, delta ):
        """ handles a mouse wheel change for the slider body.
        """
        low, high = self.value
        if delta >= 0.0:
            delta = min( delta, self.factory.high - high )
        else:
            delta = max( delta, self.factory.low - low )

        self.update_object( ( low + delta, high + delta ) )


    def _mouse_wheel_right ( self, delta ):
        """ Handles a mouse wheel change for the right slider tip.
        """
        factory   = self.factory
        low, high = self.value
        self.update_object( ( low, min( max( high + delta,
                        low + factory.min_range ), low + factory.max_range ) ) )


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
        value   = control.value
        values  = value.split( ',' )
        if len( values ) == 1:
            values = values[0].split()

        try:
            self.update_object( map( float, values ) )

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

    @on_facet_set( 'factory:range_locked' )
    def _factory_range_locked_modified ( self ):
        """ Handles the factory 'range_locked' facet being modified.
        """
        self.range = self.value[1] - self.value[0]


    @on_facet_set( 'factory:[show_ends, show_range]' )
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


    @on_facet_set( 'factory:[low, high, increment, min_range, max_range]' )
    def _self_range_modified ( self ):
        """ Handles one of the factory range slider values being changed.
        """
        if self.adapter is not None:
            self.update_object( self.value )


    @on_facet_set( 'factory:tip_style' )
    def _factory_tip_style_modified ( self ):
        """ Handles the factory 'tip_style' facet being changed.
        """
        style             = self.factory.tip_style
        self.left_theme   = Theme( image = '@facets:slider_left_%d'   % style )
        self.right_theme  = Theme( image = '@facets:slider_right_%d'  % style )
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
        self.track_theme = Theme( image = '@facets:slider_track_%d' %
                                          self.factory.track_style )

        self._refresh()

#-------------------------------------------------------------------------------
#  'RangeSliderEditor' class:
#-------------------------------------------------------------------------------

class RangeSliderEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _RangeSliderEditor

    # Can the user tab into the editor?
    tab_stop = Bool( False )

    # The low end of the slider range:
    low = Float( 0.0, facet_value = True )

    # The high end of the slider range:
    high = Float( 1.0, facet_value = True )

    # The smallest allowed increment:
    increment = Float( 0.01, facet_value = True )

    # The smallest allowed range:
    min_range = Float( 0.0, facet_value = True )

    # The largest allowed range:
    max_range = Float( max_float, facet_value = True )

    # Is the size of the range locked?
    range_locked = Bool( False, facet_value = True )

    # Where should the high/low values be displayed:
    show_ends = Enum( 'Tip', 'Body', 'None', facet_value = True )

    # Where should the range be displayed:
    show_range = Enum( 'None', 'Body', facet_value = True )

    # The style to use for the slider tips:
    tip_style = Range( 1, 30, facet_value = True )

    # The style to use for the slider body:
    body_style = Range( 0, 30, facet_value = True )

    # The style to use for the slider track:
    track_style = Range( 1, 15, facet_value = True )

#-- EOF ------------------------------------------------------------------------