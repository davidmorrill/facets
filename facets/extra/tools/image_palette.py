"""
Defines the ImagePalette tool for rapdily creating HLSA transform based
variations of an input image.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
import Range, Tuple, List, Instance, Image, Theme, View, VGroup, HSplit, \
       UItem, on_facet_set

from facets.ui.pyface.timer.api \
    import do_after

from facets.extra.helper.image \
    import HLSATransform, hlsa_derived_image

from facets.ui.editors.light_table_editor \
    import LightTableEditor, ThemedImage, GridLayout

from facets.extra.helper.themes \
    import Scrubber, Slider

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ImagePalette' class:
#-------------------------------------------------------------------------------

class ImagePalette ( Tool ):
    """ Defines the ImagePalette tool for rapdily creating HLSA transform based
        variations of an input image.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Image Palette'

    # The input image:
    input_image = Image( connect = 'to: input image' )

    # A version of the current input image scaled to the 'width' setting (for
    # performance reasons):
    scaled_image = Image

    # The current output image:
    output_image = Image( connect = 'from: output image' )

    # The currently selected image:
    selected_image = Image

    # The number of variation images to create:
    count = Range( 1, 250, 9, update = True, save_state = True )

    # The width of the LightTable images:
    width = Range( 16, 500, 120, save_state = True )

    # The hue variation to use:
    hue = Tuple( ( 0.0, 1.0 ), update = True, save_state = True )

    # The lightness variation to use:
    lightness = Tuple( ( 0.0, 0.0 ), update = True, save_state = True )

    # The saturation variation to use:
    saturation = Tuple( ( 0.0, 0.0 ), update = True, save_state = True )

    # The alpha variation to use:
    alpha = Tuple( ( 0.0, 0.0 ), update = True, save_state = True )

    # The current list of variation images:
    images = List # ( Image )

    # The GridLayout used to display the images on the light table:
    layout = Instance( GridLayout, { 'margin': 0, 'spacing': 0, 'width': 150 } )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            HSplit(
                UItem( 'images',
                       width  = 470,
                       editor = LightTableEditor(
                           selection_mode = 'item',
                           selected       = 'selected_image',
                           layout         = self.layout,
                           adapter        = ThemedImage(
                               normal_theme = Theme( '@xform:b?l20',
                                                     content = 5 ),
                               transform = HLSATransform( lightness = -0.15 ),
                               lightness = 0.12 ) )
                ),
                VGroup(
                    VGroup(
                        Scrubber( 'count', 'Number of variations to create' ),
                        Scrubber( 'object.layout.width',
                                  'Width of each image' ),
                        Scrubber( 'object.layout.ratio',
                            'Ratio of width to height for each image',
                            increment = 0.01
                        ),
                        label       = 'Light Table',
                        group_theme = '@xform:btd?L10'
                    ),
                    VGroup(
                        Slider( 'hue', low = 0.0, high = 1.0 ),
                        Slider( 'lightness' ),
                        Slider( 'saturation' ),
                        Slider( 'alpha' ),
                        label       = 'HLSA Transform',
                        group_theme = '@xform:btd?L10'
                    )
                ),
                id          = 'splitter',
                group_theme = Theme( '@xform:b?L25', content = -1 )
            ),
            title     = 'Image Palette',
            id        = 'facets.extra.tools.image_palette.ImagePalette',
            width     = 0.5,
            height    = 0.5,
            resizable = True
        )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'input_image, layout:width' )
    def _scaled_image_modified ( self ):
        """ Handles any facet affecting the scaled version of the image being
            changed.
        """
        image = self.input_image
        if image is not None:
            self.scaled_image = image.scale( ( self.layout.width, 0 ) )


    def _scaled_image_set ( self ):
        """ Handles the 'scaled_image' facet being changed.
        """
        self._create_variations()


    def _selected_image_set ( self, image ):
        """ Handles the 'selected_image' facet being changed.
        """
        if image is not None:
            image = hlsa_derived_image( self.input_image, image.transform )

        self.output_image = image


    @on_facet_set( '+update, input_image.modified' )
    def _images_modified ( self ):
        """ Handles any facet affecting the list of variation images being
            changed.
        """
        do_after( 150, self._create_variations )

    #-- Private Methods --------------------------------------------------------

    def _create_variations ( self ):
        """ Creates all of the variations of the input image.
        """
        images = []
        image  = self.scaled_image
        if image is not None:
            hue,        hue_delta        = self._range_for( self.hue )
            lightness,  lightness_delta  = self._range_for( self.lightness )
            saturation, saturation_delta = self._range_for( self.saturation )
            alpha,      alpha_delta      = self._range_for( self.alpha )
            for i in xrange( self.count ):
                transform = HLSATransform(
                    hue        = hue,
                    lightness  = lightness,
                    saturation = saturation,
                    alpha      = alpha
                )
                images.append( hlsa_derived_image( image, transform ) )
                hue        += hue_delta
                lightness  += lightness_delta
                saturation += saturation_delta
                alpha      += alpha_delta

        self.images = images


    def _range_for ( self, low_high ):
        """ Returns the starting value and increment 'delta' for the (low, high)
            tuple specified by *low_high*.
        """
        low, high = low_high
        delta     = high - low
        if delta == 0.0:
            return ( low, delta )

        return ( low, delta / self.count )

#-- Run the test case (if invoked from the command line) -----------------------

if __name__ == '__main__':
    ImagePalette(
        input_image = r'C:\Assembla\trunk\facets_extra\assets\Facets_power.png'
    ).edit_facets()

#-- EOF ------------------------------------------------------------------------
