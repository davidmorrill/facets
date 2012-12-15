"""
Implementation of a FontEditor demo plugin for Facets UI demo program.

This demo shows each of the four styles of the FontEditor
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.core_api \
    import HasFacets, Font

from facets.api \
    import Item, Group, View

#-- FontEditorDemo Class -------------------------------------------------------

class FontEditorDemo ( HasFacets ):
    """ Defines the main FontEditor demo class. """

    # Define a Font facet to view:
    font_facet = Font

    # Display specification (one Item per editor style):
    font_group = Group(
        Item( 'font_facet', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'font_facet', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'font_facet', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'font_facet', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        font_group,
        title     = 'FontEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

#-- Create the demo ------------------------------------------------------------

demo = FontEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------