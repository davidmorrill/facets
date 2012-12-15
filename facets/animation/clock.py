"""
Defines a singleton Clock for use with driving animations and other timed
events. The clock updates 24 times/second. It also provide additional facets
that update once per second ('seconds') and once per minute ('minutes').
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from time \
    import time

from math \
    import trunc

from facets.api \
    import SingletonHasPrivateFacets, Float, toolkit

#-------------------------------------------------------------------------------
#  'Clock' singleton:
#-------------------------------------------------------------------------------

class Clock ( SingletonHasPrivateFacets ):
    """ Defines a singleton Clock for use with driving animations and other
        timed events. The clock updates 30 times/second. It also provide
        additional facets that update once per second ('seconds') and once per
        minute ('minutes').
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current system time (updated 30 times/second):
    time = Float

    # The current system time truncated to seconds (changes once per second):
    seconds = Float

    # The current system time truncated to minutes (changes once per minute):
    minutes = Float

    #-- Facets Method Overrides ------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object by creating the timer.
        """
        self._timer = toolkit().create_timer( 1000.0 / 30.0, self._update )
        self._update()

    #-- Private Methods --------------------------------------------------------

    def _update ( self ):
        """ Handles a timer pop.
        """
        self.time    = t = time()
        self.seconds = trunc( t )
        self.minutes = trunc( t / 60.0 ) * 60.0

