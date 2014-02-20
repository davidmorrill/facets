"""
# ListEditor Demo #

This example demonstrates using the various styles of the **ListEditor**, which
allows the user to add, delete and update values for a facet whose value is a
list of strings.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, List, Str

from facets.api \
    import Item, Group, View

#-- ListEditorDemo Class -------------------------------------------------------

class ListEditorDemo ( HasFacets ):
    """ Defines the main ListEditor demo class. """

    # Define a List facet to display:
    play_list = List( Str, [ "The Merchant of Venice", "Hamlet", "MacBeth" ] )

    # Items are used to define display, one per editor style:
    list_group = Group(
        Item( 'play_list', style = 'simple',   label = 'Simple', height = 75 ),
        Item( '_' ),
        Item( 'play_list', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'play_list', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'play_list', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        list_group,
        title     = 'ListEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = ListEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------