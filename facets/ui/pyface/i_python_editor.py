"""
A widget for editing Python code.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Bool, Event, Interface, Unicode

from key_pressed_event \
    import KeyPressedEvent

#-------------------------------------------------------------------------------
#  'IPythonEditor' class:
#-------------------------------------------------------------------------------

class IPythonEditor ( Interface ):
    """ A widget for editing Python code.
    """

    #-- 'IPythonEditor' interface ----------------------------------------------

    # Has the file in the editor been modified?
    dirty = Bool( False )

    # The pathname of the file being edited.
    path = Unicode

    # Should line numbers be shown in the margin?
    show_line_numbers = Bool( True )

    #-- Events -----------------------------------------------------------------

    # The contents of the editor has changed.
    changed = Event

    # A key has been pressed.
    key_pressed = Event( KeyPressedEvent )

    #-- 'IPythonEditor' Interface ----------------------------------------------

    def load ( self, path = None ):
        """ Loads the contents of the editor.
        """


    def save ( self, path = None ):
        """ Saves the contents of the editor.
        """


    # FIXME v3: This is very dependent on the underlying implementation.
    def set_style ( self, n, fore, back ):
        """ Set the foreground and background colors for a particular style and
            set the font and size to default values.
        """


    def select_line ( self, lineno ):
        """ Selects the specified line.
        """

#-------------------------------------------------------------------------------
#  'MPythonEditor' class:
#-------------------------------------------------------------------------------

class MPythonEditor ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IPythonEditor interface.

        Implements: _changed_path()
    """

    #-- Facet Event Handlers ---------------------------------------------------

    def _changed_path ( self ):
        """ Called when the path to the file is changed.
        """
        if self.control is not None:
            self.load()

#-- EOF ------------------------------------------------------------------------