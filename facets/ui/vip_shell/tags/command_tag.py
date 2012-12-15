"""
Defines the CommandTag class used to handle shell command embedded in a shell
item's content.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str

from shell_tag \
    import ShellTag

#-------------------------------------------------------------------------------
#  'CommandTag' class:
#-------------------------------------------------------------------------------

class CommandTag ( ShellTag ):
    """ Defines the CommandTag class used to handle shell command embedded in a
        shell item's content.
    """

    #-- Facet Definitions ------------------------------------------------------


    # The command:
    command = Str

    #-- Public Methods ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left-clicking on the tag.
        """
        self.shell.do_command( self.command )


    def right_click ( self ):
        """ Handles the user right-clicking on the tag.
        """
        self.shell.append( self.command )

#-- EOF ------------------------------------------------------------------------
