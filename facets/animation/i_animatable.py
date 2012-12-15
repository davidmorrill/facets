"""
Defines the IAnimatable interface that any animation class must implement.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Interface, Event, Bool, Range

#-------------------------------------------------------------------------------
#  'IAnimatable' Interface:
#-------------------------------------------------------------------------------

class IAnimatable ( Interface ):
    """ Defines the IAnimatable interface that any animation class must
        implement.
    """

    #-- Facet Interface Definitions --------------------------------------------

    # Event to fire when animation should start:
    start = Event( Bool )

    # Event to fire when animation should stop:
    stop = Event( Bool )

    # Event fired when animation completes or is stopped:
    stopped = Event( Bool )

    # Is the animation currently running or not?
    running = Bool

    # The number of times the animation should repeat (0 = Indefinitely):
    repeat = Range( 0, None, 1 )

    # Should repeated animations reverse (True) or start over (False):
    reverse = Bool

#-- EOF ------------------------------------------------------------------------
