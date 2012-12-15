"""
Defines the Spiral2DIntPath class that implements an animatable integer
parametric path for 2D points using a simple circular spiral traversal
algorithm (i.e. it traces a full circle from the start point to the end point
through a center point projected through the vector from the start to end
points.

The value 'scale' specifies the scaling factor to apply to calculate the center
point as a multiple of the distance from the start to the end point.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt, pi, sin, cos, atan2

from facets.api \
    import Range, View

from path \
    import Path

from helper \
    import FRange

#-------------------------------------------------------------------------------
#  'Spiral2DIntPath' class:
#-------------------------------------------------------------------------------

class Spiral2DIntPath ( Path ):
    """ Defines the Spiral2DIntPath class that implements an animatable integer
        parametric path for 2D points using a simple circular spiral traversal
        algorithm (i.e. it traces a full circle from the start point to the end
        point through a center point projected through the vector from the start
        to end points.

        The value 'scale' specifies the scaling factor to apply to calculate the
        center point as a multiple of the distance from the start to the end
        point.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The scaling factor used to calculate the center point:
    scale = Range( 0.0, 1.25, 0.5, event = 'modified' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( FRange( 'scale' ) )

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the semi-circular linear integer value along the path at
            time t for a path whose start value is v0, and whose end value is
            v1.
        """
        s      = self.scale
        x0, y0 = v0
        x1, y1 = v1
        xc     = x0 + (s * (x1 - x0))
        yc     = y0 + (s * (y1 - y0))
        dx0    = x0 - xc
        dy0    = y0 - yc
        dx1    = x1 - xc
        dy1    = y1 - yc
        r0     = sqrt( (dx0 * dx0) + (dy0 * dy0) )
        r1     = sqrt( (dx1 * dx1) + (dy1 * dy1) )
        r      = r0 + ((r1 - r0) * t)
        a      = atan2( dy0, dx0 ) + ((1.0 + (s > 1.0)) * pi * t)

        return ( int( round( xc + (r * cos( a )) ) ),
                 int( round( yc + (r * sin( a )) ) ) )

#-- EOF ------------------------------------------------------------------------
