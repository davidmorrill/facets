"""
Facet definition for a PyQt-based color.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtGui \
    import QColor

from facets.core_api \
    import Facet, FacetError

from facets.core.facet_base \
    import normalized_color

from facets.ui.core_editors \
    import ColorEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The standard color types:
ColorTypes = ( int, long, tuple, list )

#-------------------------------------------------------------------------------
#  Convert a number into a QColor object:
#-------------------------------------------------------------------------------

def convert_to_color ( object, name, value ):
    """ Converts a number into a QColor object.
    """
    if isinstance( value, QColor ):
        return value

    if isinstance( value, ColorTypes ):
        return QColor( *normalized_color( value, has_alpha = True ) )

    color = None
    if isinstance( value, basestring ):
        # Allow for spaces in the string value:
        value = value.replace( ' ', '' )
    else:
        # Try the toolkit agnostic format:
        try:
            tup = eval( value )
            if isinstance( tup, tuple ):
                if 3 <= len( tup ) <= 4:
                    try:
                        color = QColor( *tup )
                    except TypeError:
                        raise FacetError
                else:
                    raise FacetError
        except:
            pass

    if color is None:
        # Let the constructor handle the value:
        try:
            color = QColor( value )
        except TypeError:
            raise FacetError

    if color.isValid():
        return color

    raise FacetError

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
#  Define PyQt specific color facets:
#-------------------------------------------------------------------------------

ColorFacets = ( Facet( 'white', standard_colors, convert_to_color,
                       editor = ColorEditor ),
                Facet( 'white', None, standard_colors, convert_to_color,
                       editor = ColorEditor ) )

def PyQtColor ( default = 'white', allow_none = False, **metadata ):
    """ Defines PyQt-specific color facets.
    """
    return ColorFacets[ allow_none is True ]( default, **metadata )

#-- EOF ------------------------------------------------------------------------