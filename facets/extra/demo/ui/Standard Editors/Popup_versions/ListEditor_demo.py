"""
Implemention of a ListEditor demo plugin for Facets UI demo program

This demo shows each of the four styles of ListEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Str, Item, Group, View

#-- ListEditorDemo Class -------------------------------------------------------

class ListEditorDemo ( HasFacets ):
    """ This class specifies the details of the BooleanEditor demo.
    """

    # The Facet to be displayed in the editor:
    play_list = List( Str, [ "The Merchant of Venice", "Hamlet", "MacBeth" ] )

    # Items are used to define display; one per editor style:
    list_group = Group( Item( 'play_list', style = 'simple', label = 'Simple' ),
                        Item( '_' ),
                        Item( 'play_list', style = 'custom', label = 'Custom' ),
                        Item( '_' ),
                        Item( 'play_list', style = 'text', label = 'Text' ),
                        Item( '_' ),
                        Item( 'play_list',
                              style = 'readonly',
                              label = 'ReadOnly' ) )

    # Demo view:
    view1 = View(
        list_group,
        title   = 'ListEditor',
        buttons = [ 'OK' ],
        height  = 400,
        width   = 400
    )

#-- Create the demo ------------------------------------------------------------

popup = ListEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------