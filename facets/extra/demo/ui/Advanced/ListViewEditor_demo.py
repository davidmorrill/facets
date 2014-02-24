"""
# ListViewEditor Demo #

This example provides a simple demonstration of the **ListViewEditor**, which
can be used for editing and displaying lists of objects. In this case the
objects are all strings, but other data types can be edited as well. In fact,
the list of objects being edited does not need to be homogenous, and different
data types can appear in the same list, each with their own specific editor.

Refer also to the *Todo mvc* demo in the *Applications* folder for another
example which edits a list of **ToDo** objects.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Str, View, UItem, ListViewEditor

#-- ShoppingListDemo Class -----------------------------------------------------

class ShoppingListDemo ( HasFacets ):

    # The list of things to buy at the store:
    shopping_list = List( Str )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        UItem( 'shopping_list', editor = ListViewEditor() ),
        title  = 'Shopping List',
        width  = 0.2,
        height = 0.5
    )

    def _shopping_list_default ( self ):
        return [
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
       ]

#-- Create the demo ------------------------------------------------------------

demo = ShoppingListDemo

#-- Run the demo (in invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------