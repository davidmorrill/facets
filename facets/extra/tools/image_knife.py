"""
Defines the ImageKnife tool, which allows you to perform several useful
operations on an input image:
  - Crop
  - Scale
  - Alpha trim
  - Squeeze

The resulting image is provided as the output of the tool.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from time \
    import time

from os \
    import makedirs

from os.path \
    import splitext, join, dirname, basename, abspath, isdir, exists

from glob \
    import glob

from facets.api \
    import HasPrivateFacets, Any, List, Str, Image, Bool, Range, Enum, Event, \
           File, Directory, Instance, Theme, Color, Property, Button, View,   \
           HSplit, HGroup, VGroup, Item, UItem, ImageZoomEditor,              \
           ThemedCheckboxEditor, HistoryEditor, GridEditor, HLSColorEditor,   \
           SyncValue, spring, on_facet_set, property_depends_on

from facets.core.facet_base \
    import save_file

from facets.ui.pyface.timer.api \
    import do_later, do_after

from facets.extra.helper.image \
    import HLSATransform, hlsa_derived_image

from facets.ui.editors.light_table_editor \
    import LightTableEditor, ThemedImage, GridLayout

from facets.ui.grid_adapter \
    import GridAdapter

from facets.extra.helper.themes \
    import Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from output file types to file extensions:
TypeMap = {
    'Portable Network Graphics (.png)':  '.png',
    'JPEG (.jpg)':                       '.jpg'
}

#-------------------------------------------------------------------------------
#  'ImageKnife' class:
#-------------------------------------------------------------------------------

class ImageKnife ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Image Knife'

    # The input image:
    input_image = Image( connect = 'to: input image' )

    # The output image:
    output_image = Image( connect = 'from: output image' )

    # The name of an input image file:
    input_file_name = File( connect = 'to: image file name' )

    # The output image file name:
    output_file_name = File

    # Event fired when the user wants to save the output image to a file:
    save_file = Button( '@icons2:Floppy?H94' )

    # Event fired when the user wants to save multiple files to a folder:
    save_folder = Button( '@icons2:Folder?H41' )

    # Is cropping enabled?
    can_crop = Bool( True, save_state = True, update = True )

    # Is scaling enabled:
    can_scale = Bool( True, save_state = True, update = True )

    # Is alpha trimming enabled?
    can_trim = Bool( False, save_state = True, update = True )

    # Is image squeezing enabled?
    can_squeeze = Bool( False, save_state = True, update = True )

    # Is HLSA transform enabled?
    can_transform = Bool( False, save_state = True, update = True )

    # Event fired when the user wants to reset the cropping values:
    reset_crop = Button( '@facets:minimize?H56' )

    # Event fired when the user wants to reset the scaling values:
    reset_scale = Button( '@facets:minimize?H56' )

    # Event fired when the user wants to reset the alpha trim values:
    reset_trim = Button( '@facets:minimize?H56' )

    # Event fired when the user wants to reset the squeeze values:
    reset_squeeze = Button( '@facets:minimize?H56' )

    # Event fired when the suer wants to reset the HLSA transform values:
    reset_transform = Button( '@facets:minimize?H56' )

    # The alpha trim level (represents the percentage alpha level):
    alpha = Range( 0, 100, 5, save_state = True, update = True )

    # The squeeze amount (in pixels):
    squeeze = Range( 1, 200, 20, save_state = True, update = True )

    # The squeeze tolerance (an abstract quantity):
    tolerance = Range( 0.0, 10.0, 0.4, save_state = True, update = True )

    # The scaling factor (represents a percentage of original image size):
    scale = Range( 1.0, 300.0, 100.0, save_state = True, update = True )

    # The image filter to use when scaling:
    filter = Enum( 'Quadratic', 'Bell', 'Box', 'CatmullRom', 'Cosine',
                   'CubicConvolution', 'CubicSpline', 'Hermite', 'Lanczos3',
                   'Lanczos8', 'Mitchell', 'QuadraticBSpline', 'Triangle',
                   save_state = True, update = True )

    # The cropping boundaries:
    left   = Range( 0, 4000, 0, update = True )
    right  = Range( 0, 4000, 0, update = True )
    top    = Range( 0, 4000, 0, update = True )
    bottom = Range( 0, 4000, 0, update = True )

    # The current image region selection bounds:
    bounds = Any # Tuple( Int, Int, Int, Int )

    # The HLSA transform to apply:
    transform = Instance( HLSATransform, () )

    # The input and output image sizes:
    size = Property

    # Should the ImageZoomEditor be automatically reset after the input image
    # is changed?
    auto_reset = Bool( True, save_state = True )

    # The background color for the ImageZoomEditor:
    bg_color = Color( 0x303030, save_state = True )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                HGroup(
                    UItem( 'output_image',
                           editor = ImageZoomEditor(
                               channel    = 'hue',
                               selected   = 'bounds',
                               auto_reset = SyncValue( self, 'auto_reset' ),
                               bg_color   = SyncValue( self, 'bg_color'   )
                           )
                    ),
                    VGroup(
                        HGroup(
                            UItem( 'can_crop',
                                editor = ThemedCheckboxEditor(
                                    image       = '@icons:crop?H41',
                                    on_tooltip  = 'Crop image (click to '
                                                  'disable)',
                                    off_tooltip = 'No image crop (click to '
                                                  'enable)' )
                            ),
                            UItem( 'can_scale',
                                editor = ThemedCheckboxEditor(
                                    image       = '@icons:scale?H41',
                                    on_tooltip  = 'Scale image (click to '
                                                  'disable)',
                                    off_tooltip = 'No image scale (click to '
                                                  'enable)' )
                            ),
                            UItem( 'can_trim',
                                editor = ThemedCheckboxEditor(
                                    image       = '@icons:trim?H41',
                                    on_tooltip  = 'Trim image edges (click to '
                                                  'disable)',
                                    off_tooltip = 'No image trim (click to '
                                                  'enable)' )
                            ),
                            UItem( 'can_squeeze',
                                editor = ThemedCheckboxEditor(
                                    image       = '@icons:squeeze?H41',
                                    on_tooltip  = 'Squeeze image (click to '
                                                  'disable)',
                                    off_tooltip = 'No image squeeze (click to '
                                                  'enable)' )
                            ),
                            UItem( 'can_transform',
                                editor = ThemedCheckboxEditor(
                                    image       = '@icons:hlsa_transform?H41',
                                    on_tooltip  = 'HLSA transform image (click '
                                                  'to disable)',
                                    off_tooltip = 'No image transform (click '
                                                  'to enable)' )
                            ),
                            spring,
                            UItem( 'auto_reset',
                                editor = ThemedCheckboxEditor(
                                    image       = '@icons2:Refresh',
                                    on_tooltip  = 'Automatically recenter '
                                                  'image (click to disable)',
                                    off_tooltip = 'Leave image as is (click '
                                                  'to recenter)' )
                            ),
                            group_theme = '@xform:b?L5'
                        ),
                        HGroup(
                            UItem( 'reset_crop',
                                   enabled_when = 'can_crop',
                                   tooltip      = 'Reset the crop values'
                            ),
                            UItem( 'reset_scale',
                                   enabled_when = 'can_scale',
                                   tooltip      = 'Reset the scale value'
                            ),
                            UItem( 'reset_trim',
                                   enabled_when = 'can_trim',
                                   tooltip      = 'Reset the alpha trim value'
                            ),
                            UItem( 'reset_squeeze',
                                   enabled_when = 'can_squeeze',
                                   tooltip      = 'Reset the squeeze values'
                            ),
                            UItem( 'reset_transform',
                                   enabled_when = 'can_transform',
                                   tooltip = 'Reset the HLSA transform values'
                            ),
                            spring,
                            UItem( 'save_folder',
                                   tooltip      = 'Save multiple images to a '
                                                  'folder',
                                   enabled_when = 'output_image is not None'
                            ),
                            UItem( 'save_file',
                                   tooltip      = 'Save output image to a file',
                                   enabled_when = 'output_image is not None'
                            ),
                            group_theme = '@xform:b?L5'
                        ),
                        VGroup(
                            UItem( 'size', style = 'readonly' ),
                            label       = 'Size',
                            group_theme = Theme( '@xform:btd?L10',
                                                 content = ( 10, 10, 5, 5 ) )
                        ),
                        VGroup(
                            Scrubber( 'left', 'Left crop boundary',
                                      width = 88 ),
                            Scrubber( 'right', 'Right crop boundary',
                                      width = 88 ),
                            Scrubber( 'top', 'Top crop boundary',
                                      width = 88 ),
                            Scrubber( 'bottom', 'Bottom crop boundary',
                                      width = 88 ),
                            label        = 'Crop',
                            group_theme  = '@xform:btd?L10',
                            visible_when = 'can_crop'
                        ),
                        VGroup(
                            Scrubber( 'scale', 'Scale factor',
                                width     = 88,
                                increment = 1.0
                            ),
                            Item( 'filter' ),
                            label        = 'Scale',
                            group_theme  = '@xform:btd?L10',
                            visible_when = 'can_scale'
                        ),
                        VGroup(
                            Scrubber( 'alpha', 'Alpha trim level', width = 88 ),
                            label        = 'Trim',
                            group_theme  = '@xform:btd?L10',
                            visible_when = 'can_trim'
                        ),
                        VGroup(
                            Scrubber( 'squeeze', 'Squeeze amount', width = 88 ),
                            Scrubber( 'tolerance', 'Squeeze tolerance',
                                width     = 88,
                                increment = 0.01
                            ),
                            label        = 'Squeeze',
                            group_theme  = '@xform:btd?L10',
                            visible_when = 'can_squeeze'
                        ),
                        VGroup(
                            Scrubber( 'object.transform.hue',
                                'Hue transform amount',
                                width     = 88,
                                increment = 0.01
                            ),
                            Scrubber( 'object.transform.lightness',
                                'Lightness transform amount',
                                width     = 88,
                                increment = 0.01
                            ),
                            Scrubber( 'object.transform.saturation',
                                'Saturation transform amount',
                                width     = 88,
                                increment = 0.01
                            ),
                            Scrubber( 'object.transform.alpha',
                                'Alpha transform amount',
                                width     = 88,
                                increment = 0.01
                            ),
                            label        = 'HLSA Transform',
                            group_theme  = '@xform:btd?L10',
                            visible_when = 'can_transform'
                        ),
                        HGroup(
                            UItem( 'bg_color',
                                editor = HLSColorEditor( edit = 'lightness' ),
                            ),
                            group_theme  = '@xform:b?L10'
                       )
                    )
                ),
                group_theme = Theme( '@xform:b?L20', content = -1 )
            ),
            id        = 'facets.extra.tools.image_knife.ImageKnife',
            width     = 0.5,
            height    = 0.5,
            resizable = True
        )

    #-- Public Methods ---------------------------------------------------------

    def convert_image ( self, image ):
        """ Returns a new version of the specified *image* with all of the
            current image knife operations applied.
        """
        if self.can_transform:
            image = hlsa_derived_image( image, self.transform )

        if self.can_scale:
            image = image.scale( self.scale / 100.0, self.filter )

        if self.can_trim:
            image = image.trim( self.alpha / 100.0 )

        if self.can_squeeze:
            image = image.squeeze( self.squeeze, self.tolerance )

        if self.can_crop:
            width, height = image.width, image.height
            image = image.crop(
                min( self.left, width  - 1 ),
                min( self.top,  height - 1 ),
                max( width  - self.left - self.right,  1 ),
                max( height - self.top  - self.bottom, 1 )
            )

        return image

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'output_image' )
    def _get_size ( self ):
        if self.output_image is None:
            return ''

        return '[ %d, %d ] -> [ %d, %d ]' % (
            self.input_image.width,
            self.input_image.height,
            self.output_image.width,
            self.output_image.height
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _input_file_name_set ( self, file_name ):
        """ Handles the 'input_file_name' facet being changed.
        """
        self.input_image = file_name


    def _input_image_set ( self, image ):
        """ Handles the 'input_image' facet being changed.
        """
        if image is not None:
            root, ext = splitext( image.name.lstrip( '@' ) )
            self.output_file_name = '%s_knifed%s' % ( root, ext or '.png' )
            if not self.auto_reset:
                do_later( self._reset_image_zoom_editor )


    def _save_file_set ( self ):
        """ Handles the user clicking the 'save file' button.
        """
        file_name = save_file( self.output_file_name )
        if file_name is not None:
            self.output_file_name = file_name
            self.output_image.save( file_name )


    def _save_folder_set ( self ):
        """ Handles the user clicking the 'save folder' button.
        """
        BatchKnife( knife = self ).edit_facets()


    def _reset_crop_set ( self ):
        """ Handles the 'reset_crop' event being fired.
        """
        self.left = self.right = self.top = self.bottom = 0


    def _reset_scale_set ( self ):
        """ Handles the 'reset_scale' event being fired.
        """
        self.scale  = 100.0
        self.filter = 'Quadratic'


    def _reset_trim_set ( self ):
        """ Handles the 'reset_trim' event being fired.
        """
        self.alpha = 5


    def _reset_squeeze_set ( self ):
        """ Handles the 'reset_squeeze' event being fired.
        """
        self.squeeze   = 20
        self.tolerance = 0.4


    def _reset_transform_set ( self ):
        """ Handles the 'reset_transform' event being fired.
        """
        self.transform.set(
            hue        = 0.0,
            lightness  = 0.0,
            saturation = 0.0,
            alpha      = 0.0
        )


    def _bounds_set ( self, bounds ):
        """ Handles the 'bounds' facet being changed.
        """
        x, y, dx, dy = bounds
        if self.can_crop and ((dx * dy) >= 256):
            image        = self.convert_image( self.input_image )
            self.left   += x
            self.top    += y
            self.right  += image.width  - (x + dx)
            self.bottom += image.height - (y + dy)


    @on_facet_set( '+update, input_image.modified, transform:modified' )
    def _output_image_modified ( self ):
        """ Handles any facet affecting the output image being changed.
        """
        # If the input image is too large, schedule the update for later;
        # otherwise do it now. This helps makes the tool more responsive when
        # working with larger images using the editing widgets:
        image = self.input_image
        if (image is not None) and ((image.width * image.height) > 300000):
            do_later( self._update_image )
        else:
            self._update_image()

    #-- Private Methods --------------------------------------------------------

    def _update_image ( self ):
        """ Update the output image based on the current value of all of the
            input settings.
        """
        if self.input_image is not None:
            self.output_image = self.convert_image( self.input_image )


    def _reset_image_zoom_editor ( self ):
        """ Resets the ImageZoomEditor editor after the input image changes.
        """
        self.auto_reset = True
        self.auto_reset = False

#-------------------------------------------------------------------------------
#  'FileAdapter' class:
#-------------------------------------------------------------------------------

class FileAdapter ( GridAdapter ):

    columns       = [ ( 'File', 'file' ) ]
    even_bg_color = 0xF8F8F8
    auto_filter   = True

    def file_content ( self ):
        return basename( self.item )

#-------------------------------------------------------------------------------
#  'BatchKnife' class:
#-------------------------------------------------------------------------------

class BatchKnife ( HasPrivateFacets ):
    """ Batch converts some or all image files in a specified directory using
        the settings of a spacified ImageKnife tool object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The ImageKnife whose settings we are using:
    knife = Instance( ImageKnife )

    # The input directory:
    input_path = Str

    # The output directory:
    output_path = Directory

    # The (optional) prefix to attach to each generated file:
    prefix = Str

    # The (optional) suffix to add to each generated file:
    suffix = Str

    # The (optional) file glob used to filter the images to convert:
    filter = Str( '*.png,*.jpg,*.jpeg' )

    # The type of output image files to create:
    type = Enum( 'Same as original file', 'Portable Network Graphics (.png)',
                 'JPEG (.jpg)' )

    # The possible list of image files to convert:
    all_files = List

    # The selected list of image files to convert:
    selected_files = List

    # Can existing files be overwritten?
    overwrite = Bool( False )

    # Indicates whether or not the selected files can be converted:
    can_convert = Property

    # The event fired when the user wants to start the image conversion process:
    convert = Button( 'Convert' )

    # Event fired when one or more images have been converted:
    converted = Event

    # The current file conversion status:
    status = Str

    # The current image being converted:
    image = Image

    # The GridLayout used to display the images on the light table:
    layout = Instance( GridLayout, { 'margin': 0, 'spacing': 0, 'width': 100 } )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                VGroup(
                    Item( 'output_path',
                          label   = 'Path',
                          tooltip = 'Directory for converted files'
                    ),
                    group_theme = '@xform:b?L25'
                ),
                HGroup(
                    VGroup(
                        Item( 'prefix',
                              tooltip = 'Prefix string to add to the '
                                        'beginning of each file'
                        ),
                        Item( 'suffix',
                              tooltip = 'Suffix string to add to the end of '
                                        'each file'
                        )
                    ),
                    VGroup(
                        Item( 'filter',
                              tooltip = 'Image file filter (separate multiple '
                                        'items with commas',
                              editor  = HistoryEditor( entries = 10 )
                        ),
                        Item( 'type',
                              tooltip = 'The type of output image files to '
                                        'create'
                        )
                    ),
                    group_theme = '@xform:b?L25'
                ),
                HGroup(
                    UItem( 'convert',
                           enabled_when = 'can_convert'
                    ),
                    UItem( 'overwrite',
                           editor = ThemedCheckboxEditor(
                               image       = '@icons2:PadlockOpen?H41',
                               off_image   = '@icons2:Padlock?H41',
                               on_tooltip  = 'Overwrite existing files without '
                                             'warning (click to prevent)',
                               off_tooltip = 'Do not allow overwriting files '
                                             '(click to allow)'
                           )
                    ),
                    UItem( 'status',
                           style   = 'readonly',
                           springy = True
                    ),
                    Scrubber( 'object.layout.width',
                        'Size of light table items',
                        width     = 88,
                        increment = 10
                    ),
                    group_theme = '@xform:b?L15'
                ),
                HSplit(
                    UItem( 'all_files',
                           label  = 'File names',
                           id     = 'details',
                           dock   = 'tab',
                           editor = GridEditor(
                               adapter        = FileAdapter,
                               operations     = [],
                               selection_mode = 'rows',
                               selected       = 'selected_files' )
                    ),
                    UItem( 'all_files',
                           label  = 'Images',
                           id     = 'light_table',
                           dock   = 'tab',
                           editor = LightTableEditor(
                               selection_mode = 'items',
                               selected       = 'selected_files',
                               layout         = self.layout,
                               adapter        = ThemedImage(
                                   normal_theme = Theme( '@xform:b',
                                                         content = 4 ),
                                   transform    = HLSATransform(
                                                      lightness = -0.3 ),
                                   lightness = 0.12 ) )
                    ),
                    id          = 'splitter',
                    group_theme = Theme( '@xform:b?L25', content = -1 )
                )
            ),
            title = 'Batch Image Knife Converter',
            id    = 'facets.extra.tools.image_knife.BatchKnife',
            width = 0.33
        )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'selected_files, prefix, suffix, overwrite, converted' )
    def _get_can_convert ( self ):
        if not self.overwrite:
            count = 0
            for file_name in self.selected_files:
                if exists( self._output_file_name_for( file_name ) ):
                    count += 1

            if count > 0:
                self.status = '%d output files already exist' % count

                return False

        self.status = ''

        return True

    #-- Facet Event Handlers ---------------------------------------------------

    def _knife_set ( self, knife ):
        """ Handles the 'knife' facet being changed.
        """
        self.input_path  = dirname( abspath( knife.input_image.name ) )
        self.output_path = join( self.input_path, 'knife' )


    def _input_path_set ( self ):
        """ Handles the 'input_path' facet being changed.
        """
        self._find_files()
        self.selected_files = self.all_files


    def _filter_set ( self ):
        """ Handles the 'filter' facet being changed.
        """
        do_after( 1000, self._find_files )


    def _convert_set ( self ):
        """ Handles the 'convert' event being fired.
        """
        self._convert_images()

    #-- Private Methods --------------------------------------------------------

    def _find_files ( self ):
        """ Finds all files match match the current search parameters.
        """
        files = set()
        path  = self.input_path
        for glb in (self.filter.strip() or '*.png,*.jpg,*.jpeg').split( ',' ):
            files.update( glob( join( path, glb.strip() ) ) )

        files = list( files )
        files.sort()
        self.all_files      = files
        #self.selected_files = [ file for file in self.selected_files
        #                             if file in files ]


    def _convert_images ( self ):
        """ Convert all of the currently selected images using the image knife
            settings.
        """
        now  = time()
        path = self.output_path
        if not isdir( path ):
            try:
                makedirs( path )
            except:
                self.status = 'Could not create directory: %s' % path

                return

        for file_name in self.selected_files:
            if not self._convert_image( file_name ):
                break

        self.status = '%d files converted in %.2f seconds' % (
                      len( self.selected_files ), time() - now )
        do_after( 3000, self.set, converted = True )


    def _convert_image ( self, file_name ):
        """ Converts the specified *file_name* image using the image knife
            settings.
        """
        self.image = file_name
        image      = self.image
        if image is None:
            self.status = 'Could not load image: %s' % file_name

            return False

        file_name = self._output_file_name_for( file_name )
        self.knife.convert_image( image ).save( file_name )

        return True


    def _output_file_name_for ( self, file_name ):
        """ Returns the output file name corresponding to a specified input
            *file_name*.
        """
        root, ext = splitext( basename( file_name ) )
        ext       = TypeMap.get( self.type, ext )

        return join( self.output_path,
                     '%s%s%s%s' % ( self.prefix, root, self.suffix, ext ) )

#-- Run the tool test case (if invoked from the command line) ------------------

if __name__ == '__main__':
    ImageKnife(
        input_image = r'C:\temp\Genetica\Icon4\Icon4_A.png'
    ).edit_facets()

#-- EOF ------------------------------------------------------------------------
