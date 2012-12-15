"""
Utility functions for working with wx Fonts.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

#-------------------------------------------------------------------------------
#  Function Definitions:
#-------------------------------------------------------------------------------

def new_font_like ( font, **kw ):
    """ Creates a new font, like another one, only different.  Maybe.
    """
    point_size = kw.get( 'point_size', font.GetPointSize() )
    family     = kw.get( 'family', font.GetFamily() )
    style      = kw.get( 'style', font.GetStyle() )
    weight     = kw.get( 'weight', font.GetWeight() )
    underline  = kw.get( 'underline', font.GetUnderlined() )
    face_name  = kw.get( 'face_name', font.GetFaceName() )

    return wx.Font( point_size, family, style, weight, underline, face_name )

#-- EOF ------------------------------------------------------------------------