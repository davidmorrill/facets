"""
Facet definition for a wxPython-based color.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.core_api \
    import Facet, FacetError

from facets.api \
    import ColorEditor

# Version dependent imports (ColourPtr not defined in wxPython 2.5):
try:
    ColourPtr = wx.ColourPtr
except:
    class ColourPtr ( object ): pass

#-------------------------------------------------------------------------------
#  Convert a number into a wxColour object:
#-------------------------------------------------------------------------------

def convert_to_color ( object, name, value ):
    """ Converts a number into a wxColour object.
    """
    # Try the GUI toolkit neutral format:
    try:
        tup = eval( value )
    except:
        tup = value

    if isinstance( tup, tuple ):
        if 3 <= len( tup ) <= 4:
            for c in tup:
                if not isinstance( c, int ):
                    raise FacetError

            return wx.Colour( *tup )
        else:
            raise FacetError

    if isinstance( value, ColourPtr ):
        return wx.Colour( value.Red(), value.Green(), value.Blue() )

    elif isinstance( value, wx.Colour ):
        return value

    elif isinstance( value, str ) and value in standard_colors:
        return wx.NamedColour( value )

    elif isinstance( value, int ):
        num = int( value )
        return wx.Colour( num / 0x10000, ( num / 0x100 ) & 0xFF, num & 0xFF )

    raise FacetError

convert_to_color.info = ('a string of the form (r,g,b) or (r,g,b,a) where r, '
                         'g, b, and a are integers from 0 to 255, a wx.Colour '
                         'instance, an integer which in hex is of the form '
                         '0xRRGGBB, where RR is red, GG is green, and BB is '
                         'blue')

#-------------------------------------------------------------------------------
#  Standard colors:
#-------------------------------------------------------------------------------

standard_colors = {}
for name in [ 'aquamarine', 'black', 'blue', 'blue violet', 'brown',
              'cadet blue', 'coral', 'cornflower blue', 'cyan', 'dark grey',
              'dark green', 'dark olive green', 'dark orchid',
              'dark slate blue', 'dark slate grey', 'dark turquoise',
              'dim grey', 'firebrick', 'forest green', 'gold', 'goldenrod',
              'grey', 'green', 'green yellow', 'indian red', 'khaki',
              'light blue', 'light grey', 'light steel blue', 'lime green',
              'magenta', 'maroon', 'medium aquamarine', 'medium blue',
              'medium forest green', 'medium goldenrod', 'medium orchid',
              'medium sea green', 'medium slate blue', 'medium spring green',
              'medium turquoise', 'medium violet red', 'midnight blue', 'navy',
              'orange', 'orange red', 'orchid', 'pale green', 'pink', 'plum',
              'purple', 'red', 'salmon', 'sea green', 'sienna', 'sky blue',
              'slate blue', 'spring green', 'steel blue', 'tan', 'thistle',
              'turquoise', 'violet', 'violet red', 'wheat', 'white', 'yellow',
              'yellow green' ]:
    try:
        standard_colors[ name ] = convert_to_color( None, None,
                                                    wx.NamedColour( name ) )
    except:
        pass

#-------------------------------------------------------------------------------
#  Define wxPython specific color facets:
#-------------------------------------------------------------------------------

ColorFacets = ( Facet( 'white', standard_colors, convert_to_color,
                       editor = ColorEditor ),
                Facet( 'white', None, standard_colors, convert_to_color,
                       editor = ColorEditor ) )

def WxColor ( default = 'white', allow_none = False, **metadata ):
    """ Defines wxPython-specific color facets.
    """
    return ColorFacets[ allow_none is True ]( default, **metadata )

#-- EOF ------------------------------------------------------------------------