"""
Facets pyface package component
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

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

    size = Property( Tuple )

    title = Unicode

    #-- Events -----------------------------------------------------------------

    activated = Event

    closed =  Event

    closing =  Event

    deactivated = Event

    key_pressed = Event( KeyPressedEvent )

    opened = Event

    opening = Event

    #-- Private Facets ---------------------------------------------------------

    # Shadow facet for position:
    _position = Tuple( ( -1, -1 ) )

    # Shadow facet for size:
    _size = Tuple( ( -1, -1 ) )

    #-- 'IWindow' Interface ----------------------------------------------------

    def show ( self, visible ):
        self.control.Show( visible )

    #-- Protected 'IWindow' Interface ------------------------------------------

    def _add_event_listeners ( self ):
        wx.EVT_ACTIVATE( self.control, self._wx_on_activate )
        wx.EVT_CLOSE( self.control, self._wx_on_close )
        wx.EVT_SIZE( self.control, self._wx_on_control_size )
        wx.EVT_MOVE( self.control, self._wx_on_control_move )
        wx.EVT_CHAR( self.control, self._wx_on_char )

    #-- Private Methods --------------------------------------------------------

    def _get_position ( self ):
        """ Property getter for position.
        """
        return self._position

    def _set_position ( self, position ):
        """ Property setter for position.
        """
        if self.control is not None:
            self.control.SetPosition( position )

        old = self._position
        self._position = position

        self.facet_property_set( 'position', old, position )


    def _get_size ( self ):
        """ Property getter for size.
        """
        return self._size

    def _set_size ( self, size ):
        """ Property setter for size. """

        if self.control is not None:
            self.control.SetSize( size )

        old = self._size
        self._size = size

        self.facet_property_set( 'size', old, size )

    #-- Facet Event Handlers ---------------------------------------------------

    def _title_set ( self, title ):
        """ Static facet change handler.
        """
        if self.control is not None:
            self.control.SetTitle( title )

    #-- wx Event Handlers ------------------------------------------------------

    def _wx_on_activate ( self, event ):
        """ Called when the frame is being activated or deactivated.
        """
        if event.GetActive():
            self.activated = self
        else:
            self.deactivated = self


    def _wx_on_close ( self, event ):
        """ Called when the frame is being closed.
        """
        self.close()


    def _wx_on_control_move ( self, event ):
        """ Called when the window is resized.
        """
        # Get the real position and set the facet without performing
        # notification.

        # WXBUG - From the API documentation you would think that you could
        # call event.GetPosition directly, but that would be wrong.  The pixel
        # reported by that call is the pixel just below the window menu and
        # just right of the Windows-drawn border.
        self._position = event.GetEventObject().GetPositionTuple()

        event.Skip()


    def _wx_on_control_size ( self, event ):
        """ Called when the window is resized.
        """
        # Get the new size and set the shadow facet without performing
        # notification.
        wxsize = event.GetSize()

        self._size = ( wxsize.GetWidth(), wxsize.GetHeight() )

        event.Skip()


    def _wx_on_char ( self, event ):
        """ Called when a key is pressed when the tree has focus.
        """
        self.key_pressed = KeyPressedEvent(
            alt_down     = event.m_altDown == 1,
            control_down = event.m_controlDown == 1,
            shift_down   = event.m_shiftDown == 1,
            key_code     = event.m_keyCode,
            event        = event
        )

        event.Skip()

#-- EOF ------------------------------------------------------------------------