"""
Defines the EasyTweener class that does another type of 'Ease Out/Ease In'
motion 'tween.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import sin, pi

from tweener \
    import Tweener

from helper \
    import pi_two

#-------------------------------------------------------------------------------
#  'EasyTweener' class:
#-------------------------------------------------------------------------------

class EasyTweener ( Tweener ):
    """ Defines the EasyTweener class that does another type of
        'Ease In/Ease Out' motion 'tween.
    """

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0. The result for t = 0.0 should be 0.0, and for t = 1.0
            should be 1.0. All results must be in the range from 0.0 to 1.0.
        """
        return ((1.0 + sin( (pi * t) - pi_two )) / 2.0)

#-- EOF ------------------------------------------------------------------------
