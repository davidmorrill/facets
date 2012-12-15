"""
Defines the TimeCommand VIP Shell command used to time the execution of Python
commands.
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

# Help information for the 'time' command:
TimeHelp = """
Turns on execution timing for the remainder of the command execution. This
command should proceed one or more Python expression or code blocks to be timed.

When the command is completed, the execution time for each separate block of
Python code executed is displayed. You can use the 'no-op' command ([[/#]]) to
separate several blocks of Python code if desired.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'TimeCommand' class:
#-------------------------------------------------------------------------------

class TimeCommand ( ShellCommand ):
    """ Times code execution of subsequent Python commands.
    """

    summary = 'Times subsequent Python code in the same command.'
    help    = TimeHelp


    def execute ( self ):
        """ Times code execution.
        """
        self.has_no_options()
        self.shell.timing = True

#-- EOF ------------------------------------------------------------------------
