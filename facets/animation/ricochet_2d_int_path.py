"""
Defines the Ricochet2DIntPath class that implements an animatable integer
parametric path for 2D points using a 'ricochet' path, as if the path were
ricocheting off a point on the bisector of the line between the two points at a
certain angle.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sin, cos, atan2, sqrt, pi

from facets.api \
    import Range, View

from path \
    import Path

from helper \
    import IRange, FRange

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Degress to radians conversion factor:
d2r = pi / 180.0

#-------------------------------------------------------------------------------
#  'Ricochet2DIntPath' class:
#-------------------------------------------------------------------------------

class Ricochet2DIntPath ( Path ):
    """ Defines the Ricochet2DIntPath class that implements an animatable
        integer parametric path for 2D points using a 'ricochet' path, as if
        the path were ricocheting off a point on the bisector of the line
        between the two points at a certain angle.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The angle (in degrees) of the ricochet (0 = no ricochet):
    angle = Range( 0, 45, 38, event = 'modified' )

    # The fraction of the distance along the path the ricochet point is at right
    # angles to:
    offset = Range( 0.2, 0.8, 0.5, event = 'modified' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( IRange( 'angle' ), FRange( 'offset' ) )

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
        if d == 0.0:
            return v0

        b  = self.angle * d2r
        ab = b + atan2( dy, dx )
        d1 = self.offset * d
        r  = d1 / cos( b )
        x2 = x0 + (r * cos( ab ))
        y2 = y0 + (r * sin( ab ))
        d -= d1
        h  = r * sin( b )
        t1 = r / (r + sqrt( (d * d) + (h * h) ))
        if t <= t1:
            return ( int( round( x0 + ((t * (x2 - x0)) / t1) ) ),
                     int( round( y0 + ((t * (y2 - y0)) / t1) ) ) )

        return ( int( round( x2 + (((t - t1) * (x1 - x2)) / (1.0 - t1)) ) ),
                 int( round( y2 + (((t - t1) * (y1 - y2)) / (1.0 - t1)) ) ) )

#-- EOF ------------------------------------------------------------------------
