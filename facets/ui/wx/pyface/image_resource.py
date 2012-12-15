"""
WxPython specific implementation of an ImageResource.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from numpy \
    import array, fromstring, reshape, ravel, insert, uint8

from facets.core_api \
    import Any, cached_property

from facets.ui.pyface.i_image_resource \
    import MImageResource

#-------------------------------------------------------------------------------
#  'ImageResource' class:
#-------------------------------------------------------------------------------

class ImageResource ( MImageResource ):
    """ The wx toolkit specific implementation of an ImageResource.  See the
        i_image_resource module for the API documentation.
    """

    #-- Class Constants --------------------------------------------------------

    # The "image not found" icon:
    _image_not_found_icon = None

    #-- Private Facets ---------------------------------------------------------

    # The resource manager reference for the image:
    _ref = Any

    #-- Property Implementations -----------------------------------------------

    def _get_width ( self ):
        return self.bitmap.GetWidth()


    def _get_height ( self ):
        return self.bitmap.GetHeight()


    @cached_property
    def _get_pixels ( self ):
        image  = self.image
        pixels = reshape( fromstring( image.GetData(), uint8 ),
                          ( self.height, self.width, 3 ) )[ :, :, ::-1 ]
        alpha  = 255
        if image.HasAlpha():
            alpha = reshape( fromstring( image.GetAlphaBuffer(), uint8 ),
                             ( self.height, self.width ) )

        return insert( pixels, 3, alpha, axis = 2 )


    @cached_property
    def _get_mono_bitmap ( self ):
        # fixme: I think we are destroying the original image here. We probably
        # need to create a new image from the original...

        image     = self.image
        data      = reshape( fromstring( image.GetData(), uint8 ),
                             ( -1, 3 ) ) * array( [ [ 0.297, 0.589, 0.114 ] ] )
        t         = data[:,0] + data[:,1] + data[:,2]
        data[:,0] = data[:,1] = data[:,2] = t
        image.SetData( ravel( data.astype( uint8 ) ).tostring() )
        image.SetMaskColour( 0, 0, 0 )

        return image.ConvertToBitmap()

    #-- ImageResource Interface ------------------------------------------------

    def create_bitmap ( self, size = None ):
        if size is None:
            return self.image.ConvertToBitmap()

        return self.create_image( size ).ConvertToBitmap()


    def create_icon ( self, size = None ):
        ref = self._get_ref( size )
        if ref is not None:
            icon = wx.Icon( self.absolute_path, wx.BITMAP_TYPE_ICO )
        else:
            icon = ImageResource._image_not_found_icon
            if icon is None:
                image = self._get_image_not_found_image()

                # Convert the image to a bitmap first and then create an icon
                # from that:
                icon = wx.EmptyIcon()
                icon.CopyFromBitmap( image.ConvertToBitmap() )

                # Cache the result globally:
                ImageResource._image_not_found_icon = icon

        return icon

#-- EOF ------------------------------------------------------------------------