"""
Defines the RetrogradeTweener class that that travels partway through the time
cycle, then backtracks part of the way, then proceeds to the end of the cycle.
The amount of retrograde movement is defined by the 'amount' facet, which can
range from 0.0 (no retrograde movement) to 1.0 (goes to the end, back to the
beginning, then back to the end again).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Range, Float, View

from tweener \
    import Tweener

from helper \
    import FRange

#-------------------------------------------------------------------------------
#  'RetrogradeTweener' class:
#-------------------------------------------------------------------------------

class RetrogradeTweener ( Tweener ):
    """ Defines the RetrogradeTweener class that that travels partway through
        the time cycle, then backtracks part of the way, then proceeds to the
        end of the cycle. The amount of retrograde movement is defined by the
        'amount' facet, which can  range from 0.0 (no retrograde movement) to
        1.0 (goes to the end, back to the beginning, then back to the end
        again).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The amount of retrograde movement:
    amount = Range( 0.0, 1.0, 0.5, event = 'modified' )

    # The reversal points (expressed in t: 0.0..1.0):
    t1 = Float( 0.375 )
    t2 = Float( 0.625 )

    # The time distance needed to reach t1 and t2:
    td1 = Float( 0.75 )
    td2 = Float( 0.25 )

    # The total time distance travelled in a cycle:
    tt = Float( 2.0 )

    #-- Facet View Definitions -------------------------------------------------

    view = View( FRange( 'amount' ) )

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0. The result for t = 0.0 should be 0.0, and for t = 1.0
            should be 1.0. All results must be in the range from 0.0 to 1.0.
        """
        if t <= self.t1:
            return (t * self.tt)

        if t >= self.t2:
            return self.td2 + ((t - self.t2) * self.tt)

        return self.td1 - ((t - self.t1) * self.tt)

    #-- Facet Event Handlers ---------------------------------------------------

    def _amount_set ( self ):
        """ Handles the 'amount' facet being changed.
        """
        amount   = self.amount
        self.tt  = (2.0 * amount) + 1.0
        self.t1  = (amount + 1.0) / (2.0 * self.tt)
        self.t2  = 1.0 - self.t1
        self.td1 = (1.0 + amount) / 2.0
        self.td2 = 1.0 - self.td1

#-- EOF ------------------------------------------------------------------------
