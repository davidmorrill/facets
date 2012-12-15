"""
Implementation of a CompoundEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the CompoundEditor
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