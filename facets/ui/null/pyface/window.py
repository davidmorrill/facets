"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Event, implements, Property, Unicode, Tuple

from facets.ui.pyface.i_window \
    import IWindow, MWindow

from facets.ui.pyface.key_pressed_event \
    import KeyPressedEvent

from widget \
    import Widget

#-------------------------------------------------------------------------------
#  'Window' class:
#-------------------------------------------------------------------------------

class Window ( MWindow, Widget ):
    """ The toolkit specific implementation of a Window. See the IWindow
        interface for the API documentation.
    """

    implements( IWindow )

    #-- 'IWindow' interface ----------------------------------------------------

    position = Property( Tuple )
    size     = Property( Tuple )
    title    = Unicode

    #-- Events -----------------------------------------------------------------

    activated   = Event
    closed      =  Event
    closing     =  Event
    deactivated = Event
    key_pressed = Event( KeyPressedEvent )
    opened      = Event
    opening     = Event

    #-- Private interface ------------------------------------------------------

    # Shadow facet for position.
    _position = Tuple( ( -1, -1 ) )

    # Shadow facet for size.
    _size = Tuple( ( -1, -1 ) )

    #-- 'IWindow' Interface ----------------------------------------------------

    def show ( self, visible ):
        pass

    #-- Protected 'IWindow' Interface ------------------------------------------

    def _add_event_listeners ( self ):
        pass

    #-- Property Implementations -----------------------------------------------

    def _get_position ( self ):
        """ Property getter for position.
        """
        return self._position

    def _set_position ( self, position ):
        """ Property setter for position.
        """
        old = self._position
        self._position = position

        self.facet_property_set( 'position', old, position )


    def _get_size ( self ):
        """ Property getter for size.
        """
        return self._size

    def _set_size ( self, size ):
        """ Property setter for size.
        """
        old = self._size
        self._size = size

        self.facet_property_set( 'size', old, size )

#-- EOF ------------------------------------------------------------------------