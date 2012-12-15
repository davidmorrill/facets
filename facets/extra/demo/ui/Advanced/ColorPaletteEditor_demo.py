"""
A demo of the ColorPaletteEditor which allows the user to pick colors using a
user customizable color palette.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Color, View, VGroup, UItem, HLSColorEditor, \
           ColorPaletteEditor

#-------------------------------------------------------------------------------
#  'ColorPaletteEditorDemo' class:
#-------------------------------------------------------------------------------

class ColorPaletteEditorDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The color being edited:
    color = Color( 0x8080FF )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            UItem( 'color',
                   editor = HLSColorEditor(),
                   height = -35
            ),
            group_theme = '#themes:tool_options_group'
        ),
        VGroup(
            UItem( 'color',
                   id        = 'color_editor',
                   resizable = True,
                   editor    = ColorPaletteEditor(
                       cell_size    = 25,
                       cell_rows    = 1,
                       cell_columns = 1,
                       alpha        = True )
            ),
            group_theme = '#themes:tool_options_group'
        ),
        title  = 'Color Palette Editor Demo',
        id     = 'facets.extra.demo.ui.Advanced.ColorPaletteEditor_demo',
        width  = 250,
        height = 400
    )

#-- Create the demo ------------------------------------------------------------

demo = ColorPaletteEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------