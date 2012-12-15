"""
Defines the ImageTransition base class for animating the transition from one
image to another (as used in videos and web pages).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Image, Range

#-------------------------------------------------------------------------------
#  'ImageTransition' class:
#-------------------------------------------------------------------------------

class ImageTransition ( HasPrivateFacets ):
    """ Defines the ImageTransition base class for animating the transition from
        one image to another (as used in videos and web pages).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The image displayed at time 0.0:
    image_0 = Image

    # The image displayed at time 1.0:
    image_1 = Image

    # The current time in the transition:
    time = Range( 0.0, 1.0 )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g, x, y ):
        """ Paints the transition at the current time into the graphics context
            *g* at location (*x*,*y*), which defines the upper-left corner of
            where the images are drawn.

            This is an abstract method that must be overridden in a subclass.
        """
        raise NotImplementedError


    def clone ( self ):
        """ Returns a clone of the image transition.
        """
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------
