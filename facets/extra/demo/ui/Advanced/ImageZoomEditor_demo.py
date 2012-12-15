"""
Demonstrates the ImageZoomEditor, an editor which allows zooming into and out
of an ImageResource image.

The editor supports the following operations:

 - Ctrl-drag the mouse to pan the image being edited around the view.

 - Use the mouse wheel to zoom into and out of the image. The image zooms around
   the current mouse position.

 - Ctrl-middle mouse button drag up and down to zoom into and out of the image.
   The image zooms around the original point under the pointer when the middle
   mouse button was pressed.

 - Right click the view to reset the image back to its original starting
   position in the top-left hand corner of the view with a 1:1 scale.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Image, Bool, Enum, Color, List, Tuple, Button, View, \
           HGroup, VGroup, Item, SyncValue, ImageZoomEditor, HLSColorEditor, \
           spring

#-------------------------------------------------------------------------------
#  Color Editor Definition:
#-------------------------------------------------------------------------------

color_editor = HLSColorEditor( cells = 9, cell_size = 9, edit = 'lightness' )

#-------------------------------------------------------------------------------
#  'ImageZoomEditorDemo' class:
#-------------------------------------------------------------------------------

class ImageZoomEditorDemo ( HasFacets ):
    """ Demonstrates a simple use of the ImageZoomEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The image being edited:
    image = Image( '@std:BlackChromeB' )

    # The editor background color:
    background_color = Color( 0x303030 )

    # The grid color:
    grid_color = Color( 0x707070 )

    # The current selection:
    selected = Tuple( 0, 0, 0, 0 )

    # The current list of overlay regions:
    overlays = List

    # Should delta values be displayed?
    delta = Bool( False )

    # Which channel should be displayed?
    channel = Enum( 'none', 'red', 'green', 'blue', 'alpha',
                    'hue', 'lightness', 'saturation' )

    # Clear the list of overlay regions:
    clear = Button( 'Clear' )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        """ Returns the view to display.
        """
        return View(
            VGroup(
                HGroup(
                    Item( 'background_color',
                          label  = 'Background',
                          editor = color_editor
                    ),
                    Item( 'grid_color',
                          label  = 'Grid',
                          editor = color_editor
                    ),
                    '_',
                    Item( 'channel' ),
                    Item( 'delta', label = 'Show delta' ),
                    '_',
                    spring,
                    Item( 'clear', show_label = False ),
                    group_theme = '@cells:mg'
                ),
                Item( 'image',
                      show_label = False,
                      editor     = ImageZoomEditor(
                          bg_color   = SyncValue( self, 'background_color' ),
                          grid_color = SyncValue( self, 'grid_color' ),
                          overlays   = SyncValue( self, 'overlays' ),
                          channel    = SyncValue( self, 'channel' ),
                          delta      = SyncValue( self, 'delta' ),
                          selected   = 'selected',
                      )
                )
            ),
            resizable = True,
            width     = 0.8,
            height    = 0.8
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _clear_set ( self ):
        """ Handles the 'clear' button being clicked.
        """
        del self.overlays[:]


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if (selected not in self.overlays) and (selected[0] >= 0):
            self.overlays.append( selected )

#-- Create a demo --------------------------------------------------------------

demo = ImageZoomEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------