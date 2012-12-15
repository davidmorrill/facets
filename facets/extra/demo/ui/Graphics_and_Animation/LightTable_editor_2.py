"""
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Instance, Any, Image, Theme, View, HSplit, VSplit, \
           UItem, ImageZoomEditor

from facets.ui.image \
    import ImageLibrary

from facets.ui.editors.light_table_editor \
    import LightTableEditor, GridLayout, ThemedImage

#-- LightTableDemo class -------------------------------------------------------

class LightTableDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of images to display:
    images = List

    # The current selected image name:
    selected = Any

    # The current selected image:
    image = Image

    # The horizontal GridLayout used to display the images on the light table:
    layout_horizontal = Instance( GridLayout,
                                  dict( margin = 0, spacing = 0, rows = 1 ) )

    # The vertical GridLayout used to display the images on the light table:
    layout_vertical = Instance( GridLayout,
                                dict( margin = 0, spacing = 0, rows = 2 ) )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VSplit(
                UItem( 'images', editor = LightTableEditor(
                    selection_mode  = 'item',
                    show_scrollbars = False,
                    hover_size      = ( 110, 110 ),
                    selected        = 'selected',
                    scroll          = 'horizontal',
                    layout          = self.layout_horizontal,
                    adapter         = ThemedImage(
                        normal_theme = Theme( '@xform:b?l25', content = 4 ) ) )
                ),
                HSplit(
                    UItem( 'images', editor = LightTableEditor(
                        selection_mode  = 'item',
                        show_scrollbars = False,
                        hover_size      = ( 110, 110 ),
                        selected        = 'selected',
                        layout          = self.layout_vertical,
                        adapter         = ThemedImage(
                        normal_theme = Theme( '@xform:b?l25', content = 4 ) ) )
                    ),
                    UItem( 'image',
                           editor = ImageZoomEditor( channel = 'red' )
                    )
                )
            ),
            width     = 0.70,
            height    = 0.90,
            resizable = True
        )

    #-- Facet Default Values ---------------------------------------------------

    def _images_default ( self ):
        return [
            image_info.image_name
            for image_info in ImageLibrary().catalog[ 'particles' ].images
        ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_set ( self, selected ):
        self.image = selected

#-- Create the demo ------------------------------------------------------------

demo = LightTableDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------