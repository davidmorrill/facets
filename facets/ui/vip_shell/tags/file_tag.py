"""
Defines the FileTag class used to handle file references embedded in a shell
item's content.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import File, Int

from facets.ui.vip_shell.helper \
    import file_class_for

from shell_tag \
    import ShellTag

#-------------------------------------------------------------------------------
#  'FileTag' class:
#-------------------------------------------------------------------------------

class FileTag ( ShellTag ):
    """ Defines the FileTag class used to handle file references embedded in a
        shell item's content.
    """
    #-- Facet Definitions ------------------------------------------------------

    # The file name:
    file = File

    # An optional line number within the file:
    line = Int

    #-- Public Methods ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left-clicking on the tag.
        """
        shell = self.shell
        shell.append_items( shell.history_item_for(
            file_class_for( self.file ), self.file,
            line   = self.line,
            parent = self.shell_item.parent
        ) )


    def right_click ( self ):
        """ Handles the user right-clicking on the tag.
        """
        self.shell.append( self.file )

#-- EOF ------------------------------------------------------------------------
