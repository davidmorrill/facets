"""
Defines the LXCommand VIP Shell command used to list the Python source files
most recently executed by the shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.vip_shell.items.api \
    import PythonFileItem

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Help information about using the 'lx' command:
LXHelp = """
Lists all of the most recently executed Python source files from most to least
recently used.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'LXCommand' class:
#-------------------------------------------------------------------------------

class LXCommand ( ShellCommand ):
    """ Lists the most recently executed files.
    """

    summary = 'Lists the most recently executed Python source files.'
    help    = LXHelp


    def execute ( self ):
        """ Lists the most recently executed Python source files.
        """
        self.has_no_options()
        hif = self.shell.history_item_for

        return [ hif( PythonFileItem, file_name )
                 for file_name in self.shell.mru_execfile_names ]

#-- EOF ------------------------------------------------------------------------
