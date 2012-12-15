"""
A tool for working with a collection of images using a 'collage' style that
allows images to be moved, scaled, selected and have their HLSA colors adjusted
using a virtual pasteboard.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import List, Range, Enum, Image, Instance, Theme, ATheme, View, Item, \
           UItem, HToolbar, SyncValue, on_facet_set, spring

from facets.extra.helper.themes \
    import Scrubber

from facets.extra.editors.collage_editor \
    import CollageEditor, CollageItem

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Theme content border adjustments:
FlatAdjust  = (  0,  0,  0,  0 )
BevelAdjust = ( -1, -1, -1, -1 )
BevelLabelT = (  0,  0,  0,  3 )
BevelLabelB = (  0,  0,  0,  0 )
PhotoAdjust = ( -2, -3, -2, -3 )
PhotoLabelT = (  0,  0,  2,  0 )
PhotoLabelB = (  0,  0,  0,  5 )

# Mapping from theme and title style to image name:
CollageThemes = {
    'Flat_Dark_None': (
        '@xform:bg?l20',      '@xform:bg?L20',    -1, FlatAdjust, BevelLabelT
    ),
    'Flat_Light_None': (
        '@xform:bg?L20',      '@xform:bg?l20',    -1, FlatAdjust, BevelLabelT
    ),
    'Bevel_Dark_None': (
        '@xform:b?l20',      '@xform:b?L20',      -1, BevelAdjust, BevelLabelT
    ),
    'Bevel_Dark_Top': (
        '@xform:btd?l20',    '@xform:btd?L20',    -1, BevelAdjust, BevelLabelT
    ),
    'Bevel_Dark_Bottom': (
        '@xform:bbd?l20',    '@xform:bbd?L20',    -1, BevelAdjust, BevelLabelB
    ),
    'Bevel_Light_None': (
        '@xform:b?L20',      '@xform:b?l20',      -1, BevelAdjust, BevelLabelT
    ),
    'Bevel_Light_Top': (
        '@xform:btd?L20',    '@xform:btd?l20',    -1, BevelAdjust, BevelLabelT
    ),
    'Bevel_Light_Bottom': (
        '@xform:bbd?L20',    '@xform:bbd?l20',    -1, BevelAdjust, BevelLabelB
    ),
    'Photo_None': (
        '@xform:photo?L20',  '@xform:photo',      -2, PhotoAdjust, PhotoLabelT
    ),
    'Photo_Top': (
        '@xform:photot?L20', '@xform:photot',     -2, PhotoAdjust, PhotoLabelT
    ),
    'Photo_Bottom': (
        '@xform:photob?L20', '@xform:photob',     -2, PhotoAdjust, PhotoLabelB
    )
}

#-------------------------------------------------------------------------------
#  'Collage' class:
#-------------------------------------------------------------------------------

class Collage ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Collage'

    # The current list of images:
    images = List( Image, connect = 'to: list of images' )

    # The current input image:
    image = Image( connect = 'to: input image' )

    # The currently selected collage image item's base image:
    selected_image = Image( connect = 'from: selected image' )

    # The currently selected collage image item's scaled image:
    selected_scaled_image = Image( connect = 'from: selected scaled image' )

    # The currently selected collage image item's cropped image:
    selected_cropped_image = Image( connect = 'from: selected cropped image' )

    # The currently selected collage image item:
    selected_item = Instance( CollageItem )

    # The maximum initial width of a collage image item:
    item_width = Range( 100, 1024, 256, save_state = True )

    # The maximum initial height of a collage image item:
    item_height = Range( 100, 1024, 256, save_state = True )

    # The collage image item theme:
    item_theme = ATheme( Theme( '@xform:b?L20', content = -1 ) )

    # The collage image item theme used when an item is selected:
    item_selected_theme = ATheme( Theme( '@xform:b?L20', content = -1 ) )

    # The item theme style to use:
    theme = Enum( 'Bevel Dark', 'Bevel Light', 'Flat Dark', 'Flat Light',
                  'Photo', 'None', save_state = True )

    # The item title style to use:
    title = Enum( 'None', 'Top', 'Bottom', save_state = True )

    # The item border width to use:
    border = Range( 0, 30, 5, save_state = True )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'images',
                   editor = CollageEditor(
                       selected_item       = 'selected_item',
                       item_width          = SyncValue( self, 'item_width'  ),
                       item_height         = SyncValue( self, 'item_height' ),
                       item_theme          = SyncValue( self, 'item_theme'  ),
                       item_selected_theme = SyncValue( self,
                                                        'item_selected_theme' )
                   )
            ),
            id     = 'facets.extra.tools.collage.Collage',
            width  = 0.50,
            height = 0.80
        )


    options = View(
        HToolbar(
            spring,
            Item( 'theme',
                  tooltip = 'Theme to use for each image item'
            ),
            Item( 'title',
                  tooltip = 'Style of title to use for each image item'
            ),
            Scrubber( 'border',
                'Width of border around each image item (in pixels)',
                width = 50
            ),
            Scrubber( 'item_width',
                'Maximum initial width of new image items (in pixels)',
                width     = 50,
                increment = 10
            ),
            Scrubber( 'item_height',
                'Maximum initial height of new image items (in pixels)',
                width     = 50,
                increment = 10
            ),
            group_theme = Theme( '@xform:b?L10', content = ( 4, 0, 4, 4 ) ),
            id          = 'tb'
        ),
        id = 'facets.extra.tools.collage.Collage.options'
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _image_set ( self, image ):
        """ Handles the 'image' facet being changed.
        """
        if image is not None:
            self.images.append( image )


    def _selected_item_set ( self, item ):
        """ Handles the 'selected_item' facet being changed.
        """
        if item is None:
            self.selected_image         = self.selected_scaled_image = \
            self.selected_cropped_image = None
        else:
            self.selected_image         = item.image
            self.selected_scaled_image  = item.scaled_image
            self.selected_cropped_image = item.cropped_image


    @on_facet_set( 'theme, title, border' )
    def _theme_modified ( self ):
        """ Handles any facet affecting the image item theme being changed.
        """
        title  = self.title
        theme  = self.theme.replace( ' ', '_' )
        themes = CollageThemes.get( '%s_%s' % ( theme, title ) )
        if (themes is None) and (title != 'None'):
            themes = CollageThemes.get( '%s_None' % theme )

        if themes is None:
            self.item_theme = self.item_selected_theme = None
        else:
            border     = max( self.border, themes[2] )
            l, r, t, b = themes[3]
            content    = ( l + border, r + border, t + border, b + border )
            label      = themes[4]
            self.item_theme = Theme(
                themes[0], content = content, label = label
            )
            self.item_selected_theme = Theme(
                themes[1], content = content, label = label
            )

#-- EOF ------------------------------------------------------------------------
