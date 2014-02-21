"""
# SetEditor Demo #

This example demonstrates using the various styles of the **SetEditor**, which
allows the user to select a set of values from among a finite set of possible
legal values.

Typically, a **SetEditor** is used to edit a list of values which must be
constrained to contain a unique (non-duplicated) collection of values chosen
from a known universe of statically or dynamically specified values.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Item, Group, View, Tabbed, SetEditor

#-- SetEditorDemo Class --------------------------------------------------------

class SetEditorDemo ( HasFacets ):
    """ Defines the SetEditor demo class.
    """

    # Define a facet each for four SetEditor variants:
    unord_nma_set = List( editor = SetEditor(
        values             = [ 'kumquats', 'pomegranates', 'kiwi' ],
        can_move_all       = False,
        left_column_title  = 'Available Fruit',
        right_column_title = 'Exotic Fruit Bowl' )
    )

    unord_ma_set = List( editor = SetEditor(
        values             = [ 'kumquats', 'pomegranates', 'kiwi' ],
        left_column_title  = 'Available Fruit',
        right_column_title = 'Exotic Fruit Bowl' )
    )

    ord_nma_set = List( editor = SetEditor(
        values             = [ 'apples', 'berries', 'cantaloupe' ],
        ordered            = True,
        can_move_all       = False,
        left_column_title  = 'Available Fruit',
        right_column_title = 'Fruit Bowl' )
    )

    ord_ma_set = List( editor = SetEditor(
        values             = [ 'apples', 'berries', 'cantaloupe' ],
        ordered            = True,
        left_column_title  = 'Available Fruit',
        right_column_title = 'Fruit Bowl' )
    )

    # SetEditor display, unordered, no move-all buttons:
    no_nma_group = Group(
        Item( 'unord_nma_set', style = 'simple' ),
        label       = 'Unord I',
        show_labels = False
    )

    # SetEditor display, unordered, move-all buttons:
    no_ma_group = Group(
        Item( 'unord_ma_set', style = 'simple' ),
        label       = 'Unord II',
        show_labels = False
    )

    # SetEditor display, ordered, no move-all buttons:
    o_nma_group = Group(
        Item( 'ord_nma_set', style = 'simple' ),
        label       = 'Ord I',
        show_labels = False
    )

    # SetEditor display, ordered, move-all buttons:
    o_ma_group = Group(
        Item( 'ord_ma_set', style = 'simple' ),
        label       = 'Ord II',
        show_labels = False
    )

    # The view includes one group per data type. These will be displayed
    # on separate tabbed panels:
    view = View(
        Tabbed(
            no_nma_group,
            no_ma_group,
            o_nma_group,
            o_ma_group
        ),
        title   = 'SetEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

demo = SetEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------