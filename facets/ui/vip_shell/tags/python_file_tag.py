"""
Defines the PythonFileTag class used to handle Python source file references
embedded in a shell item's content.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from file_tag \
    import FileTag

#-------------------------------------------------------------------------------
#  'PythonFileTag' class:
#-------------------------------------------------------------------------------

class PythonFileTag ( FileTag ):
    """ Defines the PythonFileTag class used to handle Python source file
        references embedded in a shell item's content.
    """

    #-- Public Methods ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left-clicking on the tag.
        """
        from facets.ui.editors.vip_shell_editor import VIPShellCode

        line = self.line or 1
        self.shell.add_code_item( VIPShellCode(
            file_name     = self.file,
            code          = self.shell.source_for( self.file ),
            code_line     = line,
            selected_line = line
        ) )

#-- EOF ------------------------------------------------------------------------
