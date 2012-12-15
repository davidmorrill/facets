"""
Defines the Overshoot2DIntPath class that implements an animatable integer
parametric path for 2D points using a path that overshoots the target by a
fraction 'amount', and then retraces its way back along the path to the target.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Range, View

from linear_2d_int_path \
    import Linear2DIntPath

from helper \
    import FRange

#-------------------------------------------------------------------------------
#  'Overshoot2DIntPath' class:
#-------------------------------------------------------------------------------

class Overshoot2DIntPath ( Linear2DIntPath ):
    """ Defines the Overshoot2DIntPath class that implements an animatable
        integer parametric path for 2D points using a path that overshoots the
        target by a fraction 'amount', and then retraces its way back along the
        path to the target.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The amount of 'overshoot' to use:
    amount = Range( 0.0, 1.0, 0.10, event = 'modified' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( FRange( 'amount' ) )

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the overshoot value along the path at time t for a path
            whose start value is v0, and whose end value is v1.
        """
        x0, y0 = v0
        x1, y1 = v1
        a      = self.amount
        a1     = a + 1.0
        x2     = x0 + ((x1 - x0) * a1)
        y2     = y0 + ((y1 - y0) * a1)
        t1     = a1 / (a1 + a)
        if t <= t1:
            dt = t / t1

            return ( int( round( x0 + ((x2 - x0) * dt) ) ),
                     int( round( y0 + ((y2 - y0) * dt) ) ) )

        dt = (t - t1) / (1.0 - t1)

        return ( int( round( x2 + ((x1 - x2) * dt) ) ),
                 int( round( y2 + ((y1 - y2) * dt) ) ) )

#-- EOF ------------------------------------------------------------------------
