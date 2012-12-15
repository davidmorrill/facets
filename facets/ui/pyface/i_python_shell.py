"""
The interface for an interactive Python shell.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Event

from key_pressed_event \
    import KeyPressedEvent

from i_widget \
    import IWidget

#-------------------------------------------------------------------------------
#  'IPythonShell' class:
#-------------------------------------------------------------------------------

class IPythonShell ( IWidget ):
    """ The interface for an interactive Python shell.
    """

    #-- 'IPythonShell' Interface -----------------------------------------------

    # FIXME v3: This can probably be removed if it is not part of the API.
    # fixme: Hack for demo.
    command_executed = Event

    # A key has been pressed.
    key_pressed = Event( KeyPressedEvent )

    #-- 'IPythonShell' Interface -----------------------------------------------

    def interpreter ( self ):
        """ Returns the code.InteractiveInterpreter instance.
        """


    def bind ( self, name, value ):
        """ Binds a name to a value in the interpreter's namespace.
        """


    def execute_command ( self, command, hidden = True ):
        """ Execute a command in the interpreter.

            If 'hidden' is True then nothing is shown in the shell - not even
            a blank line.
        """

#-------------------------------------------------------------------------------
#  'MPythonShell' class:
#-------------------------------------------------------------------------------

class MPythonShell ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IPythonShell interface.

        Implements: bind(), _on_command_executed()
    """

    #-- 'IPythonShell' Interface -----------------------------------------------

    def bind ( self, name, value ):
        """ Binds a name to a value in the interpreter's namespace.
        """
        self.interpreter().locals[ name ] = value

    #-- Private Interface ------------------------------------------------------

    def _on_command_executed ( self ):
        """ Called when a command has been executed in the shell.
        """
        self.command_executed = self

#-- EOF ------------------------------------------------------------------------