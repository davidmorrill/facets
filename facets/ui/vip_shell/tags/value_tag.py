"""
Defines the ValueTag class used to handle arbitrary Python value references
embedded in a shell item's content.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Str

from facets.ui.vip_shell.helper \
    import as_repr

from shell_tag \
    import ShellTag

#-------------------------------------------------------------------------------
#  'ValueTag' class:
#-------------------------------------------------------------------------------

class ValueTag ( ShellTag ):
    """ Defines the ValueTag class used to handle arbitrary Python value
        references embedded in a shell item's content.
    """

    #-- Facet Definitions ------------------------------------------------------

    # An optional label to display with the value:
    label = Str

    # The value:
    value = Any

    #-- Facet Default Values ---------------------------------------------------

    def _tooltip_default ( self ):
        return as_repr( self.value )

    #-- Public Methods ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left-clicking on the tag.
        """
        from facets.ui.vip_shell.items.result_item import ResultItem

        shell = self.shell
        shell.append_items( shell.history_item_for(
            ResultItem, self.value,
            label  = self.label,
            parent = self.shell_item.parent,
            lod    = 1
        ) )
        self.shell.set_result( self.value )

#-- EOF ------------------------------------------------------------------------
