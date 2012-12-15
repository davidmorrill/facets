"""
Defines the Path base class for implementing animatable 1D parametric paths.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Either, Instance, List, Event, View

from facets.core.facet_base \
    import SequenceTypes

#-------------------------------------------------------------------------------
#  'Path' class:
#-------------------------------------------------------------------------------

class Path ( HasPrivateFacets ):
    """ Defines the Path base class for implementing animatable 1D parametric
        paths.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Event fired when one of the parameters defining the path is modified:
    modified = Event

    #-- Facet View Definitions -------------------------------------------------

    view = View()

    #-- Public Methods ---------------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the value along the path at time t for a path whose start
            value is v0, and whose end value is v1.
        """
        if not isinstance( v0, SequenceTypes ):
            return (v0 + ((v1 - v0) * t))

        return v0.__class__(
            [ (v0[ i ] + ((v1[ i ] - v0[ i ]) * t))
              for i in xrange( len( v0 ) ) ]
        )

#-------------------------------------------------------------------------------
#  Reusable definitions:
#-------------------------------------------------------------------------------

# The base class is a linear path:
LinearPath = Path

# Define a reusable type:
APath = Either( Instance( Path ), List( Instance( Path ) ) )

# Define a reusable instance:
Linear = LinearPath()

#-- EOF ------------------------------------------------------------------------
