"""
The toolkit specific implementation of a Window. See the IWindow interface
for the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide \
    import QtCore, QtGui

from facets.core_api \
    import Event, implements, Property, Unicode

from facets.core_api \
    import Tuple

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
    closed      = Event
    closing     = Event
    deactivated = Event
    key_pressed = Event( KeyPressedEvent )
    opened      = Event
    opening     = Event

    #-- Private Interface ------------------------------------------------------

    # Shadow facet for position:
    _position = Tuple( ( -1, -1 ) )

    # Shadow facet for size:
    _size = Tuple( ( -1, -1 ) )

    #-- IWindow Interface ------------------------------------------------------

    def show ( self, visible ):
        self.control.setVisible( visible )

    #-- Protected IWindow Interface --------------------------------------------

    def _add_event_listeners ( self ):
        self._event_filter = _EventFilter( self )

    #-- IWidget Interface  -----------------------------------------------------

    def destroy ( self ):
        self._event_filter = None

        if self.control is not None:
            # Avoid problems with recursive calls.
            control = self.control
            self.control = None
            control.close()

    #-- Property Implementations -----------------------------------------------

    def _get_position ( self ):
        """ Property getter for position. """

        return self._position

    def _set_position ( self, position ):
        """ Property setter for position. """

        if self.control is not None:
            self.control.move( * position )

        old = self._position
        self._position = position

        self.facet_property_set( 'position', old, position )


    def _get_size ( self ):
        """ Property getter for size. """

        return self._size

    def _set_size ( self, size ):
        """ Property setter for size. """

        if self.control is not None:
            self.control.resize( * size )

        old = self._size
        self._size = size

        self.facet_property_set( 'size', old, size )

    #-- Facet Event Handlers ---------------------------------------------------

    def _title_set ( self, title ):
        """ Handles the 'title' facet being changed.
        """
        if self.control is not None:
            self.control.setWindowTitle( title )

#-------------------------------------------------------------------------------
#  '_EventFilter' class:
#-------------------------------------------------------------------------------

class _EventFilter ( QtCore.QObject ):
    """ An internal class that watches for certain events on behalf of the
        Window instance.
    """

    def __init__ ( self, window ):
        """ Initialise the event filter.
        """
        QtCore.QObject.__init__( self )

        window.control.installEventFilter( self )
        self._window = window


    def eventFilter ( self, obj, e ):
        """ Adds any event listeners required by the window.
        """
        window = self._window

        # Sanity check:
        if obj is not window.control:
            return False

        if e.type() == QtCore.QEvent.Close:
            window.close()

            if window.control is not None:
                e.ignore()

            return True

        if e.type() == QtCore.QEvent.WindowStateChange:
            if obj.windowState() & QtCore.Qt.WindowActive:
                window.activated = window
            else:
                window.deactivated = window
        elif e.type() == QtCore.QEvent.Resize:
            # Get the new size and set the shadow facet without performing
            # notification:
            size = e.size()
            window._size = ( size.width(), size.height() )
        elif e.type() == QtCore.QEvent.Move:
            # Get the real position and set the facet without performing
            # notification:
            pos = e.pos()
            window._position = ( pos.x(), pos.y() )
        elif e.type() == QtCore.QEvent.KeyPress:
            # Pyface doesn't seem to be Unicode aware. Only keep the key code
            # if it corresponds to a single Latin1 character:
            kstr = e.text().toLatin1()

            if kstr.length() == 1:
                kcode = ord( kstr.at( 0 ) )
            else:
                kcode = 0

            mods = e.modifiers()

            window.key_pressed = KeyPressedEvent(
                alt_down     = (( mods & QtCore.Qt.AltModifier ) ==
                                QtCore.Qt.AltModifier),
                control_down = (( mods & QtCore.Qt.ControlModifier ) ==
                                QtCore.Qt.ControlModifier),
                shift_down   = (( mods & QtCore.Qt.ShiftModifier ) ==
                                QtCore.Qt.ShiftModifier),
                key_code     = kcode,
                event        = QtGui.QKeyEvent( e )
            )

        return False

#-- EOF ------------------------------------------------------------------------