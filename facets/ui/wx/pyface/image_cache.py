"""
Facets pyface package component
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.core_api \
    import HasFacets, implements

from facets.ui.pyface.i_image_cache \
    import IImageCache, MImageCache

#-------------------------------------------------------------------------------
#  'ImageCache' class:
#-------------------------------------------------------------------------------

class ImageCache ( MImageCache, HasFacets ):
    """ The toolkit specific implementation of an ImageCache. See the
        IImageCache interface for the API documentation.
    """

    implements( IImageCache )

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, width, height ):
        self._width = width
        self._height = height

        # The images in the cache!
        self._images = {} # {filename : wx.Image}

        # The images in the cache converted to bitmaps.
        self._bitmaps = {} # {filename : wx.Bitmap}

    #-- 'ImageCache' Interface -------------------------------------------------

    def get_image ( self, filename ):
        # Try the cache first:
        image = self._images.get( filename )

        if image is None:
            # Load the image from the file and add it to the list.
            #
            # N.B 'wx.BITMAP_TYPE_ANY' tells wxPython to attempt to autodetect
            # --- the image format.
            image = wx.Image( filename, wx.BITMAP_TYPE_ANY )

            # We force all images in the cache to be the same size:
            if ((image.GetWidth()  != self._width) or
                (image.GetHeight() != self._height)):
                image.Rescale( self._width, self._height )

            # Add the bitmap to the cache:
            self._images[ filename ] = image

        return image


    def get_bitmap ( self, filename ):
        # Try the cache first:
        bmp = self._bitmaps.get( filename )
        if bmp is None:
            # Get the image:
            image = self.get_image( filename )

            # Convert the alpha channel to a mask:
            image.ConvertAlphaToMask()

            # Convert it to a bitmaps:
            bmp = image.ConvertToBitmap()

            # Add the bitmap to the cache:
            self._bitmaps[ filename ] = bmp

        return bmp

#-- EOF ------------------------------------------------------------------------