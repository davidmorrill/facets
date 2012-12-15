"""
Implementation of a FontEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the FontEditor.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Font, Item, Group, View

#-- FontEditorDemo Class -------------------------------------------------------

class FontEditorDemo ( HasFacets ):
    """ This class specifies the details of the FontEditor demo.
    """

    # To demonstrate any given Facet editor, an appropriate Facet is required:
    font_facet = Font

    # Display specification (one Item per editor style):
    font_group = Group(
        Item( 'font_facet', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'font_facet', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( 'font_facet', style = 'text', label = 'Text' ),
        Item( '_' ),
        Item( 'font_facet', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view1 = View(
        font_group,
        title   = 'FontEditor',
        buttons = [ 'OK' ]
    )

#-- Create the demo ------------------------------------------------------------

popup = FontEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------