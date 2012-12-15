"""
Defines the LinearIntPath class for implementing animatable linear integer
parametric paths.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from path \
    import Path

from facets.core.facet_base \
    import SequenceTypes

#-------------------------------------------------------------------------------
#  'LinearIntPath' class:
#-------------------------------------------------------------------------------

class LinearIntPath ( Path ):
    """ Defines the LinearIntPath class for implementing animatable linear
        integer parametric paths.
    """

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the linear integer value along the path at time t for a
            path whose start value is v0, and whose end value is v1.
        """
        if not isinstance( v0, SequenceTypes ):
            return int( round( v0 + ((v1 - v0) * t) ) )

        return v0.__class__(
            [ int( round( v0[ i ] + ((v1[ i ] - v0[ i ]) * t) ) )
              for i in xrange( len( v0 ) ) ]
        )

# Define a reusable instance:
LinearInt = LinearIntPath()

#-- EOF ------------------------------------------------------------------------
