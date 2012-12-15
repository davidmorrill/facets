"""
GUI toolkit neutral class to aid in automatically computing the 'slice' points
for a specified ImageResource and then drawing it so that it can be 'stretched'
to fit a larger region than the original image.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from colorsys \
    import rgb_to_hls

from numpy \
    import maximum, minimum

from facets.core_api \
    import HasPrivateFacets, Instance, Int, List, Enum, Bool, Any

from i_image_resource \
    import AnImageResource

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# GUI toolkit neutral colors:
BLACK = ( 0, 0, 0 )
WHITE = ( 255, 255, 255 )
RED   = ( 255, 0, 0 )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def paint_parent ( g, window ):
    """ Recursively paint the parent's background if they have an associated
        image slice.
    """
    parent = window.parent
    slice  = parent.image_slice
    if slice is not None:
        x, y   = window.position
        dx, dy = parent.size
        slice.fill( g, -x, -y, dx, dy )
    else:
        # Otherwise, just paint the normal window background color:
        dx, dy  = window.size
        g.brush = parent.background_color
        color   = g.pen
        g.pen   = None
        g.draw_rectangle( 0, 0, dx, dy )
        g.pen   = color

    return slice

#-------------------------------------------------------------------------------
#  'ImageSlice' class:
#-------------------------------------------------------------------------------

class ImageSlice ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The ImageResource to be sliced and drawn:
    image = Instance( AnImageResource )

    # The minimum number of adjacent, identical rows/columns needed to identify
    # a repeatable section:
    threshold = Int( 10 )

    # The maximum number of 'stretchable' rows and columns:
    stretch_rows    = Enum( 1, 2 )
    stretch_columns = Enum( 1, 2 )

    # Width/height of the image borders:
    top    = Int
    bottom = Int
    left   = Int
    right  = Int

    # Width/height of the extended image borders:
    xtop    = Int
    xbottom = Int
    xleft   = Int
    xright  = Int

    # The color to use for content text:
    content_color = Any # Tuple( Int, Int, Int )

    # The color to use for label text:
    label_color = Any # Tuple( Int, Int, Int )

    # The background color of the image:
    bg_color = Any # Tuple( Int, Int, Int )

    # Should debugging slice lines be drawn?
    debug = Bool( False )

    #-- Private Facets ---------------------------------------------------------

    # The current image's opaque bitmap:
    opaque_bitmap = Any

    # Size of the current image:
    dx = Int
    dy = Int

    # Size of the current image's slices:
    dxs = List
    dys = List

    # Fixed minimum size of current image:
    fdx = Int
    fdy = Int

    #-- Public Methods ---------------------------------------------------------

    def fill ( self, g, x, y, dx, dy, transparent = True ):
        """ 'Stretch fill' the specified region of a device context with the
            sliced image.
        """
        # Create the source image graphics object:
        if transparent:
            bitmap = self.image.bitmap
        else:
            bitmap = self.opaque_bitmap

        ig = g.graphics_bitmap( bitmap )

        # Set up the drawing parameters:
        sdx, sdy = self.dx, self.dx
        dxs, dys = self.dxs, self.dys
        tdx, tdy = dx - self.fdx, dy - self.fdy

        # Calculate vertical slice sizes to use for source and destination:
        n = len( dxs )
        if n == 1:
            pdxs = [ ( 0, 0 ), ( 1, max( 1, tdx / 2 ) ), ( sdx - 2, sdx - 2 ),
                     ( 1, max( 1, tdx - ( tdx / 2 ) ) ), ( 0, 0 ) ]
        elif n == 3:
            pdxs = [ ( dxs[0], dxs[0] ), ( dxs[1], max( 0, tdx ) ), ( 0, 0 ),
                     ( 0, 0 ), ( dxs[2], dxs[2] ) ]
        else:
            pdxs = [ ( dxs[0], dxs[0] ), ( dxs[1], max( 0, tdx / 2 ) ),
                     ( dxs[2], dxs[2] ), ( dxs[3], max( 0, tdx - (tdx / 2) ) ),
                     ( dxs[4], dxs[4] ) ]

        # Calculate horizontal slice sizes to use for source and destination:
        n = len( dys )
        if n == 1:
            pdys = [ ( 0, 0 ), ( 1, max( 1, tdy / 2 ) ), ( sdy - 2, sdy - 2 ),
                     ( 1, max( 1, tdy - (tdy / 2) ) ), ( 0, 0 ) ]
        elif n == 3:
            pdys = [ ( dys[0], dys[0] ), ( dys[1], max( 0, tdy ) ), ( 0, 0 ),
                     ( 0, 0 ), ( dys[2], dys[2] ) ]
        else:
            pdys = [ ( dys[0], dys[0] ), ( dys[1], max( 0, tdy / 2 ) ),
                     ( dys[2], dys[2] ), ( dys[3], max( 0, tdy - (tdy / 2) ) ),
                     ( dys[4], dys[4] ) ]

        # Iterate over each cell, performing a stretch fill from the source
        # image to the destination window:
        last_x, last_y = x + dx, y + dy
        y0, iy0 = y, 0
        for idy, wdy in pdys:
            if y0 >= last_y:
                break

            if wdy != 0:
                x0, ix0 = x, 0
                for idx, wdx in pdxs:
                    if x0 >= last_x:
                        break

                    if wdx != 0:
                        self._fill( ig, ix0, iy0, idx, idy,
                                    g,  x0,  y0,  wdx, wdy )
                        x0 += wdx
                    ix0 += idx
                y0 += wdy
            iy0 += idy

        if self.debug:
            g.pen = RED
            g.draw_line( x, y + self.top, last_x, y + self.top )
            g.draw_line( x, last_y - self.bottom - 1,
                         last_x, last_y - self.bottom - 1 )
            g.draw_line( x + self.left, y, x + self.left, last_y )
            g.draw_line( last_x - self.right - 1, y,
                         last_x - self.right - 1, last_y )

    #-- Event Handlers ---------------------------------------------------------

    def _image_set ( self, image ):
        """ Handles the 'image' facet being changed.
        """
        bitmap = image.bitmap

        # Save the bitmap size information:
        self.dx, self.dy = image.width, image.height

        # Create the opaque version of the bitmap:
        self.opaque_bitmap = self.x_bitmap_opaque( bitmap )

        # Finally, analyze the image to find out its characteristics:
        self._analyze_bitmap()

    #-- Private Methods --------------------------------------------------------

    def _analyze_bitmap ( self ):
        """ Analyzes the bitmap.
        """
        # Get the image data:
        threshold = self.threshold
        dx, dy    = self.dx, self.dy
        data      = self.x_bitmap_data( self.opaque_bitmap )

        # Find the horizontal slices:
        matches  = []
        y, last  = 0, dy - 1
        max_diff = 0.10 * dx
        while y < last:
            y_data = data[y]
            for y2 in xrange( y + 1, dy ):
                y2_data = data[y2]
                if (maximum( y_data, y2_data ) -
                    minimum( y_data, y2_data )).sum() > max_diff:
                    break

            n = y2 - y
            if n >= threshold:
                matches.append( ( y, n ) )

            y = y2

        n = len( matches )
        if n == 0:
            if dy > 50:
                matches = [ ( 0, dy ) ]
            else:
                matches = [ ( dy / 2, 1 ) ]
        elif n > self.stretch_rows:
            matches.sort( lambda l, r: cmp( r[1], l[1] ) )
            matches = matches[ : self.stretch_rows ]

        # Calculate and save the horizontal slice sizes:
        self.fdy, self.dys = self._calculate_dxy( dy, matches )

        # Find the vertical slices:
        matches  = []
        x, last  = 0, dx - 1
        max_diff = 0.10 * dy
        while x < last:
            x_data = data[ :, x ]
            for x2 in xrange( x + 1, dx ):
                if abs( x_data - data[ :, x2 ] ).sum() > max_diff:
                    break

            n = x2 - x
            if n >= threshold:
                matches.append( ( x, n ) )

            x = x2

        n = len( matches )
        if n == 0:
            if dx > 50:
                matches = [ ( 0, dx ) ]
            else:
                matches = [ ( dx / 2, 1 ) ]
        elif n > self.stretch_columns:
            matches.sort( lambda l, r: cmp( r[1], l[1] ) )
            matches = matches[ : self.stretch_columns ]

        # Calculate and save the vertical slice sizes:
        self.fdx, self.dxs = self._calculate_dxy( dx, matches )

        # Save the border size information:
        self.top    = min( dy / 2, self.dys[0]  )
        self.bottom = min( dy / 2, self.dys[-1] )
        self.left   = min( dx / 2, self.dxs[0]  )
        self.right  = min( dx / 2, self.dxs[-1] )

        # Find the optimal size for the borders (i.e. xleft, xright, ... ):
        self._find_best_borders( data )

        # Save the background color:
        x, y          = (dx / 2), (dy / 2)
        r, g, b       = data[ y, x ]
        self.bg_color = ( r, g, b )

        # Find the best contrasting text color (black or white):
        self.content_color = self._find_best_color( data, x, y )

        # Find the best contrasting label color:
        if self.xtop >= self.xbottom:
            y = self.xtop / 2
        else:
            y = dy - (self.xbottom / 2) - 1

        self.label_color = self._find_best_color( data, x, y )


    def _fill ( self, ig, ix, iy, idx, idy, g, x, y, dx, dy ):
        """ Performs a stretch fill of a region of an image into a region of a
            window device context.
        """
        last_x, last_y = x + dx, y + dy
        while y < last_y:
            ddy = min( idy, last_y - y )
            x0  = x
            while x0 < last_x:
                ddx = min( idx, last_x - x0 )
                g.blit( x0, y, ddx, ddy, ig, ix, iy )
                x0 += ddx

            y += ddy


    def _calculate_dxy ( self, d, matches ):
        """ Calculate the size of all image slices for a specified set of
            matches.
        """
        if len( matches ) == 1:
            d1, d2 = matches[0]

            return ( d - d2, [ d1, d2, d - d1 - d2 ] )

        d1, d2 = matches[0]
        d3, d4 = matches[1]

        return ( d - d2 - d4, [ d1, d2, d3 - d1 - d2, d4, d - d3 - d4 ] )


    def _find_best_borders ( self, data ):
        """ Find the best set of image slice border sizes (e.g. for images with
            rounded corners, there should exist a better set of borders than
            the ones computed by the image slice algorithm.
        """
        # Make sure the image size is worth bothering about:
        dx, dy = self.dx, self.dy
        if (dx < 5) or (dy < 5):
            return

        # Calculate the starting point:
        left = right  = dx / 2
        top  = bottom = dy / 2

        # Calculate the end points:
        last_y = dy - 1
        last_x = dx - 1

        # Mark which edges as 'scanning':
        t = b = l = r = True

        # Keep looping while at last one edge is still 'scanning':
        while l or r or t or b:

            # Calculate the current core area size:
            height = bottom - top + 1
            width  = right - left + 1

            # Try to extend all edges that are still 'scanning':
            nl = (l and (left > 0) and
                  self._is_equal( data, left - 1, top, left, top, 1, height ))

            nr = (r and (right < last_x) and
                  self._is_equal( data, right + 1, top, right, top, 1, height ))

            nt = (t and (top > 0) and
                 self._is_equal( data, left, top - 1, left, top, width, 1 ))

            nb = (b and (bottom < last_y) and
                  self._is_equal( data, left, bottom + 1, left, bottom,
                                  width, 1 ))

            # Now check the corners of the edges:
            tl = ((not nl) or (not nt) or
                  self._is_equal( data, left - 1, top - 1, left, top, 1, 1 ))

            tr = ((not nr) or (not nt) or
                  self._is_equal( data, right + 1, top - 1, right, top, 1, 1 ))

            bl = ((not nl) or (not nb) or
                  self._is_equal( data, left - 1, bottom + 1, left, bottom,
                                  1, 1 ))

            br = ((not nr) or (not nb) or
                  self._is_equal( data, right + 1, bottom + 1, right, bottom,
                                  1, 1 ))

            # Calculate the new edge 'scanning' values:
            l = nl and tl and bl
            r = nr and tr and br
            t = nt and tl and tr
            b = nb and bl and br

            # Adjust the coordinate of an edge if it is still 'scanning':
            left   -= l
            right  += r
            top    -= t
            bottom += b

        # Now compute the best set of image border sizes using the current set
        # and the ones we just calculated:
        self.xleft   = min( self.left,   left )
        self.xright  = min( self.right,  dx - right - 1 )
        self.xtop    = min( self.top,    top )
        self.xbottom = min( self.bottom, dy - bottom - 1 )

        # If the image border sizes are too great a percentage of the total
        # size, discard them since we are probably dealing with a gradient:
        if (self.xtop + self.xbottom) > ((4 * dy) / 5):
            self.xtop = self.xbottom = 0

        if (self.xleft + self.xright) > ((4 * dx) / 5):
            self.xleft = self.xright = 0


    def _find_best_color ( self, data, x, y ):
        """ Find the best contrasting text color for a specified pixel
            coordinate.
        """
        r, g, b = data[ y, x ]
        h, l, s = rgb_to_hls( r / 255.0, g / 255.0, b / 255.0 )
        text_color = BLACK
        if l < 0.50:
            text_color = WHITE

        return text_color


    def _is_equal ( self, data, x0, y0, x1, y1, dx, dy ):
        """ Determines if two identically sized regions of an image array are
            'the same' (i.e. within some slight color variance of each other).
        """
        return (abs( data[ y0: y0 + dy, x0: x0 + dx ] -
                     data[ y1: y1 + dy, x1: x1 + dx ] ).sum() <
                (0.10 * dx * dy))

# Define a reusable, default ImageSlice object:
default_image_slice = ImageSlice()

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

image_slice_cache = {}

def image_slice_for ( image ):
    """ Returns a (possibly cached) ImageSlice.
    """
    global image_slice_cache

    result = image_slice_cache.get( image )
    if result is None:
        image_slice_cache[ image ] = result = ImageSlice( image = image )

    return result

#-------------------------------------------------------------------------------
# Add the toolkit specific extensions:
#-------------------------------------------------------------------------------

from facets.ui.pyface.toolkit \
    import toolkit_object

toolkit_object( 'image_slice:ImageSliceX' )

#-- EOF ------------------------------------------------------------------------