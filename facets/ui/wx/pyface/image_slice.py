"""
The wxPython specific implementation extensions of the ImageSlice class.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

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
        dx = bitmap.GetWidth()
        dy = bitmap.GetHeight()
        opaque_bitmap = wx.EmptyBitmap( dx, dy )
        mdc2 = wx.MemoryDC()
        mdc2.SelectObject( opaque_bitmap )
        mdc2.SetBrush( wx.Brush( WindowColor ) )
        mdc2.SetPen( wx.TRANSPARENT_PEN )
        mdc2.DrawRectangle( 0, 0, dx, dy )
        mdc = wx.MemoryDC()
        mdc.SelectObject( bitmap )
        mdc2.Blit( 0, 0, dx, dy, mdc, 0, 0, useMask = True )
        mdc.SelectObject(  wx.NullBitmap )
        mdc2.SelectObject( wx.NullBitmap )

        return opaque_bitmap


    def x_bitmap_data ( self, bitmap ):
        """ Returns the image data associated with the specified bitmap in a
            form that can easily be analyzed.
        """
        return reshape( fromstring( bitmap.ConvertToImage().GetData(), uint8 ),
                        ( bitmap.GetHeight(), bitmap.GetWidth(), 3 ) )

#-- EOF ------------------------------------------------------------------------