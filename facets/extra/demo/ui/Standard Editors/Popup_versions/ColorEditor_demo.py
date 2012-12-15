"""
Implementation of a ColorEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the ColorEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Color, Item, Group, View

#-- ColorEditorDemo Class ------------------------------------------------------

class ColorEditorDemo ( HasFacets ):
    """ This class specifies the details of the ColorEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    color_facet = Color

    # Items are used to define the demo display - one item per editor style:
    color_group = Group(
        Item( 'color_facet', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'color_facet', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'color_facet', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'color_facet', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view1 = View(
        color_group,
        title   = 'ColorEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

popup = ColorEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------