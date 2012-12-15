"""
Facet definition for a null-based (i.e., no UI) font.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Facet, FacetHandler, FacetError

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping of strings to valid font families
font_families = [
    'default',
    'decorative',
    'roman',
    'script',
    'swiss',
    'modern'
]


# Mapping of strings to font styles
font_styles = [
    'slant',
    'italic'
]


# Mapping of strings font weights
font_weights = [
    'light',
    'bold'
]


# Strings to ignore in text representations of fonts
font_noise = [ 'pt', 'point', 'family' ]

#-------------------------------------------------------------------------------
#  'FacetFont' class'
#-------------------------------------------------------------------------------

class FacetFont ( FacetHandler ):
    """ Ensures that values assigned to a facet attribute are valid font
        descriptor strings; the value actually assigned is the corresponding
        canonical font descriptor string.
    """

    #-- Public Methods ---------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that the value is a valid font descriptor string.
        """
        try:
            point_size = family = style = weight = underline = ''
            facename   = [ ]
            for word in value.split():
                lword = word.lower()
                if lword in font_families:
                    family = ' ' + lword
                elif lword in font_styles:
                    style = ' ' + lword
                elif lword in font_weights:
                    weight = ' ' + lword
                elif lword == 'underline':
                    underline = ' ' + lword
                elif lword not in font_noise:
                    try:
                        int( lword )
                        point_size = lword + ' pt'
                    except:
                        facename.append( word )

            return ( '%s%s%s%s%s%s' % ( point_size, family, style, weight,
                    underline, ' '.join( facename ) ) ).strip()
        except:
            pass

        raise FacetError(
            object, name, 'a font descriptor string', repr( value )
        )

    def info ( self ):
        return ("a string describing a font (e.g. '12 pt bold italic "
                "swiss family Arial' or 'default 12')")

#-------------------------------------------------------------------------------
#  Define a 'null' specific font facet:
#-------------------------------------------------------------------------------

fh       = FacetFont()
NullFont = Facet( fh.validate( None, None, 'Arial 10' ), fh )

#-- EOF ------------------------------------------------------------------------