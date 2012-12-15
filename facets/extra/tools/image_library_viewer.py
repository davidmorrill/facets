"""
A feature-enabled tool for viewing the contents of the Facets image library.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import isdir, basename

from facets.api \
    import Str, List, File, Directory, Constant, Instance, Int, Float, Bool,   \
           Property, Color, FacetError, cached_property, View, VGroup, HGroup, \
           Item, GridEditor, spring

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.image \
    import ImageLibrary, ImageInfo

from facets.ui.key_bindings \
    import KeyBindings, KeyBinding

from facets.extra.features.api \
    import DropFile

from image_browser \
    import ImageItem

from tools \
    import Tool

# fixme: We need to add a toolkit independent version of the clipboard...
###from facets.ui.wx.util.clipboard \
###    import clipboard

####-------------------------------------------------------------------------------
####  'ImageHandler' class:
####-------------------------------------------------------------------------------
###
###class ImageHandler ( Handler ):
###
###    #-- Facet Definitions ------------------------------------------------------
###
###    # The UIInfo object for the view:
###    info = Instance( UIInfo )
###
###    # The image we want to display:
###    image = Instance( ImageItem )
###
###    #-- Handler Interface ------------------------------------------------------
###
###    def init_info ( self, info ):
###        self.info = info
###
###    #-- Facets Default Values --------------------------------------------------
###
###    def _image_default ( self ):
###        object = self.info.object
###
###        return ImageItem( name = object.image_name, image = object.image_name )
###
####-------------------------------------------------------------------------------
####  Editor pop-up views:
####-------------------------------------------------------------------------------
###
###image_view = View(
###    Item( 'handler.image', style = 'custom', show_label = False ),
###    kind    = 'info',
###    handler = ImageHandler
###)
###
###description_view = View(
###    Item( 'description', style = 'readonly', show_label = False ),
###    kind       = 'info',
###    width      = 0.20,
###    height     = 0.20,
###    resizable  = True,
###    scrollable = True
###)
###
###copyright_view = View(
###    Item( 'copyright', style = 'readonly', show_label = False ),
###    kind       = 'info',
###    width      = 0.20,
###    height     = 0.20,
###    resizable  = True,
###    scrollable = True
###)
###
###license_view = View(
###    Item( 'license', style = 'readonly', show_label = False ),
###    kind       = 'info',
###    width      = 0.20,
###    height     = 0.20,
###    resizable  = True,
###    scrollable = True
###)
###
####-------------------------------------------------------------------------------
####  Image library viewer table editor definition:
####-------------------------------------------------------------------------------
###
###class LibraryColumn ( ObjectColumn ):
###
###    editable = False
###
###class NameColumn ( LibraryColumn ):
###
###    def on_dclick ( self, object ):
###        clipboard.text_data = "'%s'" % object.image_name

#-------------------------------------------------------------------------------
#  The list of all available grid adapter columns:
#-------------------------------------------------------------------------------

grid_adapter_columns = [
    ( 'Volume',      'volume'      ),
    ( 'Name',        'name'        ),
    ( 'Width',       'width'       ),
    ( 'Height',      'height'      ),
    ( 'Category',    'category'    ),
    ( 'Keywords',    'keywords'    ),
    ( 'Description', 'description' ),
    ( 'Copyright',   'copyright'   ),
    ( 'License',     'license'     ),
]

#-------------------------------------------------------------------------------
# 'ImageGridAdapter' class:
#-------------------------------------------------------------------------------

class ImageGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping image data into a GridEditor.
    """

    # The columns to display:
    columns = grid_adapter_columns

    # Allow automatic column filtering:
    auto_filter = True

    # Selection colors:
    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    # Column widths:
    image_width          = Float( 42 )
    volume_width         = Float( 0.10 )
    name_width           = Float( 0.10 )
    width_width          = Float( 0.075 )
    height_width         = Float( 0.075 )
    category_width       = Float( 0.10 )
    keywords_width       = Float( 0.10 )
    description_width    = Float( 0.10 )
    copyright_width      = Float( 0.10 )
    license_width        = Float( 0.10 )

    # Column alignments:
    image_alignment      = Str( 'center' )
    width_alignment      = Str( 'center' )
    height_alignment     = Str( 'center' )
    category_alignment   = Str( 'center' )

    # Editable columns:
    image_name_can_edit  = Bool( False )
    width_can_edit       = Bool( False )
    height_can_edit      = Bool( False )
    category_can_edit    = Bool( False )

    # Column contents:
    image_content        = Property
    volume_content       = Property
    keywords_content     = Property
    description_content  = Property
    copyright_content    = Property
    license_content      = Property

    # Column image:
    image_image          = Property

    #-- Property Implementations -----------------------------------------------

    def _get_image_image ( self ):
        item = self.item
        if (item.height <= 32) and (item.width <= 32):
            return item.image_name

        return None


    def _get_image_content ( self ):
        return ''


    def _get_volume_content ( self ):
        name = self.item.image_name

        return name[ 1: name.find( ':' ) ]


    def _get_keywords_content ( self ):
        return ', '.join( self.item.keywords )


    def _get_description_content ( self ):
        return self._column_text()


    def _get_copyright_content ( self ):
        return self._column_text()


    def _get_license_content ( self ):
        return self._column_text()

    #-- Private Methods --------------------------------------------------------

    def _column_text ( self ):
        """ Returns the text associated with current item.
        """
        text = getattr( self.item, self.column_id )
        col  = text.find( '\n' )
        if col <= 0:
            col = 80
        else:
            col = min( col, 80 )

        return text[ : col ]

###image_table_editor = TableEditor(
###        ImageColumn( label = 'Image',
###                     auto_editable = True, view  = image_view,
###        NameColumn(     name = 'name',
###        TextColumn(     name = 'description',
###                        auto_editable = True, view  = description_view ),
###        TextColumn(     name = 'copyright',
###                        auto_editable = True, view  = copyright_view ),
###        TextColumn(     name = 'license',
###                        auto_editable = True, view  = license_view ),
###    ],
###    filtered_indices    = 'filtered_indices',
###)

#-------------------------------------------------------------------------------
#  Image library viewer key bindings:
#-------------------------------------------------------------------------------

image_viewer_key_bindings = KeyBindings(
    KeyBinding( binding     = 'Ctrl-a',
                method      = '_select_all',
                description = 'Select all images.' ),
    KeyBinding( binding     = 'Ctrl-Shift-a',
                method      = '_unselect_all',
                description = 'Unselect all images.' ),
    KeyBinding( binding     = 'Ctrl-c',
                method      = '_copy_to_clipboard',
                description = 'Copy selected image names to the clipboard.' ),
    KeyBinding( binding     = 'Ctrl-k',
                method      = 'edit_bindings',
                description = 'Edits the keyboard bindings.' ),
)

#-------------------------------------------------------------------------------
#  'ImageLibraryViewer' class:
#-------------------------------------------------------------------------------

class ImageLibraryViewer ( Tool ):

    # The name of the tool:
    name = 'Image Library Viewer'

    # The currently selected list of image names:
    image_names = List( Str, connect = 'from: selected image names' )

    # The name of an image volume (i.e. directory or .zip file) to be added to
    # the image library:
    new_volume = File( connect   = 'to: a path or image volume to add to the '
                                   'image library',
                       drop_file = DropFile( extensions = [ '.zip' ],
                           tooltip = 'Drop an image library .zip file to add '
                                     'it to the image library' ) )

    # The name of a directory containing image files to be added to the image
    # library:
    new_directory = Directory( connect = 'to: a directory containing image '
                                      'files to be added to the image library' )

    # Reference to the image library:
    image_library = Constant( ImageLibrary() )

    # The list of currently selected ImageInfo objects:
    selected_images = List( ImageInfo )

    # The current list of filtered image indices:
    filtered_indices = List( Int )

    # The total number of image library images:
    total = Property( depends_on = 'image_library.images' )

    # The current number of filtered image library images:
    current = Property( depends_on = 'filtered_indices' )

    # Should all grid columns be displayed?
    show_all_columns = Bool( True, save_state = True )

    # The GrdiAdapter in the view:
    grid_adapter = Instance( ImageGridAdapter, () )

    #-- Facets UI View Definitions ---------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                Item( 'object.image_library.images',
                      id         = 'images',
                      show_label = False,
                      editor     = GridEditor(
                          adapter        = self.grid_adapter,
                          operations     = [],
                          selection_mode = 'rows',
                          selected       = 'selected_images'
                      )
                ),
                HGroup(
                    spring,
                    '_',
                    #Item( 'current',
                    #      label = 'Current images',
                    #      style = 'readonly',
                    #      width = -45 ),
                    #'_',
                    Item( 'total',
                          label = 'Total images',
                          style = 'readonly',
                          width = -45 ),
                ),
            ),
            title        = 'Image Library Viewer',
            id           = 'facets.extra.tools.image_library_viewer.'
                           'ImageLibraryViewer',
            width        = 0.75,
            height       = 0.75,
            resizable    = True,
            key_bindings = image_viewer_key_bindings
        )


    options = View(
        VGroup(
            Item( 'show_all_columns' ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_total ( self ):
        return len( self.image_library.images )


    @cached_property
    def _get_current ( self ):
        return len( self.filtered_indices )

    #-- Event Handlers ---------------------------------------------------------

    def _new_volume_set ( self, volume ):
        """ Handles the 'new_volume' facet being changed.
        """
        try:
            self.image_library.add_volume( volume )
        except FacetError, excp:
            pass # fixme: Display an error dialog here...


    def _new_directory_set ( self, directory ):
        """ Handles the 'new_directory' facet being changed.
        """
        if isdir( directory ):
            name    = basename( directory )
            catalog = self.image_library.catalog
            if name in catalog:
                count = 2
                while True:
                    new_name = '%s_%d' % ( name, count )
                    if new_name not in catalog:
                        name = new_name
                        break

                    count += 1
            try:
                self.image_library.add_path( name, directory )
            except FacetError, excp:
                pass # fixme: Display an error dialog here...


    def _selected_images_set ( self ):
        """ Handles the 'selected_image' facet being changed.
        """
        self.image_names = [ img.image_name for img in self.selected_images ]


    def _show_all_columns_set ( self, show_all_columns ):
        """ Handles the 'show_all_columns' facet being changed.
        """
        if show_all_columns:
            self.grid_adapter.columns = grid_adapter_columns
        else:
            self.grid_adapter.columns = grid_adapter_columns[:4]

    #-- Command Handlers -------------------------------------------------------

    def _select_all ( self, info = None ):
        """ Handles the user requesting that all images be selected.
        """
        images = self.image_library.images
        self.selected_images = [ images[ i ] for i in self.filtered_indices ]


    def _unselect_all ( self, info = None ):
        """ Handles the user requesting that all images be unselected.
        """
        self.selected_images = []


    def _copy_to_clipboard ( self, info = None ):
        """ Copies all currently selected image names to the system clipboard.
        """
        clipboard.text_data = ', '.join( [ "'%s'" % name
                                           for name in self.image_names ] )

#-------------------------------------------------------------------------------
#  Run the tool (if invoked from the command line):
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    ImageLibraryViewer().edit_facets()

#-- EOF ------------------------------------------------------------------------