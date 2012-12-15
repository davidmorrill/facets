"""
The abstract interface for all pyface top-level windows.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Event, Tuple, Unicode

from constant \
    import NO

from key_pressed_event \
    import KeyPressedEvent

from i_widget \
    import IWidget

#-------------------------------------------------------------------------------
#  'IWindow' class:
#-------------------------------------------------------------------------------

class IWindow ( IWidget ):
    """ The abstract interface for all pyface top-level windows.

        A pyface top-level window has no visual representation until it is
        opened (ie. its 'control' facet will be None until it is opened).
    """

    #-- 'IWindow' interface ----------------------------------------------------

    # The position of the window.
    position = Tuple

    # The size of the window.
    size = Tuple

    # The window title.
    title = Unicode

    #-- Events -----------------------------------------------------------------

    # The window has been activated.
    activated = Event

    # The window has been closed.
    closed =  Event

    # The window is about to be closed.
    closing =  Event

    # The window has been deactivated.
    deactivated = Event

    # A key was pressed while the window had focus.
    # FIXME v3: This smells of a hack. What's so special about key presses?
    # FIXME v3: Unicode
    key_pressed = Event( KeyPressedEvent )

    # The window has been opened.
    opened = Event

    # The window is about to open.
    opening = Event

    #-- 'IWindow' Interface ----------------------------------------------------

    def open ( self ):
        """ Opens the window.
        """


    def close ( self ):
        """ Closes the window.
        """


    def show ( self, visible ):
        """ Show or hide the window.

            visible is set if the window should be shown.
        """


    def confirm ( self, message, title = None, cancel = False, default = NO ):
        """ Convenience method to show a confirmation dialog.

            **message** is the text of the message to display.
            **title** is the text of the window title.
            **cancel** is set if the dialog should contain a Cancel button.
            **default** is the default button.
        """


    def information ( self, message, title = 'Information' ):
        """ Convenience method to show an information message dialog.

            **message** is the text of the message to display.
            **title** is the text of the window title.
        """


    def warning ( self, message, title = 'Warning' ):
        """ Convenience method to show a warning message dialog.

            **message** is the text of the message to display.
            **title** is the text of the window title.
        """


    def error ( self, message, title = 'Error' ):
        """ Convenience method to show an error message dialog.

            **message** is the text of the message to display.
            **title** is the text of the window title.
        """

    #-- Protected 'IWindow' Interface ------------------------------------------

    def _add_event_listeners ( self ):
        """ Adds any event listeners required by the window.
        """

#-------------------------------------------------------------------------------
#  'MWindow' class:
#-------------------------------------------------------------------------------

class MWindow ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IWindow interface.

        Implements: close(), confirm(), open()
        Reimplements: _create()
    """

    #-- 'IWindow' Interface ----------------------------------------------------

    def open ( self ):
        """ Opens the window.
        """
        # Facet notification:
        self.opening = self

        if self.control is None:
            self._create()

        self.show( True )

        # Facet notification:
        self.opened = self


    def close ( self ):
        """ Closes the window.
        """
        if self.control is not None:
            # Facet notification:
            self.closing = self

            # Cleanup the toolkit-specific control:
            self.destroy()

            # Facet notification:
            self.closed = self


    def confirm ( self, message, title = None, cancel = False, default = NO ):
        """ Convenience method to show a confirmation dialog.
        """
        from confirmation_dialog import confirm

        return confirm( self.control, message, title, cancel, default )


    def information ( self, message, title = 'Information' ):
        """ Convenience method to show an information message dialog.
        """
        from message_dialog import information

        return information( self.control, message, title )


    def warning ( self, message, title = 'Warning' ):
        """ Convenience method to show a warning message dialog.
        """
        from message_dialog import warning

        return warning( self.control, message, title )


    def error ( self, message, title = 'Error' ):
        """ Convenience method to show an error message dialog.
        """
        from message_dialog import error

        return error( self.control, message, title )

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create ( self ):
        """ Creates the window's widget hierarchy.
        """
        # Create the toolkit-specific control:
        super( MWindow, self )._create()

        # Wire up event any event listeners required by the window:
        self._add_event_listeners()

#-- EOF ------------------------------------------------------------------------