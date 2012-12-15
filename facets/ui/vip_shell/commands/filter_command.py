"""
Defines the FCommand VIP Shell command used to filter the set of history items
displayed by the shell.
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

# Help information about using the 'filter' command:
FilterHelp = """
Displays only the visible items in the shell history which contain a case
insensitive match of the search string specified by the command's options. If no
option string is specified, then all visible history items are displayed.

Examples:
<</= test>> = Display only visible history items containing the string 'test'.
<</=>>      = Display all visible history items (i.e. removes any previous filter).
"""

#-------------------------------------------------------------------------------
#  'FilterCommand' class:
#-------------------------------------------------------------------------------

class FilterCommand ( ShellCommand ):
    """ Filters the visible shell history items using the filter string
        specified by the command's options.
    """

    summary = 'Displays only items matching a specified search string.'
    help    = FilterHelp


    def execute ( self ):
        """ Displays only the visible history items matching the search string
            specified by the command's options.
        """
        self.shell.filter.text = self.options

#-- EOF ------------------------------------------------------------------------
