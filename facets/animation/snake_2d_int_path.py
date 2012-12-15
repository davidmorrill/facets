"""
Defines the Snake2DIntPath class that implements an animatable integer
parametric path for 2D points using a 'snake' path, as if the path were snaking
along the line between the two points.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt, sin, cos, atan2

from facets.api \
    import Range, View

from path \
    import Path

from helper \
    import IRange, FRange, two_pi

#-------------------------------------------------------------------------------
#  'Snake2DIntPath' class:
#-------------------------------------------------------------------------------

class Snake2DIntPath ( Path ):
    """ Defines the Snake2DIntPath class that implements an animatable integer
        parametric path for 2D points using a 'snake' path, as if the path were
        snaking along the line between the two points.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The scaling factor used to scale the snake path width:
    scale = Range( 0.0, 1.0, 0.18, event = 'modified' )

    # The number of snake cycles to make:
    cycles = Range( 1, 5, 1, event = 'modified' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( FRange( 'scale' ), IRange( 'cycles' ) )

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the ricochet value along the path at time t for a path whose
            start value is v0, and whose end value is v1.
        """
        x0, y0 = v0
        x1, y1 = v1
        dx     = x1 - x0
        dy     = y1 - y0
        d      = sqrt( (dx * dx) + (dy * dy) )
        d1     = t * d
        d2     = self.scale * d * sin( two_pi * t * self.cycles )
        b      = atan2( d2, d1 )
        r      = d1 / cos( b )
        ab     = b + atan2( dy, dx )

        return ( int( round( x0 + (r * cos( ab )) ) ),
                 int( round( y0 + (r * sin( ab )) ) ) )

#-- EOF ------------------------------------------------------------------------
