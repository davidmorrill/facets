"""
Defines the ColorPath class for implementing animatable parametric color paths.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from colorsys \
    import rgb_to_hls, hls_to_rgb

from facets.api \
    import Str, Float

from facets.core.facet_base \
    import normalized_color

from path \
    import Path

#-------------------------------------------------------------------------------
#  'ColorPath' class:
#-------------------------------------------------------------------------------

class ColorPath ( Path ):
    """ Defines the ColorPath class for implementing animatable color parametric
        paths.
    """

    #-- Facet Definitions ------------------------------------------------------

    # A string describing the color components to include in the path. The path
    # is in HLSA (Hue/Lightness/Saturation/Alpha) space, so the string should
    # contain one or more of the characters 'H', 'L', 'S' or 'A' (case
    # insensitive):
    hlsa = Str( 'hlsa' )

    #-- Private Facet Definitions ----------------------------------------------

    # Each value is 1.0 if the corresponding color component is included in the
    # path calculation, and 0.0 if it is not:
    use_h = Float
    use_l = Float
    use_s = Float
    use_a = Float

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the color value along the path at time t for a path whose
            start value is v0, and whose end value is v1.
        """
        c0         = normalized_color( v0, has_alpha = True, as_int = False )
        c1         = normalized_color( v1, has_alpha = True, as_int = False )
        h0, l0, s0 = rgb_to_hls( *c0[:3] )
        h1, l1, s1 = rgb_to_hls( *c1[:3] )
        return (
            hls_to_rgb(
                h0 + ((h1 - h0) * t * self.use_h),
                l0 + ((l1 - l0) * t * self.use_l),
                s0 + ((s1 - s0) * t * self.use_s)
            ) + ( c0[3] + ((c1[3] - c0[3]) * t * self.use_a), )
        )

    #-- Facet Default Values ---------------------------------------------------

    def _use_h_default ( self ):
        return self._uses( 'h' )


    def _use_l_default ( self ):
        return self._uses( 'l' )


    def _use_s_default ( self ):
        return self._uses( 's' )


    def _use_a_default ( self ):
        return self._uses( 'a' )

    #-- Public Methods ---------------------------------------------------------

    def _uses ( self, component ):
        """ Returns whether or not the color *component* is in the 'hlsa' color
            space descriptor.
        """
        return (1.0 if self.hlsa.lower().find( component ) >= 0 else 0.0)

# Define reusable instances:
HLSAColorPath = ColorPath()
HColorPath    = ColorPath( hlsa = 'h' )
LColorPath    = ColorPath( hlsa = 'l' )
SColorPath    = ColorPath( hlsa = 's' )
AColorPath    = ColorPath( hlsa = 'a' )

#-- EOF ------------------------------------------------------------------------