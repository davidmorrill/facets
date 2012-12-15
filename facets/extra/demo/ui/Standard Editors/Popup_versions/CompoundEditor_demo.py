"""
Implementation of a CompoundEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the CompoundEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Facet, Range, Item, Group, View

#-- CompoundEditorDemo Class ---------------------------------------------------

class CompoundEditorDemo ( HasFacets ):
    """ This class specifies the details of the CompoundEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    compound_facet = Facet( 1, Range( 1, 6 ), 'a', 'b', 'c', 'd', 'e', 'f' )


    # Display specification (one Item per editor style):
    comp_group = Group(
        Item( 'compound_facet', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'compound_facet', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( 'compound_facet', style = 'text', label = 'Text' ),
        Item( '_' ),
        Item( 'compound_facet',
             style = 'readonly',
             label = 'ReadOnly' )
    )

    # Demo view:
    view1 = View(
        comp_group,
        title   = 'CompoundEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

popup = CompoundEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------