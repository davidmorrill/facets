"""
# Multi-select String List #

A demo showing how to use a **GridEditor** to create a multi-select list box.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, List, Str, Property, View, HGroup, Item, \
           GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- MultiSelectAdapter Class ---------------------------------------------------

class MultiSelectAdapter ( GridAdapter ):

    columns = [ ( 'Value', 'value' ) ]

    value_text = Property

    def _get_value_text ( self ):
        return self.item

#-- MultiSelect Class ----------------------------------------------------------

class MultiSelect ( HasPrivateFacets ):

    choices  = List( Str )
    selected = List( Str )

    view = View(
        HGroup(
            Item( 'choices',
                  show_label = False,
                  editor     = GridEditor(
                                   adapter        = MultiSelectAdapter,
                                   operations     = [],
                                   show_titles    = False,
                                   selected       = 'selected',
                                   selection_mode = 'rows' )
            ),
            Item( 'selected',
                  show_label = False,
                  editor     = GridEditor(
                                   adapter      = MultiSelectAdapter,
                                   operations   = [],
                                   show_titles  = False )
            )
        )
    )

#-- Create the demo ------------------------------------------------------------

demo = MultiSelect(
    choices = [ 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                'nine', 'ten'
] )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------