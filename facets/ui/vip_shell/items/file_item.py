"""
Defines the FileItem class used by the VIP Shell to represent a file system
file.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Int

from facets.core.facet_base \
    import read_file

from facets.ui.vip_shell.helper \
    import file_info_for

from path_item \
    import PathItem

#-------------------------------------------------------------------------------
#  'FileItem' class:
#-------------------------------------------------------------------------------

class FileItem ( PathItem ):
    """ A file.
    """

    #-- Facet Definitions ------------------------------------------------------

    # An optional line number within the file:
    line = Int

    # Does the file contain binary data?
    is_binary = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def click ( self, event ):
        """ Handles the user clicking an item without the shift or alt
            modifiers.
        """
        if event.control_down:
            self.shell.append( self.item )
        else:
            contents = self.item_contents
            if (len( contents ) == 0) or self.is_binary:
                contents = self.item_label

            self.shell.replace_code( contents )
            if self.line > 0:
                self.shell.goto_line( self.line )

    #-- Facet Default Values ---------------------------------------------------

    def _item_label_default ( self ):
        return file_info_for( self.item )


    def _item_contents_default ( self ):
        contents = read_file( self.item )
        if contents is None:
            return ''

        if (contents.find( '\x00' ) >= 0) or (contents.find( '\xFF' ) >= 0):
            self.is_binary = True
            if len( contents ) > 20:
                return ('%s   [...binary data...]   %s' %
                       ( repr( contents[:10]  )[1:-1],
                         repr( contents[-10:] )[1:-1] ))

            return repr( contents )[1:-1]

        return contents.rstrip()

#-- EOF ------------------------------------------------------------------------
