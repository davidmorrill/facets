"""
Implementation of a BooleanEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the BooleanEditor
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Bool, Item, Group, View

#-- BooleanEditorDemo Class ----------------------------------------------------

class BooleanEditorDemo ( HasFacets ):
    """ This class specifies the details of the BooleanEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    boolean_facet = Bool

    # Items are used to define the demo display - one Item per editor style:
    bool_group = Group(
        Item( 'boolean_facet', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'boolean_facet', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( 'boolean_facet', style = 'text', label = 'Text' ),
        Item( '_' ),
        Item( 'boolean_facet', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view1 = View(
        bool_group,
        title   = 'BooleanEditor',
        buttons = [ 'OK' ],
        width   = 300
    )

#-- Create the demo ------------------------------------------------------------

popup = BooleanEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------