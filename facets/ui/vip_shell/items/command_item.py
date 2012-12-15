"""
Defines the CommandItem class used by the VIP Shell to represent Python and
shell commands.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.vip_shell.helper \
    import remove_color

from shell_item \
    import ShellItem

#-------------------------------------------------------------------------------
#  'CommandItem' class:
#-------------------------------------------------------------------------------

class CommandItem ( ShellItem ):
    """ A Python or VIP Shell command.
    """

    #-- Facet Definitions ------------------------------------------------------

    type       = 'command'
    icon       = '@facets:shell_command'
    color_code = '\x00E'
    file_ext   = 'py'

    #-- Public Methods ---------------------------------------------------------

    def can_execute ( self ):
        """ Returns True if the item can be 'executed' in some meaningful
            fashion, and False if it cannot.
        """
        return True


    def execute ( self ):
        """ Re-executes the command.
        """
        self.shell.do_command( self.item, self )

        # Clear any current last command executed to force any new attempts to
        # execute code to create a new command item:
        self.shell.last_command = None


    def replace_code ( self, code ):
        """ Replace the code editor's current contents with the specified
            *code*.
        """
        super( CommandItem, self ).replace_code( code )

        # Mark this command as the last command 'executed' by the shell:
        self.shell.last_command = self


    def shell_value ( self ):
        """ Returns the item as a value the user can manipulate in the shell.
        """
        return remove_color( self.item )

#-- EOF ------------------------------------------------------------------------
