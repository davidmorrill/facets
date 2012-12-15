"""
Defines the WipeImageTransition class for animating the transition from one
image to another (as used in videos and web pages) using a 'wipe' or 'push'
style.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from random \
    import shuffle

from facets.api \
    import Enum, Range, Property, property_depends_on

from facets.core.facet_base \
    import clamp

from image_transition \
    import ImageTransition

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The vertical directions:
Vertical = set( ( 'up', 'down', 'up_down', 'vertical_out', 'vertical_in' ) )

#-------------------------------------------------------------------------------
#  'WipeImageTransition' class:
#-------------------------------------------------------------------------------

class WipeImageTransition ( ImageTransition ):
    """ Defines the WipeImageTransition class for animating the transition from
        one image to another (as used in videos and web pages) using a 'wipe' or
        'push' style.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The transition style:
    style = Enum( 'wipe', 'push' )

    # The transition direction:
    direction = Enum( 'left', 'right', 'left_right', 'up', 'down', 'up_down',
                      'vertical_out', 'vertical_in', 'horizontal_out',
                      'horizontal_in' )

    # The number of rows (or columns) to use:
    elements = Range( 1, 64, 1 )

    # The transition mode:
    mode = Enum( 'left_right', 'right_left', 'top_bottom', 'bottom_top',
                 'middle', 'random' )

    # The delay to the start of the last element:
    delay = Range( 0.0, 1.0, 0.4 )

    #-- Private Facets ---------------------------------------------------------

    # The offset to the start of each image element (x or y, depending upon the
    # direction):
    offset = Property

    # The element(s) assigned to each animation 'channel':
    channel = Property

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g, x, y ):
        """ Paints the transition at the current time into the graphics context
            *g* at location (*x*,*y*), which defines the upper-left corner of
            where the images are drawn.
        """
        img       = self.image_0
        image_0   = img.bitmap
        image_1   = self.image_1.bitmap
        dx        = img.width
        dy        = img.height
        offset    = self.offset
        channel   = self.channel
        time      = self.time
        handler   = getattr( self, '_%s_%s' % ( self.direction, self.style ) )
        dxy       = ( dx, dy )[ self.direction in Vertical ]
        delay     = dt = 0.0
        if len( channel ) > 1:
            delay = self.delay
            dt    = delay / (len( channel ) - 1)

        time_base = 1.0 - delay

        for i, element in enumerate( channel ):
            t   = clamp( (time - (i * dt)) / time_base, 0.0, 1.0 )
            xy0 = int( round( t * dxy ) )
            for j in element:
                handler( g, image_0, image_1, i, x, y,
                         offset[ j ], offset[ j + 1 ], xy0, dxy )


    def clone ( self ):
        """ Returns a clone of the image transition.
        """
        return self.__class__( **self.get(
            'style', 'direction', 'elements', 'mode', 'delay'
        ) )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'image_0, direction, elements' )
    def _get_offset ( self ):
        image = self.image_0
        n     = self.elements
        dxy   = image.height
        if self.direction in Vertical:
            dxy = image.width

        delta  = float( dxy ) / n
        xy     = 0.0
        offset = []
        for i in xrange( n ):
            offset.append( int( round( xy ) ) )
            xy += delta

        offset.append( dxy )

        return offset


    @property_depends_on( 'elements, mode' )
    def _get_channel ( self ):
        n       = self.elements
        mode    = self.mode
        channel = range( n )
        if mode == 'random':
            shuffle( channel )
        elif mode == 'middle':
            result = []
            j      = n / 2
            if (n % 2) == 1:
                result = [ ( j, ) ]

            left  = channel[ : j ]
            right = channel[ -j: ]
            left.reverse()

            return result + zip( left, right )
        elif mode in ( 'right_left', 'bottom_top' ):
            channel.reverse()

        return [ ( i, ) for i in channel ]

    #-- Private Methods --------------------------------------------------------

    def _up_wipe ( self, g, image_0, image_1, i, x, y, x0, x1, y0, dy ):
        """ Handles an up wipe effect.
        """
        dx10 = x1 - x0
        g.blit( x + x0, y, dx10, dy - y0, image_0, x0, 0, dx10, dy - y0 )
        g.blit( x + x0, y + dy - y0, dx10, y0, image_1, x0, dy - y0, dx10, y0 )


    def _up_push ( self, g, image_0, image_1, i, x, y, x0, x1, y0, dy ):
        """ Handles an up push effect.
        """
        dx10 = x1 - x0
        g.blit( x + x0, y, dx10, dy - y0, image_0, x0, y0, dx10, dy - y0 )
        g.blit( x + x0, y + dy - y0, dx10, y0, image_1, x0, 0, dx10, y0 )


    def _down_wipe ( self, g, image_0, image_1, i, x, y, x0, x1, y0, dy ):
        """ Handles a down wipe effect.
        """
        dx10 = x1 - x0
        g.blit( x + x0, y + y0, dx10, dy - y0, image_0, x0, y0, dx10, dy - y0 )
        g.blit( x + x0, y, dx10, y0, image_1, x0, 0, dx10, y0 )


    def _down_push ( self, g, image_0, image_1, i, x, y, x0, x1, y0, dy ):
        """ Handles a down push effect.
        """
        dx10 = x1 - x0
        g.blit( x + x0, y + y0, dx10, dy - y0, image_0, x0, 0, dx10, dy - y0 )
        g.blit( x + x0, y, dx10, y0, image_1, x0, dy - y0, dx10, y0 )


    def _up_down_wipe ( self, g, image_0, image_1, i, x, y, x0, x1, y0, dy ):
        """ Handles an up/down wipe effect.
        """
        if (i % 2) == 0:
            self._up_wipe( g, image_0, image_1, i, x, y, x0, x1, y0, dy )
        else:
            self._down_wipe( g, image_0, image_1, i, x, y, x0, x1, y0, dy )


    def _up_down_push ( self, g, image_0, image_1, i, x, y, x0, x1, y0, dy ):
        """ Handles an up/down push effect.
        """
        if (i % 2) == 0:
            self._up_push( g, image_0, image_1, i, x, y, x0, x1, y0, dy )
        else:
            self._down_push( g, image_0, image_1, i, x, y, x0, x1, y0, dy )


    def _left_wipe ( self, g, image_0, image_1, i, x, y, y0, y1, x0, dx ):
        """ Handles a left wipe effect.
        """
        dy10 = y1 - y0
        g.blit( x, y + y0, dx - x0, dy10, image_0, 0, y0, dx - x0, dy10 )
        g.blit( x + dx - x0, y + y0, x0, dy10, image_1, dx - x0, y0, x0,  dy10 )


    def _left_push ( self, g, image_0, image_1, i, x, y, y0, y1, x0, dx ):
        """ Handles a left push effect.
        """
        dy10 = y1 - y0
        g.blit( x, y + y0, dx - x0, dy10, image_0, x0, y0, dx - x0, dy10 )
        g.blit( x + dx - x0, y + y0, x0, dy10, image_1, 0, y0, x0, dy10 )


    def _right_wipe ( self, g, image_0, image_1, i, x, y, y0, y1, x0, dx ):
        """ Handles a right wipe effect.
        """
        dy10 = y1 - y0
        g.blit( x + x0, y + y0, dx - x0, dy10, image_0, x0, y0, dx - x0, dy10 )
        g.blit( x, y + y0, x0, dy10, image_1, 0, y0, x0, dy10 )


    def _right_push ( self, g, image_0, image_1, i, x, y, y0, y1, x0, dx ):
        """ Handles a right push effect.
        """
        dy10 = y1 - y0
        g.blit( x + x0, y + y0, dx - x0, dy10, image_0, 0, y0, dx - x0, dy10 )
        g.blit( x, y + y0, x0, dy10, image_1, dx - x0, y0, x0, dy10 )


    def _left_right_wipe ( self, g, image_0, image_1, i, x, y, y0, y1, x0, dx ):
        """ Handles a left/right wipe effect.
        """
        if (i % 2) == 0:
            self._left_wipe(  g, image_0, image_1, i, x, y, y0, y1, x0, dx )
        else:
            self._right_wipe( g, image_0, image_1, i, x, y, y0, y1, x0, dx )


    def _left_right_push ( self, g, image_0, image_1, i, x, y, y0, y1, x0, dx ):
        """ Handles an up/down push effect.
        """
        if (i % 2) == 0:
            self._left_push(  g, image_0, image_1, i, x, y, y0, y1, x0, dx )
        else:
            self._right_push( g, image_0, image_1, i, x, y, y0, y1, x0, dx )


    def _vertical_out_wipe ( self, g, image_0, image_1, i, x, y, x0, x1, y0,
                                   dy ):
        """ Handles a vertical out wipe effect.
        """
        ddy2 = (dy / 2) - (y0 / 2)
        yt   = y0 + ddy2
        dx10 = x1 - x0
        g.blit( x + x0, y, dx10, ddy2, image_0, x0, 0, dx10, ddy2 )
        g.blit( x + x0, y + yt, dx10, dy - yt, image_0, x0, yt, dx10, dy - yt )
        g.blit( x + x0, y + ddy2, dx10, y0, image_1, x0, ddy2, dx10, y0 )


    def _vertical_out_push ( self, g, image_0, image_1, i, x, y, x0, x1, y0,
                                  dy ):
        """ Handles a vertical out push effect.
        """
        y02  = y0 / 2
        dy2  = dy / 2
        ddy2 = dy2 - y02
        yt   = ddy2 + y0
        dy02 = y0 - y02
        dx10 = x1 - x0
        g.blit( x + x0, y, dx10, ddy2, image_0, x0, dy - ddy2, dx10, ddy2 )
        g.blit( x + x0, y + yt, dx10, dy - yt, image_0, x0, y0, dx10, dy - yt )
        g.blit( x + x0, y + ddy2, dx10, y02, image_1, x0, 0, dx10, y02 )
        g.blit( x + x0, y + dy2, dx10, dy02, image_1, x0, dy - dy02, dx10,
                dy02 )


    def _vertical_in_wipe ( self, g, image_0, image_1, i, x, y, x0, x1, y0,
                                  dy ):
        """ Handles a vertical in wipe effect.
        """
        ddy2 = (dy / 2) - (y0 / 2)
        yt   = y0 + ddy2
        dx10 = x1 - x0
        g.blit( x + x0, y + ddy2, dx10, y0, image_0, x0, ddy2, dx10, y0 )
        g.blit( x + x0, y, dx10, ddy2, image_1, x0, 0, dx10, ddy2 )
        g.blit( x + x0, y + yt, dx10, dy - yt, image_1, x0, yt, dx10, dy - yt )


    def _vertical_in_push ( self, g, image_0, image_1, i, x, y, x0, x1, y0,
                                  dy ):
        """ Handles a vertical in push effect.
        """
        y02  = y0 / 2
        dy2  = dy / 2
        ddy2 = dy2 - y02
        yt   = ddy2 + y0
        dy02 = y0 - y02
        dx10 = x1 - x0
        g.blit( x + x0, y + ddy2, dx10, y02, image_0, x0, 0, dx10, y02 )
        g.blit( x + x0, y + dy2, dx10, dy02, image_0, x0, dy - dy02, dx10,
                dy02 )
        g.blit( x + x0, y, dx10, ddy2, image_1, x0, y02, dx10, ddy2 )
        g.blit( x + x0, y + yt, dx10, dy - yt, image_1, x0, dy2, dx10, dy - yt )


    def _horizontal_out_wipe ( self, g, image_0, image_1, i, x, y, y0, y1, x0,
                                     dx ):
        """ Handles a horizontal out wipe effect.
        """
        ddx2 = (dx / 2) - (x0 / 2)
        xt   = x0 + ddx2
        dy10 = y1 - y0
        g.blit( x, y + y0, ddx2, dy10, image_0, 0, y0, ddx2, dy10 )
        g.blit( x + xt, y + y0, dx - xt, dy10, image_0, xt, y0, dx - xt, dy10 )
        g.blit( x + ddx2, y + y0, x0, dy10, image_1, ddx2, y0, x0, dy10 )


    def _horizontal_out_push ( self, g, image_0, image_1, i, x, y, y0, y1, x0,
                                     dx ):
        """ Handles a horizontal out push effect.
        """
        x02  = x0 / 2
        dx2  = dx / 2
        ddx2 = dx2 - x02
        xt   = ddx2 + x0
        dx02 = x0 - x02
        dy10 = y1 - y0
        g.blit( x, y + y0, ddx2, dy10, image_0, dx - ddx2, y0, ddx2, dy10 )
        g.blit( x + xt, y + y0, dx - xt, dy10, image_0, x0, y0, dx - xt, dy10 )
        g.blit( x + ddx2, y + y0, x02, dy10, image_1, 0, y0, x02, dy10 )
        g.blit( x + dx2, y + y0, dx02, dy10, image_1, dx - dx02, y0, dx02,
                dy10 )


    def _horizontal_in_wipe ( self, g, image_0, image_1, i, x, y, y0, y1, x0,
                                    dx ):
        """ Handles a horizontal in wipe effect.
        """
        ddx2 = (dx / 2) - (x0 / 2)
        xt   = x0 + ddx2
        dy10 = y1 - y0
        g.blit( x + ddx2, y + y0, x0, dy10, image_0, ddx2, y0, x0, dy10 )
        g.blit( x, y + y0, ddx2, dy10, image_1, 0, y0, ddx2, dy10 )
        g.blit( x + xt, y + y0, dx - xt, dy10, image_1, xt, y0, dx - xt, dy10 )


    def _horizontal_in_push ( self, g, image_0, image_1, i, x, y, y0, y1, x0,
                                    dx ):
        """ Handles a horizontal in push effect.
        """
        x02  = x0 / 2
        dx2  = dx / 2
        ddx2 = dx2 - x02
        xt   = ddx2 + x0
        dx02 = x0 - x02
        dy10 = y1 - y0
        g.blit( x + ddx2, y + y0, x02, dy10, image_0, 0, y0, x02, dy10 )
        g.blit( x + dx2, y + y0, dx02, dy10, image_0, dx - dx02, y0, dx02,
                dy10 )
        g.blit( x, y + y0, ddx2, dy10, image_1, x02, y0, ddx2, dy10 )
        g.blit( x + xt, y + y0, dx - xt, dy10, image_1, dx2, y0, dx - xt, dy10 )

#-------------------------------------------------------------------------------
#  'PushImageTransition'
#-------------------------------------------------------------------------------

class PushImageTransition ( WipeImageTransition ):
    """ Defines the PushImageTransition class for animating the transition from
        one image to another (as used in videos and web pages) using a 'wipe' or
        'push' style. This is the same as the WipeImageTransition, but defaults
        to doing a 'push' instead of a 'wipe'
    """

    #-- Facet Definitions ------------------------------------------------------

    # The transition style:
    style = 'push'

#-- EOF ------------------------------------------------------------------------
