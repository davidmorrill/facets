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
    import Any, Enum, Bool, Color, Image, SyncValue, View, HGroup, Item, \
           ImageZoomEditor, HLSColorEditor, spring

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.extra.helper.multi_page_tool \
    import MultiPageTool, PageTool, OwnerValue

#-------------------------------------------------------------------------------
#  'ImageZoomerPage' class:
#-------------------------------------------------------------------------------

class ImageZoomerPage ( PageTool ):

    #-- Facet Definitions ------------------------------------------------------

    # The channel data to display:
    channel = OwnerValue

    # Should delta information be displayed:
    delta = OwnerValue

    # The background color to use for the ImageZoomEditor:
    bg_color = OwnerValue

    # The current image being zoomed:
    image = Image( cache = False )

    # The value describing the image to view:
    value = Any( connect = 'to' )

    # The name of the page:
    page_name = Any

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

    #-- Facet Default Values ---------------------------------------------------

    def _page_name_default ( self ):
        return (self.image.name if self.image is not None else None)

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

#-------------------------------------------------------------------------------
#  'ImageZoomer' class:
#-------------------------------------------------------------------------------

class ImageZoomer ( MultiPageTool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Image Zoomer'

    # The page tool class this tool creates and manages:
    page_tool_class = ImageZoomerPage

    # The channel data to display:
    channel = Enum( 'hue', [ 'none', 'red', 'green', 'blue', 'alpha',
                             'hue', 'lightness', 'saturation' ],
                    save_state = True )

    # Should delta information be displayed:
    delta = Bool( False, save_state = True )

    # The background color to use for the ImageZoomEditor:
    bg_color = Color( 0x303030, save_state = True )

    #-- Facet View Definitions -------------------------------------------------

    page_options = HGroup(
        Item( 'channel' ),
        Item( 'delta', label = 'Show delta' ),
        Item( 'bg_color',
              label  = 'Background color',
              width  = -350,
              editor = HLSColorEditor(
                  edit  = 'lightness',
                  cells = 15
              )
        )
    )

#-- EOF ------------------------------------------------------------------------