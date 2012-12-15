"""
Defines the Tweener base class used for calculating animation frame values.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Callable, Event, Either, List, Instance, View

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

# The tweener identity function:
identity = lambda t: t

#-------------------------------------------------------------------------------
#  'Tweener' class:
#-------------------------------------------------------------------------------

class Tweener ( HasPrivateFacets ):
    """ The base class for calculating animation frame values.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The tweener this one is composed with:
    compose = Callable( identity )

    # Event fired when one of the parameters defining the tweener is modified:
    modified = Event

    #-- Facet View Definitions -------------------------------------------------

    view = View()

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, compose = None, **facets ):
        """ Initializes the object. It accepts another tweener or f(t) *compose*
            that this tweener will be composed with. The default is the identity
            function: f(t) = t.
        """
        if compose is not None:
            self.compose = compose

        super( Tweener, self ).__init__( **facets )


    def __call__ ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0, composed with the object's 'compose' tweener or
            function.
        """
        return self.at( self.compose( t ) )


    def at ( self, t ):
        """ Returns the tween mapped time t' for time t, where t is between
            0.0 and 1.0. The result must be in the range from 0.0 to 1.0. This
            method must be overridden by any subclass.
        """
        return t

#-------------------------------------------------------------------------------
#  Reusable definitions:
#-------------------------------------------------------------------------------

# The base class is a linear tweener:
LinearTweener = Tweener

# Define a reusable type:
ATweener = Either( Instance( Tweener ), List( Instance( Tweener ) ) )

# Create a reusable constant value:
NoEasing = LinearTweener()

#-- EOF ------------------------------------------------------------------------
