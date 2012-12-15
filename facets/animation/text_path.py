"""
Defines the TextPath class that animates a transition from one string value to
another.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from path \
    import Path

#-------------------------------------------------------------------------------
#  'TextPath' class:
#-------------------------------------------------------------------------------

class TextPath ( Path ):
    """ Defines the TextPath class that animates a transition from one string
        value to another.
    """

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the linear integer value along the path at time t for a
            path whose start value is v0, and whose end value is v1.
        """
        n1, n2 = len( v0 ), len( v1 )
        n      = int( t * (n1 + n2 + 1) )
        if n < n1:
            return v0[ : n1 - n ]

        return v1[ : n - n1 ]

# Define a reusable instance:
Text = TextPath()

#-- EOF ------------------------------------------------------------------------
