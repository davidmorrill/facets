"""
Facet definition for a wxPython-based font.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.core_api \
    import Facet, FacetHandler, FacetError

from facets.ui.core_editors \
    import FontEditor

from facets.ui.font \
    import font_select

#-------------------------------------------------------------------------------
#  Convert a string into a valid 'wxFont' object (if possible):
#-------------------------------------------------------------------------------

# Mapping of strings to valid wxFont families:
font_families = {
    'default':    wx.DEFAULT,
    'decorative': wx.DECORATIVE,
    'roman':      wx.ROMAN,
    'script':     wx.SCRIPT,
    'swiss':      wx.SWISS,
    'modern':     wx.MODERN
}

# Mapping of strings to wxFont styles:
font_styles = {
    'slant':  wx.SLANT,
    'italic': wx.ITALIC
}

# Mapping of strings wxFont weights:
font_weights = {
    'light': wx.LIGHT,
    'bold':  wx.BOLD
}

# Strings to ignore in text representations of fonts:
font_noise = [ 'pt', 'point', 'family' ]

#-------------------------------------------------------------------------------
#  Converts a wx.Font into a string description of itself:
#-------------------------------------------------------------------------------

def font_to_str ( font ):
    """ Converts a wx.Font into a string description of itself.
    """
    weight = { wx.LIGHT:  ' Light',
               wx.BOLD:   ' Bold'   }.get( font.GetWeight(), '' )
    style  = { wx.SLANT:  ' Slant',
               wx.ITALIC: ' Italic' }.get( font.GetStyle(), '' )
    underline = ''
    if font.GetUnderlined():
        underline = ' underline'
    return '%s point %s%s%s%s' % (
           font.GetPointSize(), font.GetFaceName(), style, weight, underline )

#-------------------------------------------------------------------------------
#  Create a FacetFont object from a string description:
#-------------------------------------------------------------------------------

def create_facets_font ( value ):
    """ Create a FacetFont object from a string description.
    """
    if isinstance( value, wx.Font ):
        value = font_to_str( value )

    # Replace any list of fonts by a single matching font:
    value = font_select( value )

    point_size = None
    family     = wx.DEFAULT
    style      = wx.NORMAL
    weight     = wx.NORMAL
    underline  = 0
    facename   = []
    for word in value.split():
        lword = word.lower()
        if font_families.has_key( lword ):
            family = font_families[ lword ]
        elif font_styles.has_key( lword ):
            style = font_styles[ lword ]
        elif font_weights.has_key( lword ):
            weight = font_weights[ lword ]
        elif lword == 'underline':
            underline = 1
        elif lword not in font_noise:
            if point_size is None:
                try:
                    point_size = int( lword )
                    continue
                except:
                    pass

            facename.append( word )

    return FacetsFont( point_size or 10, family, style, weight, underline,
                       ' '.join( facename ) )

#-------------------------------------------------------------------------------
#  'FacetsFont' class:
#-------------------------------------------------------------------------------

class FacetsFont ( wx.Font ):
    """ A Facets-specific wx.Font.
    """

    def __reduce_ex__ ( self, protocol ):
        """ Returns the pickleable form of a FacetsFont object.
        """
        return ( create_facets_font, ( font_to_str( self ), ) )


    def __str__ ( self ):
        """ Returns a printable form of the font.
        """
        return font_to_str( self )

#-------------------------------------------------------------------------------
#  'FacetWXFont' class'
#-------------------------------------------------------------------------------

class FacetWXFont ( FacetHandler ):
    """ Ensures that values assigned to a facet attribute are valid font
        descriptor strings; the value actually assigned is the corresponding
        FacetsFont.
    """

    def validate ( self, object, name, value ):
        """ Validates that the value is a valid font descriptor string. If so,
            it returns the corresponding FacetsFont; otherwise, it raises a
            FacetError.
        """
        if value is None:
            return None

        try:
            return create_facets_font( value )
        except:
            pass

        raise FacetError(
            object, name, 'a font descriptor string', repr( value )
        )

    def info ( self ):
        return ( "a string describing a font (e.g. '12 pt bold italic "
                 "swiss family Arial' or 'default 12')" )

#-------------------------------------------------------------------------------
#  Define a wxPython specific font facet:
#-------------------------------------------------------------------------------

fh     = FacetWXFont()
WxFont = Facet( create_facets_font( 'Arial 10' ), fh, editor = FontEditor )

#-- EOF ------------------------------------------------------------------------