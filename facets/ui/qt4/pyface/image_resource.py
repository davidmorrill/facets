"""
The Qt4 toolkit specific implementation of an ImageResource. See the
i_image_resource module for the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import abspath

from numpy \
    import reshape, fromstring, uint8

from PyQt4.QtGui \
    import QIcon

from facets.core_api \
    import Any, cached_property

from facets.ui.pyface.i_image_resource \
    import MImageResource

from facets.ui.qt4.adapters.graphics \
    import QtGraphics, painter_for

#-------------------------------------------------------------------------------
#  'ImageResource' class:
#-------------------------------------------------------------------------------

class ImageResource ( MImageResource ):
    """ The Qt4 toolkit specific implementation of an ImageResource. See the
        i_image_resource module for the API documentation.
    """

    #-- Private Interface ------------------------------------------------------

    # The resource manager reference for the image.
    _ref = Any

    #-- Property Implementations -----------------------------------------------

    def _get_width ( self ):
        return self.bitmap.width()


    def _get_height ( self ):
        return self.bitmap.height()


    def _get_graphics ( self ):
        return QtGraphics( painter_for( self.bitmap ) )


    @cached_property
    def _get_pixels ( self ):
        image = self.bitmap.toImage()
        bits  = image.bits()
        bits.setsize( image.numBytes() )

        return reshape( fromstring( bits.asstring(), uint8 ),
                        ( self.height, self.width, 4 ) )  # [ 0:, 0:, 2:-5:-1 ]


    @cached_property
    def _get_mono_bitmap ( self ):
        # fixme: Implement this correctly...
        return self.bitmap

    #-- 'ImageResource' Interface ----------------------------------------------

    # Qt doesn't specifically require bitmaps anywhere so just use images:
    create_bitmap             = MImageResource.create_image
    create_bitmap_from_pixels = MImageResource.create_image_from_pixels


    def create_icon ( self, size = None ):
        ref = self._get_ref( size )

        if ref is not None:
            image = ref.load()
        else:
            image = self._get_image_not_found_image()

        return QIcon( image )


    def create_icon_from_pixels ( self ):
        """ Creates a toolkit specific icon from the 'pixels' for this resource.
        """
        return QIcon( self.create_image_from_pixels() )


    def save ( self, file_name ):
        """ Saves the image to the specified *file_name*. The *file_name*
            extension determines the format the file is saved in, and may be
            '.png', '.jpg' or '.jpeg', although other file formats may be
            supported, depending upon the underlying GUI toolkit implementation.
        """
        self.bitmap.save( file_name )

    #-- Private Methods --------------------------------------------------------

    def _get_absolute_path ( self ):
        # FIXME: This doesn't quite wotk the new notion of image size. We
        # should find out who is actually using this facet, and for what!
        # (AboutDialog uses it to include the path name in some HTML.)
        ref = self._get_ref()
        if ref is not None:
            return abspath( self._ref.filename )

        return self._get_image_not_found().absolute_path

#-- EOF ------------------------------------------------------------------------