"""
Defines the EaseOutEaseInTweener class that does an 'Ease Out/Ease In' motion
'tween.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import tanh

from tweener \
    import Tweener

from helper \
    import tanh25

#-------------------------------------------------------------------------------
#  'EaseOutEaseInTweener' class:
#-------------------------------------------------------------------------------

class EaseOutEaseInTweener ( Tweener ):
    """ Defines the EaseInEaseOutTweener class that does an 'Ease In/Ease Out'
        motion 'tween.
    """

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0. The result for t = 0.0 should be 0.0, and for t = 1.0
            should be 1.0. All results must be in the range from 0.0 to 1.0.
        """
        return ((tanh( 5.0 * t - 2.5 ) / tanh25) + 1.0) / 2.0

#-------------------------------------------------------------------------------
#  Reusable definitions:
#-------------------------------------------------------------------------------

# Create a reusable constant value:
EaseOutEaseIn = EaseOutEaseInTweener()

#-- EOF ------------------------------------------------------------------------
