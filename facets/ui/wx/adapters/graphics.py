"""
Defines the concrete wxPython specific implementation of the Graphics class for
providing GUI toolkit neutral graphics support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.ui.adapters.graphics \
    import Graphics

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from abstract line styles to wx specific line styles:
LineStyle = {
    'solid': wx.SOLID,
    'dash':  wx.SHORT_DASH,
    'dot':   wx.DOT
}

# Standard integer types:
IntTypes = ( int, long )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def color_for ( color ):
    """ Returns the specified color as a wx.Colour.
    """
    if isinstance( color, wx.Colour ):
        return color

    if isinstance( color, tuple ):
        return wx.Colour( *color )

    if not isinstance( color, IntTypes ):
        from facets.extra.helper.debug import log
        log( 'Graphics adapter received an invalid color value: %s' % color )
        color = 0

    return wx.Colour( (color >> 16) & 0xFF,
                      (color >>  8) & 0xFF,
                      color         & 0xFF,
                      255 - ((color >> 24) & 0xFF) )


def dc_for ( dc ):
    """ Returns a device context that supports the extended wx drawing API if
        possible. Otherwise, it returns the original device context.
    """
    try:
        gcdc       = wx.GCDC( dc )
        gcdc._size = dc.GetSize()

        return gcdc
    except:
        return dc

#-------------------------------------------------------------------------------
#  'WxGraphics' class:
#-------------------------------------------------------------------------------

class WxGraphics ( Graphics ):

    #-- Property Implementations -----------------------------------------------

    def _get_pen ( self ):
        return self.graphics.GetPen()

    def _set_pen ( self, pen ):
        from facets.ui.pen import Pen

        if pen is None:
            pen = wx.TRANSPARENT_PEN
        elif isinstance( pen, Pen ):
            pen = wx.Pen( pen.color, pen.width, LineStyle[ pen.style ] )
        elif not isinstance( pen, wx.Pen ):
            pen = wx.Pen( color_for( pen ), 1, wx.SOLID )

        self.graphics.SetPen( pen )


    def _get_brush ( self ):
        return self.graphics.GetBrush()

    def _set_brush ( self, color ):
        if color is None:
            self.graphics.SetBrush( wx.TRANSPARENT_BRUSH )
        else:
            self.graphics.SetBrush( wx.Brush( color_for( color ), wx.SOLID ) )


    def _set_xor_mode ( self, is_xor_mode ):
        if is_xor_mode:
            self.graphics.SetLogicalFunction( wx.XOR )


    def _get_font ( self ):
        return self.graphics.GetFont()

    def _set_font ( self, font ):
        self.graphics.SetFont( font )


    def _get_text_color ( self ):
        return self.graphics.GetTextForegroundColour()

    def _set_text_color ( self, color ):
        self.graphics.SetTextForeground( color_for( color ) )


    def _get_text_background_color ( self ):
        if self.graphics.GetBackgroundMode() == wx.TRANSPARENT:
            return None

        return self.graphics.GetTextBackground()

    def _set_text_background_color ( self, color ):
        if color is None:
            self.graphics.SetBackgroundMode( wx.TRANSPARENT )
            return

        self.graphics.SetTextBackground( color_for( color ) )
        self.graphics.SetBackgroundMode( wx.SOLID )


    def _get_opacity ( self ):
        raise NotImplementedError

    def _set_opacity ( self, opacity ):
        raise NotImplementedError


    def _get_clipping_bounds ( self ):
        return self.graphics.GetClippingBox()

    def _set_clipping_bounds ( self, x_y_dx_dy ):
        self.graphics.DestroyClippingRegion()
        if x_y_dx_dy is not None:
            self.graphics.SetClippingRegion( *x_y_dx_dy )


    def _get_size ( self ):
        return self.graphics.GetSizeTuple()

    #-- Method Definitions -----------------------------------------------------

    def draw_rectangle ( self, x, y, dx, dy ):
        """ Draws a rectangle at the specified position and with the specified
            width and height.
        """
        self.graphics.DrawRectangle( x, y, dx, dy )


    def draw_rounded_rectangle ( self, x, y, dx, dy, radius ):
        """ Draws a rectangle with rounded corners at the specified position
            and with the specified size and corner radius.
        """
        self.graphics.DrawRoundedRectangle( x, y, dx, dy, radius )


    def draw_circle ( self, x, y, radius ):
        """ Draws a circle with the specified center point (x,y) and radius.
        """
        self.graphics.DrawCircle( x, y, radius )


    def draw_line ( self, x1, y1, x2, y2 ):
        """ Draws a line from (x1,y1) to (x2,y2).
        """
        if y1 == y2:
            if x2 > x1:
                x2 += 1
            else:
                x2 -= 1
        elif x1 == x2:
            if y2 > y1:
                y2 += 1
            else:
                y2 -= 1

        self.graphics.DrawLine( x1, y1, x2, y2 )


    def draw_bitmap ( self, bitmap, x, y ):
        """ Draws a specified bitmap at the specified location.
        """
        self.graphics.DrawBitmap( bitmap, x, y, True )


    def bitmap_size ( self, bitmap ):
        """ Returns the size (dx,dy) of the specified toolkit specific bitmap:
        """
        return ( bitmap.GetWidth(), bitmap.GetHeight() )


    def draw_text ( self, text, x, y ):
        """ Draws the specified text string at the specified (x,y) location.
        """
        self.graphics.DrawText( text, x, y )


    def text_size ( self, text ):
        """ Returns the size (dx,dy) of the specified text using the current
            font.
        """
        return self.graphics.GetTextExtent( text )


    def graphics_bitmap ( self, bitmap ):
        """ Returns a new graphics memory object using the specified bitmap.
        """
        dc = wx.MemoryDC()
        dc.SelectObject( bitmap )

        return WxGraphics( dc )


    def graphics_buffer ( self, dx = None, dy = None, alpha = False ):
        """ Returns a new graphics memory object of the specified size (dx,dy)
            that can be used to implement a buffered screen update. If
            alpha is True, the resulting graphics object should support an
            alpha channel; otherwise it does not need to.
        """
        dc  = BufferDC( self.graphics, dx, dy )
        dc2 = dc_for( dc )

        return WxGraphics( dc2, _dc = dc, bitmap = dc.bitmap )


    def blit ( self, dst_x, dst_y, dst_dx, dst_dy, g,
                     src_x = 0, src_y = 0, src_dx = None, src_dy = None ):
        """ Performs a standard BLT (block transfer) operation from one graphics
            object to another, copying g(src_x,src_y,src_dx,syc_dy) to
            self(dst_x,dst_y,dst_dx,dst_dy). If src_dx or src_dy is None, then
            the corresponding dst_dx or dst_dy value is used to determine the
            source rectangle size. Note that g may also specify a bitmap, as
            returned by an ImageResource 'bitmap' attribute, in place of a
            graphics adapter.
        """
        dst_dc = self._dc or self.graphics
        if isinstance( g, Graphics ):
            src_dc = g.graphics
        else:
            src_dc = wx.MemoryDC()
            src_dc.SelectObject( g )

        if src_dx is None:
            src_dx = dst_dx

        if src_dy is None:
            src_dy = dst_dy

        if (src_dx == dst_dx) and (src_dy == dst_dy):
            dst_dc.Blit( dst_x, dst_y, dst_dx, dst_dy, src_dc, src_x, src_y,
                         useMask = True )
        else:
            sx = float( dst_dx ) / src_dx
            sy = float( dst_dy ) / src_dy
            dst_dc.SetUserScale( sx, sy )
            dst_dc.Blit( int( round( dst_x / sx ) ),
                         int( round( dst_y / sy ) ),
                         int( round( dst_dx / sx ) ),
                         int( round( dst_dy / sy ) ),
                         src_dc, src_x, src_y, useMask = True )
            dst_dc.SetUserScale( 1.0, 1.0 )


    def copy ( self, x = 0, y = 0 ):
        """ Copies the contents of the graphics buffer back to the graphics
            object it was created from at the specified (x,y) location.
        """
        self._dc.copy( x, y )

#-------------------------------------------------------------------------------
#  'BufferDC' class:
#-------------------------------------------------------------------------------

# Precompute a value needed by the BufferDC constructor:
none_none = ( None, None )

class BufferDC ( wx.MemoryDC ):
    """ An off-screen buffer class.

        This class implements a off-screen output buffer. Data is meant to
        be drawn in the buffer and then blitted directly to the output device
        context.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, dc, width = None, height = None ):
        """ Initializes the buffer.
        """
        wx.MemoryDC.__init__( self )

        if width is None:
            # Note: Sometimes the dc is a GCDC, which returns really large (and
            # incorrect) values for size, so the 'gc_for' function attaches a
            # correct size value to the GCDC in the '_size' attribute. So, if
            # the dc has a '_size' attribute, we use that value instead of the
            # value reported by the GetSize() method:
            width, height = getattr( dc, '_size', none_none )
            if width is None:
                width, height = dc.GetSize()

        self.dc     = dc
        self.bitmap = wx.EmptyBitmap( width, height )

        self.SelectObject( self.bitmap )

        self.SetFont( dc.GetFont() )


    def copy ( self, x = 0, y = 0 ):
        """ Performs the blit of the buffer contents to the specified device
            context location.
        """
        self.dc.Blit( x, y, self.bitmap.GetWidth(), self.bitmap.GetHeight(),
                      self, 0, 0 )

#-- EOF ------------------------------------------------------------------------