"""
Defines an UIEvent base class that each GUI toolkit backend must provide a
concrete implementation of.

The UIEvent class adapts a GUI toolkit event to provide a set of toolkit neutral
properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Str, Property, Any

#-------------------------------------------------------------------------------
#  'UIEvent' class:
#-------------------------------------------------------------------------------

class UIEvent ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The GUI toolkit specific mouse event being adapted:
    event = Any

    # The name of the event (e.g. 'left_up', 'paint', 'key'):
    name = Str

    # The value associated with the event:
    value = Property

    # The x position of the mouse:
    x = Property

    # The y position of the mouse:
    y = Property

    # The x position of the mouse on the screen:
    screen_x = Property

    # The y position of the mouse on the screen:
    screen_y = Property

    # Is the left mouse button down?
    left_down = Property

    # Is thr right mouse button down:
    right_down = Property

    # Is the 'Shift' key pressed?
    shift_down = Property

    # Is the 'Control' key pressed?
    control_down = Property

    # Is the 'Alt' key pressed?
    alt_down = Property

    # The key code of the key being pressed:
    key_code = Property

    # The amount by which the mouse wheel has rotated:
    wheel_change = Property

    # Was the window activated?
    activated = Property

    # The (adapted) control associated with the event:
    control = Property

    # Has the event been completely handled (True/False)?
    handled = Property

    #-- Method Implementations -------------------------------------------------

    def __init__ ( self, event, **facets ):
        """ Initializes the object by saving the mouse event being adapted.
        """
        super( UIEvent, self ).__init__( **facets )

        self.event = event

    def __call__ ( self ):
        """ Returns the mouse event being adapted.
        """
        return self.event

    #-- Property Implementations -----------------------------------------------

    def _get_value ( self ):
        raise NotImplementedError


    def _get_x ( self ):
        raise NotImplementedError

    def _get_y ( self ):
        raise NotImplementedError

    def _get_screen_x ( self ):
        raise NotImplementedError

    def _get_screen_y ( self ):
        raise NotImplementedError

    def _get_left_down ( self ):
        raise NotImplementedError

    def _get_right_down ( self ):
        raise NotImplementedError

    def _get_shift_down ( self ):
        raise NotImplementedError

    def _get_control_down ( self ):
        raise NotImplementedError

    def _get_alt_down ( self ):
        raise NotImplementedError

    def _get_key_code ( self ):
        raise NotImplementedError

    def _get_wheel_change ( self ):
        raise NotImplementedError

    def _get_activated ( self ):
        raise NotImplementedError

    def _get_control ( self ):
        raise NotImplementedError

    def _set_handled ( self, handled ):
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------