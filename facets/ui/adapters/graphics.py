"""
Defines a Graphics base class that each GUI toolkit backend must provide a
concrete implementation of.

The Graphics class adapts a GUI toolkit specific graphics object (such as a
wx.DC or Qt.QPainter object) to provide a set of toolkit neutral properties
and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Property, Any

#-------------------------------------------------------------------------------
#  'Graphics' class:
#-------------------------------------------------------------------------------

class Graphics ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The GUI toolkit specific graphics object being adapted:
    graphics = Any

    # The current pen:
    pen = Property

    # The current brush:
    brush = Property

    # Should drawing be performed using the XOR drawing mode?
    xor_mode = Property

    # Should anti-aliased drawing be performed (if possible)?
    anti_alias = Property

    # The current font being used by the graphics object:
    font = Property

    # The color used to draw text:
    text_color = Property

    # The background color used to draw text:
    text_background_color = Property

    # The opacity used when drawing:
    opacity = Property

    # The bounds of the clipping area:
    clipping_bounds = Property

    # The size of the graphics area:
    size = Property

    # The bitmap associated with the graphics object (if any):
    bitmap = Any

    #-- Method Implementations -------------------------------------------------

    def __init__ ( self, graphics, **facets ):
        """ Initializes the object by saving the graphics object being adapted.
        """
        super( Graphics, self ).__init__( **facets )

        self.graphics = graphics


    def __call__ ( self ):
        """ Returns the graphics object being adapted.
        """
        return self.graphics

    #-- Property Implementations -----------------------------------------------

    def _get_pen ( self ):
        raise NotImplementedError

    def _set_pen ( self, color ):
        raise NotImplementedError


    def _get_brush ( self ):
        raise NotImplementedError

    def _set_brush ( self, color ):
        raise NotImplementedError


    def _set_xor_mode ( self, is_xor_mode ):
        raise NotImplementedError


    def _set_anti_alias ( self, anti_alias ):
        raise NotImplementedError


    def _get_font ( self ):
        raise NotImplementedError

    def _set_font ( self, font ):
        raise NotImplementedError


    def _get_text_color ( self ):
        raise NotImplementedError

    def _set_text_color ( self, color ):
        raise NotImplementedError


    def _get_text_background_color ( self ):
        raise NotImplementedError

    def _set_text_background_color ( self, color ):
        raise NotImplementedError


    def _get_opacity ( self ):
        raise NotImplementedError

    def _set_opacity ( self, opacity ):
        raise NotImplementedError


    def _get_clipping_bounds ( self ):
        raise NotImplementedError

    def _set_clipping_bounds ( self, x_y_dx_dy ):
        raise NotImplementedError


    def _get_size ( self ):
        raise NotImplementedError

    #-- Method Definitions -----------------------------------------------------

    def draw_rectangle ( self, x, y, dx, dy ):
        """ Draws a rectangle at the specified position and with the specified
            width and height.
        """
        raise NotImplementedError


    def draw_rounded_rectangle ( self, x, y, dx, dy, radius ):
        """ Draws a rectangle with rounded corners at the specified position
            and with the specified size and corner radius.
        """
        raise NotImplementedError


    def draw_circle ( self, x, y, radius ):
        """ Draws a circle with the specified center point (x,y) and radius.
        """
        raise NotImplementedError


    def draw_line ( self, x1, y1, x2, y2 ):
        """ Draws a line from (x1,y1) to (x2,y2).
        """
        raise NotImplementedError


    def draw_polygon ( self, points ):
        """ Draws the closed polygon specified by *points*. *points* can either
            be a list of Point objects or a Polygon object.
        """
        raise NotImplementedError


    def draw_polyline ( self, points ):
        """ Draws the polyline specified by *points*. *points* can either
            be a list of Point objects or a Polygon object.
        """
        raise NotImplementedError


    def draw_bitmap ( self, bitmap, x, y ):
        """ Draws a specified bitmap at the specified location.
        """
        raise NotImplementedError


    def bitmap_size ( self, bitmap ):
        """ Returns the size (dx,dy) of the specified toolkit specific bitmap:
        """
        raise NotImplementedError


    def draw_text ( self, text, x, y ):
        """ Draws the specified text string at the specified (x,y) location.
        """
        raise NotImplementedError


    def text_size ( self, text ):
        """ Returns the size (dx,dy) of the specified text using the current
            font.
        """
        raise NotImplementedError


    def graphics_bitmap ( self, bitmap ):
        """ Returns a new graphics memory object using the specified bitmap.
        """
        raise NotImplementedError


    def graphics_buffer ( self, dx = None, dy = None, alpha = False ):
        """ Returns a new graphics memory object of the specified size (dx,dy)
            that can be used to implement a buffered screen update. If
            alpha is True, the resulting graphics object should support an
            alpha channel; otherwise it does not need to.
        """
        raise NotImplementedError


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
        raise NotImplementedError


    def copy ( self, x = 0, y = 0 ):
        """ Copies the contents of the graphics buffer back to the graphics
            object it was created from at the specified (x,y) location.
        """
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------