"""
Defines the PWDCommand VIP Shell command used to print the current working
directory for the shell.
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

# Help information about using the 'pwd' command:
PWDHelp = """
Displays the shell's current working directory.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'PWDCommand' class:
#-------------------------------------------------------------------------------

class PWDCommand ( ShellCommand ):
    """ Displays the current working directory.
    """

    summary = 'Display the name of the current working directory.'
    help    = PWDHelp


    def execute ( self ):
        """ Displays the name of the current working directory.
        """
        self.has_no_options()
        print self.shell.cwd

#-- EOF ------------------------------------------------------------------------
