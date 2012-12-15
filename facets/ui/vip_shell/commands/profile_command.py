"""
Defines the ProfileCommand VIP Shell command used to profile the execution of
Python commands.
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

# Help information for the 'profile' command:
ProfileHelp = """
Turns on profiling for the remainder of the command execution. This command
should proceed a Python expression or code block to be profiled.

When the command is completed, the profiling data is written to a file in the
current working directory, and the name of the file is sent to the shell's
'profile' output to allow external tools, such as the [[ProfileViewer]], to analyze
and display the results.

See also the [[/pp]] command to print the profiler results directly in the shell.
"""[1:-1]

# Help information for the 'profile and print' command:
ProfilePrintHelp = """
Turns on profiling for the remainder of the command execution. This command
should proceed a Python expression or code block to be profiled.

When the command is completed, the profiling data is written to a file in the
current working directory, and then the results are analyzed and printed to the
shell's output. The name of the file is also sent to the shell's 'profile'
output to allow external tools, such as the [[ProfileViewer]], to analyze and
display the results.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'ProfileCommand' class:
#-------------------------------------------------------------------------------

class ProfileCommand ( ShellCommand ):
    """ Profiles code execution of subsequent Python commands.
    """

    def execute ( self ):
        """ Profiles code execution.
        """
        self.has_no_options()
        self.shell.profile_code( self.command == 'pp' )


    def show_help ( self ):
        """ Displays help for using the 'profile' command.
        """
        if self.command == 'pp':
            return ProfilePrintHelp

        return ProfileHelp

    #-- Facet Default Values ---------------------------------------------------

    def _summary_default ( self ):
        if self.command == 'pp':
            return ('Profiles subsequent Python code in the same command and '
                    'prints the results.')

        return 'Profiles subsequent Python code in the same command.'

#-- EOF ------------------------------------------------------------------------
