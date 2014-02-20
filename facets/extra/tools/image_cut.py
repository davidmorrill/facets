"""
Defines the ImageCut tool that exports a collection of subimages based on a
single input image and a list of regions within the image.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Enum, Bool, Color, Image, List, SyncValue, View, HGroup, \
           VGroup, Item, UItem, ImageZoomEditor, HLSColorEditor, spring

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ImageCut' class:
#-------------------------------------------------------------------------------

class ImageCut ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'ImageCut'

    # The channel data to display in the ImageZoomEditor:
    channel = Enum( 'hue', [ 'none', 'red', 'green', 'blue', 'alpha',
                             'hue', 'lightness', 'saturation' ],
                    save_state = True )

    # Should delta information be displayed:
    delta = Bool( False, save_state = True )

    # The background color to use for the ImageZoomEditor:
    bg_color = Color( 0x303030, save_state = True )

    # The item external tools connect to provide the image to view:
    value = Any( connect = 'to' )

    # The image from which the subimages are being extracted:
    input_image = Image( cache = False )

    # The current exported subimage:
    output_image = Image( connect = 'from' )

    # The list of input regions used for extracting the subimages:
    regions = List( connect = 'to' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'input_image',
                   editor = ImageZoomEditor(
                                channel    = SyncValue( self, 'channel'  ),
                                delta      = SyncValue( self, 'delta'    ),
                                overlays   = SyncValue( self, 'regions'  ),
                                bg_color   = SyncValue( self, 'bg_color' ),
                                allow_drop = True )
            )
        )


    options = View(
        VGroup(
            HGroup(
                Item( 'channel' ),
                Item( 'delta', label = 'Show delta' ),
                Item( 'bg_color',
                      label  = 'Background color',
                      width  = -350,
                      editor = HLSColorEditor(
                          edit  = 'lightness',
                          cells = 15
                      )
                ),
                spring
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        if isinstance( value, ( list, tuple ) ) and (len( value ) > 0):
            value = value[0]

        if isinstance( value, ( basestring, AnImageResource ) ):
            self.input_image = value
        else:
            self.input_image = '@std:alert16'


    def _regions_set ( self ):
        """ Handles the 'regions' facets being changed by exporting all of the
            subimages corresponding to the regions within the current input
            image.
        """
        image = self.input_image
        for region in self.regions:
            self.output_image = image.crop( *region )

#-- EOF ------------------------------------------------------------------------