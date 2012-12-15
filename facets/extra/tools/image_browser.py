"""
A feature-enabled tool for browsing collections of images.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Property, Str, List, View, Item, ImageEditor

from facets.ui.ui_facets \
    import Image, ATheme

from facets.ui.theme \
    import Theme

from facets.ui.editors.list_canvas_editor \
    import ListCanvasEditor, ListCanvasAdapter

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  The ListCanvasEditor definition:
#-------------------------------------------------------------------------------

class ImageBrowserAdapter ( ListCanvasAdapter ):

    #-- Class Constants --------------------------------------------------------

    # Disable minimizing all items (to save screen real estate):
    can_minimize = False

    ImageItem_theme_active = ATheme(
        Theme( '@facets:photo_frame_active',
               label     = ( 0, 0, -3, 2 ),
               content   = 0,
               border    = ( 1, 7, 1, 7 ),
               alignment = 'center'
        )
    )

    ImageItem_theme_inactive = ATheme(
        Theme( '@facets:photo_frame_inactive',
               label     = ( 0, 0, -3, 2 ),
               content   = 0,
               border    = ( 1, 7, 1, 7 ),
               alignment = 'center'
        )
    )

    ImageItem_theme_hover = ATheme(
        Theme( '@facets:photo_frame_hover',
               label     = ( 0, 0, -3, 2 ),
               content   = 0,
               border    = ( 1, 7, 1, 7 ),
               alignment = 'center'
        )
    )

    ImageItem_title   = Property
    ImageItem_tooltip = Property

    #-- Property Implementations -----------------------------------------------

    def _get_ImageItem_title ( self ):
        return self.item.name


    def _get_ImageItem_tooltip ( self ):
        return self.item.name


list_canvas_editor = ListCanvasEditor(
    adapter    = ImageBrowserAdapter(),
    scrollable = True,
    operations = [ 'move', 'size', 'status' ]
)

#-------------------------------------------------------------------------------
#  'ImageItem' class:
#-------------------------------------------------------------------------------

class ImageItem ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the item being displayed:
    name = Str

    # The image being displayed:
    image = Image

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'image',
              show_label = False,
              editor     = ImageEditor()
        )
    )

#-------------------------------------------------------------------------------
#  'ImageBrowser' class:
#-------------------------------------------------------------------------------

class ImageBrowser ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Image Browser' )

    # The list of image names being browsed:
    image_names = List( Str, connect = 'to: list of image names to browse' )

    # The list of ImageItems being browsed:
    images = List( ImageItem )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'images',
              show_label = False,
              editor     = list_canvas_editor
        ),
        title     = 'Image Browser',
        id        = 'facets.extra.tools.image_browser.ImageBrowser',
        width     = 0.5,
        height    = 0.5,
        resizable = True
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _image_names_set ( self ):
        """ Handles the 'image_names' facet being changed.
        """
        self.images = [ ImageItem( name = image_name, image = image_name )
                        for image_name in self.image_names ]

#-- EOF ------------------------------------------------------------------------