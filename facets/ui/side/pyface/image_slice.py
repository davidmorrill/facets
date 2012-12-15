"""
The Qt4 specific implementation extensions of the ImageSlice class.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtGui \
    import QPixmap, QPainter

from numpy \
    import reshape, fromstring, uint8

from facets.core_api \
    import Category

from facets.ui.colors \
    import WindowColor

from facets.ui.pyface.image_slice \
    import ImageSlice

#-------------------------------------------------------------------------------
#  'ImageSliceX' class:
#-------------------------------------------------------------------------------

class ImageSliceX ( Category, ImageSlice ):

    #-- Extension Methods ------------------------------------------------------

    def x_bitmap_opaque ( self, bitmap ):
        """ Returns a version of the specified bitmap with no transparency.
        """
        dx = bitmap.width()
        dy = bitmap.height()
        opaque_bitmap = QPixmap( dx, dy )
        opaque_bitmap.fill( WindowColor )
        q = QPainter( opaque_bitmap )
        q.drawPixmap( 0, 0, bitmap )

        return opaque_bitmap


    def x_bitmap_data ( self, bitmap ):
        """ Returns the image data associated with the specified bitmap in a
            form that can easily be analyzed.
        """
        image = bitmap.toImage()
        bits  = image.bits()
        ### PYSIDE: bits.setsize( image.numBytes() )
        ### PYSIDE:
        ### PYSIDE: return reshape( fromstring( bits.asstring(), uint8 ),
        ### PYSIDE:            ( bitmap.height(), bitmap.width(), 4 ) )[ 0:, 0:, 2:-5:-1 ]

        return reshape( fromstring( bits, uint8 ),
                   ( bitmap.height(), bitmap.width(), 4 ) )[ 0:, 0:, 2:-5:-1 ]

#-- EOF ------------------------------------------------------------------------