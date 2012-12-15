"""
A feature-enabled tool for tiling an input image.

To Do:
- Add an output image corresponding to the tileable version of the input image.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Str, Image, Color, Range, Button, View, VGroup, HToolbar, \
           UItem, Item, Include, SyncValue, HLSColorEditor,                \
           ThemedCheckboxEditor, on_facet_set

from facets.extra.editors.image_tiler_editor \
    import ImageTilerEditor

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ImageTiler' class:
#-------------------------------------------------------------------------------

class ImageTiler ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Image Tiler' )

    # The input image:
    image = Image( '@particles:face1', connect = 'to: image to tile' )

    # The scaled version of the image being tiled:
    scaled_image = Image

    # The current image scaling factor:
    scale = Range( 0.05, 5.0, 1.0 )

    # The current scaled image width:
    width = Range( 8, 1024, 32 )

    # The current scaled image height:
    height = Range( 8, 1024, 32 )

    # The background color for the editor:
    bg_color = Color( 0xF0F0F0, facet_value = True )

    # The width of the border to draw around each image:
    border = Range( 0, 32 )

    # The amount of horizontal spacing between tiled images:
    x_spacing = Range( -1024, 1024, 0 )

    # The amount of vertical spacing between tiled images:
    y_spacing = Range( -1024, 1024, 0 )

    # The amount of horizontal shift applied to each new row:
    x_shift = Range( -1024, 1024, 0 )

    # The amount of vertical shift applied to each new column:
    y_shift = Range( -1024, 1024, 0 )

    # The x coordinate of the top-left tiled image:
    x_origin = Range( -1024, 1024, 0 )

    # The y coordinate of the top-left tiled image:
    y_origin = Range( -1024, 1024, 0 )

    # Should the toolbar be displayed?
    show_toolbar = Bool( True )

    # Resets the controls back to their default values:
    reset = Button( '@icons2:Delete' )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                UItem( 'scaled_image',
                       editor = ImageTilerEditor(
                           bg_color  = SyncValue( self, 'bg_color'  ),
                           border    = SyncValue( self, 'border'    ),
                           x_spacing = SyncValue( self, 'x_spacing' ),
                           y_spacing = SyncValue( self, 'y_spacing' ),
                           x_shift   = SyncValue( self, 'x_shift'   ),
                           y_shift   = SyncValue( self, 'y_shift'   ),
                           x_origin  = SyncValue( self, 'x_origin'  ),
                           y_origin  = SyncValue( self, 'y_origin'  )
                       )
                ),
                VGroup(
                    Include( 'toolbar' ),
                    visible_when = 'show_toolbar'
                )
            ),
            title     = 'Image Tiler',
            id        = 'facets.extra.tools.image_tiler.ImageTiler',
            width     = 0.5,
            height    = 0.5,
            resizable = True
        )


    options = View(
        Include( 'toolbar' ),
        width = 600
    )

    toolbar = HToolbar(
        VGroup(
            Scrubber( 'width',  label = 'X' ),
            Scrubber( 'height', label = 'Y' ),
            label       = 'Size',
            group_theme = '@xform:btd?L20',
        ),
        VGroup(
            Scrubber( 'x_spacing', label = 'X' ),
            Scrubber( 'y_spacing', label = 'Y' ),
            label       = 'Spacing',
            group_theme = '@xform:btd?L20',
        ),
        VGroup(
            Scrubber( 'x_shift', label = 'X' ),
            Scrubber( 'y_shift', label = 'Y' ),
            label       = 'Shift',
            group_theme = '@xform:btd?L20',
        ),
        VGroup(
            Scrubber( 'x_origin', label = 'X' ),
            Scrubber( 'y_origin', label = 'Y' ),
            label       = 'Origin',
            group_theme = '@xform:btd?L20',
        ),
        VGroup(
            Scrubber( 'scale' ),
            Scrubber( 'border' ),
            label       = 'Miscellaneous',
            group_theme = '@xform:btd?L20',
        ),
        VGroup(
            Item( 'bg_color',
                   springy = True,
                   editor  = HLSColorEditor( edit = 'all' )
            ),
            show_labels = False,
            springy     = True,
            label       = 'BG Color',
            group_theme = '@xform:btd?L20'
        ),
        VGroup(
            Item( 'reset',
                  tooltip = 'Click to reset settings back to defaults'
            ),
            Item( 'show_toolbar',
                  editor = ThemedCheckboxEditor(
                      image       = '@facets:minus?H53l6S52',
                      off_image   = '@facets:plus?H53l6S52',
                      on_tooltip  = 'Click to hide toolbar',
                      off_tooltip = 'Click to show toolbar' )
            ),
            show_labels = False,
            group_theme = '@xform:btd?L20'
        ),
        padding   = 0,
        spacing   = 0,
        alignment = 'fill',
        id        = 'tb'
    )

    #-- Default Facet Values ---------------------------------------------------

    def _scaled_image_default ( self ):
        return self.image

    #-- Facet Event Handlers ---------------------------------------------------

    def _image_set ( self, old, new ):
        """ Handles the 'image' facet being changed.
        """
        if new is not None:
            if ((old is None)             or
                (new.width  != old.width) or
                (new.height != old.height)):
                self.width  = new.width
                self.height = new.height

            self._size_modified()


    @on_facet_set( 'width, height, scale' )
    def _size_modified ( self ):
        """ Handles the scaled image size being changed.
        """
        self.scaled_image = self.image.scale( (
            int( round( self.width  * self.scale ) ),
            int( round( self.height * self.scale ) )
        ) )


    def _reset_set ( self ):
        """ Handles the 'reset' button being clicked.
        """
        self.set(
            bg_color  = 0xF0F0F0,
            border    = 0,
            scale     = 1.0,
            width     = self.image.width,
            height    = self.image.height,
            x_spacing = 0,
            y_spacing = 0,
            x_shift   = 0,
            y_shift   = 0,
            x_origin  = 0,
            y_origin  = 0
        )

#-- EOF ------------------------------------------------------------------------
