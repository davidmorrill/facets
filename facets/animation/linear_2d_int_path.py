"""
Defines the Linear2DIntPathbase class for implementing animatable integer
parametric paths for 2D points. The base class also implements a simple linear
path between the two points.
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
#  'Linear2DIntPath' class:
#-------------------------------------------------------------------------------

class Linear2DIntPath ( Path ):
    """ Defines the Linear2DIntPathbase class for implementing animatable
        integer parametric paths for 2D points. The base class also implements a
        simple linear path between the two points.
    """

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the linear integer value along the path at time t for a
            path whose start value is v0, and whose end value is v1.
        """
        return ( int( round( v0[0] + ((v1[0] - v0[0]) * t) ) ),
                 int( round( v0[1] + ((v1[1] - v0[1]) * t) ) ) )

# Define a reusable instance:
Linear2DInt = Linear2DIntPath()

#-- EOF ------------------------------------------------------------------------
