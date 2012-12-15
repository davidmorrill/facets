"""
Facet definition for a Qt-based color.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtGui \
    import QColor

from facets.core_api \
    import Facet, FacetError

from facets.ui.core_editors \
    import ColorEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The standard integer types:
IntTypes = ( int, long )

#-------------------------------------------------------------------------------
#  Convert a number into a QColor object:
#-------------------------------------------------------------------------------

def convert_to_color ( object, name, value ):
    """ Converts a number into a QColor object.
    """
    # Handle the case of a number of the form: 0xAARRGGBB, where the alpha AA
    # value is inverted (i.e. 00 = opaque, FF = transparent):
    if isinstance( value, IntTypes ):
        return QColor( int( (value >> 16) & 0xFF ),
                       int( (value >>  8) & 0xFF ),
                       int( value         & 0xFF ),
                       int( 255 - ((value >> 24) & 0xFF) ) )

    # Try the toolkit agnostic format.
    try:
        tup = eval( value )
    except:
        tup = value

    if isinstance( tup, tuple ):
        if 3 <= len( tup ) <= 4:
            try:
                color = QColor( *tup )
            except TypeError:
                raise FacetError
        else:
            raise FacetError
    else:
        if isinstance( value, basestring ):
            # Allow for spaces in the string value.
            value = value.replace( ' ', '' )

        # Let the standard ctors handle the value.
        try:
            color = QColor( value )
        except TypeError:
            raise FacetError

    if not color.isValid():
        raise FacetError

    return color

convert_to_color.info = ('a string of the form (r,g,b) or (r,g,b,a) where r, '
                         'g, b, and a are integers from 0 to 255, a QColor '
                         'instance, a Qt.GlobalColor, an integer which in hex '
                         'is of the form 0xRRGGBB, a string of the form #RGB, '
                         '#RRGGBB, #RRRGGGBBB or #RRRRGGGGBBBB')

#-------------------------------------------------------------------------------
#  Standard colors:
#-------------------------------------------------------------------------------

# Note that this is slightly different from the wx implementation in that the
# names do not include spaces and the full set of SVG color keywords is
# supported.
standard_colors = {}
for name in QColor.colorNames():
    standard_colors[ str( name ) ] = QColor( name )

#-------------------------------------------------------------------------------
#  Define Qt specific color facets:
#-------------------------------------------------------------------------------

ColorFacets = ( Facet( 'white', standard_colors, convert_to_color,
                       editor = ColorEditor ),
                Facet( 'white', None, standard_colors, convert_to_color,
                       editor = ColorEditor ) )

def QtColor ( default = 'white', allow_none = False, **metadata ):
    """ Defines Qt-specific color facets.
    """
    return ColorFacets[ allow_none is True ]( default, **metadata )

#-- EOF ------------------------------------------------------------------------