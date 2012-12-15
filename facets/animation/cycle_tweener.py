"""
Defines the CycleTweener class that cycles between t = 0.0..1.0 'cycles' times.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import fmod

from facets.api \
    import Range, View

from helper \
    import IRange

from tweener \
    import Tweener

#-------------------------------------------------------------------------------
#  'CycleTweener' class:
#-------------------------------------------------------------------------------

class CycleTweener ( Tweener ):
    """ Defines the CycleTweener class that cycles between t = 0.0..1.0 'cycles'
        times.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The number of cycles to perform:
    cycles = Range( 1, None, 1, event = 'modified' )

    #-- Facet View Definitions -------------------------------------------------

    view = View( IRange( 'cycles' ) )

    #-- Tweener Method Overrides -----------------------------------------------

    def at ( self, t ):
        v = fmod( t * self.cycles, 1.0 )
        if v >= 0.50:
            v = 1.0 - v

        return (2.0 * v)

#-- EOF ------------------------------------------------------------------------
