"""
Facet definition for an RGB-based color, which is a tuple of the form
(*red*, *green*, *blue*), where *red*, *green* and *blue* are floats in the
range from 0.0 to 1.0.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Facet, FacetError

from facets.core.facet_base \
    import SequenceTypes

from facets.api \
    import ColorEditor

from facets.ui.wx.editors.color_facet \
    import standard_colors

#-------------------------------------------------------------------------------
#  Convert a number into an RGB tuple:
#-------------------------------------------------------------------------------

def range_check ( value ):
    """ Checks that *value* can be converted to a value in the range 0.0 to 1.0.

        If so, it returns the floating point value; otherwise, it raises a
        FacetError.
    """
    value = float( value )
    if 0.0 <= value <= 1.0:
        return value

    raise FacetError

def convert_to_color ( object, name, value ):
    """ Converts a tuple or an integer to an RGB color value, or raises a
        FacetError if that is not possible.
    """
    if (type( value ) in SequenceTypes) and (len( value ) == 3):
        return ( range_check( value[0] ),
                 range_check( value[1] ),
                 range_check( value[2] ) )

    if type( value ) is int:
        num = int( value )
        return ((num / 0x10000)        / 255.0
                ((num / 0x100) & 0xFF) / 255.0,
                (num & 0xFF)           / 255.0 )

    raise FacetError

convert_to_color.info = ('a tuple of the form (r,g,b), where r, g, and b '
    'are floats in the range from 0.0 to 1.0, or an integer which in hex is of '
    'the form 0xRRGGBB, where RR is red, GG is green, and BB is blue')

#-------------------------------------------------------------------------------
#  Standard colors:
#-------------------------------------------------------------------------------

# RGB versions of standard colors:
rgb_standard_colors = {}
for name, color in standard_colors.items():
    rgb_standard_colors[ name ] = ( color.Red(  ) / 255.0,
                                    color.Green() / 255.0,
                                    color.Blue()  / 255.0 )

#-------------------------------------------------------------------------------
#  Define wxPython specific color facets:
#-------------------------------------------------------------------------------

# Facet whose value must be an RGB color:
RGBColor = Facet( 'white', convert_to_color, rgb_standard_colors,
                  editor = ColorEditor )

#-- EOF ------------------------------------------------------------------------