"""
# CompoundEditor Demo #

This example demonstrates using the various styles of the **CompoundEditor**,
which is the default editor used for *compound* facets.

A *compound* facet is created when several facets are combined to form a new
facet which accepts any value which is valid for at least one of the component
facets. The CompoundEditor synthesizes a editor for such a facet by combining
the default editors for each of the component facets.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Facet, Range

from facets.api \
    import Item, Group, View

#-- CompoundEditorDemo Class ---------------------------------------------------

class CompoundEditorDemo ( HasFacets ):
    """ Defines the main CompoundEditor demo class.
    """

    # Define a compund facet to view:
    compound_facet = Facet( 1, Range( 1, 6 ), 'a', 'b', 'c', 'd', 'e', 'f' )


    # Display specification (one Item per editor style):
    comp_group = Group(
        Item( 'compound_facet', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'compound_facet', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'compound_facet', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'compound_facet', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        comp_group,
        title     = 'CompoundEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = CompoundEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------