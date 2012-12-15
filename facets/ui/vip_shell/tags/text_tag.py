"""
Defines the TextTag class used to provide additional textual information that
can be embedded in a shell item's content.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str

from facets.ui.vip_shell.helper \
    import replace_markers

from shell_tag \
    import ShellTag

#-------------------------------------------------------------------------------
#  'TextTag' class:
#-------------------------------------------------------------------------------

class TextTag ( ShellTag ):
    """ Defines the TextTag class used to provide additional textual information
        that can be embedded in a shell item's content.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The text for the tag:
    text = Str

    #-- Public Methods ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left-clicking on the tag.
        """
        from facets.ui.vip_shell.items.output_item import OutputItem

        shell = self.shell
        shell.append_items( shell.history_item_for(
            OutputItem, replace_markers( self.text ),
            parent = self.shell_item.parent, lod = 2
        ) )

#-- EOF ------------------------------------------------------------------------
