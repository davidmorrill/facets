"""
Facet definition for a Qt-based font.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtGui \
    import QFont

from facets.core_api \
    import Facet, FacetHandler, FacetError

from facets.ui.core_editors \
    import FontEditor

from facets.ui.font \
    import font_select

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping of strings to valid QFont style hints:
font_families = {
    'default':    QFont.AnyStyle,
    'decorative': QFont.Decorative,
    'roman':      QFont.Serif,
    'script':     QFont.SansSerif,
    'swiss':      QFont.SansSerif,
    'modern':     QFont.TypeWriter
}

# Mapping of strings to QFont styles:
font_styles = {
    'slant':  QFont.StyleOblique,
    'italic': QFont.StyleItalic
}

# Mapping of strings to QFont weights:
font_weights = {
    'light': QFont.Light,
    'bold':  QFont.Bold
}

# Strings to ignore in text representations of fonts:
font_noise = [ 'pt', 'point', 'family' ]

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# A cache mapping font names to FacetFont objects:
font_cache = {}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def font_to_str ( font ):
    """ Converts a QFont into a string description of itself.
    """
    weight = { QFont.Light:  ' Light',
               QFont.Bold:   ' Bold'   }.get( font.weight(), '' )
    style  = { QFont.StyleOblique:  ' Slant',
               QFont.StyleItalic:   ' Italic' }.get( font.style(), '' )
    underline = ''
    if font.underline():
        underline = ' underline'

    return '%s point %s%s%s%s' % ( font.pointSize(), unicode( font.family() ),
                                   style, weight, underline )


def create_facets_font ( value ):
    """ Creates a FacetFont object from a string description.
    """
    global font_cache

    if isinstance( value, QFont ):
        return FacetsFont( value )

    # Replace any list of fonts by a single matching font:
    value = font_select( value )

    # Check to see if the font is already in the cache, and return it if it is:
    font = font_cache.get( value )
    if font is not None:
        return font

    point_size = None
    family     = ''
    style      = QFont.StyleNormal
    weight     = QFont.Normal
    underline  = False
    facename   = []

    for word in value.split():
        lword = word.lower()
        if font_families.has_key( lword ):
            f = QFont()
            f.setStyleHint( font_families[ lword ] )
            family = f.defaultFamily()
        elif font_styles.has_key( lword ):
            style = font_styles[ lword ]
        elif font_weights.has_key( lword ):
            weight = font_weights[ lword ]
        elif lword == 'underline':
            underline = True
        elif lword not in font_noise:
            if point_size is None:
                try:
                    point_size = int( lword )
                    continue
                except:
                    pass

            facename.append( word )

    if facename:
        family = ' '.join( facename )

    if family:
        font = FacetsFont( family )
    else:
        font = FacetsFont()

    font.setStyle( style )
    font.setWeight( weight )
    font.setUnderline( underline )

    if point_size is not None:
        font.setPointSize( point_size )

    font_cache[ value ] = font

    return font

#-------------------------------------------------------------------------------
#  'FacetsFont' class:
#-------------------------------------------------------------------------------

class FacetsFont ( QFont ):
    """ A Facets-specific QFont.
    """

    #-- Public Methods ---------------------------------------------------------

    def __reduce_ex__ ( self, protocol ):
        """ Returns the pickleable form of a FacetsFont object.
        """
        return ( create_facets_font, ( font_to_str( self ), ) )


    def __str__ ( self ):
        """ Returns a printable form of the font.
        """
        return font_to_str( self )

#-------------------------------------------------------------------------------
#  'FacetQtFont' class'
#-------------------------------------------------------------------------------

class FacetQtFont ( FacetHandler ):
    """ Ensures that values assigned to a facet attribute are valid font
        descriptor strings; the value actually assigned is the corresponding
        FacetsFont.
    """

    #-- Public Methods ---------------------------------------------------------

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
        return ("a string describing a font (e.g. '12 pt bold italic "
                "swiss family Arial' or 'default 12')")

#-------------------------------------------------------------------------------
#  Define a Qt specific font facet:
#-------------------------------------------------------------------------------

QtFont = Facet( FacetsFont(), FacetQtFont(), editor = FontEditor )

#-- EOF ------------------------------------------------------------------------