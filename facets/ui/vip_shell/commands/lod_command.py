"""
Defines the LODCommand that sets the 'level of detail' (i.e. lod) settings for
all items returned by any sub-command executed in the same command block.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Enum

from shell_command \
    import ShellCommand

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The help message for the command:
HELP = """
Sets the level of detail for all items returned by other sub-commands to the
level of detail specified by the [[options]], which should be one of:

[[low]]:    Lowest level of detail (shows a single line)
[[medium]]: Medium level of detail (may omit some content)
[[high]]:   Highest level of detail (shows all content)

The default is: <<low>>.
"""[1:-1]

#-------------------------------------------------------------------------------
#  'LODCommand' class:
#-------------------------------------------------------------------------------

class LODCommand ( ShellCommand ):
    """ Defines the LODCommand that sets the 'level of detail' (i.e. lod)
        settings for all items returned by any sub-command executed in the same
        command block.
    """

    #-- Facet Definitions ------------------------------------------------------

    summary = 'Sets the level of detail for all items in the command.'
    help    = HELP

    # The level of detail to be set on each ShellItem returned:
    lod = Enum( 0, 1, 2 )

    #-- Public Methods ---------------------------------------------------------

    def execute ( self ):
        """ Validate the options and request a callback when all commands have
            been run.
        """
        if self.options != '':
            try:
                self.lod = { 'low': 0, 'medium': 1, 'high': 2 }[ self.options ]
            except:
                raise SyntaxError(
                    "The options for the /lod command must be 'low', 'medium' "
                    "or 'high'."
                )

        return self.callback


    def callback ( self ):
        """ Process all of the ShellItems that were generated by the command.
        """
        for item in self.items:
            item.lod = self.lod

#-- EOF ------------------------------------------------------------------------
