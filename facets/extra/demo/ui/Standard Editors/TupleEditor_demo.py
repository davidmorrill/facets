"""
# TupleEditor Demo #

This example demonstrates using the **TupleEditor**, which, as its name implies,
allows editing facets whose values are Python *tuples*.

Each element of an edited tuple has its own specific sub-editor, based on the
element's data type. Since Python tuples are immutable, changing any tuple
element's value causes a new tuple containing the changed value to be assigned
to the facet being edited.

In this example, the edited tuple has the type:

    Tuple( Color, Range( 1, 10 ), Str )

which defines a tuple whose:

- First value is a color.
- Second value is an integer in the range from 1 to 10.
- Third value is an arbitrary string.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Tuple, Color, Range, Str, Item, Group, View

#-- TupleEditorDemo Class ------------------------------------------------------

class TupleEditorDemo ( HasFacets ):

    # Define a tuple-based facet to edit:
    tuple = Tuple( Color, Range( 1, 10 ), Str )

    # Demo view:
    view = View(
        Item( 'tuple' ),
        title = 'TupleEditor',
    )

#-- Create the demo ------------------------------------------------------------

demo = TupleEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------