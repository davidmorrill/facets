"""
Demonstrates the HLSColorEditor, an editor which allows the user to select a
color using a flexible HLSA (Hue, Lightness, Saturation, Alpha) based palette.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Range, Enum, Bool, Color, View, VSplit, VGroup, \
           HGroup, Item, SyncValue, HLSColorEditor, ScrubberEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Define a common scrubber editor to use for various fields:
se = ScrubberEditor()

#-------------------------------------------------------------------------------
#  'HLSColorEditorDemo' class:
#-------------------------------------------------------------------------------

class HLSColorEditorDemo ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The (nominal) number of color cells to display (per channel):
    cells = Range( 5, 50, 15 )

    # The size (in pixels) of each color cell square:
    size = Range( 9, 200, 40 )

    # The size of the border around each color cell:
    border = Range( 0, 2, 1 )

    # The empty of empty space between eah color cell:
    space = Range( 0, 5, 0 )

    # The editing style the color editor should support:
    edit = Enum( 'all', 'any', 'hue', 'saturation', 'lightness', 'alpha' )

    # The orientation of the color cells within the editor:
    orientation = Enum( 'horizontal', 'vertical' )

    # Does the color editor support an 'alpha' channel:
    alpha = Bool( True )

    # The current value of the color being edited:
    c = Color( 0xFF0000 )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VSplit(
                HGroup(
                    VGroup(
                        Item( 'cells',
                              item_theme = '#themes:ScrubberEditor',
                              editor     = se
                        ),
                        Item( 'size',
                              item_theme = '#themes:ScrubberEditor',
                              editor     = se
                        ),
                        Item( 'border',
                              item_theme = '#themes:ScrubberEditor',
                              editor     = se
                        ),
                        Item( 'space',
                              item_theme = '#themes:ScrubberEditor',
                              editor     = se
                        ),
                        Item( 'edit' ),
                        Item( 'orientation' ),
                        Item( 'alpha' )
                    ),
                    '_',
                    Item( 'c',
                          style      = 'readonly',
                          show_label = False,
                          width      = -300
                    )
                ),
                VGroup(
                    '_',
                    Item( 'c',
                          editor = HLSColorEditor(
                              cell_size   = SyncValue( self, 'size'        ),
                              cells       = SyncValue( self, 'cells'       ),
                              border      = SyncValue( self, 'border'      ),
                              space       = SyncValue( self, 'space'       ),
                              edit        = SyncValue( self, 'edit'        ),
                              orientation = SyncValue( self, 'orientation' ),
                              alpha       = SyncValue( self, 'alpha'       ) )
                    ),
                    show_labels = False
                )
            ),
            title  = 'HLS Color Editor Demo',
            id     = 'facets.extra.demo.ui.Advanced.HLSColorEditor_demo',
            width  = 500,
            height = 400
        )

#-- Create the demo ------------------------------------------------------------

demo = HLSColorEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------