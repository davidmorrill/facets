"""
Defines the concrete Qt4 specific implementation of the Graphics class for
providing GUI toolkit neutral graphics support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import Qt, QPoint, QPointF

from PyQt4.QtGui \
    import QColor, QPainter, QPen, QBrush, QPixmap, QFontMetrics, QPolygonF

from facets.ui.adapters.graphics \
    import Graphics

from facets.ui.qt4.font_facet \
    import create_facets_font

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from abstract line styles to Qt specific line styles:
LineStyles = {
    'solid': Qt.SolidLine,
    'dash':  Qt.DashLine,
    'dot':   Qt.DotLine
}

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def color_for ( color ):
    """ Returns the specified color as a QColor.
    """
    if isinstance( color, tuple ):
        if isinstance( color[0], float ):
            color = [ int( 255.0 * c ) for c in color ]

        return QColor( *color )

    if isinstance( color, int ):
        return QColor(
            (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
        )

    return color


def painter_for ( context ):
    """ Returns a QPainter for the specified *context* object.
    """
    graphics = QPainter( context )
    graphics.setRenderHint( QPainter.TextAntialiasing )

    return graphics


def points_for ( points ):
    """ Returns a list of QPointF objects derived from *points*, which can
        either be a list of Point objects or a Polygon object.
    """
    # Process a list of Point objects:
    if isinstance( points, list ):
        return QPolygonF( [ point_for( point ) for point in points ] )

    # Process a Polygon object:
    if points._cached is None:
        points._cached = QPolygonF(
            [ point_for( point ) for point in points.points ]
        )

    return points._cached


def point_for ( point ):
    """ Returns the QPoint object corresponding to the Point object specified by
        *point*.
    """
    if point._cached is None:
        point._cached = QPointF( *point.xy )

    return point._cached

#-------------------------------------------------------------------------------
#  'QtGraphics' class:
#-------------------------------------------------------------------------------

class QtGraphics ( Graphics ):

    #-- Property Implementations -----------------------------------------------

    def _get_pen ( self ):
        return self.graphics.pen()

    def _set_pen ( self, pen ):
        from facets.ui.pen import Pen

        self._no_pen = (pen is None)
        if self._no_pen:
            pen = Qt.NoPen
        elif isinstance( pen, Pen ):
            qpen = QPen( pen.color )
            qpen.setStyle( LineStyles[ pen.style ] )
            qpen.setWidth( pen.width )
            pen = qpen
        elif not isinstance( pen, QPen ):
            pen = color_for( pen )

        self.graphics.setPen( pen )


    def _get_brush ( self ):
        return self.graphics.brush()

    def _set_brush ( self, color ):
        if color is None:
            self.graphics.setBrush( Qt.NoBrush )
        else:
            self.graphics.setBrush( QBrush( color_for( color ) ) )


    def _set_xor_mode ( self, is_xor_mode ):
        if is_xor_mode:
            self.graphics.setCompositionMode( QPainter.CompositionMode_Xor )


    def _set_anti_alias ( self, anti_alias ):
        self.graphics.setRenderHint( QPainter.Antialiasing, anti_alias )


    def _get_font ( self ):
        if self._font is not None:
            return self._font

        return self.graphics.font()

    def _set_font ( self, font ):
        if isinstance( font, int ):
            font = str( font )

        if isinstance( font, basestring ):
            font = create_facets_font( font )

        ascent = getattr( font, '_ascent', None )
        if ascent is None:
            font._ascent = ascent = QFontMetrics( font ).ascent()

        self._ascent = ascent
        self._font   = font
        if not self._temp_graphics:
            self.graphics.setFont( font )


    def _get_text_color ( self ):
        return self.graphics.pen().color()

    def _set_text_color ( self, color ):
        self._set_pen( color )


    def _get_text_background_color ( self ):
        if self.graphics.backgroundMode() == Qt.TransparentMode:
            return None

        return self.graphics.background().color()

    def _set_text_background_color ( self, color ):
        if color is None:
            self.graphics.setBackgroundMode( Qt.TransparentMode )

            return

        self.graphics.setBackground( QBrush( color_for( color ) ) )
        self.graphics.setBackgroundMode( Qt.OpaqueMode )


    def _get_opacity ( self ):
        return self.graphics.opacity()

    def _set_opacity ( self, opacity ):
        self.graphics.setOpacity( opacity )


    def _get_clipping_bounds ( self ):
        rect = self.graphics.clipRegion().boundingRect()

        return ( rect.x(), rect.y(), rect.width(), rect.height() )

    def _set_clipping_bounds ( self, x_y_dx_dy ):
        if x_y_dx_dy is None:
            self.graphics.setClipping( False )
        else:
            self.graphics.setClipping( True )
            self.graphics.setClipRect( *x_y_dx_dy )


    def _get_size ( self ):
        # fixme: I'm not sure if this is the right call to make...
        rect = self.graphics.viewport()

        return ( rect.width(), rect.height() )

    #-- Method Definitions -----------------------------------------------------

    def draw_rectangle ( self, x, y, dx, dy ):
        """ Draws a rectangle at the specified position and with the specified
            width and height.
        """
        if self._no_pen:
            self.graphics.drawRect( x, y, dx, dy )
        else:
            self.graphics.drawRect( x, y, dx - 1, dy - 1 )


    def draw_rounded_rectangle ( self, x, y, dx, dy, radius ):
        """ Draws a rectangle with rounded corners at the specified position
            and with the specified size and corner radius.
        """
        self.graphics.drawRoundedRect( x, y, dx, dy,
                                       float( radius ), float( radius ) )


    def draw_circle ( self, x, y, radius ):
        """ Draws a circle with the specified center point (x,y) and radius.
        """
        self.graphics.drawEllipse( QPoint( x, y ), radius, radius )


    def draw_line ( self, x1, y1, x2, y2 ):
        """ Draws a line from (x1,y1) to (x2,y2).
        """
        self.graphics.drawLine( x1, y1, x2, y2 )


    def draw_polygon ( self, points ):
        """ Draws the closed polygon specified by *points*. *points* can either
            be a list of Point objects or a Polygon object.
        """
        self.graphics.drawPolygon( points_for( points ) )


    def draw_polyline ( self, points ):
        """ Draws the polyline specified by *points*. *points* can either
            be a list of Point objects or a Polygon object.
        """
        self.graphics.drawPolyline( points_for( points ) )


    def draw_bitmap ( self, bitmap, x, y ):
        """ Draws a specified bitmap at the specified location.
        """
        self.graphics.drawPixmap( x, y, bitmap )


    def bitmap_size ( self, bitmap ):
        """ Returns the size (dx,dy) of the specified toolkit specific bitmap:
        """
        return ( bitmap.width(), bitmap.height() )


    def draw_text ( self, text, x, y ):
        """ Draws the specified text string at the specified (x,y) location.
        """
        self.graphics.drawText( x, y + (self._ascent or 12), text )


    def text_size ( self, text ):
        """ Returns the size (dx,dy) of the specified text using the current
            font.
        """
        rect = QFontMetrics( self.font ).boundingRect( text )

        return ( rect.width(), rect.height() )


    def graphics_bitmap ( self, bitmap ):
        """ Returns a new graphics memory object using the specified bitmap.
        """
        return QtGraphics( painter_for( bitmap ) )


    def graphics_buffer ( self, dx = None, dy = None, alpha = False ):
        """ Returns a new graphics memory object of the specified size (dx,dy)
            that can be used to implement a buffered screen update. If
            alpha is True, the resulting graphics object should support an
            alpha channel; otherwise it does not need to.
        """
        # According to the Qt documentation, all Qt screen updates are
        # double-buffered, so this support is normally not really needed. As a
        # result, we simply return 'self' and ignore the 'copy' method in the
        # case where (dx,dy) is not specified:
        if dx is None:
            return self

        # fixme: Do we need to worry about 'alpha':
        pixmap   = QPixmap( dx, dy )
        graphics = painter_for( pixmap )
        graphics.setFont( self.font )

        return QtGraphics( graphics, _painter = self.graphics,
                                     bitmap   = pixmap )


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
        if src_dx is None:
            src_dx = dst_dx

        if src_dy is None:
            src_dy = dst_dy

        # Convert an AbstractGraphics Adapter to a QPixmap (if it is not already
        # one):
        if isinstance( g, Graphics ):
            # fixme: I think that for all actual use cases, 'g' will be created
            # from a QPixmap, so the 'device' call will work...
            g = g.graphics.device()

        self.graphics.drawPixmap( dst_x, dst_y, dst_dx, dst_dy, g,
                                  src_x, src_y, src_dx, src_dy )


    def copy ( self, x = 0, y = 0 ):
        """ Copies the contents of the graphics buffer back to the graphics
            object it was created from at the specified (x,y) location.
        """
        painter = self._painter
        if painter is not None:
            painter.drawPixmap( x, y, self.bitmap )
            control = getattr( painter, '_control', None )
            if control is not None:
                control.update()

#-- EOF ------------------------------------------------------------------------