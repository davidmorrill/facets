"""
Defines a number of GUI toolkit independent color facets which represent color
values numerically using various combinations of ints, floats and tuples.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.facet_base \
    import normalized_color

from facets.core.facet_handlers \
    import FacetType, NoDefaultSpecified

#-------------------------------------------------------------------------------
#  'RGB' facet:
#-------------------------------------------------------------------------------

class RGB ( FacetType ):
    """ Defines a color facet whose value is a Python int of the form: 0xRRGGBB.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = 0x0000FF

    # A description of the type of value this facet represents:
    info_text = 'an RGB color whose value is an integer of the form 0xRRGGBB'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, default_value = NoDefaultSpecified, **metadata ):
        """ Initializes the object.
        """
        if default_value is not NoDefaultSpecified:
            try:
                default_value = self.validate( None, None, default_value )
            except:
                pass

        super( RGB, self ).__init__( default_value, **metadata )


    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            r, g, b = normalized_color( value )

            return ((r << 16) + (g << 8) + b)
        except:
            self.error( object, name, value )


    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        from facets.api import HLSColorEditor

        return HLSColorEditor()

#-------------------------------------------------------------------------------
#  'RGBA' facet:
#-------------------------------------------------------------------------------

class RGBA ( RGB ):
    """ Defines a color facet whose value is a Python int of the form:
        0xAARRGGBB.
    """

    #-- Class Constants --------------------------------------------------------

    # A description of the type of value this facet represents:
    info_text = 'an RGBA color whose value is an integer of the form 0xAARRGGBB'

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            r, g, b, a = normalized_color( value, True )

            return (((255 - a) << 24) + (r << 16) + (g << 8) + b)
        except:
            self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'RGBInt' facet:
#-------------------------------------------------------------------------------

class RGBInt ( RGB ):
    """ Defines a color facet whose value is a Python tuple of the form:
        ( red, green, blue ), where red, green and blue are all ints in the
        range from 0 to 255.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = ( 0, 0, 255 )

    # A description of the type of value this facet represents:
    info_text = ('an RGB color whose value is an integer tuple of the form '
                 '(red,green,blue)')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            return normalized_color( value )
        except:
            self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'RGBAInt' facet:
#-------------------------------------------------------------------------------

class RGBAInt ( RGB ):
    """ Defines a color facet whose value is a Python tuple of the form:
        ( red, green, blue, alpha ), where red, green, blue and alpha are all
        ints in the range from 0 to 255.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = ( 0, 0, 255, 255 )

    # A description of the type of value this facet represents:
    info_text = ('an RGBA color whose value is an integer tuple of the form '
                 '(red,green,blue,alpha)')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            return normalized_color( value, True )
        except:
            self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'RGBFloat' facet:
#-------------------------------------------------------------------------------

class RGBFloat ( RGB ):
    """ Defines a color facet whose value is a Python tuple of the form:
        ( red, green, blue ), where red, green and blue are all floats in the
        range from 0.0 to 1.0.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = ( 0.0, 0.0, 1.0 )

    # A description of the type of value this facet represents:
    info_text = ('an RGB color whose value is a float tuple of the form '
                 '(red,green,blue)')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            return normalized_color( value, False, False )
        except:
            self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'RGBAFloat' facet:
#-------------------------------------------------------------------------------

class RGBAFloat ( RGB ):
    """ Defines a color facet whose value is a Python tuple of the form:
        ( red, green, blue, alpha ), where red, green, blue and alpha are all
        floats in the range from 0.0 to 1.0.
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = ( 0.0, 0.0, 1.0, 1.0 )

    # A description of the type of value this facet represents:
    info_text = ('an RGBA color whose value is a float tuple of the form '
                 '(red,green,blue,alpha)')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            return normalized_color( value, True, False )
        except:
            self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'HLS' facet:
#-------------------------------------------------------------------------------

class HLS ( RGB ):
    """ Defines a color facet whose value is a Python tuple of the form:
        ( hue [0..359], level [0.0..1.0], saturation [0.0..1.0] )
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = ( 240, 0.5, 1.0 )

    # A description of the type of value this facet represents:
    info_text = ('an HLS color whose value is a tuple of the form '
                 '(hue,level,saturation)')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            from colorsys import rgb_to_hls

            h, l, s = rgb_to_hls( *normalized_color( value, False, False ) )

            return ( int( round( 360.0 * h ) ) % 360, l, s )
        except:
            self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'HLSA' facet:
#-------------------------------------------------------------------------------

class HLSA ( RGB ):
    """ Defines a color facet whose value is a Python tuple of the form:
        ( hue [0..359], level [0.0..1.0], saturation [0.0..1.0],
          alpha [0.0..1.0] )
    """

    #-- Class Constants --------------------------------------------------------

    # The default value for the facet:
    default_value = ( 240, 0.5, 1.0, 1.0 )

    # A description of the type of value this facet represents:
    info_text = ('an HLSA color whose value is a tuple of the form '
                 '(hue,level,saturation,alpha)')

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this facet.
        """
        try:
            from colorsys import rgb_to_hls

            r, g, b, a = normalized_color( value, True, False )
            h, l, s    = rgb_to_hls( r, g, b )

            return ( int( round( 360.0 * h ) ) % 360, l, s, a )
        except:
            self.error( object, name, value )

#-- EOF ------------------------------------------------------------------------
