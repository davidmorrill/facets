"""
# ListStrEditor Demo #

Simple demonstration of the **ListStrEditor**, which can be used for editing and
displaying lists of strings, or other data that can be logically mapped to a
list of strings.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Str, View, Item, ListStrEditor

#-- ShoppingListDemo Class -----------------------------------------------------

class ShoppingListDemo ( HasFacets ):

    # The list of things to buy at the store:
    shopping_list = List( Str )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'shopping_list',
              show_label = False,
              editor = ListStrEditor( title = 'Shopping List', auto_add = True )
        ),
        title     = 'Shopping List',
        width     = 0.2,
        height    = 0.5,
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = ShoppingListDemo( shopping_list = [
    'Carrots',
    'Potatoes (5 lb. bag)',
    'Cocoa Puffs',
    'Ice Cream (French Vanilla)',
    'Peanut Butter',
    'Whole wheat bread',
    'Ground beef (2 lbs.)',
    'Paper towels',
    'Soup (3 cans)',
    'Laundry detergent'
] )

#-- Run the demo (in invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------