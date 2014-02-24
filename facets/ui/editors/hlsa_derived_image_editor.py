"""
Defines an editor for an HSLADerivedImage object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Str, Color, Instance, Theme, UIEditor, ImageZoomEditor,    \
           BasicEditorFactory, View, Item, HSplit, VSplit, VGroup, toolkit, \
           on_facet_set

from facets.extra.helper.image \
    import HLSADerivedImage, HLSATransform

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The ImageZoomEditor used for viewing ImageResource objects:
image_editor = ImageZoomEditor( channel = 'hue' )

# The common group theme used by the various views:
GroupTheme = Theme( '@xform:btd?H61L20S9', content = ( 5, 5, 5, 5 ) )

# The common background group theme used by the various views:
BGTheme = '@xform:bg?L32'

#-------------------------------------------------------------------------------
#  '_HLSADerivedImageEditor' class:
#-------------------------------------------------------------------------------

class _HLSADerivedImageEditor ( UIEditor ):
    """ An editor for editing HLSADerivedImage objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The custom HLSADerived image used to display/visualize the mask:
    mask_image = Instance( HLSADerivedImage )

    # Local copy of the image being edited:
    image = Instance( HLSADerivedImage )

    # The current derived image encoding:
    encoded = Str

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        if self.factory.edit_mask:
            return View(
                VSplit(
                    HSplit(
                        Item( 'editor.mask_image',
                              show_label = False,
                              editor     = ImageZoomEditor(
                                  channel  = 'hue',
                                  float    = True,
                                  bg_color = self.factory.facet_value(
                                                                    'bg_color' )
                              ),
                        ),
                        VGroup(
                            VGroup(
                                Item( 'editor.image.mask', style = 'custom' ),
                                group_theme = GroupTheme,
                                show_labels = False,
                                label       = 'Mask'
                            ),
                            VGroup()
                        ),
                        id          = 'splitter1',
                        group_theme = '#themes:toolbar_group'
                    ),
                    self._mask_group(),
                    show_labels = False,
                    group_theme = BGTheme,
                    id          = 'main_splitter'
                ),
                id = 'facets.extra.helper.image.HLSADerivedImageEditor.masked'
            )

        return View(
            VGroup( self._mask_group(), group_theme = BGTheme ),
            id = 'facets.extra.helper.image.HLSADerivedImageEditor.unmasked'
        )

    #-- UIEditor Method Overrides ----------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        # We need to set up the image before creating the view, so force an
        # update now:
        self.update_editor()

        self.sync_value( self.factory.encoded, 'encoded', 'both' )

        return super( _HLSADerivedImageEditor, self ).init_ui( parent )

    #-- Editor Method Overrides ------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        image = self.value
        if image is not self._last_image:
            self._last_image = image
            if not isinstance( image, HLSADerivedImage ):
                image = HLSADerivedImage( base_image = image )

            self.image = image
            if self.factory.edit_mask:
                self.mask_image = HLSADerivedImage(
                    base_image       = image.base_image,
                    mask             = image.mask,
                    transform_masked = HLSATransform( alpha      = -0.8,
                                                      saturation = -1.0 )
                )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'image:encoded' )
    def _encoded_modified ( self ):
        """ Handles the image's 'encoded' facet being changed.
        """
        self.encoded = code = self.image.encoded
        if code != '':
            toolkit().clipboard().text = code


    def _encoded_set ( self, encoded ):
        """ Handles the 'encoded' facet being changed.
        """
        self.image.encoded = encoded

    #-- Private Methods --------------------------------------------------------

    def _mask_group ( self ):
        """ Returns the group containing the 'mask' editing items.
        """
        return HSplit(
            Item( 'editor.image',
                  show_label = False,
                  editor     = ImageZoomEditor(
                      channel  = 'hue',
                      float    = True,
                      bg_color = self.factory.facet_value( 'bg_color' )
                  )
            ),
            VGroup(
                VGroup(
                    Item( 'editor.image.transform',
                          style = 'custom'
                    ),
                    group_theme = GroupTheme,
                    show_labels = False,
                    label       = 'Unmasked Transform'
                ),
                VGroup(
                    Item( 'editor.image.transform_masked',
                          style = 'custom'
                    ),
                    group_theme = GroupTheme,
                    show_labels = False,
                    label       = 'Masked Transform'
                ),
                show_labels = False
            ),
            id          = 'splitter',
            group_theme = '#themes:toolbar_group'
        )

#-------------------------------------------------------------------------------
#  'HLSADerivedImageEditor' class:
#-------------------------------------------------------------------------------

class HLSADerivedImageEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _HLSADerivedImageEditor

    # Should the mask editor be displayed?
    edit_mask = Bool( True )

    # The optional object facet containing the current derived image encoding:
    encoded = Str

    # The background color to use for the ImageZoomEditors:
    bg_color = Color( 0x303030, facet_value = True )

#-- EOF ------------------------------------------------------------------------