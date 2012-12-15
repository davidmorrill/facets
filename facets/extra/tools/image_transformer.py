"""
Defines the image transformer tool that allows performing simple HLSA-based
transformations on images.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Any, Instance, Color, Image, Theme, SyncValue, View, HToolbar, \
           VGroup, Item, UItem

from facets.ui.editors.hls_color_editor \
    import HLSColorEditor

from facets.extra.helper.image \
    import HLSADerivedImage

from facets.extra.editors.hlsa_derived_image_editor \
    import HLSADerivedImageEditor

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ImageTransformer' class:
#-------------------------------------------------------------------------------

class ImageTransformer ( Tool ):
    """ Defines the image transformer tool that allows performing simple
        HLSA-based transformations on images.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Image Transformer' )

    # The item external tools connect to provide the image to view:
    value = Any( connect = 'to' )

    # The current image being transformed:
    image = Image( '@xform:li', cache = False )

    # The derived image beind edited:
    derived_image = Instance( HLSADerivedImage, connect = 'from' )

    # The encoding of the current derived image:
    encoded = Str

    # The background color used for the ImageZoomEditors:
    bg_color = Color( 0x303030 )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                UItem( 'derived_image',
                       id     = 'image',
                       editor = HLSADerivedImageEditor(
                           encoded  = 'encoded',
                           bg_color = SyncValue( self, 'bg_color' ) )
                )
            ),
            id = 'facets.extra.tools.image_transformer.ImageTransformer',
        )


    options = View(
        HToolbar(
            Item( 'encoded', width = 0.25 ),
            '_',
            UItem( 'bg_color',
                   editor = HLSColorEditor( edit = 'lightness' ),
                   width  = 0.75
            ),
            group_theme = Theme( '@xform:b?L10', content = 1 ),
            id          = 'tb'
        ),
        id = 'facets.extra.tools.image_transformer.ImageTransformer.options',
    )

    #-- Facet Default Values ---------------------------------------------------

    def _derived_image_default ( self ):
        return HLSADerivedImage( base_image = self.image )

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


    def _image_set ( self, image ):
        """ Handles the 'image' facet being changed.
        """
        self.derived_image = HLSADerivedImage( base_image = image )

#-- EOF ------------------------------------------------------------------------