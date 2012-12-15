"""
Defines the BounceTweener class that bounces near the end of the time interval.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sin, pi

from facets.api \
    import Range, View

from tweener \
    import Tweener

from helper \
    import IRange, FRange

#-------------------------------------------------------------------------------
#  'BounceTweener' class:
#-------------------------------------------------------------------------------

class BounceTweener ( Tweener ):
    """ Defines the BounceTweener class that bounces near the end of the time
        interval.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The time until the first bounce begins:
    time = Range( 0.1, 1.0, 0.45, event = 'modified' )

    # The maximum height of the bounce:
    height = Range( 0.0, 1.0, 0.1, event = 'modified' )

    # The number of bounces:
    bounces = Range( 1, 5, 2, event = 'modified' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( FRange( 'time' ), FRange( 'height' ), IRange( 'bounces' ) )

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0. The result for t = 0.0 should be 0.0, and for t = 1.0
            should be 1.0. All results must be in the range from 0.0 to 1.0.
        """
        t1 = self.time
        dt = t - t1
        if dt <= 0.0:
            return (t / t1)

        tf = dt / (1.0 - t1)

        return 1.0 - (self.height * (1.0 - tf) *
                      abs( sin( pi * self.bounces * tf ) ))

#-- EOF ------------------------------------------------------------------------
