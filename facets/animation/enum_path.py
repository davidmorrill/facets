"""
Defines the EnumPath class for implementing animatable enumerated values.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any

from facets.core.facet_base \
    import SequenceTypes

from path \
    import Path

#-------------------------------------------------------------------------------
#  'EnumPath' class:
#-------------------------------------------------------------------------------

class EnumPath ( Path ):
    """ Defines the EnumPath class for implementing animatable enumerated
        values.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The set of values to use for the enumeration:
    values = Any # list or tuple of values

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the enumerated value from 'values' at time t for a path
            whose start value is v0, and whose end value is v1.
        """
        values = self.values
        if not isinstance( values, SequenceTypes ):
            return v0

        try:
            i0 = values.index( v0 )
        except:
            i0 = 0

        n = len( values )
        try:
            i1 = values.index( v1 )
        except:
            i1 = n - 1

        if i1 < i0:
            i1 += n

        return values[ min( int( i0 + (t * (i1 - i0 + 1)) ), i1 ) % n ]

#-- EOF ------------------------------------------------------------------------
