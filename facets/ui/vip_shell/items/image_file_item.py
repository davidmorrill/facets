"""
Defines the ImageFileItem class used by the VIP Shell to represent a file system
image file.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Image, Bool, Color, Enum, View, VGroup, HGroup, \
           Item, SyncValue, ImageZoomEditor, HLSColorEditor, on_facet_set

from facets.ui.menu \
    import Action

from facets.ui.vip_shell.helper \
    import file_info_for

from path_item \
    import PathItem

from view_item \
    import ViewItem

#-------------------------------------------------------------------------------
#  Color Editor Definition:
#-------------------------------------------------------------------------------

color_editor = HLSColorEditor( cells = 9, cell_size = 9, edit = 'lightness' )

#-------------------------------------------------------------------------------
#  'ImageZoomer' class:
#-------------------------------------------------------------------------------

class ImageZoomer ( HasFacets ):
    """ Allows a specified image to be zoomed using the ImageZoomEditor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The image being edited:
    image = Image

    # The name of the view:
    name = Str

    # The editor background color:
    background_color = Color( 0x303030 )

    # The grid color:
    grid_color = Color( 0x707070 )

    # Should delta values be displayed?
    delta = Bool( False )

    # Which channel should be displayed?
    channel = Enum( 'none', 'red', 'green', 'blue', 'alpha',
                    'hue', 'lightness', 'saturation' )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        """ Returns the view to display.
        """
        return View(
            VGroup(
                HGroup(
                    Item( 'background_color',
                          label  = 'Background',
                          editor = color_editor
                    ),
                    Item( 'grid_color',
                          label  = 'Grid',
                          editor = color_editor
                    ),
                    '_',
                    Item( 'channel' ),
                    Item( 'delta', label = 'Show delta' ),
                    group_theme = '@cells:mg'
                ),
                Item( 'image',
                      show_label = False,
                      editor     = ImageZoomEditor(
                          bg_color   = SyncValue( self, 'background_color' ),
                          grid_color = SyncValue( self, 'grid_color' ),
                          channel    = SyncValue( self, 'channel' ),
                          delta      = SyncValue( self, 'delta' )
                      )
                )
            )
        )

#-------------------------------------------------------------------------------
#  'ImageFileItem' class:
#-------------------------------------------------------------------------------

class ImageFileItem ( PathItem ):
    """ A file containing image data (e.g. a .png or .jpeg file).
    """

    #-- Class Constants --------------------------------------------------------

    # The user intername for an an item of this class:
    ui_name = 'Image File'

    #-- Facet Definitions ------------------------------------------------------

    icon = '@facets:shell_image'

    # The content image:
    content_image = Image

    # The custom tool bar actions supported by the item (if any):
    actions = [
        Action( image   = '@icons2:Magnifier?H4l9S48|h53H57',
                tooltip = 'Create an image zoom view for the item',
                action  = 'item.create_zoom_view()' ),

        Action( image   = '@icons2:Chart_1',
                tooltip = 'Create an image transformer view for the item',
                action  = 'item.create_transformer_view()' ),
    ]

    #-- Public Methods ---------------------------------------------------------

    def key_i ( self, event ):
        """ Create an inline image transformer view for the image file.

            The [[i]] key creates an inline view of the image file's contents
            using the Facets image transformer tool. This tool can be used to
            create mask and transform values that can be used to dynamically
            modify the original image when used with various theming APIs.
        """
        self.create_transformer_view()


    def key_z ( self, event ):
        """ Create an inline image zoom view for the image file.

            The [[z]] key creates an inline view of the image file's contents
            using the Facets image zoomer tool. This tool can be used to zoom
            into an image and optionally display various color channel values
            for selected regions of the image.
        """
        self.create_zoom_view()


    def create_transformer_view ( self ):
        """ Create an inline image transformer view for the image file.
        """
        from facets.extra.tools.image_transformer import ImageTransformer

        self.shell.add_item_for(
            self,
            self.shell.history_item_for( ViewItem,
                ImageTransformer(
                    image  = self.item,
                    name   = 'Image: ' + self.item
                ),
                height = 650,
                lod    = 1
            )
        )


    def create_zoom_view ( self ):
        """ Create an inline image zoom view for the image file.
        """
        self.shell.add_item_for(
            self,
            self.shell.history_item_for( ViewItem,
                ImageZoomer( image = self.item, name = 'Image: ' + self.item ),
                height = 400,
                lod    = 1
            )
        )


    def click ( self, event ):
        """ Handles the user clicking an item without the shift or alt
            modifiers.
        """
        if event.control_down:
            self.shell.append( self.item )
        else:
            self.shell.replace_code( self.item )

    #-- Facet Default Values ---------------------------------------------------

    def _item_label_default ( self ):
        return file_info_for( self.item )


    def _item_contents_default ( self ):
        return ''

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'item' )
    def _item_updated ( self, item ):
        self.content_image = item

    #-- IStackItem Interface Methods -------------------------------------------

    def label_value_for_1 ( self ):
        image = self.content_image

        return self.shell.colorize(
            self.add_id( '%s  \x00ASize: \x00C%d x %d\x006' %
                         ( self.item, image.width, image.height ) )
        )


    def paint_item_for_1 ( self, g, bounds ):
        """ Paints the text and optional label in the specified graphics
            context *g* for level of detail 1.
        """
        image            = self.content_image
        idx, idy         = image.width, image.height
        x, y, dx, dy     = self.bounds
        dx               = self.stack_width
        ax, ay, adx, ady = self.current_theme.bounds( x, y, dx, dy )
        aidx             = min( idx, adx - 4 )
        aidy             = int( round( (float( aidx ) / idx) * idy ) )
        if aidy > (ady - 10):
            aidy = min( idy, ady - 10 )
            aidx = int( round( (float( aidy ) / idy) * idx ) )
            g.blit( ax + 2, ay + 5, aidx, aidy, image.bitmap, 0, 0, idx, idy )
        else:
            g.blit( ax + (adx - aidx) / 2, ay + (ady - aidy) / 2,
                    aidx, aidy, image.bitmap, 0, 0, idx, idy )

        if self.ltext is not None:
            self.current_theme.draw_graphics_label( g, self.ltext, x, y, dx, dy,
                                                    bounds )


    def paint_item_for_2 ( self, g, bounds ):
        """ Paints the text and optional label in the specified graphics
            context *g* for level of detail 2.
        """
        image            = self.content_image
        idx, idy         = image.width, image.height
        x, y, dx, dy     = self.bounds
        dx               = self.stack_width
        ax, ay, adx, ady = self.current_theme.bounds( x, y, dx, dy )
        adx              = max( adx, idx )
        g.draw_bitmap( image.bitmap,
                       ax + ((adx - idx) / 2), ay + ((ady - idy) / 2) )

        if self.ltext is not None:
            self.current_theme.draw_graphics_label( g, self.ltext, x, y, dx, dy,
                                                    bounds )


    def size_item_for_1 ( self, g ):
        """ Returns the current size of the item.
        """
        image            = self.content_image
        idx, idy         = image.width, image.height
        ax, ay, adx, ady = self.current_theme.bounds( 0, 0, 0, 0 )
        dx               = self.stack_width
        rdx              = min( dx, idx + 4 - adx )
        rdy              = (int( round( (float( rdx - 4 + adx ) / idx) * idy ) )
                            + 10 - ady)

        return ( rdx, rdy )


    def size_item_for_2 ( self, g ):
        """ Returns the current size of the item.
        """
        image            = self.content_image
        idx, idy         = image.width, image.height
        ax, ay, adx, ady = self.current_theme.bounds( 0, 0, 0, 0 )

        return ( idx + 4 - adx, idy + 10 - ady )

#-- EOF ------------------------------------------------------------------------
