"""
# SlideshowEditor #
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Image, View, UItem, HSplit, VSplit, \
           SlideshowEditor, ImageZoomEditor

from facets.ui.image \
    import ImageLibrary

#-- SlideshowEditorDemo class --------------------------------------------------

class SlideshowEditorDemo ( HasFacets ):

    images   = List
    images2  = List
    selected = Image

    def default_facets_view ( self ):
        return View(
            HSplit(
                VSplit(
                    UItem( 'images2',
                           label  = 'Slideshow 1',
                           dock   = 'tab',
                           editor = SlideshowEditor(
                                        hold        = 0.5,
                                        transition  = 0.4,
                                        transitions = 'left, right',
                                        transition_order = 'random' ),
                           width  = -50,
                           height = -50
                    ),
                    UItem( 'selected',
                           label  = 'Image Zoom',
                           dock   = 'tab',
                           editor = ImageZoomEditor( channel = 'hue' ),
                           width  = -50,
                           height = -100
                    )
                ),
                UItem( 'images',
                       label  = 'Slideshow 2',
                       dock   = 'tab',
                       editor = SlideshowEditor(
                           selected    = 'selected',
                           image_order = 'shuffle',
                           transitions = 'down, left, up, right'
                       ),
                       width = -200
                )
            ),
            width  = 0.75,
            height = 0.90
        )

    def _images_default ( self ):
        try:
            return ImageLibrary().catalog[ 'demo' ].image_names
        except:
            return ImageLibrary().catalog[ 'led'  ].image_names

    def _images2_default ( self ):
        return ImageLibrary().catalog[ 'particles' ].image_names

#-- Create the demo ------------------------------------------------------------

demo = SlideshowEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
