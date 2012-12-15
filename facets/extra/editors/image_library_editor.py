"""
A custom editor for selecting images from the image library.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Enum, List, Constant, Property, View, HGroup, Item, UIEditor, \
           BasicEditorFactory, property_depends_on

from facets.ui.image \
    import ImageLibrary

#-------------------------------------------------------------------------------
#  '_ImageLibraryEditor' class:
#-------------------------------------------------------------------------------

class _ImageLibraryEditor ( UIEditor ):
    """ A custom editor for selecting images from the image library.
    """

    #-- Facet Definitions ------------------------------------------------------

    # A reference to the system image library:
    library = Constant( ImageLibrary() )

    # The currently selected volume:
    volume = Enum( values = 'volumes' )

    # The list of all available volumes in the image library:
    volumes = List

    # The currently selected image:
    image = Enum( values = 'images' )

    # The list of all images within the currently selected volume:
    images = Property

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        HGroup(
            Item( 'volume', width = 125, springy = True ),
            Item( 'image',  width = 125, springy = True )
        )
    )

    #-- UIEditor Method Overrides ----------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        value = self.value
        image = None
        if isinstance( value, basestring ) and (value[:1] == '@'):
            col = value.find( ':' )
            if col > 0:
                self.volume = value[ 1: col ]
                image       = value[ col + 1: ]
                col         = image.find( '?' )
                if col >= 0:
                    image = image[ : col ]

                self.image = image

        if image is None:
            self._image_set()

        return self.edit_facets( parent = parent, kind = 'editor' )

    #-- Facet Default Values ---------------------------------------------------

    def _volume_default ( self ):
        return self.volumes[0]


    def _volumes_default ( self ):
        result = self.library.catalog.keys()
        result.sort()

        return result

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'volume' )
    def _get_images ( self ):
        n      = len( self.volume ) + 2
        volume = self.library.catalog[ self.volume ]
        result = [ key[ n: ] for key in volume.catalog.iterkeys() ]
        result.sort()

        return result

    #-- Facet Event Handlers ---------------------------------------------------

    def _volume_set ( self ):
        """ Handles the 'volume' facet being changed.
        """
        self.image = self.images[0]


    def _image_set ( self ):
        """ Handles the 'image' facet being changed.
        """
        self.value = '@%s:%s' % ( self.volume, self.image )

#-------------------------------------------------------------------------------
#  'ImageLibraryEditor' class:
#-------------------------------------------------------------------------------

class ImageLibraryEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ImageLibraryEditor

#-- EOF ------------------------------------------------------------------------
