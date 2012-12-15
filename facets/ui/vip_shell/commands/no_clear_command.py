"""
Defines the NoClearCommand VIP Shell command used to prevent clearing the
shell's code buffer after a successful command execution.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information about using the 'no clear' command:
Help = """
Prevents clearing the shell's code buffer after a successful command execution.
This can be useful when you are iteratively developing code, since it eliminates
the need to keep retrieving the last version of the code back into the code editor.

This command does not have any options.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'NoClearCommand' class:
#-------------------------------------------------------------------------------

class NoClearCommand ( ShellCommand ):
    """ Prevents clearing the shell's code buffer after a successful command
        execution.
    """

    summary = ("Prevents clearing the code buffer after a successful command "
               "execution.")
    help    = Help


    def execute ( self ):
        """ Tells the shell not to clear the code buffer after a successful
            command execution.
        """
        self.has_no_options()
        self.shell.clear_buffer = False

#-- EOF ------------------------------------------------------------------------
