"""
Defines a collection of drawable object classes.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt

from itertools \
    import ifilter

from facets.api \
    import HasFacets, HasPrivateFacets, List, Event, Instance, Str, Int, Any, \
           Float, Tuple, Bool, Range, Font, ATheme, Image, on_facet_set, inn

from facets.ui.ui_facets \
    import Alignment

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# A 2D quantity:
Value2D = Tuple( Float, Float )

#-------------------------------------------------------------------------------
#  'Point' class:
#-------------------------------------------------------------------------------

class Point ( HasPrivateFacets ):
    """ Defines an abstract Point object that can be used with a Graphics
        object.

        Note that it is the responsibility of the GUI toolkit specific
        subclasses of Graphics to correctly interpret the values of the Point
        object for their toolkit.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The (x,y) coordinate of the point:
    xy = Value2D

    # The (optional) owner of the point:
    owner = Instance( HasFacets )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, x = 0.0, y = 0.0, **facets ):
        """ Initializes the object.
        """
        super( Point, self ).__init__( **facets )

        self.xy = ( x, y )

    #-- Facet Event Handlers ---------------------------------------------------

    def _xy_set ( self ):
        """ Handles either the 'xy' facet of the point being changed.
        """
        del self._cached
        if self.owner is not None:
            self.owner.modified = self

#-------------------------------------------------------------------------------
#  'OwnedObject' class:
#-------------------------------------------------------------------------------

class OwnedObject ( HasPrivateFacets ):
    """ Defines an abstract object that has an owner and can signal to the
        owner that it has been modified.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The (optional) owner of this object:
    owner = Instance( HasFacets )

    # Event fired when any attribute affecting the visual appearance of the
    # object is modified:
    modified = Event

    #-- Public Methods ---------------------------------------------------------

    def remove ( self ):
        """ Removes the object from its owner.
        """
        inn( self.owner ).remove( self )

    #-- Facet Event Handlers ---------------------------------------------------

    def _modified_set ( self ):
        """ Handles the 'modified' facet being changed.
        """
        # Discard any optional cached values:
        del self._cached

        # Notify the owner (if any) that we have been modified:
        inn( self.owner ).set( modified = self )

#-------------------------------------------------------------------------------
#  'Drawable' class:
#-------------------------------------------------------------------------------

class Drawable ( OwnedObject ):
    """ Base class for a 'smart' object that knows how to draw itself.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the object being drawn?
    visible = Bool( True, event = 'notify_owner' )

    # The opacity used for drawing the object:
    opacity = Range( 0.0, 1.0, 1.0, event = 'notify_owner' )

    #-- Public Methods ---------------------------------------------------------

    def draw ( self, g ):
        """ Draws the polygon in the graphics context specified by *g*.
        """
        if self.visible and (self.opacity > 0.0):
            opacity   = g.opacity
            g.opacity = opacity * self.opacity
            self.paint( g )
            g.opacity = opacity

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Paints the object.

            Must be overridden by a subclass.
        """
        raise NotImplementedError

    #-- Facet Event Handlers ---------------------------------------------------

    def _notify_owner_set ( self ):
        """ Handles a visual attribute being modified by notifying the owner.
        """
        if self.owner is not None:
            self.owner.modified = self

#-------------------------------------------------------------------------------
#  'Text' class:
#-------------------------------------------------------------------------------

class Text ( Drawable ):
    """ Draws a string of text.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The text origin:
    origin = Value2D( event = 'notify_owner' )

    # The font to use to draw the text:
    font = Font( event = 'notify_owner' )

    # The text color:
    color = Any( 0x000000, event = 'notify_owner' )

    # The text to draw:
    text = Str( event = 'notify_owner' )

    #-- Drawable Method Overrides ----------------------------------------------

    def paint ( self, g ):
        """ Draws a string of text in the graphics context specified by *g*.
        """
        g.font       = self.font
        g.text_color = self.color
        x, y         = self.origin
        g.draw_text( self.text, x, y )

    #-- Public Methods ---------------------------------------------------------

    def item_at ( self, x, y ):
        """ Returns the item if it contains the point specified by (*x*,*y*) and
            None if it does not.
        """
        # fixme: implement this...
        return None


    def text_size ( self, g ):
        """ Returns the minimum size needed to display the current text using
            the current font for the graphics context *g*.
        """
        old_font, g.font = g.font, self.font
        result           = g.text_size( self.text )
        g.font           = old_font

        return result

#-------------------------------------------------------------------------------
#  'ThemedText' class:
#-------------------------------------------------------------------------------

class ThemedText ( Drawable ):
    """ Draws a string of text with a themed background.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The themed object origin:
    origin = Value2D( event = 'notify_owner' )

    # The size of the themed object:
    size = Value2D( None, event = 'notify_owner' )

    # The theme to use for the background:
    theme = ATheme( '@xform:b', event = 'notify_owner' )

    # The alignment of the text within the content part of the themed object:
    alignment = Alignment( 'left', event = 'notify_owner' )

    # The text to draw:
    text = Str( event = 'notify_owner' )

    # An optional image to draw with the text:
    image = Image

    # The label text to draw:
    label = Str( event = 'notify_owner' )

    #-- Drawable Method Overrides ----------------------------------------------

    def paint ( self, g ):
        """ Draws a themed text object.
        """
        theme = self.theme
        text  = self.text
        image = self.image
        if self.size is None:
            g.font    = theme.content_font
            self.size = theme.size_for( g, text, image )

        dx, dy = self.size
        x,  y  = self.origin
        theme.fill( g, x, y, dx, dy )

        if text != '':
            g.font = theme.content_font
            theme.draw_text( g, text, self.alignment, x, y, dx, dy, image )

        if self.label != '':
            g.font = theme.label_font
            theme.draw_label( g, self.label, None, x, y, dx, dy )

    #-- Public Methods ---------------------------------------------------------

    def item_at ( self, x, y ):
        """ Returns the item if it contains the point specified by (*x*,*y*) and
            None if it does not.
        """
        x0, y0 = self.origin
        dx, dy = self.size

        return (self if (x0 <= x < (x0 + dx)) and (y0 <= y < (y0 + dy)) else
                None)

#-------------------------------------------------------------------------------
#  'Penable' class:
#-------------------------------------------------------------------------------

class Penable ( Drawable ):
    """ Base class for a 'smart' object that knows how to draw itself using a
        pen and brush.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The pen used to draw the object:
    pen = Any( 0, event = 'notify_owner' ) # Color or Pen

    # The brush used to draw the object:
    brush = Any( None, event = 'notify_owner' )

    # Should the object be rendered using anti-aliasing?
    anti_alias = Bool( True, event = 'notify_owner' )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Draws the object in the graphics context specified by *g*.
        """
        g.pen        = self.pen
        g.brush      = self.brush
        g.anti_alias = self.anti_alias
        self.stroke( g )

    #-- Public Methods ---------------------------------------------------------

    def stroke ( self, g ):
        """ Strokes the object using the current pen and brush.

            Must be overridden by a subclass.
        """
        raise NotImplementedError

#-------------------------------------------------------------------------------
#  'Line' class:
#-------------------------------------------------------------------------------

class Line ( Penable ):
    """ Draws a line.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The start point of the line:
    p0 = Value2D( event = 'notify_owner' )

    # The end point of the line:
    p1 = Value2D( 5.0, event = 'notify_owner' )

    #-- Penable Method Overrides -----------------------------------------------

    def stroke ( self, g ):
        """ Draws a line in the graphics context specified by *g*.
        """
        x0, y0 = self.p0
        x1, y1 = self.p1
        g.draw_line( x0, y0, x1, y1 )

    #-- Public Methods ---------------------------------------------------------

    def item_at ( self, x, y ):
        """ Returns the item if it contains the point specified by (*x*,*y*) and
            None if it does not.
        """
        # fixme: implement this...
        return None

#-------------------------------------------------------------------------------
#  'Circle' class:
#-------------------------------------------------------------------------------

class Circle ( Penable ):
    """ Draws a circle.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The center of the circle:
    origin = Value2D( event = 'notify_owner' )

    # The radius of the circle:
    radius = Float( 5.0, event = 'notify_owner' )

    #-- Penable Method Overrides -----------------------------------------------

    def stroke ( self, g ):
        """ Draws a circle in the graphics context specified by *g*.
        """
        x, y = self.origin
        g.draw_circle( x, y, self.radius )

    #-- Public Methods ---------------------------------------------------------

    def item_at ( self, x, y ):
        """ Returns the item if it contains the point specified by (*x*,*y*) and
            None if it does not.
        """
        x0, y0 = self.origin
        dx     = x - x0
        dy     = y - y0

        return (self if sqrt( (dx * dx) + (dy * dy) ) <= self.radius else None)

#-------------------------------------------------------------------------------
#  'Rectangle' class:
#-------------------------------------------------------------------------------

class Rectangle ( Penable ):
    """ Draws a rectangle.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The origin of the rectangle:
    origin = Value2D( event = 'notify_owner' )

    # The size of the rectangle:
    size = Value2D( ( 10.0, 10.0 ), event = 'notify_owner' )

    # The corner radius:
    radius = Float( event = 'notify_owner' )

    # Should the object be rendered using anti-aliasing (override)?
    anti_alias = False

    #-- Penable Method Overrides -----------------------------------------------

    def stroke ( self, g ):
        """ Draws a rectangle in the graphics context specified by *g*.
        """
        x, y   = self.origin
        dx, dy = self.size
        if (dx != 0) and (dy != 0):
            if dx < 0:
                x += dx
                dx = -dx

            if dy < 0:
                y += dy
                dy = -dy

            if self.radius > 0.0:
                g.draw_rounded_rectangle( x, y, dx, dy, self.radius )
            else:
                g.draw_rectangle( x, y, dx, dy )

    #-- Public Methods ---------------------------------------------------------

    def item_at ( self, x, y ):
        """ Returns the item if it contains the point specified by (*x*,*y*) and
            None if it does not.
        """
        x0, y0 = self.origin
        dx, dy = self.size
        if dx < 0:
            x0 += dx
            dx  = -dx

        if dy < 0:
            y0 += dy
            dy  = -dy

        if not ((x0 <= x < (x0 + dx)) and (y0 <= y < (y0 + dy))):
            return None

        r = self.radius
        if r == 0.0:
            return self

        x0r = x0 + r
        x1r = x0 + dx - r
        y0r = y0 + r
        y1r = y0 + dy - r
        if (x0r <= x < x1r) or (y0r <= y < y1r):
            return self

        xr = x - (x0r if x < x0r else x1r)
        yr = y - (y0r if y < y0r else y1r)

        return (self if sqrt( (xr * xr) + (yr * yr) ) <= r else None)

#-------------------------------------------------------------------------------
#  'Polygon' class:
#-------------------------------------------------------------------------------

class Polygon ( Penable ):
    """ Draws a closed polygon.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The points forming the polygon:
    points = List # ( Point )

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'points[]' )
    def _points_modified ( self, removed, added ):
        """ Handles points being added to or removed from the polygon.
        """
        for point in removed:
            point.owner = None

        for point in added:
            point.owner = self

        self._modified_set()

    #-- Penable Method Overrides -----------------------------------------------

    def stroke ( self, g ):
        """ Draws an open polyline in the graphics context specified by *g*.
        """
        g.draw_polygon( self )

    #-- Public Methods ---------------------------------------------------------

    def remove ( self, point ):
        """ Removes the specified *point*.
        """
        if point in self.points:
            self.points.remove( point )


    def item_at ( self, x, y ):
        """ Returns the item if it contains the point specified by (*x*,*y*) and
            None if it does not.
        """
        # fixme: implement this...
        return None

#-------------------------------------------------------------------------------
#  'Polyline' class:
#-------------------------------------------------------------------------------

class Polyline ( Polygon ):
    """ Draws an open polyline.
    """

    #-- Penable Method Overrides -----------------------------------------------

    def stroke ( self, g ):
        """ Draws an open polyline in the graphics context specified by *g*.
        """
        g.draw_polyline( self )


    def item_at ( self, x, y ):
        """ Returns the item if it contains the point specified by (*x*,*y*) and
            None if it does not.
        """
        # fixme: implement this...
        return None

#-------------------------------------------------------------------------------
#  'DrawableCanvas' class:
#-------------------------------------------------------------------------------

class DrawableCanvas ( Drawable ):
    """ Defines a DrawableCanvas class for managing and drawing drawable
        objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of drawable objects:
    content = List # ( Drawable objects )

    # The tooltip for the canvas:
    tooltip = Str

    # The current display bounds of the canvas:
    bounds = Tuple( Int, Int, Int, Int )

    # The current mouse event state:
    state = Str( 'normal' )

    #-- Public Methods ---------------------------------------------------------

    def remove ( self, item = None ):
        """ Removes the specified *item*.
        """
        if item is None:
            super( DrawableCanvas, self ).remove()
        elif item in self.content:
            self.content.remove( item )


    def paint ( self, g ):
        """ Paints the contents of the canvas in the graphics context specified
            by *g*.
        """
        for item in self.content:
            item.draw( g )


    def item_at ( self, x, y ):
        """ Returns the topmost item (if any) containing the point specified by
            (*x*,*y*).
        """
        for item in reversed( self.content ):
            if item.visible and (item.opacity > 0.0):
               result = inn( item, 'item_at' )( x, y )
               if result is not None:
                   return result

        return None

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'content[]' )
    def _content_modified ( self, removed, added ):
        """ Handles the 'content' facet being modified.
        """
        for item in removed:
            item.owner = None
            item.halt_animated_facets()

        for item in added:
            item.owner = self

        self.modified = True


    def _bounds_set ( self, bounds ):
        """ Handles the 'bounds' facet being changed.
        """
        for item in ifilter( lambda x: isinstance( x, DrawableCanvas ),
                             self.content ):
            item.bounds = bounds

#-- EOF ------------------------------------------------------------------------
