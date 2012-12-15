"""
A feature-enabled tool for building Facets UI ImageLibrary image volumes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import remove

from os.path \
    import abspath, dirname, basename, join, splitext, isdir, exists

from zipfile \
    import ZipFile, ZIP_DEFLATED

from facets.api \
    import HasPrivateFacets, File, Float, Str, List, Button, Color, Property, \
           Constant, cached_property, View, HGroup, VGroup, Tabbed, Item, \
           Label, Theme, FileEditor, GridEditor, ListStrEditor, HistoryEditor

from facets.ui.grid_adapter \
    import GridAdapter

from facets.ui.image \
    import ImageLibrary, ImageVolume, ImageVolumeInfo, ImageInfo, FastZipFile, \
           time_stamp_for

from facets.extra.helper.themes \
    import LabelTheme, InsetTheme

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The set of recognized image file extensions:
ImageExtensions = ( '.png', '.jpg', '.jpeg', '.gif' )

# The standard Group Theme we are using:
GroupTheme = Theme( '@std:XG1', content = 4 )

#-------------------------------------------------------------------------------
#  'VolumeContentsGridAdapter' class:
#-------------------------------------------------------------------------------

class VolumeContentsGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping from volume contents tool data to the
        GridEditor.
    """

    columns = [
        ( 'File Name',  'file_name' ),
        ( 'Image Name', 'image_name' ),
    ]

    selection_bg_color   = Color( 0xFBD391 )
    selection_text_color = Color( 0x000000 )

    # Column widths:
    file_name_width  = Float( 0.75 )
    image_name_width = Float( 0.25 )


volume_contents_grid_editor = GridEditor(
    adapter    = VolumeContentsGridAdapter,
    operations = []
)

#-------------------------------------------------------------------------------
#  'ImageVolumeItem' class:
#-------------------------------------------------------------------------------

class ImageVolumeItem ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The file name of the item:
    file_name = File

    # The image name of the item:
    image_name = Str

#-------------------------------------------------------------------------------
#  'ImageVolumeBuilder' class:
#-------------------------------------------------------------------------------

class ImageVolumeBuilder ( Tool ):
    """ A feature-enabled tool for building Facets UI ImageLibrary image
        volumes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Image Volume Builder' )

    # Reference to the image library:
    image_library = Constant( ImageLibrary() )

    #-- Volume Information -----------------------------------------------------

    # The category of the ImageVolume being built:
    category = Str( 'General' )

    # The description of the ImageVolume being built:
    description = Str( 'No volume description specified.' )

    # The keywords associated with the ImageVolume being built:
    keywords = List( Str )

    #-- Image Information ------------------------------------------------------

    # The image category:
    image_category = Str

    # The image description:
    image_description = Str

    # The image keywords:
    image_keywords = List( Str )

    #-- Copyright/License Information ------------------------------------------

    # The image/volume copyright:
    copyright = Str( 'No copyright information specified.' )

    # The image/volume license:
    license = Str( 'No license information specified.' )

    # The file containing the license text:
    license_file = File

    #-- Volume Content ---------------------------------------------------------

    # The files to be used to build the image volume:
    files = List( File,
                connect = 'to: list of file names to build image volume with' )

    # The filtered list of files to build the image volume from:
    build_files = Property( List, depends_on = 'files[]' )

    #-- Volume File Name -------------------------------------------------------

    # The zip file name of the image volume:
    volume_name = File

    # The fully qualified zip file name of the volume:
    fq_volume_name = Property

    # Is the current volume name valid?
    is_valid_name = Property( depends_on = 'volume_name, files' )

    # The button for building the image library:
    build = Button( 'Build' )

    # Status message:
    status = Str

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            Tabbed(
                VGroup(
                    VGroup(
                        Label( 'Volume Contents', LabelTheme ),
                        Item( 'build_files',
                              show_label = False,
                              editor     = volume_contents_grid_editor
                        ),
                        group_theme = InsetTheme
                    ),
                    group_theme = GroupTheme,
                    label       = 'Volume Contents'
                ),
                VGroup(
                    VGroup(
                        Item( 'category', label = 'Volume category' ),
                        group_theme = InsetTheme
                    ),
                    HGroup(
                        VGroup(
                            Label( 'Volume keywords', LabelTheme ),
                            Item( 'keywords',
                                  editor = ListStrEditor( auto_add = True )
                            ),
                            show_labels = False
                        ),
                        VGroup(
                            Label( 'Volume description', LabelTheme ),
                            Item( 'description', style = 'custom' ),
                            show_labels = False
                        ),
                        group_theme = InsetTheme
                    ),
                    group_theme = GroupTheme,
                    label       = 'Volume Information'
                ),
                VGroup(
                    VGroup(
                        Item( 'image_category' ),
                        group_theme = InsetTheme
                    ),
                    HGroup(
                        VGroup(
                            Label( 'Image keywords', LabelTheme ),
                            Item( 'image_keywords',
                                  editor = ListStrEditor( auto_add = True )
                            ),
                            show_labels = False
                        ),
                        VGroup(
                            Label( 'Image description', LabelTheme ),
                            Item( 'image_description', style = 'custom' ),
                            show_labels = False
                        ),
                        group_theme = InsetTheme
                    ),
                    group_theme = GroupTheme,
                    label       = 'Image Information'
                ),
                VGroup(
                    VGroup(
                        Item( 'copyright',
                              id     = 'copyright',
                              label  = '  Copyright',
                              editor = HistoryEditor()
                        ),
                        group_theme = InsetTheme
                    ),
                    VGroup(
                        Item( 'license_file',
                              id     = 'license_file',
                              editor = FileEditor( entries = 10 )
                        ),
                        group_theme = InsetTheme
                    ),
                    VGroup(
                        Item( 'license',
                              label = '      License',
                              style = 'custom',
                        ),
                        group_theme = InsetTheme
                    ),
                    group_theme = GroupTheme,
                    label       = 'Copyright/License'
                ),
                id = 'tabbed'
            ),
            HGroup(
                Item( 'volume_name',
                      id      = 'volume_name',
                      label   = 'File name',
                      editor  = FileEditor( entries = 10 ),
                      springy = True
                ),
                Item( 'build',
                      show_label   = False,
                      enabled_when = 'is_valid_name'
                ),
                group_theme = InsetTheme
            ),
            HGroup(
                Item( 'status',
                      show_label = False,
                      style      = 'readonly',
                      springy    = True
                ),
                group_theme = InsetTheme
            ),
            group_theme = '@std:XG1'
        ),
        id        = 'facets.extra.tools.image_volume_builder.'
                    'ImageVolumeBuilder',
        title     = 'Image Volume Builder',
        width     = 0.75,
        height    = 0.75,
        resizable = True
    )

    #-- Property Implementations -----------------------------------------------

    def _get_fq_volume_name ( self ):
        name      = abspath( self.volume_name )
        root, ext = splitext( name )
        if ext == '':
            name += '.zip'

        return name


    @cached_property
    def _get_is_valid_name ( self ):
        return ((len( self.volume_name ) > 0)      and
                (not isdir( self.fq_volume_name )) and
                (len( self.build_files ) > 0))


    @cached_property
    def _get_build_files ( self ):
        n   = self._find_common_prefix_length()
        inf = self._image_name_for
        return [ ImageVolumeItem( file_name  = file_name,
                                  image_name = inf( file_name, n ) )
                 for file_name in self.files
                 if splitext( file_name )[1] in ImageExtensions ]

    #--Facets Event Handlers ---------------------------------------------------

    def _license_file_set ( self, file_name ):
        """ Handles the license file facet being changed.
        """
        try:
            fh      = file( file_name, 'rb' )
            license = fh.read()
            fh.close()
        except:
            return

        if (len( license ) > 0) and (license.find( '\x00' ) < 0):
            self.license = license


    def _build_set ( self ):
        """ Handles the user requesting that the volume be built.
        """
        file_name = self.fq_volume_name
        if exists( file_name ):
            # fixme: Handle the case of the file name already existing here...
            pass

        self._build_volume( file_name )

    #-- Private Methods --------------------------------------------------------

    def _find_common_prefix_length ( self ):
        """ Returns the length of the longest common file prefix shared by all
            input files.
        """
        files = [ abspath( file ) for file in self.files ]

        if len( files ) == 0:
            return 0

        prefix = join( dirname( files[0] ), '' )
        while True:
            n = len( prefix )
            for file in files:
                if prefix != file[:n]:
                    break
            else:
                return n

            new_prefix = join( dirname( dirname( prefix ) ), '' )
            if new_prefix == prefix:
                return n

            prefix = new_prefix


    def _image_name_for ( self, file_name, n ):
        """ Returns the coresponding image name for a specified **file_name**
            with a specified common prefix length of **n**.
        """
        return file_name[ n: ].replace( '\\', '_' ).replace( '/', '_' )


    def _build_volume ( self, file_name ):
        """ Creates the image volume using the specified file name and the
            current user supplied information and input files.
        """
        # Set the current status:
        self.status = 'Saving to %s...' % file_name

        # Create an image volume to hold the information collected. Note that we
        # set a bogus time stamp to force the ImageLibrary to reload all of the
        # image information from the actual files so that we end up with the
        # correct image sizes:
        volume = ImageVolume(
            category   = self.category,
            keywords   = self.keywords,
            time_stamp = time_stamp_for( 0.0 ),
            info       = [ ImageVolumeInfo(
                               description = self.description,
                               copyright   = self.copyright,
                               license     = self.license ) ]
        )

        # Create an ImageInfo descriptor for each image file that will become
        # part of the volume:
        volume_name   = splitext( basename( file_name ) )[ 0 ]
        volume.images = [ ImageInfo(
                              name        = item.image_name,
                              image_name  = '@%s:%s' % ( volume_name,
                                                         item.image_name ),
                              description = self.image_description,
                              category    = self.image_category,
                              keywords    = self.image_keywords )
                          for item in self.build_files ]

        # Pre-compute the images code, because it can require a long time
        # to load all of the images so that we can determine their size, and we
        # don't want that time to interfere with the time stamp of the image
        # volume:
        images_code = volume.images_code

        # Create the new zip file:
        zf = ZipFile( file_name, 'w', ZIP_DEFLATED )

        # Assume that an error will occur:
        error = True
        fh    = None
        try:
            # Copy all of the image files from the file system to the new zip
            # file:
            for item in self.build_files:
                fh   = file( item.file_name, 'rb' )
                data = fh.read()
                fh.close()
                fh = None
                zf.writestr( item.image_name, data )

            # Write the volume manifest source code to the zip file:
            zf.writestr( 'image_volume.py', volume.image_volume_code )

            # Write the image info source code to the zip file:
            zf.writestr( 'image_info.py', images_code )

            # Done creating the new zip file:
            zf.close()
            zf = None

            # Add the new image volume to the image library:
            self.image_library.add_volume( file_name )

            # Now invoke the normal volume save so that it can add the correct
            # image info data and license file:
            volume = [ volume for volume in self.image_library.volumes
                       if volume.path == file_name ][0]
            volume.path     = file_name
            volume.zip_file = FastZipFile( path = file_name )

            volume.save()

            # Set the final status:
            self.status = '%s has been saved successfully.' % file_name

            # Indicate no errors occurred:
            error = False
        finally:
            if fh is not None:
                fh.close()

            if zf is not None:
                zf.close()

            if error:
                self.status = 'An error occurred trying to save %s.' % file_name
                remove( file_name )

#-------------------------------------------------------------------------------
#  Test code:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    from facets.core_api import Instance
    from file_sieve      import FileSieve
    from facets.api      import VSplit

    class VolumeBuilder ( HasPrivateFacets ):

        viewer  = Instance( FileSieve )
        builder = Instance( ImageVolumeBuilder, () )

        view = View(
            VSplit(
                Item( 'viewer',
                      id    = 'viewer',
                      style = 'custom'
                ),
                Item( 'builder',
                      id    = 'builder',
                      style = 'custom'
                ),
                show_labels = False,
                id          = 'splitter'
            ),
            id        = 'facets.extra.tools.image_volume_builder'
                        '.VolumeBuilder',
            title     = 'Volume Builder',
            width     = 0.75,
            height    = 0.75,
            resizable = True
        )

        def _viewer_default ( self ):
            result = FileSieve()
            result.sync_facet( 'selected_files', self.builder, 'files',
                               mutual = False )
            return result

    VolumeBuilder().edit_facets()

#-- EOF ------------------------------------------------------------------------