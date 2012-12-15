"""
Defines the OptionsCommand shell command that allows the user to set the shell
options in-line within the shell history.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.vip_shell.items.view_item \
    import ViewItem

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The help message for the command:
HELP = """
Displays the shell options view within the history list. This command has no
options.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'OptionsCommand' class:
#-------------------------------------------------------------------------------

class OptionsCommand ( ShellCommand ):
    """ Defines the 'options' shell command.
    """

    summary = 'Displays the shell options view within the history list.'
    help    = HELP


    def execute ( self ):
        """ Analyzes and validates the options, then displays the requested
            view.
        """
        return self.shell.history_item_for(
            ViewItem, self.shell, height = 300, view = 'options_view', lod = 1
        )

#-- EOF ------------------------------------------------------------------------
