"""
Defines the image zoomer tool that allows zooming into and out of images.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Enum, Bool, Color, Image, SyncValue, View, VGroup, HGroup, \
           Item, ImageZoomEditor, HLSColorEditor, spring

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ImageZoomer' class:
#-------------------------------------------------------------------------------

class ImageZoomer ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Image Zoomer'

    # The channel data to display:
    channel = Enum( 'hue', [ 'none', 'red', 'green', 'blue', 'alpha',
                             'hue', 'lightness', 'saturation' ],
                    save_state = True )

    # Should delta information be displayed:
    delta = Bool( False, save_state = True )

    # The background color to use for the ImageZoomEditor:
    bg_color = Color( 0x303030, save_state = True )

    # The current image being zoomed:
    image = Image( cache = False )

    # The item external tools connect to provide the image to view:
    value = Any( connect = 'to' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Item( 'image',
                  show_label = False,
                  editor     = ImageZoomEditor(
                                   channel    = SyncValue( self, 'channel'  ),
                                   delta      = SyncValue( self, 'delta'    ),
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
            self.image = value
        else:
            self.image = '@std:alert16'

#-- EOF ------------------------------------------------------------------------