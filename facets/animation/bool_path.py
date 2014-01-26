"""
Defines the BoolPath class for implementing animatable parametric boolean
paths.
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
#  'BoolPath' class:
#-------------------------------------------------------------------------------

class BoolPath ( Path ):
    """ Defines the BoolPath class for implementing animatable parametric
        boolean paths.
    """

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the boolean value along the path at time t for a path whose
            start value is v0, and whose end value is v1.
        """
        return (v0 if t <= 0.5 else v1)

# Define a reusable instance:
Boolean = BoolPath()

#-- EOF ------------------------------------------------------------------------