"""
Defines the Manhattan2DIntPath class that implements an animatable integer
parametric path for 2D points using a Manhattan street traversal algorithm
(i.e. horizontal movement first, and vertical movement second).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from path \
    import Path

#-------------------------------------------------------------------------------
#  'Manhattan2DIntPath' class:
#-------------------------------------------------------------------------------

class Manhattan2DIntPath ( Path ):
    """ Defines the Manhattan2DIntPath class that implements an animatable
        integer parametric path for 2D points using a Manhattan street
        traversal algorithm (i.e. horizontal movement first, and vertical
        movement second).
    """

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the Manhattan linear integer value along the path at time t
            for a path whose start value is v0, and whose end value is v1.
        """
        x0, y0 = v0
        x1, y1 = v1
        dx     = abs( x1 - x0 )
        dy     = abs( y1 - y0 )
        dt     = dx + dy
        if dt == 0:
            return v0

        t1 = float( dx ) / (dx + dy)
        if (t <= t1) and (t1 > 0.0):
            return ( int( round( x0 + ((x1 - x0) * (t / t1)) ) ), y0 )

        return ( x1,
                 int( round( y0 + (((y1 - y0) * (t - t1)) / (1.0 - t1)) ) ) )

#-- EOF ------------------------------------------------------------------------
