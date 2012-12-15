"""
Defines the ImageCollector tool for collecting input images and organizing,
displaying and selecting them.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Range, List, Bool, Tuple, Button, Instance, Image, Theme, View, \
           HToolbar, UItem, ThemedCheckboxEditor, SyncValue, spring

from facets.ui.editors.light_table_editor \
    import LightTableEditor, ThemedImage, GridLayout, HLSATransform

from facets.ui.pyface.timer.api \
    import do_after

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ImageCollector' class:
#-------------------------------------------------------------------------------

class ImageCollector ( Tool ):
    """ Defines the ImageCollector tool for collecting input images and
        organizing, displaying and selecting them.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Image Collector'

    # The input image:
    input_image = Image( connect = 'to: input image' )

    # The current output image:
    output_image = Image( connect = 'from: output image' )

    # The list of currently collected images:
    images = List # ( Image )

    # The maximum number of images to collect:
    max_images = Range( 1, 500, 25, save_state = True )

    # Image width (when 'actual_size' is False):
    width = Range( 16, None, 150, save_state = True )

    # Image display ratio (horizontal/vertical):
    ratio = Range( 0.1, 10.0, 1.0, save_state = True )

    # The size of hover images to display:
    hover_dxy  = Range( 0, 1024, 300, save_state = True )
    hover_size = Tuple( 300, 300 )

    # Are input images being collected?
    enabled = Bool( True )

    # Event fired to clear all current images:
    clear = Button( '@icons2:Delete' )

    # The GridLayout used to display the images on the light table:
    layout = Instance( GridLayout, { 'margin': 0, 'spacing': 0, 'width': 150 } )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'images',
                   editor = LightTableEditor(
                       selection_mode = 'item',
                       selected       = 'output_image',
                       hover_size     = SyncValue( self, 'hover_size' ),
                       layout         = self.layout,
                       adapter        = ThemedImage(
                           normal_theme = Theme( '@xform:b?l20', content = 5 ),
                           transform    = HLSATransform( lightness = -0.15 ),
                           lightness    = 0.12 ) )
            ),
            id = 'facets.extra.tools.image_collector.ImageCollector'
        )


    options = View(
        HToolbar(
            UItem( 'clear', tooltip = 'Clear all images' ),
            UItem( 'enabled',
                   editor = ThemedCheckboxEditor(
                       image       = '@icons2:GearExecute',
                       on_tooltip  = 'Images are being collected (click to '
                                     'disable)',
                       off_tooltip = 'Images are not being collected '
                                     '(click to enable)' )
            ),
            Scrubber( 'max_images', 'Maximum number of images to collect',
                      width = 50 ),
            Scrubber( 'width', 'Width of each image', width = 50 ),
            Scrubber( 'ratio', 'Ratio of width to height for each image',
                      increment = 0.01 ),
            Scrubber( 'hover_dxy', 'Width and height of mouse hover images',
                      increment = 10, label = 'Hover size' ),
            spring,
            group_theme = Theme( '@xform:b?L10', content = ( 4, 0, 4, 4 ) ),
            id          = 'tb'
        ),
        id = 'facets.extra.tools.image_collector.ImageCollector.options'
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _input_image_set ( self, image ):
        """ Handles the 'input_image' facet being modified.
        """
        if self.enabled and (image is not None):
            self.images.append( image )
            self._check_count()


    def _max_images_set ( self ):
        """ Handles the 'max_images' facet being changed.
        """
        do_after( 1000, self._check_count )


    def _width_set ( self, width ):
        """ Handles the 'width' facet being chnged.
        """
        self.layout.width = width


    def _ratio_set ( self, ratio ):
        """ Handles the 'ratio' facet being chnged.
        """
        self.layout.ratio = ratio


    def _hover_dxy_set ( self, size ):
        """ Handles the 'hover_dxy' facet being changed.
        """
        self.hover_size = ( size, size )


    def _clear_set ( self ):
        """ Handles the 'clear' event being fired.
        """
        del self.images[:]

    #-- Private Methods --------------------------------------------------------

    def _check_count ( self ):
        """ Checks the number of images against the maximum image count and
            eliminates any excess images.
        """
        n = len( self.images ) - self.max_images
        if n > 0:
            del self.images[ : n ]

#-- EOF ------------------------------------------------------------------------
