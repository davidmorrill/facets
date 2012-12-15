"""
Defines the RampTweener class that has a time curve like:     ___ so that it
delays the start and speeds up the end based on the      ___/    'cycle' value
which is the fraction of time, 0.0..1.0, spent making the transition.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Range, View

from tweener \
    import Tweener

from helper \
    import FRange

#-------------------------------------------------------------------------------
#  'RampTweener' class:
#-------------------------------------------------------------------------------

class RampTweener ( Tweener ):
    """ Defines the RampTweener class that has a time curve like:  ___ so that
        it delays the start and speeds up the end based on    ___/    the
        'cycle' value which is the fraction of time, 0.0..1.0, spent making the
        transition.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The fraction of the time cycle spent in the 'ramp':
    cycle = Range( 0.0, 1.0, 0.5, event = 'modified' )

    # The fraction of the time not in the 'ramp' at which 'ramp' starts:
    start = Range( 0.0, 1.0, 0.5, event = 'modified' )

    # The maximum level reached before starting the 'ramp':
    level = Range( 0.0, 1.0, 0.0, event = 'modified' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( FRange( 'cycle' ), FRange( 'start' ), FRange( 'level' ) )

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0. The result for t = 0.0 should be 0.0, and for t = 1.0
            should be 1.0. All results must be in the range from 0.0 to 1.0.
        """
        tnr   = 1.0 - self.cycle
        ts    = tnr * self.start
        dte   = tnr - ts
        level = self.level

        if t <= ts:
            if ts == 0.0:
                return level

            return ((level * t) / ts)

        if t >= (1.0 - dte):
            if t == 1.0:
                return 1.0

            return (1.0 - ((level * (1.0 - t)) / dte))

        return (level + (((1.0 - (2.0 * level)) * (t - ts)) / self.cycle))

#-- EOF ------------------------------------------------------------------------
