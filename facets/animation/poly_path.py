"""
Defines the PolyPath class for implementing animatable paths that follow the
sides of an open polygon between the start and end points.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sqrt, atan2, sin, cos

from facets.api \
    import List, on_facet_set

from path \
    import Path

#-------------------------------------------------------------------------------
#  'PolyPath' class:
#-------------------------------------------------------------------------------

class PolyPath ( Path ):
    """ Defines the EnumPath class for implementing animatable enumerated
        values.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The set of points between the start and end points of the polygon. The
    # start point is assumed to be (0,0) and the end point is (1,0). Only the
    # intermediate points should be specified:
    points = List # ( Tuple( Float, Float ) )

    #-- Private Facets ---------------------------------------------------------

    # The starting time for each path segment (= len(points)+2):
    ti = List

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the point along the polygonal path between v0 and v1 whose
            intermediate points are specified by 'points'.
        """
        ti = self.ti
        i  = 0
        while True:
            if ti[ i + 1 ] >= t:
                break

            i += 1

        x0, y0 = v0
        x1, y1 = v1
        dx     = x1 - x0
        dy     = y1 - y0
        dxy    = sqrt( (dx * dx) + (dy * dy) )
        a      = atan2( dy, dx )
        t0, t1 = ti[ i: i + 2 ]
        points = self.points
        px0    = py0 = py1 = 0.0
        px1    = 1.0
        if i > 0:
            px0, py0 = points[ i - 1 ]

        if i < len( points ):
            px1, py1 = points[ i ]

        dt   = (t - t0) / (t1 - t0)
        x    = (px0 + (dt * (px1 - px0))) * dxy
        y    = (py0 + (dt * (py1 - py0))) * dxy
        cosa = cos( a )
        sina = sin( a )

        return ( x0 + (x * cosa) - (y * sina), y0 + (y * cosa) + (x * sina) )

    #-- Facet Default Values ---------------------------------------------------

    def _ti_default ( self ):
        return self._compute_times()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'points[]' )
    def _points_modified ( self ):
        self.ti = self._compute_times()

    #-- Private Methods --------------------------------------------------------

    def _compute_times ( self ):
        """ Returns the starting time for each polygon segment.
        """
        x0 = y0 = total_length = 0.0
        dxy     = [ 0.0 ]
        for x1, y1 in (self.points + [ ( 1.0, 0.0 ) ]):
            dx            = x1 - x0
            dy            = y1 - y0
            x0, y0        = x1, y1
            total_length += sqrt( (dx * dx) + (dy * dy) )
            dxy.append( total_length )

        return [ (dxyi / total_length) for dxyi in dxy ]

#-- EOF ------------------------------------------------------------------------
