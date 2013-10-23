"""
Defines the LightTable tool for displaying and selecting images on a simulated
light table.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import listdir

from os.path \
    import isfile, dirname, join, splitext

from facets.api \
    import Str, List, Instance, Enum, Theme, Property, Any, File, Button, \
           View, HToolbar, UItem, property_depends_on, on_facet_set, spring

from facets.ui.editors.light_table_editor \
    import LightTableEditor, LightTableAnimator, GridLayout, ThemedImage, \
           HLSATransform

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The set of all supported image types (i.e. file extensions):
ImageTypes = ( '.png', '.jpg', '.jpeg' )

# Shared image transforms:
hlsa_1 = HLSATransform( hue = 0.56, lightness = -0.04, saturation = 0.13 )
hlsa_2 = HLSATransform( hue = 0.56, lightness = -0.20, saturation = 0.13 )
hlsa_3 = HLSATransform( hue = 0.56, lightness =  0.10, saturation = 0.13 )
hlsa_4 = HLSATransform( hue = 0.11, lightness = -0.16, saturation = 0.96 )
hlsa_5 = HLSATransform( hue = 0.56, lightness = -0.10, saturation = 0.13,
                        alpha = 0.96 )

# The mapping from styles to ThemedImage objects:
ThemedImages = {
    'Photo':   ThemedImage(
                   show_label   = True,
                   normal_theme = Theme( '@xform:photob?L5s|h40H60',
                                         content = 10, label = ( 0, 0, 0, 5 ) ),
                   transform    = hlsa_4 ),
    'Photo Thin': ThemedImage(
                   normal_theme = Theme( '@xform:photos' ),
                   transform    = hlsa_4 ),
    'Medium':  ThemedImage(
                   normal_theme = Theme( '@xform:b', content = 4 ),
                   transform    = hlsa_1 ),
    'Dark':    ThemedImage(
                   normal_theme = Theme( '@xform:b?l30', content = 4 ),
                   transform    = hlsa_3,
                   lightness    = 0.12 ),
    'Light':   ThemedImage(
                   normal_theme = Theme( '@xform:b?L30', content = 4 ),
                   transform    = hlsa_2 ),
    'Medium Simple': ThemedImage(
                   normal_theme = Theme( '@xform:bg', content = 4 ),
                   transform    = hlsa_1 ),
    'Dark Simple': ThemedImage(
                   normal_theme = Theme( '@xform:bg?l30', content = 4 ),
                   transform    = hlsa_3,
                   lightness    = 0.12 ),
    'Light Simple': ThemedImage(
                   normal_theme = Theme( '@xform:bg?L30', content = 4 ),
                   transform    = hlsa_2 ),
    'Round':   ThemedImage(
                   show_label   = True,
                   normal_theme = Theme( '@xform:b4bd',
                                         content = 4, label = ( 0, 0, 0, 3 ) ),
                   transform    = hlsa_1 ),
    'Square':  ThemedImage(
                   show_label   = True,
                   normal_theme = Theme( '@xform:bbd', content = 4 ),
                   transform    = hlsa_1 ),
    'Inset 1': ThemedImage(
                   normal_theme = Theme( '@xform:i6b', content = 4 ),
                   transform    = hlsa_1 ),
    'Inset 2': ThemedImage(
                   normal_theme = Theme( '@xform:e6',  content = 4 ),
                   transform    = hlsa_1 ),
    'Inset 3': ThemedImage(
                  show_label   = True,
                  normal_theme = Theme( '@xform:e6bd?l15',
                                         content = 4, label = ( 0, 0, 0, 3 ) ),
                   transform    = hlsa_1 ),
    'None':    ThemedImage(
                   normal_theme = Theme( '@xform:bg?a96', content = 4 ),
                   transform    = hlsa_5 )
}

#-------------------------------------------------------------------------------
#  'LightTable' class:
#-------------------------------------------------------------------------------

class LightTable ( Tool ):
    """ Defines the LightTable tool for displaying and selecting images on a simulated light table.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Light Table'

    # The list of images to display:
    images = List( connect   = 'to: list of images to display',
                   droppable = 'Drop a group of images here.' )

    # The name of a directory containing a group of images to display:
    directory = File( connect   = 'to: directory containing images to display',
                      droppable = 'Drop a file or directory here.' )

    # The current selected image:
    selected = Any( connect = 'from: selected image' )

    # The HLSA encoding to apply to all images:
    encoded = Str( connect = 'to: HLSA encoding' )

    # The list of ThemedImages being displayed:
    themed_images = List

    # The current ThemedImage template being used:
    themed_image = Property

    # The current ThemedImage style:
    style = Enum( 'Photo', 'Photo Thin', 'Medium', 'Medium Simple', 'Dark',
                  'Dark Simple', 'Light', 'Light Simple', 'Round', 'Square',
                  'Inset 1', 'Inset 2', 'Inset 3', 'None', save_state = True )

    # The GridLayout used to display the images on the light table:
    layout = Instance( GridLayout, () )

    # The LightTableAnimator used to animate the images on the light table:
    animator = Instance( LightTableAnimator, () )

    # Event fired to start/stop light table image animation:
    animate = Button( '@icons2:GearExecute' )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'themed_images',
                   editor = LightTableEditor(
                       selection_mode = 'item',
                       selected       = 'selected',
                       layout         = self.layout,
                       animator       = self.animator,
                       adapter        = ThemedImage(
                           normal_theme = Theme( '@xform:photob?L5s|h40H60',
                                                 content = 10,
                                                 label   = ( 0, 0, 0, 5 ) ),
                           show_label = True
                       )
                   )
            ),
            HToolbar(
                spring,
                UItem( 'animate' ),
                Scrubber( 'object.animator.time',  increment = 0.10 ),
                Scrubber( 'object.animator.cycle', increment = 0.05 ),
                Scrubber( 'object.animator.level', increment = 0.01 ),
                Scrubber( 'style', width = 100 ),
                Scrubber( 'object.layout.margin' ),
                Scrubber( 'object.layout.spacing' ),
                Scrubber( 'object.layout.width' ),
                Scrubber( 'object.layout.ratio', increment = 0.01 ),
                id = 'toolbar'
            ),
            id = 'facets.extra.tools.light_table.LightTable'
        )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'style' )
    def _get_themed_image ( self ):
        return ThemedImages[ self.style ]

    #-- Facet Event Handlers ---------------------------------------------------

    def _directory_set ( self, directory ):
        """ Handles the 'directory' facet being changed.
        """
        if isfile( directory ):
            directory = dirname( directory )

        self.images = [ join( directory, name )
                        for name in listdir( directory )
                        if splitext( name )[1] in ImageTypes ]


    @on_facet_set( 'images, themed_image, encoded' )
    def _themed_images_modified ( self ):
        selected, self.selected = self.selected, None
        ti                      = self.themed_image
        encoded                 = self.encoded
        if encoded != '':
            encoded = '?' + encoded
        self.themed_images      = [ ti( image + encoded )
                                    for image in self.images ]
        self.selected           = selected


    def _animate_set ( self ):
        """ Handles the 'animate' event being fired.
        """
        if self.animator.running:
            self.animator.stop = True
        else:
            self.animator.start = True

#-- EOF ------------------------------------------------------------------------
