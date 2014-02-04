"""
# LightTableEditor #
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Instance, Any, Button, Image, Theme, View, Tabbed, \
           HGroup, UItem, Item, ScrubberEditor, ImageZoomEditor, spring

from facets.ui.image \
    import ImageLibrary

from facets.ui.editors.light_table_editor \
    import LightTableEditor, LightTableAnimator, GridLayout

#-- Helper functions -----------------------------------------------------------

def sitem ( name, increment = 1 ):
    return Item( name,
        width      = -40,
        editor     = ScrubberEditor( increment = increment ),
        item_theme = '#themes:ScrubberEditor'
    )

#-- LightTableDemo class -------------------------------------------------------

class LightTableDemo ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of images to display:
    images = List

    # The current selected image name:
    selected = Any

    # The current selected image:
    image = Image

    # The GridLayout used to display the images on the light table:
    layout = Instance( GridLayout,
                       dict( width = 48, margin = 12, spacing = 6 ) )

    # The LightTableAnimator used to animate the images on the light table:
    animator = Instance( LightTableAnimator, () )

    # Event fired to start/stop light table image animation:
    animate = Button( '@icons2:GearExecute' )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Tabbed(
                 UItem( 'images',
                        label  = 'Light Table',
                        editor = LightTableEditor(
                            selection_mode = 'item',
                            selected       = 'selected',
                            layout         = self.layout,
                            animator       = self.animator,
                            theme          = Theme( '@tiles:FibreBoard1.jpg',
                                                    tiled = True )
                        ),
                        dock = 'tab'
                 ),
                 UItem( 'image',
                        label  = 'Image Zoom',
                        editor = ImageZoomEditor( channel = 'red' ),
                        dock   = 'tab'
                 )
            ),
            HGroup(
                spring,
                UItem( 'animate' ),
                sitem( 'object.animator.time',  0.10 ),
                sitem( 'object.animator.cycle', 0.05 ),
                sitem( 'object.animator.level', 0.01 ),
                '_',
                sitem( 'object.layout.margin'  ),
                sitem( 'object.layout.spacing' ),
                sitem( 'object.layout.width'   ),
                sitem( 'object.layout.ratio', 0.01 ),
                group_theme = '@xform:b?L10'
            ),
            width     = 0.8,
            height    = 0.8,
            resizable = True
        )

    #-- Facet Default Values ---------------------------------------------------

    def _images_default ( self ):
        return [
            image_info.image_name
            for image_info in ImageLibrary().catalog[ 'particles' ].images
        ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _animate_set ( self ):
        """ Handles the 'animate' event being fired.
        """
        if self.animator.running:
            self.animator.stop = True
        else:
            self.animator.start = True

    def _selected_set ( self, selected ):
        self.image = selected

    #-- Public Methods ---------------------------------------------------------

    def dispose ( self ):
        self.animator.stop = True

#-- Create the demo ------------------------------------------------------------

demo = LightTableDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
