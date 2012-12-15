"""
Defines the EaseInTweener class that does an 'Ease In' motion 'tween.
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
#  'EaseInTweener' class:
#-------------------------------------------------------------------------------

class EaseInTweener ( Tweener ):
    """ Defines the EaseInTweener class that does an 'Ease In' motion 'tween.
    """

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0. The result for t = 0.0 should be 0.0, and for t = 1.0
            should be 1.0. All results must be in the range from 0.0 to 1.0.
        """
        return tanh( 2.5 * t ) / tanh25

#-------------------------------------------------------------------------------
#  Reusable definitions:
#-------------------------------------------------------------------------------

# Create a reusable constant value:
EaseIn = EaseInTweener()

#-- EOF ------------------------------------------------------------------------
