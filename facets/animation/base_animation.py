"""
Defines the BaseAnimation class that provides a concrete implementation of the
IAnimatable interface.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Event, Bool, Range, implements

from i_animatable \
    import IAnimatable

#-------------------------------------------------------------------------------
#  'BaseAnimation' class:
#-------------------------------------------------------------------------------

class BaseAnimation ( HasPrivateFacets ):
    """ Defines the BaseAnimation class that provides a concrete implementation
        of the IAnimatable interface.
    """

    implements( IAnimatable )

    #-- IAnimatable Interface Implementation -----------------------------------

    # Event to fire when animation should start:
    start = Event( Bool )

    # Event to fire when animation should stop:
    stop = Event( Bool )

    # Event fired when animation completes or is stopped:
    stopped = Event( Bool )

    # Is the animation currently running or not?
    running = Bool( False )

    # The number of times the animation should repeat (0 = Indefinitely):
    repeat = Range( 0, None, 1 )

    # Should repeated animations reverse (True) or start over (False):
    reverse = Bool( True )

    #-- Public Methods ---------------------------------------------------------

    def run ( self ):
        """ Starts the animation running. Returns the object as the result.
        """
        self.start = True

        return self


    def halt ( self ):
        """ Stops the animation if it is running. Returns the object as the
            result.
        """
        self.stop = True

        return self

#-- EOF ------------------------------------------------------------------------
