"""
Defines an ImageLibrary LibraryManager for managing changes made to images
stored in an ImageLibrary ImageVolume.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, SingletonHasPrivateFacets, Instance, Int, Bool, \
           List, Button, Property, Constant, on_facet_set, cached_property,  \
           View, HGroup, Item, Theme, GridEditor, spring, VerticalNotebookEditor

from facets.ui.image \
    import ImageLibrary, ImageVolume, ImageInfo

from facets.ui.grid_adapter \
    import GridAdapter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The 'on_facet_set' listener pattern used by the ImageManager:
image_listener = ('image:[name,description,category,keywords,copyright,'
                  'license,theme:[border.-,content.-,label.-,alignment]]')

#-------------------------------------------------------------------------------
#  'ImageManager' class:
#-------------------------------------------------------------------------------

class ImageManager ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The library image being managed:
    image = Instance( ImageInfo )

    # The number of active references to the image:
    count = Int( 1 )

    # Has the image been modified in any way?
    modified = Bool( False )

    #-- Facets Event Handlers --------------------------------------------------

    @on_facet_set( image_listener )
    def _image_modified ( self ):
        """ Handles some key part of the image object being modified.
        """
        self.modified = True

#-------------------------------------------------------------------------------
#  'VolumeManagerGridAdapter' class:
#-------------------------------------------------------------------------------

class VolumeManagerGridAdapter ( GridAdapter ):
    """ Grid adapter for mapping VolumeManager data to a GridEditor.
    """

    columns = [ ( 'Image Name', 'image' ) ]

    # Adapter properties:
    text  = Property
    image = Property

    #-- Property Implementations -----------------------------------------------

    def _get_text ( self ):
        return self.item.image.image_name

    def _get_image ( self ):
        if self.item.modified:
            return '@std:alert16'

        return None

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'object:images:modified' )
    def _images_modified ( self ):
        """ Handles the list of images being edited being modified.
        """
        self.changed = True

#-------------------------------------------------------------------------------
#  'VolumeManager' class:
#-------------------------------------------------------------------------------

class VolumeManager ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The image volume being managed:
    volume = Instance( ImageVolume )

    # The list of images currently being managed:
    images = List( ImageManager )

    # The name of the volume:
    name = Property( depends_on = 'volume' )

    # Does the volume have any modified images?
    has_modified = Property( depends_on = 'images.modified' )

    # Is the volume empty (i.e. does it have no active images)?
    is_empty = Property( depends_on = 'images' )

    # Button used to save the contents of the volume:
    save = Button( 'Save' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'images',
              show_label = False,
              editor     = GridEditor( adapter    = VolumeManagerGridAdapter,
                                       operations = [] )
        ),
        HGroup(
            spring,
            Item( 'save',
                  show_label   = False,
                  enabled_when = 'has_modified'
            )
        )
    )

    #-- Public methods ---------------------------------------------------------

    def add ( self, image ):
        """ Adds a specified *image* **ImageInfo** object to the volume
            manager's collection.
        """
        im = self._find( image )
        if im is not None:
            im.count += 1
            return

        self.images.append( ImageManager( image = image ) )


    def remove ( self, image ):
        """ Removes a reference to a specified *image* **ImageInfo** object from
            the volume manager's collection.
        """
        im = self._find( image )
        if ( im is not None ) and ( im.count > 0 ):
            im.count -= 1
            if ( im.count == 0 ) and ( not im.modified ):
                self.images.remove( im )

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        return self.volume.name


    @cached_property
    def _get_has_modified ( self ):
        for image in self.images:
            if image.modified:
                return True

        return False


    def _get_is_empty ( self ):
        return ( len( self.images ) == 0 )

    #-- Facets Event Handlers --------------------------------------------------

    def _save_set ( self ):
        """ Handles the user clicking the 'Save' button.
        """
        self.volume.save()
        images = self.images
        for image in images[ : ]:
            image.modified = False
            if image.count == 0:
                images.remove( image )

    #-- Private Methods --------------------------------------------------------

    def _find ( self, image ):
        """ Attempts to return the **ImageManager** object corresponding to a
            specified *image **ImageInfo** object.
        """
        for im in self.images:
            if image is im.image:
                return im

        return None

#-------------------------------------------------------------------------------
#  'LibraryManager' class:
#-------------------------------------------------------------------------------

class LibraryManager ( SingletonHasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of image volumes currently being managed:
    volumes = List( VolumeManager )

    # Reference to the image library:
    image_library = Constant( ImageLibrary() )

    #-- Facets View Defnitions -------------------------------------------------

    view = View(
        Item( 'volumes',
              show_label = False,
              editor     = VerticalNotebookEditor(
                  closed_theme  = Theme( '@std:GL5',
                                         content   = ( 0, 0, -2, 0 ),
                                         alignment = 'center' ),
                  open_theme    = '@std:GL5TB',
                  multiple_open = True,
                  scrollable    = True,
                  double_click  = False,
                  page_name     = '.name'
              ),
              item_theme = '@std:XG1'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def add ( self, image ):
        """ Adds a specified *image* **ImageInfo** object to the library
            manager's collection.
        """
        vm = self._find( image )
        if not isinstance( vm, VolumeManager ):
            vm = VolumeManager( volume = vm )
            self.volumes.append( vm )

        vm.add( image )


    def remove ( self, image ):
        """ Removes a reference to a specified *image* **ImageInfo** object from
            the library manager's collection.
        """
        vm = self._find( image )
        if isinstance( vm, VolumeManager ):
            vm.remove( image )

    #-- Facets Event Handlers --------------------------------------------------

    @on_facet_set( 'volumes:is_empty' )
    def _volume_empty ( self, object, is_empty ):
        """ Handles a VolumeManager becoming empty.
        """
        if is_empty:
            self.volumes.remove( object )

    #-- Private Methods --------------------------------------------------------

    def _find ( self, image ):
        """ Attempts to return the **ImageVolume** object corresponding to a
            specified *image **ImageInfo** object.
        """
        volume = self.image_library.find_volume( image.image_name )
        for vm in self.volumes:
            if volume is vm.volume:
                return vm

        return volume

#-- EOF ------------------------------------------------------------------------