"""
# ColorEditor Demo #

This example demonstrates using the various styles of the **ColorEditor**,
which is a color picker used for editing facets with a color value, such as one
defined using the Color type.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Color, Item, Group, View

#-- ColorEditorDemo Class ------------------------------------------------------

class ColorEditorDemo ( HasFacets ):
    """ Defines the main ColorEditor demo. """

    # Define a Color facet to view:
    color_facet = Color

    # Items are used to define the demo display, one item per editor style:
    color_group = Group(
        Item( 'color_facet', style = 'simple',   label = 'Simple' ),
        Item(  '_' ),
        Item( 'color_facet', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'color_facet', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'color_facet', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view
    view1 = View(
        color_group,
        title     = 'ColorEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = ColorEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------